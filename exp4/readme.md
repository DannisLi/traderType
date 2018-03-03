#实验目的

使用$model_1$和$model_2$分别拟合数据集，计算四个后验概率，观察有什么不同。

#$model_1$

$$
\large
\begin{aligned}
P(y=up|x) &= \frac{e^{wx+b}}{1+e^{wx+b}} \\
P(y=down|x) &= \frac{1}{1+e^{wx+b}} \\
\arg\max &\prod P(y_i|x_i) \\
\end{aligned}
$$

#$model_2$

$$
\large
\begin{aligned}
P(y=up|x=up) &= \frac{\sum_{i=1}^n I(x_i=up\ and\ y_i=up)}{\sum_{i=1}^n I(x_i=up)} \\
P(y=down|x=up) &= \frac{\sum_{i=1}^n I(x_i=up\ and\ y_i=down)}{\sum_{i=1}^n I(x_i=up)} \\
P(y=up|x=down) &= \frac{\sum_{i=1}^n I(x_i=down\ and\ y_i=up)}{\sum_{i=1}^n I(x_i=down)} \\
P(y=down|x=down) &= \frac{\sum_{i=1}^n I(x_i=down\ and\ y_i=down)}{\sum_{i=1}^n I(x_i=down)} \\
\end{aligned}
$$

# 数据集

若某合约在T日到T+1日持仓发生变化，则将该合约的（T-1日到T日的价格变化方向，T日到T+1日持仓变化方向）加入数据集。