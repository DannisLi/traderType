#-*- coding:utf8 -*-

import datetime
import pandas as pd
from db import get_connection

conn = get_connection("investor")
cursor = conn.cursor()

data = []

# (account, is_momentum, is_reverse)
cursor.execute("select account,(case when p<=0.1 and coef>0 then 1 else 0 end),\
(case when p<=0.1 and coef<0 then 1 else 0 end) from traderType.exp1")

for account,is_momentum,is_reverse in cursor.fetchall():
    cursor.execute("select account_head_type,certificate_id,open_date,close_date from zhanghu where account=%s", (account,))
    account_head_type,certificate_id,open_date,close_date = cursor.fetchone()
    # 处理is_institution, age, open_time
    if account_head_type=='3':
        is_institution = 1
        age = None
        open_time = None
        is_Beijing_or_Shanghai = None
    else:
        is_institution = 0
        try:
            age = 2017 - int(certificate_id[6:10])
            if int(certificate_id[:2]) in [11, 31]:
                is_Beijing_or_Shanghai = 1
            else:
                is_Beijing_or_Shanghai = 0
        except:
            age = None
            is_Beijing_or_Shanghai = None
        open_time = (datetime.date(2017,1,1) - open_date).days
    # begin, end
    begin = max(datetime.date(2014,1,1), open_date)
    end = min(datetime.date(2016,12,31), close_date) if close_date is not None else datetime.date(2016,12,31)
    # 处理trade_times
    cursor.execute("select count(*) from chengjiao where account=%s", (account,))
    trade_times = 1. * cursor.fetchone()[0] / (end-begin).days * 22
    # 处理forced_times
    cursor.execute("select count(*) from chengjiao where account=%s and force_offset='1'", (account,))
    forced_times = 1. * cursor.fetchone()[0] / (end-begin).days * 252
    # 处理leverage
    cursor.execute("select avg(leverage) from leverage where account=%s", (account,))
    leverage = cursor.fetchone()[0]
    data.append([account, is_momentum, is_reverse, is_institution, age, open_time, trade_times, 
                 forced_times, is_Beijing_or_Shanghai, leverage])
    
df = pd.DataFrame(data, columns=['account', 'is_momentum', 'is_reverse', 'is_institution', 'age', 
                                 'open_time', 'trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage'])
df.to_csv('features.csv')

cursor.close()
conn.close()

