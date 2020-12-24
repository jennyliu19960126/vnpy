import requests
import re
from xml.etree import ElementTree
from datetime import datetime
from vnpy.app.database_manager.data_objects import DbBarData
from vnpy.trader.constant import Interval, Exchange

# http请求正常号
HTTP_OK = 200

SHFE_FORMAT_URL = 'http://www.shfe.com.cn/data/dailydata/kx/kx#{DATA}.dat'
CFFEX_FORMAT_URL = 'http://www.cffex.com.cn/fzjy/mrhq/#{DATAURL}/index.xml'
CZCE_FORMAT_URL = 'http://www.czce.com.cn/cn/DFSStaticFiles/Future/#{YEAR}/#{DATA}/FutureDataDaily.txt'
INE_FORMAT_URL = 'http://www.ine.cn/data/dailydata/kx/kx#{DATA}.dat'
DCE_FORMAT_URL = 'http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html'

# 大商所品种汉字与字母对应关系字典.
DCE_PRODUCT_DICT = {u'豆一': 'a', u'豆二': 'b', u'胶合板': 'bb', u'玉米': 'c',
                    u'玉米淀粉': 'cs', u'纤维板': 'fb', u'铁矿石': 'i', u'焦炭': 'j',
                    u'鸡蛋': 'jd', u'焦煤': 'jm', u'聚乙烯': 'l', u'豆粕': 'm',
                    u'棕榈油': 'p', u'聚丙烯': 'pp', u'聚氯乙烯': 'v', u'豆油': 'y',
                    u'乙二醇': 'eg', u'粳米': 'rr', u'苯乙烯': 'eb', u'液化石油气': 'pg'
                    }

# 郑商所合约Id对应的数组下标.
INDEX_CZCE_CONTRACTID = 0
# 郑商所前一天的结算价对应的数组下标.
INDEX_CZCE_PRESETTLEMENTPRICE = 1
# 郑商所今日结算价对应的数组下标.
INDEX_CZCE_SETTLEMENTPRICE = 6
# 郑商所开盘价对应的数组下标.
INDEX_CZCE_OPENPRICE = 2
# 郑商所最高价对应的数组下标.
INDEX_CZCE_HIGHESTPRICE = 3
# 郑商所最低价对应的数组下标.
INDEX_CZCE_LOWESTPRICE = 4
# 郑商所收盘价对应的数组下标.
INDEX_CZCE_CLOSEPRICE = 5
# 郑商所涨跌1对应的数组下标.
INDEX_CZCE_ZD1 = 7
# 郑商所涨跌2对应的数组下标.
INDEX_CZCE_ZD2 = 8
# 郑商所成交量对应的数组下标.
INDEX_CZCE_VOLUME = 9
# 郑商所空盘量对应的数组下标.
INDEX_CZCE_OPENINTEREST = 10
# 郑商所空盘量增减对应的数组下标.
INDEX_CZCE_OPENINTERESTCHG = 11

# 大商所商品名称对应的数组下标.
INDEX_DCE_PRDUCTNAME = 0
# 大商所交割月份对应的数组下标.
INDEX_DCE_DELIVERYMONTH = 1
# 大商所前一天的结算价对应的数组下标.
INDEX_DCE_PRESETTLEMENTPRICE = 6
# 大商所今日结算价对应的数组下标.
INDEX_DCE_SETTLEMENTPRICE = 7
# 大商所开盘价对应的数组下标.
INDEX_DCE_OPENPRICE = 2
# 大商所最高价对应的数组下标.
INDEX_DCE_HIGHESTPRICE = 3
# 大商所最低价对应的数组下标.
INDEX_DCE_LOWESTPRICE = 4
# 大商所收盘价对应的数组下标.
INDEX_DCE_CLOSEPRICE = 5
# 大商所涨跌1对应的数组下标.
INDEX_DCE_ZD1 = 8
# 大商所涨跌2对应的数组下标.
INDEX_DCE_ZD2 = 9
# 大商所成交量对应的数组下标.
INDEX_DCE_VOLUME = 10
# 大商所空盘量对应的数组下标.
INDEX_DCE_OPENINTEREST = 11
# 大商所空盘量增减对应的数组下标.
INDEX_DCE_OPENINTERESTCHG = 12


