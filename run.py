
from vnpy.trader.engine import MainEngine
from vnpy.trader.ui import MainWindow, create_qapp

from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.algo_trading import AlgoTradingApp
from vnpy.app.data_recorder import DataRecorderApp
from vnpy.app.risk_manager import RiskManagerApp
from vnpy.app.option_master import OptionMasterApp


def main():
    """"""
    qapp = create_qapp()

    main_engine = MainEngine()

    main_engine.add_app(AlgoTradingApp)
    main_engine.add_app(CtaStrategyApp)
    main_engine.add_app(DataRecorderApp)
    main_engine.add_app(OptionMasterApp)
    main_engine.add_app(RiskManagerApp)

    main_window = MainWindow(main_engine)
    main_window.showMaximized()

    qapp.exec()


if __name__ == "__main__":
    main()
