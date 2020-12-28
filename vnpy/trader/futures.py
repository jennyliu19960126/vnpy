from dataclasses import dataclass


@dataclass
class FuturesProduct(object):
    """
    期货品种类.
    """
    product_name: str  # 期货名称
    multiplier: float  # 单位价值
    price_tick: float  # 期货品种最小价格变动
    exchange: str  # 所属期货公司
    time_slices: list  # 时间段列表


@dataclass
class SpreadProduct:
    """
    价差品种类
    """
    spread_name: str  # 价差名称
    active_leg: str  # 主动腿品种名称
    passive_leg: str  # 被动腿品种名称
    ZL_months: list  # 主力月份列表


# 交易时间段元组
# 夜盘
T2100T2300 = ('21:00:10', '22:59:55')
T2100T0100 = ('21:00:10', '00:59:55')
T2100T0230 = ('21:00:10', '02:29:55')
# 上午
T0900T1015 = ('09:00:10', '10:14:55')
T1030T1130 = ('10:30:01', '11:29:55')
T0915T1130 = ('09:15:10', '11:29:55')
T0930T1130 = ('09:30:10', '11:29:55')
# 下午
T1300T1500 = ('13:00:01', '14:59:55')
T1330T1500 = ('13:30:01', '14:59:55')
T1300T1515 = ('13:00:01', '15:14:55')

