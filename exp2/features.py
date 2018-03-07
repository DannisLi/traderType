#-*- coding:utf8 -*-

import datetime
import pandas as pd
from db import get_connection

conn = get_connection("investor")
cursor = conn.cursor()

data = []

cursor.execute("select account,(case when p<=0.1 and coef>0 then 1 else 0 end),\
(case when p<=0.1 and coef<0 then 1 else 0 end) from traderType.exp1")

for account,is_momentum,is_reverse in cursor.fetchall():
    cursor.execute("select account_head_type,certificate_id,open_date from zhanghu where account=%s limit 1", (account,))
    account_head_type,certificate_id,open_date = cursor.fetchone()
    if account_head_type=='3':
        is_institution = 1
        age = None
        open_time = None
    else:
        is_institution = 0
        try:
            birth = datetime.date(certificate_id[6:10], certificate_id[10:12], certificate_id[13:14])
            age = 2017 - birth.year
        except:
            age = None
        open_time = (datetime.date(2017,1,1) - open_date).days
    data.append([account, is_momentum, is_reverse, is_institution, age, open_time])
    
df = pd.DataFrame(data, columns=['account', 'is_momentum', 'is_reverse', 'is_institution', 'age', 'open_time'])
df.to_csv('features.csv')

cursor.close()
conn.close()

