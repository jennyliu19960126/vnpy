import os
import re
import pymongo
import csv
from typing import Sequence
from threading import Thread
from queue import Queue, Empty
from copy import copy
from time import sleep

from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.event import EventEngine

from vnpy.trader.utility import load_json, extract_vt_symbol
from datetime import timedelta
from .data_objects import *

from vnpy.trader.object import LogData
from vnpy.event import Event

from vnpy.app.database_manager.parse_tool_futures import parse_all_futures_data
from vnpy.app.database_manager.parse_tool_futures_tushare import parse_all_futures_data_tushare
from vnpy.app.database_manager.parse_tool_equity import TuShareClient
from vnpy.trader.event import EVENT_LOG

APP_NAME = "DatabaseManager"


class DatabaseManagerEngine(BaseEngine):

    setting_filename = "database_manager_setting.json"

    client = None
    day_bar_thread = None
    fundamental_thread = None
    dividend_thread = None
    metrics_thread = None

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        """"""
        super().__init__(main_engine, event_engine, APP_NAME)

        self.main_engine = main_engine
        self.event_engine = event_engine

        self.database_setting = {}

        self.connect()

        self.queue = Queue()
        self.thread = Thread(target=self.run)

        self.active = True
        self.thread.start()

        self.loading_queue = Queue()
        self.loading_thread = None

    def connect(self):
        """"""
        # 我们要先从配置文件读取地址
        self.database_setting = load_json(self.setting_filename)
        host = self.database_setting["host"]
        port = self.database_setting["port"]
        # 然后连接
        self.client = pymongo.MongoClient(f"mongodb://{host}:{port}/")

    def disconnect(self):
        """"""
        self.client = None

    def run(self):
        """
        处理的事件类型
        tick，bar_1min, bar_day, st_bar_day (st for stock)
        order, trade, variable, position, account
        st_fundamental是股票的基本面信息
        """
        while self.active:
            try:
                task = self.queue.get(timeout=1)
                task_type, datas = task
                dbname = self.database_setting[task_type + "_dbname"]

                if task_type in ["tick", "bar_1min", "bar_day", "st_bar_day", "st_metrics"]:
                    for d in datas:
                        vt_symbol = d.vt_symbol
                        collection_to_update = self.client[dbname][vt_symbol]
                        query = {"datetime": d.datetime}
                        new_values = {"$set": d.__dict__}
                        collection_to_update.update_one(query, new_values, upsert=True)
                elif task_type in ["order", "trade"]:
                    for d in datas:
                        strategy_name = d.strategy_name
                        self.client[dbname][strategy_name].insert_one(d.__dict__)
                elif task_type in ["variable"]:
                    for d in datas:
                        strategy_name = d["strategy_name"]
                        d["input_time"] = datetime.now()
                        self.client[dbname][strategy_name].insert_one(d)
                elif task_type in ["position", "account"]:
                    for d in datas:
                        gateway_name = d["gateway_name"]
                        d["input_time"] = datetime.now()
                        self.client[dbname][gateway_name].insert_one(d)
                elif task_type in ["st_fundamental"]:
                    for d in datas:
                        vt_symbol = d.vt_symbol
                        collection_to_update = self.client[dbname][vt_symbol]
                        query = {"end_date": d.end_date}
                        new_values = {"$set": d.__dict__}
                        collection_to_update.update_one(query, new_values, upsert=True)
                elif task_type in ["st_dividend"]:
                    for d in datas:
                        vt_symbol = d.vt_symbol
                        collection_to_update = self.client[dbname][vt_symbol]
                        query = {"end_date": d.end_date, "decision_status": d.decision_status}
                        new_values = {"$set": d.__dict__}
                        collection_to_update.update_one(query, new_values, upsert=True)

            except Empty:
                continue

    def save_tick_data(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbTickData对象
        每个字典里面应包含合约名称
        """
        task = ("tick", copy(datas))
        self.queue.put(task)

    def save_bar_1min(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbBarData对象
        每个字典里面应包含合约名称
        """
        task = ("bar_1min", copy(datas))
        self.queue.put(task)

    def save_bar_day(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbBarData对象
        每个字典里面应包含合约名称
        """
        task = ("bar_day", copy(datas))
        self.queue.put(task)

    def save_order_data(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbOrderData的对象
        每个字典里面应包含交易单元的名称
        """
        task = ("order", copy(datas))
        self.queue.put(task)

    def save_trade_data(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbTradeData的对象
        每个字典里面应包含交易单元的名称
        """
        task = ("trade", copy(datas))
        self.queue.put(task)

    def save_variable_data(self, datas: list):
        """
        输入的参数data应该是一个列表，里面有很多dict
        """
        task = ("variable", copy(datas))
        self.queue.put(task)

    def save_position_data(self, datas: list):
        """
        输入的参数data应该是一个列表，里面有很多dict
        """
        task = ("position", copy(datas))
        self.queue.put(task)

    def save_account_data(self, datas: list):
        """
        输入的参数data应该是一个列表，里面有很多dict
        """
        task = ("account", copy(datas))
        self.queue.put(task)

    def save_stock_bar_day(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbBarData对象
        每个字典里面应包含合约名称
        """
        task = ("st_bar_day", copy(datas))
        self.queue.put(task)

    def save_stock_metrics_day(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbBarData对象
        每个字典里面应包含合约名称
        """
        task = ("st_metrics", copy(datas))
        self.queue.put(task)

    def save_stock_dividend_data(self, datas: list):
        """
        输入参数data应该是一个列表，里面有很多DbDividendData对象
        每个字典里面应包含合约名称
        """
        task = ("st_dividend", copy(datas))
        self.queue.put(task)

    def save_stock_fundamental_data(self, datas: list):
        """
        输入的参数data应该是一个列表，里面有很多DbFundamental对象
        """
        task = ("st_fundamental", copy(datas))
        self.queue.put(task)

    def save_all_parameter_info(self):
        """从csv读取参数信息，保存到数据库参数表里"""
        local_parameter_path = self.database_setting["local_parameter_path"]
        parameter_dbname = self.database_setting["parameter_dbname"]

        for file_name in os.listdir(local_parameter_path):
            strategy_name, _ = file_name.split(".")
            file_path = local_parameter_path + strategy_name + ".csv"

            with open(file_path, "rt") as f:
                reader = csv.DictReader(f)
                collection_to_update = self.client[parameter_dbname][strategy_name]
                for item in reader:
                    query = {"setno": item["setno"]}
                    new_values = {"$set": item}

                    collection_to_update.update_one(query, new_values, upsert=True)

    def get_parameter_info(self, strategy_name: str, setno: int):
        """
        从数据库里读取特定setno的策略参数
        返回一个类似下面的字典：
        {
            "n": 6,
            "m": 3,
            "filter": 20
        }
        """
        parameter_dbname = self.database_setting["parameter_dbname"]
        collection = self.client[parameter_dbname][strategy_name]
        query = {"setno": setno}

        cursor = collection.find(query)
        data = list(cursor)[0]
        data.pop("_id")
        data.pop("setno")

        # 把字符串转化为数字
        for key in data:
            try:
                data[key] = float(data[key]) if "." in data[key] else int(data[key])
            except ValueError:
                pass
            except TypeError:
                pass

        return data

    def get_bar_1min(
        self,
        vt_symbol: str,
        days: int = 10
    ) -> Sequence[BarData]:
        """
        查询数据库中的bar，返回list，list里面是BarData对象
        """
        bar_1min_dbname = self.database_setting["bar_1min_dbname"]
        now = datetime.now()
        earliest_datetime = now - timedelta(days=days)

        query = {"datetime": {"$gt": earliest_datetime}}
        cursor = self.client[bar_1min_dbname][vt_symbol].find(query)

        s = []
        for item in cursor:
            item.pop('_id')
            s.append(DbBarData(**item))

        # 把数据库中得到的字典赋给一个DbBarData对象
        data = [db_bar.to_bar() for db_bar in s]
        return data

    def get_bar_day(
        self,
        vt_symbol: str,
        days: int = 100
    ) -> Sequence[BarData]:
        """
        查询期货数据库中的bar，返回list，list里面是BarData对象
        """
        bar_day_dbname = self.database_setting["bar_day_dbname"]
        now = datetime.now()
        earliest_datetime = now - timedelta(days=days)

        query = {"datetime": {"$gt": earliest_datetime}}
        cursor = self.client[bar_day_dbname][vt_symbol].find(query)

        s = []
        for item in cursor:
            item.pop('_id')
            s.append(DbBarData(**item))

        # 把数据库中得到的字典赋给一个DbBarData对象
        data = [db_bar.to_bar() for db_bar in s]
        return data

    def get_newest_bar_day(self, vt_symbol: str):
        """
        返回一个BarData对象
        """
        bar_day_dbname = self.database_setting["bar_day_dbname"]
        # 按日期
        cursor = self.client[bar_day_dbname][vt_symbol].find().sort("datetime", -1)
        l = list(cursor)
        if l:
            data_dict = l[0]
            data_dict.pop("_id")
            bar = DbBarData(**data_dict).to_bar()

            return bar

    def get_stock_bar_day(self, vt_symbol, days=100) -> Sequence[DbStockBarData]:
        """
        返回一个list，里面都是DbStockBarData对象
        """
        bar_day_dbname = self.database_setting["st_bar_day_dbname"]
        now = datetime.now()
        earliest_datetime = now - timedelta(days=days)

        query = {"datetime": {"$gt": earliest_datetime}}
        cursor = self.client[bar_day_dbname][vt_symbol].find(query)

        datas = []
        for item in cursor:
            item.pop('_id')
            datas.append(DbStockBarData(**item))

        return datas

    def get_stock_fundamentals(self, vt_symbol) -> Sequence[DbStockFundamentalData]:
        """
        返回一个list，里面都是DbStockFundamentalData对象
        """
        bar_day_dbname = self.database_setting["st_fundamental_dbname"]

        cursor = self.client[bar_day_dbname][vt_symbol].find()

        datas = []
        for item in cursor:
            item.pop('_id')
            datas.append(DbStockFundamentalData(**item))

        return datas

    def get_stock_dividend(self, vt_symbol) -> Sequence[DbStockDividendData]:
        """
        返回一个list，里面都是DbStockFundamentalData对象
        """
        dividend_dbname = self.database_setting["st_dividend_dbname"]

        cursor = self.client[dividend_dbname][vt_symbol].find()

        datas = []
        for item in cursor:
            item.pop('_id')
            datas.append(DbStockDividendData(**item))

        return datas

    def get_order_data(self, strategy_name: str, date: datetime = None):
        """
        日末统计交易单元数据时使用
        """
        dbname = self.database_setting["order_dbname"]
        if not date:
            date = datetime.today()
            date = date.replace(hour=16, minute=30)

        if date.weekday() == 0:
            earliest_datetime = date - timedelta(days=3)
        else:
            earliest_datetime = date - timedelta(days=1)

        query = {"input_time": {"$gt": earliest_datetime}}
        cursor = self.client[dbname][strategy_name].find(query)

        datas = []
        for item in cursor:
            item.pop('_id')
            datas.append(item)

        return datas

    def get_trade_data(self, strategy_name: str, date: datetime = None):
        """
        日末统计交易单元数据时使用
        """
        dbname = self.database_setting["trade_dbname"]
        if not date:
            date = datetime.today()
            date = date.replace(hour=16, minute=30)

        if date.weekday() == 0:
            earliest_datetime = date - timedelta(days=3)
        else:
            earliest_datetime = date - timedelta(days=1)

        query = {"input_time": {"$gt": earliest_datetime}}
        cursor = self.client[dbname][strategy_name].find(query)

        datas = []
        for item in cursor:
            item.pop('_id')
            datas.append(item)

        return datas

    def get_position_data(self, strategy_name: str, date: datetime = None):
        """
        得到特定交易日日末的持仓数据
        """
        dbname = self.database_setting["variable_dbname"]
        if not date:
            date = datetime.today()

        date = date.replace(hour=18, minute=30)

        if date.weekday() == 0:
            earliest_datetime = date - timedelta(days=3)
        else:
            earliest_datetime = date - timedelta(days=1)

        query = {"input_time": {"$gt": earliest_datetime, "$lt": date}}
        cursor = self.client[dbname][strategy_name].find(query)

        datas = []
        for item in cursor:
            item.pop('_id')
            datas.append(item)

        return datas

    def complete_recent_data_with_csv(self,
                                      vt_symbol: str,
                                      interval: Interval = Interval.DAILY,
                                      days: int = 10
                                      ):
        """
        vt_symbol: 一个合约名称, 保存着合约名称，有".交易所"
        days: 补全最近x日的数据
        """
        # 判断interval，读取相应的文件和应用相应的日期格式
        if interval == Interval.MINUTE:
            suffix = "_1min.csv"
            save_func = self.save_bar_1min
            datetime_format = "%Y-%m-%d %H:%M:%S"
        elif interval == Interval.DAILY:
            suffix = "_day.csv"
            save_func = self.save_bar_day
            datetime_format = "%Y-%m-%d"
        else:
            return

        local_data_path = self.database_setting["local_data_path"]
        symbol, exchange = extract_vt_symbol(vt_symbol)
        # 如果是郑商所，补全三位数的年月
        if exchange == Exchange.CZCE:
            product_name = re.sub(r'\d', "", symbol)
            year_month = re.sub(r'\D', "", symbol)
            if int(year_month) > 800:
                file_symbol = product_name + "1" + year_month
            else:
                file_symbol = product_name + "2" + year_month
        else:
            file_symbol = symbol

        file_path = local_data_path + file_symbol + suffix
        if not os.path.exists(file_path):
            self.write_log(f"文件{file_path}不存在")
            return

        with open(file_path, "rt") as f:
            reader = csv.DictReader(f)
            bars = []
            for item in reader:
                dt = datetime.strptime(item["date"], datetime_format)
                # csv里面以时间段终点作为时间戳，但是数据库是以起点
                if interval == Interval.MINUTE:
                    dt = dt - timedelta(minutes=1)
                if datetime.today() - dt < timedelta(days=days):

                    bar = DbBarData(
                        symbol=symbol,
                        vt_symbol=vt_symbol,
                        exchange=exchange.value,
                        datetime=dt,
                        open=item["open"],
                        high=item["high"],
                        low=item["low"],
                        close=item["close"],
                        volume=item["volume"],
                        interval=interval.value,
                        gateway_name="DB",
                        input_time=datetime.now()
                    )
                    bars.append(bar)

            # insert into database
            save_func(bars)

    def delete_outdated_data(self,
                             days: int = 30
                             ):
        """
        清除x天前的分钟线数据
        一个数据库里的数据全部清理
        """
        dbname = self.database_setting["bar_1min_dbname"]

        db = self.client[dbname]
        collection_names = db.list_collection_names()
        collection_names.remove("system.indexes")
        for collection_name in collection_names:
            self.write_log(f"正在清理{collection_name}")
            collection = db[collection_name]

            now = datetime.now()
            earliest_datetime = now - timedelta(days=days)
            query = {"datetime": {"$lt": earliest_datetime}}

            collection.delete_many(query)

        # 再遍历一遍，如果collection为空，则删除该集合
        for collection_name in collection_names:
            collection = db[collection_name]
            if not list(collection.find()):
                self.write_log(f"drop集合{collection_name}")
                collection.drop()

    def parse_futures_day_from_website(self, days: int = 30):
        """"""
        current_date = datetime.today() - timedelta(days=days)

        if datetime.now().hour < 16:
            end_date = datetime.today() - timedelta(days=1)
        else:
            end_date = datetime.today()

        while current_date <= end_date:
            datas = parse_all_futures_data(current_date)
            self.save_bar_day(datas)
            self.write_log(f"下载{current_date.strftime('%Y%m%d')}数据{len(datas)}条")
            current_date = current_date + timedelta(days=1)

    def parse_futures_day_from_tushare(self, days: int = 30):
        """"""
        current_date = datetime.today() - timedelta(days=days)

        while current_date <= datetime.today():
            try:
                datas = parse_all_futures_data_tushare(current_date)
            except Exception:
                self.write_log(f"查询出错，暂停10秒")
                sleep(10)
                continue
            self.save_bar_day(datas)
            self.write_log(f"下载{current_date.strftime('%Y%m%d')}数据{len(datas)}条")
            current_date = current_date + timedelta(days=1)

    def download_stock_day_from_tushare(self, days: int = 30):
        """"""
        self.day_bar_thread = Thread(target=self._download_stock_day_from_tushare, args=[days])
        self.day_bar_thread.start()

    def _download_stock_day_from_tushare(self, days: int = 30):
        """"""
        end_date = datetime.today()
        start_date = datetime.today() - timedelta(days=days)

        ts_client = TuShareClient()

        basic_info = ts_client.get_stock_basic_info()
        ts_codes = list(basic_info.ts_code)
        ts_codes = ["510050.SH", "510510.SH", "159901.SZ"]

        while ts_codes:
            # 取出一个代码
            ts_code = ts_codes[0]
            if ts_client is not None:
                try:
                    datas = ts_client.parse_stock_bar_day(ts_code=ts_code, start_date=start_date, end_date=end_date)
                except Exception:
                    print("day_bar下载产生异常，重新初始化ts_client")
                    ts_client = TuShareClient()
                    continue
                # 保存这个代码的信息，从list中删除这个代码
                self.save_stock_bar_day(datas)
                ts_codes.remove(ts_code)
            else:
                ts_client = TuShareClient()

    def download_stock_metrics_from_tushare(self, days: int = 30):
        """"""
        self.metrics_thread = Thread(target=self._download_stock_metrics_from_tushare, args=[days])
        self.metrics_thread.start()

    def _download_stock_metrics_from_tushare(self, days: int = 30):
        """"""
        end_date = datetime.today()
        start_date = datetime.today() - timedelta(days=days)

        ts_client = TuShareClient()

        current_date = start_date

        while current_date <= end_date:
            if ts_client is not None:
                try:
                    datas = ts_client.parse_daily_metrics(trade_date=current_date)
                except Exception:
                    print("metrics下载产生异常，重新初始化ts_client")
                    ts_client = None
                    continue

                self.save_stock_metrics_day(datas)
                current_date += timedelta(days=1)
            else:
                ts_client = TuShareClient()

    def download_stock_fundamental_from_tushare(self, years: int = 10):
        """"""
        self.fundamental_thread = Thread(target=self._download_stock_fundamental_from_tushare, args=[years])
        self.fundamental_thread.start()

    def _download_stock_fundamental_from_tushare(self, years: int = 10):
        """"""
        end_date = datetime.today()
        start_date = datetime.today() - timedelta(days=years*365)

        ts_client = TuShareClient()

        basic_info = ts_client.get_stock_basic_info()
        ts_codes = list(basic_info.ts_code)

        while ts_codes:
            # 取出一个代码
            ts_code = ts_codes[0]
            if ts_client is not None:
                try:
                    datas = ts_client.parse_stock_fundamentals(
                        ts_code=ts_code,
                        start_date=start_date,
                        end_date=end_date
                    )
                except Exception:
                    print("fundamental下载产生异常，重新初始化ts_client")
                    ts_client = None
                    continue
                self.save_stock_fundamental_data(datas)
                ts_codes.remove(ts_code)
            else:
                ts_client = TuShareClient()

    def download_stock_dividend_from_tushare(self):
        """"""
        self.dividend_thread = Thread(target=self._download_stock_dividend_from_tushare)
        self.dividend_thread.start()

    def _download_stock_dividend_from_tushare(self):
        """"""
        ts_client = TuShareClient()

        basic_info = ts_client.get_stock_basic_info()
        ts_codes = list(basic_info.ts_code)

        while ts_codes:
            # 取出一个代码
            ts_code = ts_codes[0]
            if ts_client is not None:
                try:
                    datas = ts_client.parse_stock_dividend(ts_code=ts_code)
                except Exception:
                    print("dividend下载产生异常，重新初始化ts_client")
                    ts_client = None
                    continue
                self.save_stock_dividend_data(datas)
                ts_codes.remove(ts_code)
            else:
                ts_client = TuShareClient()

    def write_log(self, msg):
        log = LogData(msg=msg, gateway_name="DatabaseManager")
        event = Event(type=EVENT_LOG, data=log)
        self.event_engine.put(event)

    def close(self):

        self.active = False

        if self.thread.isAlive():
            self.thread.join()

        if self.loading_thread:
            if self.loading_thread.isAlive():
                self.loading_thread.join()

        if self.day_bar_thread:
            if self.day_bar_thread.is_alive():
                self.day_bar_thread.join()

        if self.dividend_thread:
            if self.dividend_thread.is_alive():
                self.dividend_thread.join()

        if self.fundamental_thread:
            if self.fundamental_thread.is_alive():
                self.fundamental_thread.join()

        if self.metrics_thread:
            if self.metrics_thread.is_alive():
                self.metrics_thread.join()
