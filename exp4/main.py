#-*- coding:utf8 -*-

import warnings
from statsmodels.discrete.discrete_model import Logit
from multiprocessing import Pool
from db import DB

warnings.filterwarnings('error')

def model1(X, Y):
    # return (P(up|up), P(down|up), P(up|down), P(down|down))
    logit = Logit()
    
def model2(X, Y):
    # return (P(y=1|x=1), P(y=0|x=1), P(y=1|x=0), P(y=0|x=0))
    cnt = [0] * 4
    n = len(X)
    for i in range(n):
        x = X[i]
        y = Y[i]
        if x==1:
            if y==1:
                cnt[0] += 1
            else:
                cnt[1] += 1
        else:
            if y==1:
                cnt[2] += 1
            else:
                cnt[3] += 1
    return [x/n for x in cnt]



def solve(accounts):
    db = DB("investor")
    for account in accounts:
        X = []
        Y = []
        days = db.execute_sql("(select distinct tradedate from chicang where account=%s) union \
        (select lastday from market.trade_day where day in (select distinct tradedate from chicang where account=%s) and day>='20140101')",
        (account, account))
        for day in days:
            result = db.execute_sql("select lastday,nextday from market.trade_day where day=%s and nextday<='20161231' limit 1", (day,))
            if result is None:
                continue
            else:
                lastday,nextday = result            
            contracts = db.execute_sql("select distinct vari,deli from chicang where account=%s and (day=%s or day=%s)",
                                       (account, day, nextday))
            for vari,deli in contracts:
                # 今日结算价
                settle = db.execute_sql("select settle from market.contract_daily where vari=%s and deli=%s and date=%s limit 1",
                                        (vari, deli, day))
                if settle is None:
                    continue
                else:
                    settle = settle[0]
                # 上一日结算价
                last_settle = db.execute_sql("select settle from market.contract_daily where vari=%s and deli=%s and date=%s limit 1",
                                             (vari, deli, lastday))
                if last_settle is None:
                    continue
                else:
                    last_settle = last_settle[0]
                # 价格变化
                if last_settle < settle:
                    settle_change = 1    # up
                elif last_settle > settle:
                    settle_change = 0    # down
                else:
                    continue
                # 今日持仓量（买为正，卖为负）
                oi = db.execute_sql("select sum(case when bs_flag=0 then qty else -qty end) from chicang where account=%s and tradedate=%s and \
                vari=%s and deli=%s", (account, day, vari, deli))[0]
                if oi is None:
                    oi = 0
                next_oi = db.execute_sql("select sum(case when bs_flag=0 then qty else -qty end) from chicang where account=%s and tradedate=%s and \
                vari=%s and deli=%s", (account, nextday, vari, deli))[0]
                if next_oi is None:
                    next_oi = 0
                # 客户行为
                if next_oi>oi:
                    behavior = 1    # up
                elif next_oi<oi:
                    behavior = 0    # down
                else:
                    continue
                X.append(settle_change)
                Y.append(behavior)
        if len(X)==0:
            continue
        
        model1(X, Y)
        model2(X, Y)
        

db = DB("investor")
accounts = db.execute_sql("select distinct account from chicang")
db.close()

account_num = len(accounts)
process_num = 20
account_per_precess = int(account_num/process_num)
assert account_per_precess > 0

pool = Pool()
for i in range(process_num):
    s = i * account_per_precess
    if i<process_num-1:
        t = (i+1) * account_per_precess
    else:
        t = account_num
    pool.apply_async(solve, (accounts[s:t],))
pool.close()
pool.join()
print ("finish!")


'''
for account in accounts:
    X = []
    Y = []
    for i in range(len(days)):
        #  今日持仓合约 或 明日持仓合约
        sql = "(select distinct vari_code,deliv_date from chicang where account=%s and tradedate=%s) union \
        (select distinct vari_code,deliv_date from chicang where account=%s and tradedate=%s)"
        cursor.execute(sql, (account,day,account,nextday))
        contracts = cursor.fetchall()
        for contract in contracts:
            # 结算价（要求昨天和今天都有结算价）
            sql = "select settle from commodity.contract_daily where day=%s and code=%s and deli=%s"
            if cursor.execute(sql, (day,contract[0],contract[1]))==0:
                continue
            settle = cursor.fetchone()[0]
            if cursor.execute(sql, (lastday,contract[0],contract[1]))==0:
                continue
            settle_last = cursor.fetchone()[0]
            if settle==settle_last:
                continue
            x = 1. if settle>settle_last else -1.
            x = (x, 1.)    # 增加截距
            # 持仓
            sql = "select sum(qty) from chicang where account=%s and tradedate=%s and vari_code=%s and deliv_date=%s and bs_flag=%s"
            for bs_flag in ('0','1'):
                # 今日持仓量
                cursor.execute(sql, (account,day,contract[0],contract[1],bs_flag))
                oi = cursor.fetchone()[0]
                if oi is None:
                    oi = 0
                # 明日持仓量
                cursor.execute(sql, (account,nextday,contract[0],contract[1],bs_flag))
                oi_next = cursor.fetchone()[0]
                if oi_next is None:
                    oi_next = 0
                # 行为分析
                if bs_flag=='0' and oi_next>oi:
                    y = 1
                elif bs_flag=='0' and oi_next<oi:
                    y = 0
                elif bs_flag=='1' and oi_next>oi:
                    y = 0
                elif bs_flag=='1' and oi_next<oi:
                    y = 1
                else:
                    continue
                X.append(x)
                Y.append(y)
    samples = len(X)
    if samples<20:
        continue
    logit = Logit(Y, X)
    try:
        result = logit.fit(maxiter=100, disp=False)
    except:
        continue
    w,b = result.params
    p_w,p_b = result.pvalues
    p1,p2 = result.predict(((1.,1.), (-1.,1.)))
    p2 = 1 - p2
    w = float(w)
    b = float(b)
    p_w = float(p_w)
    p_b = float(p_b)
    p1 = float(p1)
    p2 = float(p2)
    sql = "insert into price_change_direction2behavior (account,w,b,p_w,p_b,p1,p2,samples) values (" + "%s,"*7 + "%s)"
    cursor.execute(sql, (account,w,b,p_w,p_b,p1,p2,samples))
    conn.commit()
'''

