import pandas as pd
import tushare as ts
from datetime import datetime, timedelta
from vnpy.app.database_manager.data_objects import (DbStockBarData,
                                                    DbStockFundamentalData,
                                                    DbStockDividendData,
                                                    DbStockDailyMetricsData)
from vnpy.trader.constant import Interval, Exchange
from time import sleep


class TuShareClient:
    """tushare数据下载器"""

    pro = None

    def __init__(self):

        ts.set_token('39e3fb8a636f64102392ef2ef45c2e8f4e96288d6bcbb16de6c6510c')
        self.pro = ts.pro_api()

    def get_stock_basic_info(self):
        """"""
        return self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol')

    def parse_stock_bar_day(self,
                            ts_code: str,
                            start_date: datetime,
                            end_date: datetime):

        print("下载" + ts_code + "日线数据")
        symbol, exchange = ts_code.split(".")
        if exchange == "SZ":
            exchange = Exchange.SZSE.value
        if exchange == 'SH':
            exchange = Exchange.SSE.value

        sd = start_date.strftime("%Y%m%d")
        ed = end_date.strftime("%Y%m%d")

        # 此接口一分钟最多调用80次
        t1 = datetime.now()
        data = self.pro.fund_daily(ts_code=ts_code, start_date=sd, end_date=ed)
        t2 = datetime.now()

        seconds_to_wait = (timedelta(seconds=0.75) - (t2 - t1)).total_seconds()

        if seconds_to_wait >= 0:
            sleep(seconds_to_wait)
        data = data.sort_values(by="trade_date", ascending=True)
        data.index = range(len(data))

        data_list = []

        for ri in data.index:
            d = dict(data.loc[ri, ])
            db_bar = DbStockBarData()
            db_bar.exchange = exchange
            db_bar.open = d["open"]
            db_bar.high = d["high"]
            db_bar.low = d["low"]
            db_bar.close = d["close"]
            db_bar.pre_close = d["pre_close"]
            db_bar.pct_change = d["pct_chg"]
            db_bar.volume = d["vol"]
            db_bar.amount = d["amount"]
            db_bar.symbol = symbol
            db_bar.vt_symbol = ".".join([symbol, exchange])
            db_bar.datetime = datetime.strptime(d["trade_date"], "%Y%m%d")
            db_bar.input_time = datetime.now()
            db_bar.gateway_name = "Tushare"
            db_bar.interval = Interval.DAILY.value

            data_list.append(db_bar)

        return data_list

    def parse_daily_metrics(self, trade_date: datetime):
        td = trade_date.strftime("%Y%m%d")
        print("下载" + td + "每日指标")
        # 此接口一分钟最多调用80次

        t1 = datetime.now()

        df = self.pro.daily_basic(trade_date=td)

        data_list = []

        for ri in df.index:
            d = dict(df.loc[ri, ])
            exchange = ""
            symbol, e = d["ts_code"].split(".")
            if e == "SH":
                exchange = "SSE"
            elif e == "SZ":
                exchange = "SZSE"

            db_bar = DbStockDailyMetricsData()
            db_bar.exchange = exchange
            db_bar.close = d["close"]
            db_bar.pe = d["pe"]
            db_bar.pe_ttm = d["pe_ttm"]
            db_bar.pb = d["pb"]
            db_bar.total_share = d["total_share"]
            db_bar.float_share = d["float_share"]
            db_bar.free_share = d["free_share"]
            db_bar.turnover = d["turnover_rate"]
            db_bar.turnover_free = d["turnover_rate_f"]

            db_bar.symbol = symbol
            db_bar.vt_symbol = ".".join([symbol, exchange])
            db_bar.datetime = datetime.strptime(d["trade_date"], "%Y%m%d")
            db_bar.input_time = datetime.now()
            db_bar.gateway_name = "Tushare"

            data_list.append(db_bar)

        t2 = datetime.now()

        seconds_to_wait = (timedelta(seconds=0.6) - (t2 - t1)).total_seconds()

        if seconds_to_wait >= 0:
            sleep(seconds_to_wait)

        return data_list

    def parse_stock_fundamentals(self,
                                 ts_code: str,
                                 start_date: datetime,
                                 end_date: datetime):

        print("下载" + ts_code + "财报数据")

        sd = start_date.strftime("%Y%m%d")
        ed = end_date.strftime("%Y%m%d")

        # 此接口一分钟最多调用80次
        t1 = datetime.now()
        df_is = self.pro.income(ts_code=ts_code, start_date=sd, end_date=ed)
        df_bs = self.pro.balancesheet(ts_code=ts_code, start_date=sd, end_date=ed)
        df_cf = self.pro.cashflow(ts_code=ts_code, start_date=sd, end_date=ed)
        t2 = datetime.now()

        seconds_to_wait = (timedelta(seconds=0.75) - (t2 - t1)).total_seconds()

        if seconds_to_wait >= 0:
            sleep(seconds_to_wait)

        df_is = df_is.drop_duplicates(subset=["end_date"], keep='first', inplace=False)
        df_bs = df_bs.drop_duplicates(subset=["end_date"], keep='first', inplace=False)
        df_cf = df_cf.drop_duplicates(subset=["end_date"], keep='first', inplace=False)

        common_cols = ["ts_code", "end_date", "ann_date", "f_ann_date", "comp_type", "report_type"]

        df1 = pd.merge(df_is, df_bs, how="inner", on=common_cols)
        df = pd.merge(df1, df_cf, how="inner", on=common_cols)

        df = df.sort_values(by="end_date", ascending=True)
        df.index = range(len(df))

        data_list = []

        # 然后逐行插入Fundamental表里
        for ri in df.index:
            d = dict(df.loc[ri, ])
            db_data = DbStockFundamentalData()
            db_data.symbol, exchange = ts_code.split(".")
            if exchange == "SH":
                db_data.exchange = "SSE"
            if exchange == "SZ":
                db_data.exchange = "SZSE"

            db_data.vt_symbol = ".".join([db_data.symbol, db_data.exchange])

            db_data.end_date = datetime.strptime(d["end_date"], "%Y%m%d")
            db_data.announcement_date = datetime.strptime(d["ann_date"], "%Y%m%d")

            db_data.operating_revenue = d["revenue"]
            db_data.operating_cost = d["oper_cost"]
            db_data.sales_expense = d["sell_exp"]
            db_data.administrative_expense = d["admin_exp"]
            db_data.financial_expense = d["fin_exp"]
            db_data.gross_profit = d["operate_profit"]
            db_data.tax_expense = d["income_tax"]
            db_data.net_profit = d["n_income"]
            db_data.net_profit_applicable_to_parent = d["n_income_attr_p"]

            db_data.earning_per_share = d["basic_eps"]
            db_data.diluted_earning_per_share = d["diluted_eps"]

            # Balance sheet
            db_data.cash_and_cash_equivalents = d["money_cap"]
            db_data.notes_receivable = d["notes_receiv"]
            db_data.accounts_receivable = d["accounts_receiv"]
            db_data.inventory = d["inventories"]
            db_data.total_current_asset = d["total_cur_assets"]
            db_data.goodwill = d["goodwill"]

            db_data.total_asset = d["total_assets"]

            db_data.accounts_payable = d["acct_payable"]
            db_data.notes_payable = d["notes_payable"]
            db_data.total_current_liability = d["total_cur_liab"]

            db_data.total_liability = d["total_liab"]

            db_data.common_stock = d["total_share"]
            db_data.capital_surplus = d["cap_rese"]
            db_data.retain_earnings = d["undistr_porfit"]
            db_data.treasury_stock = d["treasury_share"]

            db_data.total_equity = d["total_hldr_eqy_inc_min_int"]

            # cash flow statement
            db_data.cash_flow_from_operating_activities = d["n_cashflow_act"]
            db_data.cash_flow_from_investing_activities = d["n_cashflow_inv_act"]
            db_data.cash_flow_from_financing_activities = d["n_cash_flows_fnc_act"]

            db_data.input_time = datetime.now()

            data_list.append(db_data)

        return data_list

    def parse_stock_dividend(self, ts_code: str):

        print("下载" + ts_code + "分红送股数据")

        # 此接口一分钟最多调用100次
        t1 = datetime.now()
        df = self.pro.dividend(ts_code=ts_code)
        t2 = datetime.now()

        seconds_to_wait = (timedelta(seconds=0.6) - (t2 - t1)).total_seconds()

        if seconds_to_wait >= 0:
            sleep(seconds_to_wait)

        df = df.sort_values(by="end_date", ascending=True)
        df.index = range(len(df))

        data_list = []

        # 然后逐行插入Fundamental表里
        for ri in df.index:
            d = dict(df.loc[ri, ])
            db_data = DbStockDividendData()
            db_data.symbol, exchange = ts_code.split(".")
            if exchange == "SH":
                db_data.exchange = "SSE"
            if exchange == "SZ":
                db_data.exchange = "SZSE"

            db_data.vt_symbol = ".".join([db_data.symbol, db_data.exchange])

            db_data.end_date = datetime.strptime(d["end_date"], "%Y%m%d")
            if d["ann_date"]:
                db_data.announcement_date = datetime.strptime(d["ann_date"], "%Y%m%d")

            db_data.decision_status = d["div_proc"]
            db_data.stock_dividend = d["stk_div"]
            db_data.cash_dividend_before_tax = d["cash_div_tax"]
            db_data.cash_dividend_after_tax = d["cash_div"]
            if d["record_date"]:
                db_data.record_date = datetime.strptime(d["record_date"], "%Y%m%d")
            if d["ex_date"]:
                db_data.ex_dividend_date = datetime.strptime(d["ex_date"], "%Y%m%d")
            if d["imp_ann_date"]:
                db_data.implement_announcement_date = datetime.strptime(d["imp_ann_date"], "%Y%m%d")

            db_data.gateway_name = "Tushare"
            db_data.input_time = datetime.now()

            data_list.append(db_data)

        return data_list