FuturesProductDict = {
    # 上期所相关品种
    'au': FuturesProduct('沪金', 1000, 0.05, 'SHFE', [T2100T0230, T0900T1015, T1030T1130, T1330T1500]),
    'ag': FuturesProduct('沪银', 15, 1, 'SHFE', [T2100T0230, T0900T1015, T1030T1130, T1330T1500]),
    'cu': FuturesProduct('沪铜', 5, 10, 'SHFE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500]),
    'al': FuturesProduct('沪铝', 5, 5, 'SHFE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500]),
    'zn': FuturesProduct('沪锌', 5, 5, 'SHFE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500]),
    'pb': FuturesProduct('沪铅', 5, 5, 'SHFE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500]),
    'ni': FuturesProduct('沪镍', 1, 10, 'SHFE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500]),
    'sn': FuturesProduct('沪锡', 1, 10, 'SHFE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500]),
    'ss': FuturesProduct('不锈钢', 5, 5, 'SHFE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500]),
    'rb': FuturesProduct('螺纹钢', 10, 1, 'SHFE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'hc': FuturesProduct('热卷', 10, 1, 'SHFE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'fu': FuturesProduct('燃油', 10, 1, 'SHFE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'bu': FuturesProduct('沥青', 10, 2, 'SHFE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'ru': FuturesProduct('橡胶', 10, 5, 'SHFE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'sp': FuturesProduct('纸浆', 10, 2, 'SHFE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'wr': FuturesProduct('线材', 10, 1, 'SHFE', [T0900T1015, T1030T1130, T1330T1500]),

    # 郑商所相关品种
    'CF': FuturesProduct('棉花', 5, 5, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'CY': FuturesProduct('棉纱', 5, 5, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'SR': FuturesProduct('白糖', 10, 1, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'TA': FuturesProduct('PTA', 5, 2, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'PF': FuturesProduct('短纤', 5, 2, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'OI': FuturesProduct('菜籽油', 10, 2, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'MA': FuturesProduct('甲醇', 10, 1, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'RM': FuturesProduct('菜粕', 10, 1, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'ZC': FuturesProduct('动力煤', 100, 0.2, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'FG': FuturesProduct('玻璃', 20, 1, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'SA': FuturesProduct('纯碱', 20, 1, 'CZCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'SF': FuturesProduct('硅铁', 5, 2, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'SM': FuturesProduct('锰硅', 5, 2, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'AP': FuturesProduct('苹果', 10, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'CJ': FuturesProduct('红枣', 5, 5, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'UR': FuturesProduct('尿素', 20, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'WH': FuturesProduct('郑麦', 20, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'PM': FuturesProduct('普麦', 50, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'RS': FuturesProduct('菜籽', 10, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'RI': FuturesProduct('早稻', 20, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'JR': FuturesProduct('粳稻', 20, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),
    'LR': FuturesProduct('晚稻', 20, 1, 'CZCE', [T0900T1015, T1030T1130, T1330T1500]),

    # 大商所相关品种
    'l': FuturesProduct('塑料', 5, 5, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'v': FuturesProduct('PVC', 5, 5, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'pp': FuturesProduct('PP', 5, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'eb': FuturesProduct('EB', 5, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'eg': FuturesProduct('EG', 10, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'pg': FuturesProduct('LPG', 20, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'i': FuturesProduct('铁矿', 100, 0.5, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'j': FuturesProduct('焦炭', 100, 0.5, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'jm': FuturesProduct('焦煤', 60, 0.5, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'a': FuturesProduct('豆一', 10, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'b': FuturesProduct('豆二', 10, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'c': FuturesProduct('玉米', 10, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'cs': FuturesProduct('淀粉', 10, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'm': FuturesProduct('豆粕', 10, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'y': FuturesProduct('豆油', 10, 2, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'p': FuturesProduct('棕榈油', 10, 2, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'rr': FuturesProduct('粳米', 10, 1, 'DCE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'jd': FuturesProduct('鸡蛋', 10, 1, 'DCE', [T0900T1015, T1030T1130, T1330T1500]),
    'bb': FuturesProduct('胶板', 500, 0.05, 'DCE', [T0900T1015, T1030T1130, T1330T1500]),
    'fb': FuturesProduct('纤板', 500, 0.05, 'DCE', [T0900T1015, T1030T1130, T1330T1500]),

    # 中金所相关品种
    'IF': FuturesProduct('IF', 300, 0.2, 'CFFEX', [T0930T1130, T1300T1500]),
    'IH': FuturesProduct('IH', 300, 0.2, 'CFFEX', [T0930T1130, T1300T1500]),
    'IC': FuturesProduct('IC', 200, 0.2, 'CFFEX', [T0930T1130, T1300T1500]),
    'T': FuturesProduct('十债', 10000, 0.005, 'CFFEX', [T0930T1130, T1300T1515]),
    'TF': FuturesProduct('五债', 10000, 0.005, 'CFFEX', [T0930T1130, T1300T1515]),
    'TS': FuturesProduct('二债', 20000, 0.005, 'CFFEX', [T0930T1130, T1300T1515]),

    # 上能所相关品种
    'sc': FuturesProduct('原油', 1000, 0.1, 'INE', [T2100T0230, T0900T1015, T1030T1130, T1330T1500]),
    'nr': FuturesProduct('NR', 10, 5, 'INE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'lu': FuturesProduct('LU', 10, 1, 'INE', [T2100T2300, T0900T1015, T1030T1130, T1330T1500]),
    'bc': FuturesProduct('国际铜', 5, 10, 'INE', [T2100T0100, T0900T1015, T1030T1130, T1330T1500])
}

one_five_nine = [1, 5, 9]
one_five_ten = [1, 5, 10]
six_twelve = [6, 12]
one_to_twelve = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
three_six_nine_twelve = [3, 6, 9, 12]

SpreadProductDict = {
    # 上期所相关品种
    "cu&cu": SpreadProduct("cu&cu", "cu", "cu", one_to_twelve),
    "al&al": SpreadProduct("al&al", "al", "al", one_to_twelve),
    "zn&zn": SpreadProduct("zn&zn", "zn", "zn", one_to_twelve),
    "pb&pb": SpreadProduct("pb&pb", "pb", "pb", one_to_twelve),
    "ni&ni": SpreadProduct("ni&ni", "ni", "ni", one_to_twelve),
    "sn&sn": SpreadProduct("sn&sn", "sn", "sn", one_to_twelve),
    "au&au": SpreadProduct("au&au", "au", "au", six_twelve),
    "ag&ag": SpreadProduct("ag&ag", "ag", "ag", six_twelve),
    "rb&rb": SpreadProduct("rb&rb", "rb", "rb", one_five_ten),
    "hc&hc": SpreadProduct("hc&hc", "hc", "hc", one_five_ten),
    "rb&hc": SpreadProduct("rb&hc", "rb", "hc", one_five_ten),  # SPC
    "fu&fu": SpreadProduct("fu&fu", "fu", "fu", one_five_nine),
    "bu&bu": SpreadProduct("bu&bu", "bu", "bu", six_twelve),
    "ru&ru": SpreadProduct("ru&ru", "ru", "ru", one_five_nine),
    "sp&sp": SpreadProduct("ru&ru", "ru", "ru", one_five_nine),
    # 郑商所相关品种
    "CF&CF": SpreadProduct("CF&CF", "CF", "CF", one_five_nine),
    "SR&SR": SpreadProduct("SR&SR", "SR", "SR", one_five_nine),
    "TA&TA": SpreadProduct("TA&TA", "TA", "TA", one_five_nine),
    "OI&OI": SpreadProduct("OI&OI", "OI", "OI", one_five_nine),
    "MA&MA": SpreadProduct("MA&MA", "MA", "MA", one_five_nine),
    "FG&FG": SpreadProduct("FG&FG", "FG", "FG", one_five_nine),
    "SA&SA": SpreadProduct("SA&SA", "SA", "SA", one_five_nine),
    "RM&RM": SpreadProduct("RM&RM", "RM", "RM", one_five_nine),
    'ZC&ZC': SpreadProduct("ZC&ZC", "ZC", "ZC", one_five_nine),
    "SF&SF": SpreadProduct("SF&SF", "SF", "SF", one_five_nine),
    "SM&SM": SpreadProduct("SM&SM", "SM", "SM", one_five_nine),
    "SF&SM": SpreadProduct("SF&SM", "SF", "SM", one_five_nine),  # SPC
    "SA&FG": SpreadProduct("SA&FG", "SA", "FG", one_five_nine),  # SPC
    "AP&AP": SpreadProduct("AP&AP", "AP", "AP", one_five_ten),
    # 大商所相关品种
    "c&c": SpreadProduct("c&c", "c", "c", one_five_nine),
    "cs&cs": SpreadProduct("cs&cs", "cs", "cs", one_five_nine),
    "c&cs": SpreadProduct("c&cs", "c", "cs", one_five_nine),  # SPC
    "a&a": SpreadProduct("a&a", "a", "a", one_five_nine),
    "m&m": SpreadProduct("m&m", "m", "m", one_five_nine),
    "a&m": SpreadProduct("a&m", "a", "m", one_five_nine),  # SPC
    "y&y": SpreadProduct("y&y", "y", "y", one_five_nine),
    "p&p": SpreadProduct("p&p", "p", "p", one_five_nine),
    "y&p": SpreadProduct("y&p", "y", "p", one_five_nine),  # SPC
    "jd&jd": SpreadProduct("jd&jd", "jd", "jd", one_five_nine),
    "l&l": SpreadProduct("l&l", "l", "l", one_five_nine),
    "v&v": SpreadProduct("v&v", "v", "v", one_five_nine),
    "l&v": SpreadProduct("l&v", "l", "v", one_five_nine),  # SPC
    "pp&pp": SpreadProduct("pp&pp", "pp", "pp", one_five_nine),
    "j&j": SpreadProduct("j&j", "j", "j", one_five_nine),
    "jm&jm": SpreadProduct("jm&jm", "jm", "jm", one_five_nine),
    "i&i": SpreadProduct("i&i", "i", "i", one_five_nine),
    "eg&eg": SpreadProduct("eg&eg", "eg", "eg", one_five_nine),
    # 中金所相关品种
    "IF&IF": SpreadProduct("IF&IF", "IF", "IF", one_to_twelve),
    "IC&IC": SpreadProduct("IC&IC", "IC", "IC", one_to_twelve),
    "IH&IH": SpreadProduct("IH&IH", "IH", "IH", one_to_twelve),
    "IF&IH": SpreadProduct("IF&IH", "IF", "IH", one_to_twelve),  # SPC
    "TF&TF": SpreadProduct("TF&TF", "TF", "TF", three_six_nine_twelve),
    "T&T": SpreadProduct("T&T", "T", "T", three_six_nine_twelve),
    # 上能所相关品种
    "sc&sc": SpreadProduct("sc&sc", "sc", "sc", one_to_twelve)
}
