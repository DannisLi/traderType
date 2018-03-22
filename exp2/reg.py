#-*- coding:utf8 -*-

import pandas as pd
import statsmodels.api as sm

df = pd.read_csv('features.csv', header='infer', index_col=0)

features = df.columns[3:]

# 逐个特征回归
for fea in features:
    # 洗掉样本中的缺失值
    samples = df[['is_momentum', 'is_reverse', fea]]
    samples.dropna(axis=0, how='any', inplace=True)
    # 自变量中添加截距项
    x = sm.add_constant(samples[fea].values)
    # 回归动量型
    model = sm.Logit(samples.is_momentum, x)
    result = model.fit()
    print result.summary(yname='is_momentum', xname=['intercept', fea])
    print ''
    # 回归逆向型
    model = sm.Logit(samples.is_reverse, x)
    result = model.fit()
    print result.summary(yname='is_reverse', xname=['intercept', fea])
    print ''
    
# 机构投资者全部特征回归
samples = df[df.is_institution==1]
samples = samples[['is_momentum', 'is_reverse', 'trade_times', 'forced_times', 'leverage']]
samples.dropna(axis=0, how='any', inplace=True)
x = sm.add_constant(samples[['trade_times', 'forced_times', 'leverage']].values)
# 回归动量型
model = sm.Logit(samples.is_momentum, x)
result = model.fit()
print result.summary(yname='is_momentum', xname=['intercept', 'trade_times', 'forced_times', 'leverage'])
print ''
# 回归逆向型
model = sm.Logit(samples.is_reverse, x)
result = model.fit()
print result.summary(yname='is_reverse', xname=['intercept', 'trade_times', 'forced_times', 'leverage'])
print ''

# 非机构投资者全部特征回归
samples = df[df.is_institution==0]
samples = samples[['is_momentum', 'is_reverse', 'age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage']]
samples.dropna(axis=0, how='any', inplace=True)
X = sm.add_constant(samples[['age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage']].values)
# is_monentum
Y = samples.is_momentum
model = sm.Logit(Y, X)
result = model.fit()
print result.summary(yname='is_momentum', xname=['intercept', 'age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage'])
print ''
# is_reverse
Y = samples.is_reverse
model = sm.Logit(Y, X)
result = model.fit()
print result.summary(yname='is_reverse', xname=['intercept', 'age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage'])
print ''