class DatayesClient:
    """数据下载客户端父类"""

    def __init__(self):
        """Constructor"""
        self.name = u'数据下载客户端父类'
        self.format_url = ''          # 作为模板的url
        self.url = ''                # url
        self.date = datetime.now()   # 当前日期
        self.dataType = ''           # 数据格式(json、xml、txt)
        self.header = {}             # http请求头部
        self.connection_setting()

    def connection_setting(self):
        """
        设置连接,子类实现.
        :return:
        """
        pass

    # ----------------------------------------------------------------------
    def set_date(self, date=None):
        """
        设置日期.
        :param date: 要设置的日期,必须是datetime类型.
        :return:
        """
        if not date:
            self.date = datetime.now()
        else:
            self.date = date
        self.date = self.date.replace(hour=0, minute=0, second=0, microsecond=0)

        # ----------------------------------------------------------------------
    def download_futures_data_json(self):
        """
        下载json格式的数据.
        :return:
        """
        self.__format_url()
        r = requests.get(url=self.url, headers=self.header)
        if r.status_code != HTTP_OK:
            print(u'%shttp请求失败，状态代码%s' % (self.name, r.status_code))
            return None
        else:
            return r.json()

    # ----------------------------------------------------------------------
    def download_futures_data_xml(self):
        """
        下载xml格式的数据.
        :return:
        """
        self.__format_url()
        r = requests.get(url=self.url, headers=self.header)
        if r.status_code != HTTP_OK:
            print(u'%shttp请求失败，状态代码%s' % (self.name, r.status_code))
            return None
        else:
            result = r.text
            if result.startswith('\n<!DOCTYPE'):
                # 返回此内容，说明非交易日
                return None
            root = ElementTree.fromstring(result)
            return root.getiterator('dailydata')

    # ----------------------------------------------------------------------
    def download_futures_data_txt(self):
        """
        下载txt格式的数据.
        :return:
        """
        self.__format_url()
        r = requests.get(url=self.url, headers=self.header)
        if r.status_code != HTTP_OK:
            print(u'%shttp请求失败，状态代码%s' % (self.name, r.status_code))
            return None
        else:
            return r.text

    # ----------------------------------------------------------------------
    def parse_data(self):
        """
        获取数据List.子类实现.
        :return:
        """
        pass

    # ----------------------------------------------------------------------
    def __format_url(self):
        """
        格式化url.
        :return: 格式化之后的url.
        """
        self.url = self.format_url
        self.url = self.url.replace('#{DATA}', get_today_str(self.date))
        self.url = self.url.replace('#{DATAURL}', get_today_url_str(self.date))
        self.url = self.url.replace('#{YEAR}', str(self.date.year))


class SHFEDatayesClient(DatayesClient):
    """
    上期所数据下载
    """

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.format_url = SHFE_FORMAT_URL
        self.url = SHFE_FORMAT_URL
        self.name = u'上期所数据下载器'

    def connection_setting(self):
        self.header['Accept'] = '*/*'
        self.header['Accept-Encoding'] = 'gzip, deflate, sdch'
        self.header['Accept-Language'] = 'zh-CN,zh;q=0.8'
        self.header['Cache-Control'] = 'max-age=0'
        self.header['Connection'] = 'keep-alive'
        self.header['Host'] = 'www.shfe.com.cn'
        self.header['If-Modified-Since'] = '0'
        self.header['Referer'] = 'http://www.shfe.com.cn/statements/dataview.html?paramid=kx'

    def parse_data(self):
        json_dict = self.download_futures_data_json()
        # 按品种区分的字典,key:期货品种,value,合约信息list
        db_bars = []
        if json_dict:
            for item in json_dict['o_curinstrument']:
                month_str = item['DELIVERYMONTH'].strip()
                product_id = item['PRODUCTID'].strip()
                product_str = item['PRODUCTNAME'].strip()
                filter1 = u'小计' not in month_str
                filter2 = u'总计' not in product_str
                filter3 = u'合计' not in month_str
                filter4 = 'efp' not in month_str
                # 能源所的品种不在上期所下
                filter5 = 'sc' not in product_id
                filter6 = 'nr' not in product_id
                filter7 = 'lu' not in product_id
                filter8 = 'bc' not in product_id
                if filter1 and filter2 and filter3 and filter4 and filter5 and filter6 and filter7 and filter8:
                    db_bar = generate_db_bar_shfe(item, self.date)
                    db_bars.append(db_bar)

        return db_bars


