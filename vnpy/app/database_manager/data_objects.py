from datetime import datetime
from dataclasses import dataclass

from vnpy.trader.object import TickData, BarData, OrderData, TradeData
from vnpy.trader.constant import Interval, Exchange


@dataclass
class DbTickData:
    symbol: str = ""
    vt_symbol: str = ""
    exchange: str = ""
    datetime: datetime = datetime(1990, 1, 1, 0, 0, 0)

    name: str = ""
    volume: float = 0
    open_interest: float = 0
    last_price: float = 0
    last_volume: float = 0
    limit_up: float = 0
    limit_down: float = 0

    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    close_price: float = 0
    pre_close: float = 0

    bid_price_1: float = 0
    bid_price_2: float = 0
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0

    ask_price_1: float = 0
    ask_price_2: float = 0
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0

    bid_volume_1: float = 0
    bid_volume_2: float = 0
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0

    ask_volume_1: float = 0
    ask_volume_2: float = 0
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0

    input_time: datetime = datetime.now()

    def from_tick(self, tick: TickData):
        self.symbol = tick.symbol
        self.vt_symbol = tick.vt_symbol
        self.exchange = tick.exchange.value
        self.datetime = tick.datetime
        self.volume = tick.volume

        self.name = tick.name
        self.volume = tick.volume
        self.open_interest = tick.open_interest
        self.last_price = tick.last_price
        self.last_volume = tick.last_volume
        self.limit_up = tick.limit_up
        self.limit_down = tick.limit_down

        self.open_price = tick.open_price
        self.high_price = tick.high_price
        self.low_price = tick.low_price
        self.close_price = 0
        self.pre_close = tick.pre_close

        self.bid_price_1 = tick.bid_price_1
        self.bid_price_2 = tick.bid_price_2
        self.bid_price_3 = tick.bid_price_3
        self.bid_price_4 = tick.bid_price_4
        self.bid_price_5 = tick.bid_price_5

        self.ask_price_1 = tick.ask_price_1
        self.ask_price_2 = tick.ask_price_2
        self.ask_price_3 = tick.ask_price_3
        self.ask_price_4 = tick.ask_price_4
        self.ask_price_5 = tick.ask_price_5

        self.bid_volume_1 = tick.bid_volume_1
        self.bid_volume_2 = tick.bid_volume_2
        self.bid_volume_3 = tick.bid_volume_3
        self.bid_volume_4 = tick.bid_volume_4
        self.bid_volume_5 = tick.bid_volume_5

        self.ask_volume_1 = tick.ask_volume_1
        self.ask_volume_2 = tick.ask_volume_2
        self.ask_volume_3 = tick.ask_volume_3
        self.ask_volume_4 = tick.ask_volume_4
        self.ask_volume_5 = tick.ask_volume_5

        self.input_time = datetime.now()

    def to_tick(self):
        pass


@dataclass
class DbBarData:
    symbol: str = ""
    vt_symbol: str = ""
    exchange: str = ""
    datetime: datetime = datetime(1990, 1, 1, 0, 0, 0)

    open: float = 0
    high: float = 0
    low: float = 0
    close: float = 0
    volume: float = 0
    openinterest: float = 0
    interval: str = ""
    gateway_name: str = ""
    input_time: datetime = datetime.now()

    def from_bar(self, bar: BarData):
        self.symbol = bar.symbol
        self.vt_symbol = bar.vt_symbol
        self.exchange = bar.exchange.value
        self.datetime = bar.datetime

        self.open = bar.open_price
        self.high = bar.high_price
        self.low = bar.low_price
        self.close = bar.close_price
        self.volume = bar.volume
        self.openinterest = bar.open_interest
        self.interval = bar.interval.value
        self.gateway_name = bar.gateway_name

        self.input_time = datetime.now()

    def to_bar(self):
        bar = BarData(
            symbol=self.symbol,
            exchange=Exchange(self.exchange),
            datetime=self.datetime,
            interval=Interval(self.interval),
            volume=self.volume,
            open_interest=self.openinterest,
            open_price=self.open,
            high_price=self.high,
            low_price=self.low,
            close_price=self.close,
            gateway_name="DB",
        )
        return bar


@dataclass
class DbOrderData:
    strategy_name: str = "no_strategy_name"
    algo_name: str = "no_algo_name"

    symbol: str = ""
    exchange: str = ""
    orderid: str = ""

    type: str = ""
    direction: str = ""
    offset: str = ""
    price: float = 0
    volume: float = 0
    traded: float = 0
    status: str = ""
    time: str = ""
    gateway_name: str = ""
    vt_symbol: str = ""
    vt_orderid: str = ""
    input_time: datetime = datetime.now()

    def from_order(self, order: OrderData):
        self.symbol = order.symbol
        self.exchange = order.exchange.value
        self.orderid = order.orderid

        self.type = order.type.value
        self.direction = order.direction.value
        self.offset = order.offset.value
        self.price = order.price
        self.volume = order.volume
        self.traded = order.traded
        self.status = order.status.value
        self.time = order.time
        self.gateway_name = order.gateway_name
        self.vt_symbol = order.vt_symbol
        self.vt_orderid = order.vt_orderid
        self.input_time = datetime.now()


