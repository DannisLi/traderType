#-*- coding:utf8 -*-

'''
回归分析
'''

import pandas as pd

df = pd.read_csv('features.csv', header='infer', index_col=0)
print (df)