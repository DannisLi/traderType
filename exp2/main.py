#-*- coding:utf8 -*-

'''
改变了exp2的采样方法，采用与《what makes investors trade? 》类似的采用方式，
若T日到T+1日某合约发生仓位变化，则将这两日有持仓的所有合约加入数据集。
'''

import pymysql
import numpy as np
import pandas as pd
from multiprocessing import Pool
from statsmodels.regression.linear_model import OLS

db_config = {
    'host': '219.224.169.45',
    'user': 'lizimeng',
    'password': 'codegeass',
    'db': 'investor',
    'charset': 'utf8'
}


def solve(account):
    data = []
    vari_list = []
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("(select distinct tradedate from chicang where account=%s) union \
    (select distinct lastday from market.trade_day where lastday>='20140101' and \
    day in (select distinct tradedate from chicang where account=%s))", (account,account))
    days = [row[0] for row in cursor.fetchall()]
    for day in days:
        try:
            i = tdays.index(day)
            assert 0 < i < len(tdays)-1
            nextday = tdays[i+1]
            lastday = tdays[i-1]
        except:
            continue
        
        sql = "select vari,deli,sum(case when bs_flag='0' then open_hand else -1*open_hand end) \
        from chicang where account=%s and tradedate=%s group by vari,deli"
        
        cursor.execute(sql, (account,day))
        oi = {}
        for row in cursor.fetchall():
            oi[(row[0],row[1])] = row[2]
        cursor.execute(sql, (account,nextday))
        
        next_oi = {}
        for row in cursor.fetchall():
            next_oi[(row[0],row[1])] = row[2]
        
        changed_oi = {}
        for key in oi.keys():
            try:
                changed_oi[key] = next_oi[key] - oi[key]
            except:
                changed_oi[key] = 0 - oi[key]
        for key in next_oi.keys():
            if key in changed_oi:
                continue
            changed_oi[key] = next_oi[key]
        
        if 0 in changed_oi.values() and len(set(changed_oi.values()))==1:
            # 没有仓位变化的合约
            continue
        
        for vari,deli in changed_oi.keys():
            if cursor.execute("select settle from market.contract_daily where vari=%s and deli=%s and date=%s limit 1", (vari,deli,day))==0:
                continue
            settle = cursor.fetchone()[0]
            if cursor.execute("select settle from market.contract_daily where vari=%s and deli=%s and date=%s limit 1", (vari,deli,lastday))==0:
                continue
            last_settle = cursor.fetchone()[0]
            cursor.execute("select avail_fund from zijin where account=%s and tradedate=%s limit 1", (account, day))
            avail_fund = cursor.fetchone()[0]
            month_till_deli = int(deli[2:]) - day.month
            if 2000+int(deli[:2]) > day.year:
                month_till_deli += 12
            data.append([changed_oi[key], (settle-last_settle)/last_settle, settle, avail_fund, month_till_deli, vari])
            if vari not in vari_list:
                vari_list.append(vari)
    
    if len(data)<20:
        cursor.close()
        conn.close()
        return
    
    for row in data:
        vari = row[-1]
        row.pop()
        i = vari_list.index(vari)
        dummy = [0]*(len(vari_list)-1)
        if i < len(vari_list)-1:
            dummy[i] = 1
        row.extend(dummy)
    
    name = ['changed_oi', 'return_rate', 'settle', 'avail_fund', 'month_till_deli']+['is_'+vari for vari in vari_list[:-1]]
    df = pd.DataFrame(data, columns=name, dtype=np.float64)
    
    # 消掉单一值的列
    for col in name[2:]:
        flag = True
        x = df.at[0, col]
        for y in df[col][1:]:
            if x!=y:
                flag = False
                break
        if flag:
            del df[col]
    
    df['intercept'] = 1.
    try:
        ols = OLS(df.changed_oi, df.iloc[:,1:])
        result = ols.fit()
        cursor.execute("insert into traderType.exp3 (account,samples,coef,p) values (%s,%s,%s,%s)", 
                       (account, df.shape[0], float(result.params['return_rate']), float(result.pvalues['return_rate'])))
        conn.commit()
    except:
        pass
    
    cursor.close()
    conn.close()
    

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

cursor.execute("select distinct account from chicang")
accounts = [row[0] for row in cursor.fetchall()]

cursor.execute("select date from market.trade_day where date between '20140101' and '20161231' order by date asc")
tdays = [row[0] for row in cursor.fetchall()]

cursor.close()
conn.close()

p = Pool(20)
for account in accounts:
    p.apply_async(solve, args=(account,))
p.close()
p.join()

print ('finish!')