@dataclass
class DbTradeData:
    strategy_name: str = "no_strategy_name"
    algo_name: str = "no_algo_name"

    symbol: str = ""
    exchange: str = ""
    orderid: str = ""
    tradeid: str = ""

    direction: str = ""
    offset: str = ""
    price: float = 0
    volume: float = 0
    time: str = ""
    gateway_name: str = ""
    vt_symbol: str = ""
    vt_orderid: str = ""
    vt_tradeid: str = ""
    input_time: datetime = datetime.now()

    def from_trade(self, trade: TradeData):
        self.symbol = trade.symbol
        self.exchange = trade.exchange.value
        self.orderid = trade.orderid
        self.tradeid = trade.tradeid
        self.direction = trade.direction.value

        self.offset = trade.offset.value
        self.price = trade.price
        self.volume = trade.volume
        self.time = trade.time

        self.gateway_name = trade.gateway_name
        self.vt_symbol = trade.vt_symbol
        self.vt_orderid = trade.vt_orderid
        self.vt_tradeid = trade.vt_tradeid

        self.input_time = datetime.now()


@dataclass
class DbStockBarData:
    symbol: str = ""
    vt_symbol: str = ""
    exchange: str = ""
    datetime: datetime = datetime(1990, 1, 1, 0, 0, 0)

    open: float = 0
    high: float = 0
    low: float = 0
    close: float = 0
    pre_close: float = 0
    pct_change: float = 0
    volume: float = 0
    amount: float = 0

    interval: str = ""
    gateway_name: str = ""
    input_time: datetime = datetime.now()


@dataclass
class DbStockDailyMetricsData:
    symbol: str = ""
    vt_symbol: str = ""
    exchange: str = ""
    datetime: datetime = datetime(1990, 1, 1, 0, 0, 0)

    close: float = 0
    pe: float = 0
    pe_ttm: float = 0
    pb: float = 0
    total_share: float = 0
    float_share: float = 0
    free_share: float = 0
    turnover: float = 0
    turnover_free: float = 0

    gateway_name: str = ""
    input_time: datetime = datetime.now()


@dataclass
class DbStockDividendData:
    symbol: str = ""
    vt_symbol: str = ""
    exchange: str = ""
    end_date: datetime = datetime(1990, 1, 1, 0, 0, 0)
    announcement_date: datetime = datetime(1990, 1, 1, 0, 0, 0)

    decision_status: str = ""
    stock_dividend: float = 0

    cash_dividend_before_tax: float = 0
    cash_dividend_after_tax: float = 0
    record_date: datetime = datetime(1990, 1, 1, 0, 0, 0)
    ex_dividend_date: datetime = datetime(1990, 1, 1, 0, 0, 0)
    implement_announcement_date: datetime = datetime(1990, 1, 1, 0, 0, 0)

    gateway_name: str = ""
    input_time: datetime = datetime.now()


@dataclass
class DbStockFundamentalData:
    symbol: str = ""
    vt_symbol: str = ""
    exchange: str = ""
    end_date: datetime = datetime(1990, 1, 1, 0, 0, 0)
    announcement_date: datetime = datetime(1990, 1, 1, 0, 0, 0)

    # Income statement
    operating_revenue: float = 0
    operating_cost: float = 0
    sales_expense: float = 0
    administrative_expense: float = 0
    financial_expense: float = 0
    gross_profit: float = 0
    tax_expense: float = 0
    net_profit: float = 0
    net_profit_applicable_to_parent: float = 0

    earning_per_share: float = 0
    diluted_earning_per_share: float = 0

    # Balance sheet
    cash_and_cash_equivalents: float = 0
    notes_receivable: float = 0
    accounts_receivable: float = 0
    inventory: float = 0
    total_current_asset: float = 0
    goodwill: float = 0

    total_asset: float = 0

    accounts_payable: float = 0
    notes_payable: float = 0
    total_current_liability: float = 0

    total_liability: float = 0

    common_stock: float = 0
    capital_surplus: float = 0
    retain_earnings: float = 0
    treasury_stock: float = 0

    total_equity: float = 0

    # cash flow statement
    cash_flow_from_operating_activities: float = 0
    cash_flow_from_investing_activities: float = 0
    cash_flow_from_financing_activities: float = 0

    input_time: datetime = datetime.now()
