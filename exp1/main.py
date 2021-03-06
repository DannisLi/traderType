#-*- coding:utf8 -*-


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
    # 用户交易过的品种
    vari_list = []
    # 连接数据库
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor()
    # 仓位变化的前一天
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
            # 没有仓位变化
            continue
        for vari,deli in changed_oi.keys():
            # 结算价
            sql = "select settle from market.contract_daily where vari=%s and deli=%s and date=%s limit 1"
            if cursor.execute(sql, (vari,deli,day))==0:
                continue
            settle = cursor.fetchone()[0]
            if cursor.execute(sql, (vari,deli,lastday))==0:
                continue
            last_settle = cursor.fetchone()[0]
            # 可用资金
            if cursor.execute("select avail_fund from zijin where account=%s and tradedate=%s limit 1", (account, day))==0:
                continue
            avail_fund = cursor.fetchone()[0]
            # 每手数量
            if cursor.execute("select hand from market.vari2hand where vari=%s limit 1", (vari,))==0:
                continue
            hand = cursor.fetchone()[0]
            # 据交割期时间
            month_till_deli = int(deli[2:]) - day.month
            if 2000+int(deli[:2]) > day.year:
                month_till_deli += 12
            # 加入数据集
            data.append([changed_oi[(vari,deli)], (settle-last_settle)/last_settle, settle*hand, avail_fund, month_till_deli, vari])
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
    
    name = ['changed_oi', 'return_rate', 'settle*hand', 'avail_fund', 'month_till_deli']+['is_'+vari for vari in vari_list[:-1]]
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
        cursor.execute("insert into traderType.exp1 (account,samples,coef,p) values (%s,%s,%s,%s)", 
                       (account, len(df), float(result.params['return_rate']), float(result.pvalues['return_rate'])))
        conn.commit()
    except Exception as e:
        pass
    
    cursor.close()
    conn.close()
    

conn = pymysql.connect(**db_config)
cursor = conn.cursor()

cursor.execute("select distinct account from chicang")
accounts = [row[0] for row in cursor.fetchall()]

cursor.execute("select distinct day from market.trade_day where day between '20140101' and '20161231' order by day asc")
tdays = [row[0] for row in cursor.fetchall()]

cursor.close()
conn.close()

p = Pool()
for account in accounts:
    p.apply_async(solve, args=(account,))
p.close()
p.join()

print ('finish!')
