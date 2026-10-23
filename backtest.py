from infrustructure import Account, Position, transaction_cost #账户的基建设施和交易环境
from Data.data_from_tushare import get_calendar, fetch_index_daily, fetch_stock_daily

#回测初始参数
account = Account(1, 20000, None, None)
start_date = '20200101'
end_date = '20261020'
code = '002475.SZ'
market_index = '000905.SH'

#获取交易日历
calendar = get_calendar('SZSE', '20260706', '20261020', is_open='1')
trade_date = calendar["cal_date"].sort_values(ascending=True).to_list()  # 正序



for index, date in enumerate(trade_date[:-1]):
    next_date = trade_date[index + 1]







