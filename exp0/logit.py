#-*- coding:utf8 -*-

from statsmodels.discrete.discrete_model import MNLogit
import pandas as pd
import numpy as np

df1 = pd.read_csv('momentum.csv', index_col=False)
df1['intercept'] = 1.
df2 = pd.read_csv('reverse.csv', index_col=False)
df2['intercept'] = 1.


logit1 = MNLogit(df1.momentum, df1.iloc[:,2:])
logit2 = MNLogit(df2.reverse, df2.iloc[:,2:])
result1 = logit1.fit(method='newton', max_iter=1000)
result2 = logit2.fit(method='newton', max_iter=1000)

print result1.summary()
print result2.summary()
