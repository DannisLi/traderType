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
    
