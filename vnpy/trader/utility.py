"""
General utility functions.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Callable, Dict, Tuple, Union, Optional
from decimal import Decimal
from math import floor, ceil

import numpy as np

from .object import BarData, TickData
from .constant import Exchange, Interval

import csv
import re
from pandas import DataFrame
from .futures import FuturesProductDict
from datetime import datetime, timedelta

log_formatter = logging.Formatter('[%(asctime)s] %(message)s')


def extract_vt_symbol(vt_symbol: str) -> Tuple[str, Exchange]:
    """
    :return: (symbol, exchange)
    """
    symbol, exchange_str = vt_symbol.split(".")
    return symbol, Exchange(exchange_str)


def generate_vt_symbol(symbol: str, exchange: Exchange) -> str:
    """
    return vt_symbol
    """
    return f"{symbol}.{exchange.value}"


def _get_trader_dir(temp_name: str) -> Tuple[Path, Path]:
    """
    Get path where trader is running in.
    """
    cwd = Path.cwd()
    temp_path = cwd.joinpath(temp_name)

    # If .vntrader folder exists in current working directory,
    # then use it as trader running path.
    if temp_path.exists():
        return cwd, temp_path

    # Otherwise use home path of system.
    home_path = Path.home()
    temp_path = home_path.joinpath(temp_name)

    # Create .vntrader folder under home path if not exist.
    if not temp_path.exists():
        temp_path.mkdir()

    return home_path, temp_path


TRADER_DIR, TEMP_DIR = _get_trader_dir(".vntrader")
sys.path.append(str(TRADER_DIR))


def get_file_path(filename: str) -> Path:
    """
    Get path for temp file with filename.
    """
    return TEMP_DIR.joinpath(filename)


def get_folder_path(folder_name: str) -> Path:
    """
    Get path for temp folder with folder name.
    """
    folder_path = TEMP_DIR.joinpath(folder_name)
    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path


def get_icon_path(filepath: str, ico_name: str) -> str:
    """
    Get path for icon file with ico name.
    """
    ui_path = Path(filepath).parent
    icon_path = ui_path.joinpath("ico", ico_name)
    return str(icon_path)


def load_json(filename: str) -> dict:
    """
    Load data from json file in temp path.
    """
    filepath = get_file_path(filename)

    if filepath.exists():
        with open(filepath, mode="r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    else:
        save_json(filename, {})
        return {}


def save_json(filename: str, data: dict) -> None:
    """
    Save data into json file in temp path.
    """
    filepath = get_file_path(filename)
    with open(filepath, mode="w+", encoding="UTF-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def round_to(value: float, target: float) -> float:
    """
    Round price to price tick value.
    """
    value = Decimal(str(value))
    target = Decimal(str(target))
    rounded = float(int(round(value / target)) * target)
    return rounded


def load_csv(file_name: str, folder_name: str = ""):
    """
    Load data from csv file in temp path.
    """
    folder_path = get_folder_path(folder_name)
    file_path = folder_path.joinpath(file_name)
    if file_path.exists():
        with open(file_path, mode="rt", encoding="UTF-8") as f:
            reader = csv.DictReader(f)
            data = [item for item in reader]
        return data
    else:
        return {}


def save_csv(file_name: str, data: DataFrame, folder_name: str = ""):
    """
    Save data into csv file in temp path.
    """
    folder_path = get_folder_path(folder_name)
    file_path = folder_path.joinpath(file_name)
    data.to_csv(file_path, index=False, encoding="ANSI")


def is_trading_time(vt_symbol):
    """
    判断当前是否为某个品种的交易时间
    """
    symbol, _ = extract_vt_symbol(vt_symbol)
    product_name = re.sub(r'\d', "", symbol)
    futures = FuturesProductDict.get(product_name, None)
    if not futures:
        return True

    now = datetime.now().strftime("%H:%M:%S")

    time_slices = futures.time_slices
    for time_slice in time_slices:
        if time_slice[1] < time_slice[0]:
            if now > time_slice[0] or now < time_slice[1]:
                return True
        else:
            if time_slice[0] < now < time_slice[1]:
                return True

    return False


def get_trading_day(time: datetime = datetime.today()):
    """
    获取当前交易日.
    """
    if time.hour > 18:
        # 每天晚上18点后，则认为第二天，周五晚上认为下周一.
        if time.weekday() == 4:
            time = time + timedelta(days=3)
        else:
            time = time + timedelta(days=1)
    return time.strftime("%Y%m%d")


def convert_symbol_to_vt_symbol(symbol):
    """把股票六位代码转化成vt_symbol"""
    if symbol.startswith("6") or symbol.startswith("5"):
        return ".".join([symbol, "SSE"])
    if symbol.startswith("0") or symbol.startswith("3") or symbol.startswith("1"):
        return ".".join([symbol, "SZSE"])


def floor_to(value: float, target: float) -> float:
    """
    Similar to math.floor function, but to target float number.
    """
    value = Decimal(str(value))
    target = Decimal(str(target))
    result = float(int(floor(value / target)) * target)
    return result


def ceil_to(value: float, target: float) -> float:
    """
    Similar to math.ceil function, but to target float number.
    """
    value = Decimal(str(value))
    target = Decimal(str(target))
    result = float(int(ceil(value / target)) * target)
    return result


def get_digits(value: float) -> int:
    """
    Get number of digits after decimal point.
    """
    value_str = str(value)

    if "e-" in value_str:
        _, buf = value_str.split("e-")
        return int(buf)
    elif "." in value_str:
        _, buf = value_str.split(".")
        return len(buf)
    else:
        return 0


class BarGenerator:
    """
    For:
    1. generating 1 minute bar data from tick data
    2. generateing x minute bar/x hour bar data from 1 minute data

    Notice:
    1. for x minute bar, x must be able to divide 60: 2, 3, 5, 6, 10, 15, 20, 30
    2. for x hour bar, x can be any number
    """

    def __init__(
        self,
        on_bar: Callable,
        window: int = 0,
        on_window_bar: Callable = None,
        interval: Interval = Interval.MINUTE
    ):
        """Constructor"""
        self.bar: BarData = None
        self.on_bar: Callable = on_bar

        self.interval: Interval = interval
        self.interval_count: int = 0

        self.window: int = window
        self.window_bar: BarData = None
        self.on_window_bar: Callable = on_window_bar

        self.last_tick: TickData = None
        self.last_bar: BarData = None

    def update_tick(self, tick: TickData) -> None:
        """
        Update new tick data into generator.
        """
        new_minute = False

        # Filter tick data with 0 last price
        if not tick.last_price:
            return

        # Filter tick data with older timestamp
        if self.last_tick and tick.datetime < self.last_tick.datetime:
            return

        if not self.bar:
            new_minute = True
        elif (
            (self.bar.datetime.minute != tick.datetime.minute)
            or (self.bar.datetime.hour != tick.datetime.hour)
        ):
            self.bar.datetime = self.bar.datetime.replace(
                second=0, microsecond=0
            )
            self.on_bar(self.bar)

            new_minute = True

        if new_minute:
            self.bar = BarData(
                symbol=tick.symbol,
                exchange=tick.exchange,
                interval=Interval.MINUTE,
                datetime=tick.datetime,
                gateway_name=tick.gateway_name,
                open_price=tick.last_price,
                high_price=tick.last_price,
                low_price=tick.last_price,
                close_price=tick.last_price,
                open_interest=tick.open_interest
            )
        else:
            self.bar.high_price = max(self.bar.high_price, tick.last_price)
            if tick.high_price > self.last_tick.high_price:
                self.bar.high_price = max(self.bar.high_price, tick.high_price)

            self.bar.low_price = min(self.bar.low_price, tick.last_price)
            if tick.low_price < self.last_tick.low_price:
                self.bar.low_price = min(self.bar.low_price, tick.low_price)

            self.bar.close_price = tick.last_price
            self.bar.open_interest = tick.open_interest
            self.bar.datetime = tick.datetime

        if self.last_tick:
            volume_change = tick.volume - self.last_tick.volume
            self.bar.volume += max(volume_change, 0)

        # 加上window bar的生成方法

        if not self.window:
            self.last_tick = tick
            return

        if not self.window_bar:

            dt = tick.datetime
            self.window_bar = BarData(
                symbol=tick.symbol,
                exchange=tick.exchange,
                datetime=dt,
                gateway_name=tick.gateway_name,
                open_price=tick.last_price,
                high_price=tick.last_price,
                low_price=tick.last_price
            )
        else:
            self.window_bar.high_price = max(
                self.window_bar.high_price, tick.last_price)
            self.window_bar.low_price = min(
                self.window_bar.low_price, tick.last_price)

        # Update close price/volume into window bar
        self.window_bar.close_price = tick.last_price
        self.window_bar.volume = int(tick.volume)
        self.window_bar.open_interest = tick.open_interest

        finished = False

        if self.interval == Interval.MINUTE:
            # x-minute bar
            hour_change = False
            minute_change = False

            if self.last_tick:
                hour_change = tick.datetime.hour != self.last_tick.datetime.hour
                minute_change = tick.datetime.minute != self.last_tick.datetime.minute
            if hour_change or minute_change:
                if tick.datetime.minute % self.window == 0:
                    finished = True
        elif self.interval == Interval.HOUR:
            hour_change = False
            if self.last_tick:
                hour_change = tick.datetime.hour != self.last_tick.datetime.hour
            if hour_change:
                # 1-hour bar
                if self.window == 1:
                    finished = True
                # x-hour bar
                else:
                    self.interval_count += 1

                    if self.interval_count % self.window == 0:
                        finished = True
                        self.interval_count = 0

        if finished:
            self.last_window_bar = self.window_bar
            self.on_window_bar(self.window_bar)
            self.window_bar = None

        self.last_tick = tick

    def update_bar(self, bar: BarData) -> None:
        """
        Update 1 minute bar into generator
        """
        # If not inited, creaate window bar object
        if not self.window_bar:
            # Generate timestamp for bar data
            if self.interval == Interval.MINUTE:
                dt = bar.datetime.replace(second=0, microsecond=0)
            else:
                dt = bar.datetime.replace(minute=0, second=0, microsecond=0)

            self.window_bar = BarData(
                symbol=bar.symbol,
                exchange=bar.exchange,
                datetime=dt,
                gateway_name=bar.gateway_name,
                open_price=bar.open_price,
                high_price=bar.high_price,
                low_price=bar.low_price
            )
        # Otherwise, update high/low price into window bar
        else:
            self.window_bar.high_price = max(
                self.window_bar.high_price, bar.high_price)
            self.window_bar.low_price = min(
                self.window_bar.low_price, bar.low_price)

        # Update close price/volume into window bar
        self.window_bar.close_price = bar.close_price
        self.window_bar.volume += int(bar.volume)
        self.window_bar.open_interest = bar.open_interest

        # Check if window bar completed
        finished = False

        if self.interval == Interval.MINUTE:
            # x-minute bar
            if not (bar.datetime.minute + 1) % self.window:
                finished = True
        elif self.interval == Interval.HOUR:
            if self.last_bar:
                new_hour = bar.datetime.hour != self.last_bar.datetime.hour
                last_minute = bar.datetime.minute == 59

                if new_hour or last_minute:
                    # 1-hour bar
                    if self.window == 1:
                        finished = True
                    # x-hour bar
                    else:
                        self.interval_count += 1

                        if not self.interval_count % self.window:
                            finished = True
                            self.interval_count = 0

        if finished:
            self.on_window_bar(self.window_bar)
            self.window_bar = None

        # Cache last bar object
        self.last_bar = bar

    def generate(self) -> Optional[BarData]:
        """
        Generate the bar data and call callback immediately.
        """
        bar = self.bar

        if self.bar:
            bar.datetime = bar.datetime.replace(second=0, microsecond=0)
            self.on_bar(bar)

        self.bar = None
        return bar


class ArrayManager(object):
    """
    For:
    1. time series container of bar data
    2. calculating technical indicator value
    """

    def __init__(self, size: int = 100):
        """Constructor"""
        self.count: int = 0
        self.size: int = size
        self.inited: bool = False

        self.open_array: np.ndarray = np.zeros(size)
        self.high_array: np.ndarray = np.zeros(size)
        self.low_array: np.ndarray = np.zeros(size)
        self.close_array: np.ndarray = np.zeros(size)
        self.volume_array: np.ndarray = np.zeros(size)
        self.open_interest_array: np.ndarray = np.zeros(size)

    def update_bar(self, bar: BarData) -> None:
        """
        Update new bar data into array manager.
        """
        self.count += 1
        if not self.inited and self.count >= self.size:
            self.inited = True

        self.open_array[:-1] = self.open_array[1:]
        self.high_array[:-1] = self.high_array[1:]
        self.low_array[:-1] = self.low_array[1:]
        self.close_array[:-1] = self.close_array[1:]
        self.volume_array[:-1] = self.volume_array[1:]
        self.open_interest_array[:-1] = self.open_interest_array[1:]

        self.open_array[-1] = bar.open_price
        self.high_array[-1] = bar.high_price
        self.low_array[-1] = bar.low_price
        self.close_array[-1] = bar.close_price
        self.volume_array[-1] = bar.volume
        self.open_interest_array[-1] = bar.open_interest

    @property
    def open(self) -> np.ndarray:
        """
        Get open price time series.
        """
        return self.open_array

    @property
    def high(self) -> np.ndarray:
        """
        Get high price time series.
        """
        return self.high_array

    @property
    def low(self) -> np.ndarray:
        """
        Get low price time series.
        """
        return self.low_array

    @property
    def close(self) -> np.ndarray:
        """
        Get close price time series.
        """
        return self.close_array

    @property
    def volume(self) -> np.ndarray:
        """
        Get trading volume time series.
        """
        return self.volume_array

    @property
    def open_interest(self) -> np.ndarray:
        """
        Get trading volume time series.
        """
        return self.open_interest_array


def virtual(func: Callable) -> Callable:
    """
    mark a function as "virtual", which means that this function can be override.
    any base class should use this or @abstractmethod to decorate all functions
    that can be (re)implemented by subclasses.
    """
    return func


file_handlers: Dict[str, logging.FileHandler] = {}


def _get_file_logger_handler(filename: str) -> logging.FileHandler:
    handler = file_handlers.get(filename, None)
    if handler is None:
        handler = logging.FileHandler(filename)
        file_handlers[filename] = handler  # Am i need a lock?
    return handler


def get_file_logger(filename: str) -> logging.Logger:
    """
    return a logger that writes records into a file.
    """
    logger = logging.getLogger(filename)
    handler = _get_file_logger_handler(filename)  # get singleton handler.
    handler.setFormatter(log_formatter)
    logger.addHandler(handler)  # each handler will be added only once.
    return logger
