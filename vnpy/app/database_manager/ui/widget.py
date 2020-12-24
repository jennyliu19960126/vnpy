
from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import QtWidgets
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from vnpy.trader.constant import Interval

from ..engine import (
    APP_NAME
)


class DatabaseManager(QtWidgets.QWidget):
    """"""
    days_keep = None
    days_complete = None
    days_complete_all = None
    strategy_name = None
    symbol_complete = None
    parse_days = None
    parse_tushare_days = None
    equity_bar_days = None
    fundamental_years = None
    metrics_days = None

    def __init__(self, main_engine: MainEngine, event_engine: EventEngine):
        super().__init__()

        self.main_engine = main_engine
        self.event_engine = event_engine
        self.database_manager_engine = main_engine.get_engine(APP_NAME)

        self.parse_executor = ThreadPoolExecutor(max_workers=3)

        self.init_ui()
        self.register_event()

    def init_ui(self):
        """"""
        self.setWindowTitle("数据库管理")
        self.resize(500, 300)

        complete_recent_all_button = QtWidgets.QPushButton("从csv加载活跃合约最近分钟线数据")
        complete_recent_all_button.clicked.connect(self.complete_recent_data_with_csv_all_contracts)
        self.days_complete_all = QtWidgets.QLineEdit()
        self.days_complete_all.setText("10")

        delete_outdated_button = QtWidgets.QPushButton("删除过期数据")
        delete_outdated_button.clicked.connect(self.delete_outdated_data)
        self.days_keep = QtWidgets.QLineEdit()
        self.days_keep.setText("30")

        load_param_button = QtWidgets.QPushButton("加载所有策略参数")
        load_param_button.clicked.connect(self.load_parameter_info)

        parse_button = QtWidgets.QPushButton("从网站下载期货日线数据")
        parse_button.clicked.connect(self.parse_bar_day_from_website)
        self.parse_days = QtWidgets.QLineEdit()
        self.parse_days.setText("0")

        parse_tushare_button = QtWidgets.QPushButton("从tushare下载期货日线数据")
        parse_tushare_button.clicked.connect(self.parse_bar_day_from_tushare)
        self.parse_tushare_days = QtWidgets.QLineEdit()
        self.parse_tushare_days.setText("0")

        equity_day_button = QtWidgets.QPushButton("下载股票日线数据")
        equity_day_button.clicked.connect(self.download_stock_day_from_tushare)
        self.equity_bar_days = QtWidgets.QLineEdit()
        self.equity_bar_days.setText("50")

        fundamental_button = QtWidgets.QPushButton("下载股票财报数据")
        fundamental_button.clicked.connect(self.download_stock_fundamental_from_tushare)
        self.fundamental_years = QtWidgets.QLineEdit()
        self.fundamental_years.setText("5")

        dividend_button = QtWidgets.QPushButton("下载分红送股数据")
        dividend_button.clicked.connect(self.download_stock_dividend_from_tushare)

        metrics_button = QtWidgets.QPushButton("下载股票每日指标数据")
        metrics_button.clicked.connect(self.download_stock_metrics_from_tushare)
        self.metrics_days = QtWidgets.QLineEdit()
        self.metrics_days.setText("5")

        grid = QtWidgets.QGridLayout()
        # 删除最近数据
        grid.addWidget(delete_outdated_button, 0, 1)
        grid.addWidget(self.days_keep, 0, 2)
        # 从csv加载策略参数
        grid.addWidget(load_param_button, 1, 1)
        # 从csv加载全部合约日数据
        grid.addWidget(complete_recent_all_button, 2, 1)
        grid.addWidget(self.days_complete_all, 2, 2)
        # 从网站下载日数据
        grid.addWidget(parse_button, 3, 1)
        grid.addWidget(self.parse_days, 3, 2)
        # 从tushare下载期货日数据
        grid.addWidget(parse_tushare_button, 8, 1)
        grid.addWidget(self.parse_tushare_days, 8, 2)
        # 从tushare下载股票日数据
        grid.addWidget(equity_day_button, 4, 1)
        grid.addWidget(self.equity_bar_days, 4, 2)
        # 从tushare下载股票财报数据
        grid.addWidget(fundamental_button, 5, 1)
        grid.addWidget(self.fundamental_years, 5, 2)
        # 从tushare下载股票分红数据
        grid.addWidget(dividend_button, 6, 1)
        # 从tushare下载股票每日指标数据
        grid.addWidget(metrics_button, 7, 1)
        grid.addWidget(self.metrics_days, 7, 2)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(grid)
        self.setLayout(vbox)

    def register_event(self):
        """"""
        pass

    def delete_outdated_data(self):
        """"""
        days = int(self.days_keep.text())
        self.parse_executor.submit(self.database_manager_engine.delete_outdated_data, days)

    def parse_bar_day_from_website(self):
        days = int(self.parse_days.text())
        self.parse_executor.submit(self.database_manager_engine.parse_futures_day_from_website, days)

    def parse_bar_day_from_tushare(self):
        days = int(self.parse_tushare_days.text())
        self.parse_executor.submit(self.database_manager_engine.parse_futures_day_from_tushare, days)

    def download_stock_day_from_tushare(self):
        days = int(self.equity_bar_days.text())
        self.database_manager_engine.download_stock_day_from_tushare(days=days)

    def download_stock_fundamental_from_tushare(self):
        years = int(self.fundamental_years.text())
        self.database_manager_engine.download_stock_fundamental_from_tushare(years=years)

    def download_stock_dividend_from_tushare(self):
        self.database_manager_engine.download_stock_dividend_from_tushare()

    def download_stock_metrics_from_tushare(self):
        days = int(self.metrics_days.text())
        self.database_manager_engine.download_stock_metrics_from_tushare(days=days)

    def load_parameter_info(self):
        """"""
        self.database_manager_engine.save_all_parameter_info()

    def complete_recent_data_with_csv(self):
        """"""
        vt_symbol = self.symbol_complete.text()
        days = int(self.days_complete.text())
        engine = self.database_manager_engine
        engine.complete_recent_data_with_csv(vt_symbol=vt_symbol,
                                             interval=Interval.DAILY,
                                             days=days)

    def complete_recent_data_with_csv_all_contracts(self):
        """"""
        contracts = self.main_engine.get_all_contracts()
        self.database_manager_engine.write_log(f"一共有{len(contracts)}个在线合约")

        for contract in contracts:
            vt_symbol = contract.vt_symbol
            self.database_manager_engine.loading_queue.put(vt_symbol)

            if not self.database_manager_engine.loading_thread:
                self.database_manager_engine.loading_thread = Thread(
                    target=self._complete_recent_data_with_csv_all_contracts)
                self.database_manager_engine.loading_thread.start()

    def _complete_recent_data_with_csv_all_contracts(self):
        """"""
        engine = self.database_manager_engine
        days = int(self.days_complete_all.text())

        while not engine.loading_queue.empty():
            vt_symbol = engine.loading_queue.get()
            self.database_manager_engine.write_log(f"正在加载{vt_symbol}日线数据")
            engine.complete_recent_data_with_csv(vt_symbol=vt_symbol,
                                                 interval=Interval.DAILY,
                                                 days=days)
