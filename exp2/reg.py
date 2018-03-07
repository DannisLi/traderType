#-*- coding:utf8 -*-

'''
回归分析
'''

import numpy as np
import pandas as pd
import statsmodels.api as sm

f = open('regression.csv', 'w')

df = pd.read_csv('features.csv', header='infer', index_col=0)

# 逐个特征回归
for field in ['is_institution', 'age', 'open_time']:
    is_m = []
    is_r = []
    x = []
    for index,row in df['is_momentum','is_reverse',field].dropna(axis=0, how='any'):
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
    