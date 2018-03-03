#!/usr/bin/env python
# -*-coding:utf8 -*-

# 账号、出生日期、省份、开户日期

import pymysql, re, pandas as pd, datetime
from multiprocessing import Pool
from const import db_config    # 数据库链接参数

fname1 = 'momentum.csv'
fname2 = 'reverse.csv'

# 身份证号前两位与省份名称对应关系
area = { 11: "北京", 12: "天津", 13: "河北", 14: "山西", 15: "内蒙古", 
	 21: "辽宁", 22: "吉林", 23: "黑龙江", 31: "上海",
	 32: "江苏", 33: "浙江", 34: "安徽", 35: "福建", 36: "江西",
	 37: "山东", 41: "河南", 42: "湖北", 43: "湖南", 44: "广东",
	 45: "广西", 46: "海南", 50: "重庆", 51: "四川", 52: "贵州",
	 53: "云南", 54: "西藏", 61: "陕西", 62: "甘肃", 63: "青海",
	 64: "宁夏", 65: "新疆", 71: "港澳台", 81: "港澳台", 82: "港澳台",
}

# 省份名称列表
'''
name = ["北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江", "上海", "江苏",
"浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "广西", "海南",
"重庆", "四川", "贵州", "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆"]
'''
name = ["北京上海", "河南"]

# 身份证号格式
reg = re.compile(r'\d{10}\*{8}')

def work(row):
	if not reg.match(row[1]):
		return
	conn = pymysql.connect(**db_config)
	cursor = conn.cursor()
	try:
		account = row[0]
		# 出生年
		birth = int(row[1][6:10])
		# 省份虚拟变量
		'''
		i = name.index(area[int(row[1][:2])])
		prov = [0.]*len(name)
		prov[i] += 1.
		'''
		key = int(row[1][:2])
		if key==11 or key==31:
			prov = [1., 0.]
		elif key==41:
			prov = [0., 1.]
		else:
			prov = [0., 0.]
		# 开户日期到2012年1月1日间的天数
		open_date = (row[2]-datetime.date(2012,1,1)).days
		# 确定考察时间段
		startday = max(row[2], datetime.date(2014,1,1))
		endday = datetime.date(2016,12,31)
		# 确定时间段内的交易日天数
		cursor.execute("select count(*) from market.trade_day where day between %s and %s", (startday,endday))
		days = cursor.fetchone()[0]
		# 月平均交易次数（设一个月22个交易日，下同）
		cursor.execute("select count(*) from chengjiao where account=%s and tradedate between %s and %s", (account,startday,endday))
		times = 1.* cursor.fetchone()[0] / days * 22
		# 月平均收益（百元，扣除手续费后）
		cursor.execute("select sum(profit-commission) from zijin where account=%s and tradedate between %s and %s", (account,startday,endday))
		profit = cursor.fetchone()[0] / 100 / days * 22
		# 写入文件
		if row[3]=='0':
			# 动量型
			df = pd.DataFrame([[account,1,birth,open_date,times,profit]+prov])
			df.to_csv(fname1, mode='a+', index=False, header=False)
			df = pd.DataFrame([[account,0,birth,open_date,times,profit]+prov])
			df.to_csv(fname2, mode='a+', index=False, header=False)
		elif row[3]=='1':
			# 逆向型
			df = pd.DataFrame([[account,1,birth,open_date,times,profit]+prov])
			df.to_csv(fname2, mode='a+', index=False, header=False)
			df = pd.DataFrame([[account,0,birth,open_date,times,profit]+prov])
			df.to_csv(fname1, mode='a+', index=False, header=False)
		else:
			# 不确定型
			df = pd.DataFrame([[account,0,birth,open_date,times,profit]+prov])
			df.to_csv(fname1, mode='a+', index=False, header=False)
			df.to_csv(fname2, mode='a+', index=False, header=False)
	except Exception as e:
		pass
	finally:
		cursor.close()
		conn.close()

# 写入表头
pd.DataFrame(None, columns=['account','momentum','birth','open_date','times','profit']+name).to_csv(fname1, mode='w', index=False)
pd.DataFrame(None, columns=['account','reverse','birth','open_date','times','profit']+name).to_csv(fname2, mode='w', index=False)

# 进程池
p = Pool(30)
conn = pymysql.connect(**db_config)
cursor = conn.cursor()
# 只有个人客户的生日才是有意义的，故排除了机构投资者
sql = "select zhanghu.account,certificate_id,open_date,type from zhanghu inner join traderType \
on zhanghu.account=traderType.account where account_head_type='0' and close_date is NULL"
cursor.execute(sql)
for row in cursor.fetchall():
	p.apply_async(work, args=(row,))
p.close()
p.join()
cursor.close()
conn.close()
print ("finish!")
