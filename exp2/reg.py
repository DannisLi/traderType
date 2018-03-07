#-*- coding:utf8 -*-

'''
回归分析
'''

import pandas as pd
import statsmodels.api as sm

f = open('regression.txt', 'w')

df = pd.read_csv('features.csv', header='infer', index_col=0)

# 逐个特征回归
for field in ['is_institution', 'age', 'open_time']:
    is_m = []
    is_r = []
    x = []
    samples = df[['is_momentum','is_reverse',field]]
    samples.dropna(axis=0, how='any', inplace=True)
    for index,row in samples:
        is_m.append(row['is_momentum'])
        is_r.append(row['is_reverse'])
        x.append(row[field])
    x = sm.add_constant(x)
    
    model = sm.Logit(is_m, x)
    result = model.fit()
    f.write(result.summary(yname='is_momentum', xname=['intercept', field]))
    f.write('\n')
    
    model = sm.Logit(is_r, x)
    result = model.fit()
    f.write(result.summary(yname='is_reverse', xname=['intercept', field]))
    f.write('\n')
    
f.close()