from vnpy.app.database_manager.data_objects import DbBarData
from vnpy.trader.constant import Interval
import tushare as ts
import re
import pandas
from datetime import datetime


def init_pro():
    """初始化接口"""
    ts.set_token('39e3fb8a636f64102392ef2ef45c2e8f4e96288d6bcbb16de6c6510c')
    return ts.pro_api()


def generate_db_bar(s: pandas.Series):
    """"""
    db_bar = DbBarData()

    symbol, _ = s.ts_code.split(".")

    db_bar.symbol = symbol
    db_bar.exchange = s.exchange
    db_bar.vt_symbol = ".".join([symbol, s.exchange])
    db_bar.interval = Interval.DAILY.value
    db_bar.datetime = datetime.strptime(s.trade_date, "%Y%m%d")
    db_bar.openinterest = s.oi
    db_bar.volume = s.vol
    db_bar.open = s.open
    db_bar.close = s.close
    db_bar.high = s.high
    db_bar.low = s.low

    db_bar.gateway_name = "tushare"
    db_bar.input_time = datetime.now()

    return db_bar


def parse_all_futures_data_tushare(date: datetime):
    """"""
    pro = init_pro()
    trade_date = date.strftime("%Y%m%d")
    exchanges = ["DCE", "SHFE", "CFFEX", "CZCE", "INE"]
    fields = 'ts_code,trade_date,open,high,low,close,vol,oi'
    data_list = []

    for exchange in exchanges:
        df = pro.fut_daily(trade_date=trade_date, exchange=exchange, fields=fields)

        df = df.loc[df.ts_code.apply(lambda x: len(re.sub(r'\D', "", x)) == 4), :]
        df = df.fillna(0)
        df["exchange"] = exchange

        if exchange in ["DCE", "SHFE", "INE"]:
            df["ts_code"] = df["ts_code"].apply(lambda x: x.lower())
        if exchange in ["CZCE"]:
            f = lambda x: re.sub(r'\d', "", x.split(".")[0]) + re.sub(r'\D', "", x)[1:] + "." + x.split(".")[1]
            df["ts_code"] = df["ts_code"].apply(f)

        [data_list.append(generate_db_bar(df.loc[i, :])) for i in df.index]

    return data_list


if __name__ == '__main__':
    dl = parse_all_futures_data_tushare(datetime(2019, 10, 14))
    [print(d.__dict__) for d in dl]
