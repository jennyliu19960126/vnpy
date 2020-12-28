"""
Event type string used in VN Trader.
"""

# 定时器事件
EVENT_TIMER = "eTimer"

# main_engine通用事件
EVENT_TICK = "eTick."
EVENT_TRADE = "eTrade."
EVENT_ORDER = "eOrder."
EVENT_POSITION = "ePosition."
EVENT_ACCOUNT = "eAccount."
EVENT_CONTRACT = "eContract."
EVENT_LOG = "eLog"

# Cta相关事件
EVENT_CTA_LOG = "eCtaLog"
EVENT_CTA_STRATEGY = "eCtaStrategy"
EVENT_CTA_STOPORDER = "eCtaStopOrder"

# 数据记录相关事件
EVENT_RECORDER_LOG = "eRecorderLog"
EVENT_RECORDER_UPDATE = "eRecorderUpdate"

# 数据库相关事件
EVENT_DB_LOG = "eDatabaseLog"

# 算法交易相关事件
EVENT_ALGO_LOG = "eAlgoLog"
EVENT_ALGO_SETTING = "eAlgoSetting"
EVENT_ALGO_VARIABLES = "eAlgoVariables"
EVENT_ALGO_PARAMETERS = "eAlgoParameters"

# 股票交易相关事件
EVENT_EQUITY_LOG = "eEquityLog"
EVENT_EQUITY_STRATEGY = "eEquityStrategy"