class CFFEXDatayesClient(DatayesClient):
    """
    中金所数据下载
    """
    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super().__init__()
        self.format_url = CFFEX_FORMAT_URL
        self.url = CFFEX_FORMAT_URL
        self.name = u'中金所数据下载器'

    def connection_setting(self):
        self.header['Accept'] = 'application/xml, text/xml, */*; q=0.01'
        self.header['Accept-Encoding'] = 'deflate, sdch'
        self.header['Accept-Language'] = 'zh-CN,zh;q=0.8'
        self.header['Connection'] = 'keep-alive'
        self.header['Host'] = 'www.cffex.com.cn'
        self.header['Referer'] = 'http://www.cffex.com.cn/fzjy/mrhq/'

    # ----------------------------------------------------------------------
    def parse_data(self):
        xml = self.download_futures_data_xml()
        db_bars = []
        if xml:
            for item in xml:
                product_name = item.find('instrumentid').text.strip()
                filter1 = "IO" not in product_name
                if filter1:
                    db_bar = generate_db_bar_cffex(item, self.date)
                    db_bars.append(db_bar)
        return db_bars


class CZCEDatayesClient(DatayesClient):
    """
    郑商所数据下载
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super().__init__()
        self.format_url = CZCE_FORMAT_URL
        self.url = CZCE_FORMAT_URL
        self.name = u'郑商所数据下载器'

    def connection_setting(self):
        self.header['Cache-Control'] = 'max-age=0'
        self.header['Upgrade-Insecure-Requests'] = '1'
        self.header['Accept'] = '*/*'
        self.header['Accept-Encoding'] = 'gzip, deflate'
        self.header['Accept-Language'] = 'zh-cn'
        self.header['Connection'] = 'keep-alive'
        self.header['Host'] = 'www.czce.com.cn'

    def parse_data(self):
        txt = self.download_futures_data_txt()
        db_bars = []
        if txt:
            lines = txt.splitlines(False)
            for item in lines:
                item = item.strip()
                if len(item) > 0 and is_alphabet(item[0]):
                    db_bar = generate_db_bar_czce(item, self.date)
                    db_bars.append(db_bar)

        return db_bars


class DCEDatayesClient(DatayesClient):
    """
    大商所数据下载
    """
    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.param = {}
        super().__init__()
        self.format_url = DCE_FORMAT_URL
        self.url = DCE_FORMAT_URL
        self.name = u'大商所数据下载器'

    # ----------------------------------------------------------------------
    def connection_setting(self):
        # 设置header
        self.header['Accept'] = 'application/xml, text/xml, */*; q=0.01'
        self.header['Accept-Encoding'] = 'deflate'
        self.header['Accept-Language'] = 'zh-CN'
        self.header['Connection'] = 'keep-alive'
        self.header['Host'] = 'www.dce.com.cn'
        self.header['Content-Type'] = 'application/x-www-form-urlencoded'
        self.header['Referer'] = 'http://www.dce.com.cn/publicweb/quotesdata/dayQuotesCh.html'
        self.set_param()

    # ----------------------------------------------------------------------
    def set_param(self):
        """
        设置连接参数
        :return:
        """
        self.param['dayQuotes.variety'] = 'all'
        self.param['dayQuotes.trade_type'] = '0'
        self.param['year'] = str(self.date.year)
        # 大商所的月份从0开始,需要减一
        self.param['month'] = str(self.date.month - 1)
        self.param['day'] = str(self.date.day)
        self.param['exportFlag'] = 'txt'

    def set_date(self, date=None):
        super().set_date(date)
        # 修改日期后,需要重新设置一遍请求参数.
        self.set_param()

    # ----------------------------------------------------------------------
    def download_futures_data_txt(self):
        """
        下载txt格式的数据.
        :return:
        """
        r = requests.post(url=self.url, data=self.param)
        if r.status_code != HTTP_OK:
            print(u'%shttp请求失败，状态代码%s' % (self.name, r.status_code))
            return None
        else:
            return r.text

    # ----------------------------------------------------------------------
    def parse_data(self):
        txt = self.download_futures_data_txt()
        datas = []
        lines = txt.splitlines(False)
        for line in lines:
            line = line.strip()
            if not self.to_pass(line):
                db_bar = generate_db_bar_dce(line, self.date)
                datas.append(db_bar)

        return datas

    @staticmethod
    def to_pass(string):
        """"""
        if not string:
            # 空串直接跳过.
            return True
        else:
            for item in [u'大连商品交易所', u'查询日期', u'商品名称', u'小计', u'总计']:
                if item in string:
                    # 包含一个串就跳过.
                    return True

            return False


class INEDatayesClient(DatayesClient):
    """
    能源所数据下载
    """

    def __init__(self):
        """Constructor"""
        self.param = {}
        super().__init__()
        self.format_url = INE_FORMAT_URL
        self.url = INE_FORMAT_URL
        self.name = u'能源所数据下载器'

    def connection_setting(self):
        """
        设置header
        :return:
        """
        self.header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        self.header['Accept-Encoding'] = 'gzip, deflate, sdch'
        self.header['Accept-Language'] = 'zh-CN,zh;q=0.8'
        self.header['Connection'] = 'keep-alive'
        self.header['Host'] = 'www.ine.cn'

    def parse_data(self):
        json = self.download_futures_data_json()
        # 按品种区分的字典,key:期货品种,value,合约信息list
        db_bars = []
        if json:
            for item in json['o_curinstrument']:
                month_str = item['DELIVERYMONTH'].strip()
                product_id = item['PRODUCTID'].strip()
                product_str = item['PRODUCTNAME'].strip()
                filter1 = '小计' not in month_str
                filter2 = '总计' not in product_str
                filter3 = '合计' not in month_str
                filter4 = 'efp' not in month_str
                filter5 = '_tas' not in product_id

                if filter1 and filter2 and filter3 and filter4 and filter5:
                    db_bar = generate_db_bar_ine(item, self.date)
                    db_bars.append(db_bar)

        return db_bars


def generate_db_bar_ine(json, date):
    """
    通过上期所数据,创建瑞园CtaBar对象.
    :param json: 上期所数据是以json串的形式传入.
    :param date: datatime类型,时间
    :return: RY_CtaBarData对象,barType固定为1日k线
    """
    product = json['PRODUCTID'].strip()

    db_bar = DbBarData()
    db_bar.symbol = product[:product.find('_')] + json['DELIVERYMONTH'].strip()
    db_bar.exchange = Exchange.INE.value
    db_bar.vt_symbol = ".".join([db_bar.symbol, db_bar.exchange])
    db_bar.interval = Interval.DAILY.value
    db_bar.datetime = date
    db_bar.openinterest = parse_float(json['OPENINTEREST'], 0)
    db_bar.volume = parse_float(json['VOLUME'], 0)
    db_bar.close = parse_float(json['CLOSEPRICE'], 0)
    # 当没有成交量时,开盘价也不存在,故使用收盘价代替.
    db_bar.open = parse_float(json['OPENPRICE'], db_bar.close)
    # 当没有成交量时,最高最低价都不存在,故使用开盘价代替.
    db_bar.high = parse_float(json['HIGHESTPRICE'], db_bar.open)
    db_bar.low = parse_float(json['LOWESTPRICE'], db_bar.open)
    db_bar.gateway_name = "WEBSITE"

    return db_bar


def generate_db_bar_shfe(json, date):
    """
    通过上期所数据,创建瑞园CtaBar对象.
    :param json: 上期所数据是以json串的形式传入.
    :param date: datatime类型,时间
    :return: RY_CtaBarData对象,barType固定为1日k线
    """
    product = json['PRODUCTID'].strip()

    db_bar = DbBarData()
    db_bar.symbol = product[:product.find('_')] + json['DELIVERYMONTH'].strip()
    db_bar.exchange = Exchange.SHFE.value
    db_bar.vt_symbol = ".".join([db_bar.symbol, db_bar.exchange])
    db_bar.interval = Interval.DAILY.value
    db_bar.datetime = date
    db_bar.openinterest = parse_float(json['OPENINTEREST'], 0)
    db_bar.volume = parse_float(json['VOLUME'], 0)
    db_bar.close = parse_float(json['CLOSEPRICE'], 0)
    # 当没有成交量时,开盘价也不存在,故使用收盘价代替.
    db_bar.open = parse_float(json['OPENPRICE'], db_bar.close)
    # 当没有成交量时,最高最低价都不存在,故使用开盘价代替.
    db_bar.high = parse_float(json['HIGHESTPRICE'], db_bar.open)
    db_bar.low = parse_float(json['LOWESTPRICE'], db_bar.open)
    db_bar.gateway_name = "WEBSITE"

    return db_bar


def generate_db_bar_cffex(xml, date):
    """"""
    db_bar = DbBarData()

    db_bar.symbol = xml.find('instrumentid').text.strip()
    db_bar.exchange = Exchange.CFFEX.value
    db_bar.vt_symbol = ".".join([db_bar.symbol, db_bar.exchange])
    db_bar.interval = Interval.DAILY.value

    db_bar.datetime = date
    db_bar.openinterest = parse_float(xml.find('openinterest').text.strip().replace('.0', ''))
    db_bar.volume = parse_float(xml.find('volume').text.strip())
    db_bar.close = parse_float(xml.find('closeprice').text.strip())
    # 当没有成交量时,开盘价也不存在,故使用收盘价代替.
    db_bar.open = parse_float(xml.find('openprice').text, db_bar.close)
    # 当没有成交量时,最高最低价都不存在,故使用开盘价代替.
    db_bar.high = parse_float(xml.find('highestprice').text, db_bar.open)
    db_bar.low = parse_float(xml.find('lowestprice').text, db_bar.open)
    db_bar.gateway_name = "WEBSITE"

    return db_bar


def generate_db_bar_czce(txt, date):
    """"""
    db_bar = DbBarData()
    txt = txt.replace(',', '')
    str_list = txt.split('|')

    db_bar.symbol = str_list[INDEX_CZCE_CONTRACTID].strip()
    db_bar.exchange = Exchange.CZCE.value
    db_bar.vt_symbol = ".".join([db_bar.symbol, db_bar.exchange])
    db_bar.interval = Interval.DAILY.value
    db_bar.datetime = date
    db_bar.openinterest = parse_float(str_list[INDEX_CZCE_OPENINTEREST].strip())
    db_bar.volume = parse_float(str_list[INDEX_CZCE_VOLUME].strip())
    db_bar.open = parse_float(str_list[INDEX_CZCE_OPENPRICE].strip())
    db_bar.close = parse_float(str_list[INDEX_CZCE_CLOSEPRICE].strip())
    # 当没有成交量时,最高最低价都不存在,故使用开盘价代替.
    db_bar.high = parse_float(str_list[INDEX_CZCE_HIGHESTPRICE], db_bar.open)
    db_bar.low = parse_float(str_list[INDEX_CZCE_LOWESTPRICE], db_bar.open)

    db_bar.gateway_name = "WEBSITE"

    return db_bar


def generate_db_bar_dce(txt, date):
    """"""
    db_bar = DbBarData()
    txt = txt.replace(',', '')
    str_list = txt.split()

    product = DCE_PRODUCT_DICT[str_list[INDEX_DCE_PRDUCTNAME].strip()]
    db_bar.symbol = product + str_list[INDEX_DCE_DELIVERYMONTH].strip()
    db_bar.exchange = Exchange.DCE.value
    db_bar.vt_symbol = ".".join([db_bar.symbol, db_bar.exchange])
    db_bar.interval = Interval.DAILY.value
    db_bar.datetime = date
    db_bar.openinterest = parse_float(str_list[INDEX_DCE_OPENINTEREST].strip())
    db_bar.volume = parse_float(str_list[INDEX_DCE_VOLUME].strip())
    db_bar.open = parse_float(str_list[INDEX_DCE_OPENPRICE].strip())
    db_bar.close = parse_float(str_list[INDEX_DCE_CLOSEPRICE].strip())
    # 当没有成交量时,最高最低价都不存在,故使用开盘价代替.
    db_bar.high = parse_float(str_list[INDEX_DCE_HIGHESTPRICE].strip(), db_bar.open)
    db_bar.low = parse_float(str_list[INDEX_DCE_LOWESTPRICE].strip(), db_bar.open)

    db_bar.gateway_name = "WEBSITE"

    return db_bar


def parse_float(string, default: float = 0):
    """"""
    if not string:
        return default

    try:
        if isinstance(string, str):
            return float(string.strip())
        else:
            return float(string)
    except ValueError:
        return default


def get_today_str(date=None):
    """
    获取当前日期, 以字符串形式返回.(例如:date是2016-5-11,返回20160511)
    """
    if not date:
        date = datetime.now()
    return str(date.year) + "%02d" % date.month + "%02d" % date.day


def get_today_url_str(date=None):
    """
    获取对应date的日期,以字符串url的形式返回.(例如:今天是2016-5-11,返回201605/11,与上期所相比,多了一个斜杠)
    """
    if not date:
        date = datetime.now()
    return str(date.year) + "%02d" % date.month + "/%02d" % date.day


def is_alphabet(uchar):
    """
    判断一个字符是否是字母
    """
    return re.match("[a-zA-Z]+", uchar)


def parse_all_futures_data(date: datetime):
    """"""
    data_list = []
    classes = [DCEDatayesClient, SHFEDatayesClient, CFFEXDatayesClient, CZCEDatayesClient, INEDatayesClient]
    for cls in classes:
        client = cls()
        client.set_date(date)
        data_list = data_list + client.parse_data()

    return data_list
