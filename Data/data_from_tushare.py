import tushare as ts


#创建一个接口
import json
import os

def get_calendar(exchange : str, start_date : str, end_date : str, is_open : str):
    """获取某一个交易所的交易日历
    Args:
        exchange:   交易所代码。SSE=上交所，SZSE=深交所，CFFEX=中金所，SHFE=上期所，DCE=大商所，CZCE=郑商所，INE=能源中心。
        start_date: 起始日期，  格式 YYYYMMDD，如 "20260706"
        end_date:   结束日期，  格式 YYYYMMDD，如 "20261020"
        is_open :   是否开市，  "1" 表示开市， "0"表示闭市

    Returns:
        pandas.DataFrame，每个交易日一行，主要列包括：
            exchange (str): 交易所代码
            cal_date (str): 日历日期，YYYYMMDD
            is_open (str): 是否开市，"1" 表示开市
            pretrade_date (str): 上一交易日，YYYYMMDD
    
    """
    path = os.path.join("config.json")
    with open(path, "r", encoding = 'utf-8') as f:
        config = json.load(f)
    token = config.get("tushare_token")
    pro = ts.pro_api(token)
    calendar = pro.trade_cal(exchange = exchange, start_date = start_date, end_date = end_date, is_open = is_open)
    return calendar

def fetch_stock_daily_interval(code : str , start_date : str , end_date : str ) :
    """获取单只股票在指定区间的日线行情。
    Args:
        code: 股票代码，带交易所后缀，如 "002475.SZ"。
        start_date: 起始日期，YYYYMMDD，如 "20261020"。
        end_date: 结束日期，YYYYMMDD，如 "20261021"。
        fields： 可选的，可以精确指定输出什么字段，比如盘后交易量
    Returns:
        pandas.DataFrame，列包括：
            trade_date (str): 交易日期
            open (float): 开盘价
            high (float): 最高价
            low (float): 最低价
            close (float): 收盘价
            pre_close (float): 昨收价[除权价]
            change (float): 涨跌额
            pct_chg (float): 涨跌幅(%)，基于除权后昨收计算
            vol (float): 成交量（手）
            amount (float): 成交额（千元）
            ah_vol (float): 盘后成交量（手），2026-07-06 起有数据

    """
    path = os.path.join('config.json')
    with open(path, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    token = config.get("tushare_token")
    pro = ts.pro_api(token)

    df = pro.daily(ts_code = code, start_date = start_date, end_date = end_date)
    return df

def fetch_stock_daily(code : str , trade_date: str, fields : str) :
    """获取单只股票在指定区间的日线行情。
    Args:
        code        : 股票代码，带交易所后缀，如 "002475.SZ"。
        trade_date  :
        fields      :
    Returns:
        pandas.DataFrame，列包括：
            trade_date (str)        : 交易日期
            open (float)            : 开盘价
            high (float)            : 最高价
            low (float)             : 最低价
            close (float)           : 收盘价
            pre_close (float)       : 昨收价[除权价]
            change (float)          : 涨跌额
            pct_chg (float)         : 涨跌幅(%)，基于除权后昨收计算
            vol (float)             : 成交量（手）
            amount (float)          : 成交额（千元）
            ah_vol (float)          : 盘后成交量（手），2026-07-06 起有数据

    """
    path = os.path.join('config.json')
    with open(path, 'r', encoding = 'utf-8') as f:
        config = json.load(f)
    token = config.get("tushare_token")
    pro = ts.pro_api(token)

    df = pro.daily(ts_code = code, trade_date = trade_date, fields = fields)
    return df


def fetch_index_daily(code: str, trade_date: str, fields: str):
    """获取某个指数在指定交易日的日线数据。

    股票和指数在 Tushare 中使用不同接口：
    股票用 ``pro.daily``，指数用 ``pro.index_daily``。
    例如，中证 500 的代码是 ``000905.SH``。
    """
    path = os.path.join("config.json")
    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    token = config.get("tushare_token")
    pro = ts.pro_api(token)
    return pro.index_daily(ts_code=code, trade_date=trade_date, fields=fields)

if __name__ == "__main__" :

    # calendar = get_calendar('SSE', '20260920', '20261020')
    # print(calendar)
    # print(type(calendar))

    # df = fetch_stock_daily("002475.SZ", '20261020', '20261021')
    # print(df.head())
    # print(type(df))
    sig = fetch_stock_daily('002475.SZ', '20260921', fields='ts_code,change,ah_amount,amount')
    print(sig)

