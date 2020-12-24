from pathlib import Path
from vnpy.trader.app import BaseApp
from .engine import DatabaseManagerEngine, APP_NAME


class DatabaseManagerApp(BaseApp):
    """"""
    app_name = APP_NAME
    app_module = __module__
    app_path = Path(__file__).parent
    display_name = "数据库管理"
    engine_class = DatabaseManagerEngine
    widget_name = "DatabaseManager"
    icon_name = "database.ico"
