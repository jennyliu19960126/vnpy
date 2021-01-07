from vnpy.trader.constant import Offset, Direction
from vnpy.trader.object import TradeData, OrderData, TickData
from vnpy.trader.engine import BaseEngine

from vnpy.app.algo_trading import AlgoTemplate


class GradientChaseAlgo(AlgoTemplate):
    """"""

    display_name = "GradientChase 梯度追踪"

    default_setting = {
        "account_name": "",
        "vt_symbol": "",
        "direction": [Direction.LONG.value, Direction.SHORT.value],
        "volume": 0.0,
        "offset": [
            Offset.NONE.value,
            Offset.OPEN.value,
            Offset.CLOSE.value,
            Offset.CLOSETODAY.value,
            Offset.CLOSEYESTERDAY.value
        ]
    }

    variables = [
        "traded",
        "vt_orderids",
        "order_price",
        "last_tick",
    ]

    def __init__(
        self,
        algo_engine: BaseEngine,
        algo_name: str,
        setting: dict
    ):
        """"""
        super().__init__(algo_engine, algo_name, setting)

        # Parameters
        self.account_name = setting["account_name"]
        self.vt_symbol = setting["vt_symbol"]
        self.direction = Direction(setting["direction"])
        self.volume = setting["volume"]
        self.offset = Offset(setting["offset"])

        # Variables
        self.vt_orderids = []
        self.traded = 0
        self.last_tick = None
        self.order_price = 0

        self.subscribe(self.vt_symbol)
        self.put_parameters_event()
        self.put_variables_event()

    def on_tick(self, tick: TickData):
        """"""
        # 两秒处理一次tick，防止频繁cancel
        if self.last_tick is not None:
            s = self.last_tick.datetime.second
            if tick.datetime.second == s or tick.datetime.second % 2 != 0:
                return

        self.last_tick = tick

        if self.direction == Direction.LONG:
            if not self.vt_orderids:
                self.buy_gradient_chase()
            elif self.order_price != self.last_tick.ask_price_1:
                self.cancel_all()
        else:
            if not self.vt_orderids:
                self.sell_gradient_chase()
            elif self.order_price != self.last_tick.bid_price_1:
                self.cancel_all()

        self.put_variables_event()

    def on_trade(self, trade: TradeData):
        """"""
        self.traded += trade.volume

        if self.traded >= self.volume:
            self.write_log(f"已交易数量：{self.traded}，总数量：{self.volume}")
            self.stop()
        else:
            self.put_variables_event()

    def on_order(self, order: OrderData):
        """"""
        if not order.is_active() and order.vt_orderid in self.vt_orderids:
            self.vt_orderids.remove(order.vt_orderid)

        self.put_variables_event()

    def buy_gradient_chase(self):
        """"""
        order_volume = min(self.volume - self.traded, self.last_tick.ask_volume_1//2)
        self.order_price = self.last_tick.ask_price_1
        vt_orderids = self.buy(
            self.vt_symbol,
            self.order_price,
            order_volume,
            offset=self.offset
        )
        self.vt_orderids += vt_orderids

    def sell_gradient_chase(self):
        """"""
        order_volume = min(self.volume - self.traded, self.last_tick.bid_volume_1//2)
        self.order_price = self.last_tick.bid_price_1
        vt_orderids = self.sell(
            self.vt_symbol,
            self.order_price,
            order_volume,
            offset=self.offset
        )
        self.vt_orderids += vt_orderids
