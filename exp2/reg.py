#-*- coding:utf8 -*-

import pandas as pd
import statsmodels.api as sm

df = pd.read_csv('features.csv', header='infer', index_col=0)

fields = df.columns[3:]

# 逐个特征回归
for field in fields:
    is_m = []
    is_r = []
    x = []
    samples = df[['is_momentum','is_reverse',field]]
    samples.dropna(axis=0, how='any', inplace=True)
    for index,row in samples.iterrows():
        is_m.append(row['is_momentum'])
        is_r.append(row['is_reverse'])
        x.append(row[field])
    x = sm.add_constant(x)
    
    model = sm.Logit(is_m, x)
    result = model.fit()
    print result.summary(yname='is_momentum', xname=['intercept', field])
    print ''
    
    model = sm.Logit(is_r, x)
    result = model.fit()
    print result.summary(yname='is_reverse', xname=['intercept', field])
    print ''
    
# 机构投资者全部特征回归
samples = df[df.is_institution==1]
samples = samples[['is_momentum', 'is_reverse', 'trade_times', 'forced_times', 'leverage']]
samples.dropna(axis=0, how='any', inplace=True)
X = sm.add_constant(samples[['trade_times', 'forced_times', 'leverage']].values)
# is_monentum
Y = samples.is_momentum.values
model = sm.Logit(Y, X)
result = model.fit()
print result.summary(yname='is_momentum', xname=['intercept', 'trade_times', 'forced_times', 'leverage'])
print ''
# is_reverse
Y = samples.is_reverse.values
model = sm.Logit(Y, X)
result = model.fit()
print result.summary(yname='is_reverse', xname=['intercept', 'trade_times', 'forced_times', 'leverage'])
print ''

# 非机构投资者全部特征回归
samples = df[df.is_institution==0]
samples = samples[['is_momentum', 'is_reverse', 'age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage']]
samples.dropna(axis=0, how='any', inplace=True)
X = sm.add_constant(samples[['age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage']].values)
# is_monentum
Y = samples.is_momentum.values
model = sm.Logit(Y, X)
result = model.fit()
print result.summary(yname='is_momentum', xname=['intercept', 'age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage'])
print ''
# is_reverse
Y = samples.is_reverse.values
model = sm.Logit(Y, X)
result = model.fit()
print result.summary(yname='is_reverse', xname=['intercept', 'age', 'open_time','trade_times', 'forced_times', 'is_Beijing_or_Shanghai', 'leverage'])
print ''
