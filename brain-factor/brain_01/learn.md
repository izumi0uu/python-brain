# 市场中性化策略分析

## 假设全市场共 5 个股票，收盘价分别为[5,15,66,85,25], Alpha 表达式为"-close'（注意负号),在 Neutralization Setting 为 Market 的情况下，请回答这五个股票各自的交易权重(weight)为多少？long count 和 short count 为多少（即有几个股票被做多，几个股票被做空）

## Market Neutralization（市场中性化）

定义：

- 目的是消除整体市场波动的影响
- 确保策略不受大盘涨跌影响
- 纯粹捕捉个股相对表现

实现方式：

1. 权重之和为 0

   - Σ(weights) = 0
   - 做多和做空的资金量相等

2. 相对价格

   - 减去市场平均值
   - 消除整体市场影响

## Alpha 权重标准化处理

步骤：

1. 原始 Alpha 值
   alpha = [-5, -15, -66, -85, -25]

2. 计算均值
   mean = (-5-15-66-85-25)/5 = -39.2

3. 中性化处理

   - 每个值减去均值
   - alpha_neutral = [x - mean for x in alpha]
   - 确保新的 alpha 值和为 0

4. 权重标准化
   - 除以绝对值之和
   - 确保权重之和为 0
   - 保持做多做空资金相

## Long/Short Count 计算

定义：

- Long Count: 正权重的股票数量
- Short Count: 负权重的股票数量

计算方法：

- 观察最终权重的正负
- 正权重计入 Long Count
- 负权重计入 Short Count

示例：
weights = [0.236, 0.167, -0.185, -0.315, 0.098]
Long Count = 3 (第 1、2、5 个股票)
Short Count = 2 (第 3、4 个股票)

1 Alpha 值就是-close，所以 Alpha 值为:
alpha = [-5, -15, -66, -85, -25]

2 根据 Market Neutralization 的定义，需要:
所有 weight 之和为 0（市场中性）
做多做空的资金量相等
weight 与 alpha 值成正比

3 标准化处理:
total = sum(alpha)
mean = total/5 # 计算平均值
alpha_neutral = [x - mean for x in alpha] # 减去平均值实现中性化

4 计算最终 weight:
sum_abs = sum(abs(x) for x in alpha_neutral)
weights = [x/sum_abs for x in alpha_neutral]

## 计算

1. mean = (-5-15-66-85-25)/5 = -39.2

2. alpha_neutral =
   [-5-(-39.2), -15-(-39.2), -66-(-39.2), -85-(-39.2), -25-(-39.2)]
   = [34.2, 24.2, -26.8, -45.8, 14.2]

3. sum_abs = |34.2| + |24.2| + |-26.8| + |-45.8| + |14.2| = 145.2

4. weights = [34.2/145.2, 24.2/145.2, -26.8/145.2, -45.8/145.2, 14.2/145.2]
   = [0.236, 0.167, -0.185, -0.315, 0.098]

## 最终权重

股票 1: 0.236 (做多)
股票 2: 0.167 (做多)
股票 3: -0.185 (做空)
股票 4: -0.315 (做空)
股票 5: 0.098 (做多)

Long Count = 3 (有 3 个正权重)
Short Count = 2 (有 2 个负权重)
