#-*- coding:utf8 -*-

import datetime

# 交易日列表，存储变量均为datetime.date类型
tdays = []

# 加载交易日日期数据
with open('../data/tradingday.csv', 'r') as f:
    for line in f.readlines():
        line = line.strip()
        year = int(line[:4])
        month = int(line[5:7])
        day = int(line[8:])
        tdays.append(datetime.date(year, month, day))


# 判断得否为交易日
def is_tday(d):
    return d in tdays

# 计算该交易日后第n个交易日的日期
def shift(d, n):
    i = tdays.index(d) + n
    assert i>=0
    return tdays[i]

