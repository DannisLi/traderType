#-*- coding:utf8 -*-

import pydotplus
import pandas as pd
from sklearn import tree


df1 = pd.read_csv('momentum.csv', index_col=False)
df2 = pd.read_csv('reverse.csv', index_col=False)

clf = tree.DecisionTreeClassifier(min_samples_leaf=0.08)

clf.fit(df1.iloc[:,2:].values, df1.momentum.values)
dot_data = tree.export_graphviz(clf, out_file=None, feature_names=df1.columns[2:])
graph = pydotplus.graph_from_dot_data(dot_data)
graph.write_png('momentum.png')

clf.fit(df2.iloc[:,2:].values, df2.reverse.values)
dot_data = tree.export_graphviz(clf, out_file=None, feature_names=df2.columns[2:])
graph = pydotplus.graph_from_dot_data(dot_data)
graph.write_png('reverse.png')
