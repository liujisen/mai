# Mai指标Python实现使用说明

## 简介

这是将富途牛牛Mai语言自定义指标转换为Python的完整实现，保留了所有原始功能和信号逻辑。

## 指标功能

### 1. 趋势通道
- **EMA6** (短期均线): 6日指数移动平均线
- **EMA18** (长期均线): 18日指数移动平均线
- 当EMA6在EMA18上方时为上升趋势（显示紫色）
- 当EMA6在EMA18下方时为下降趋势（显示青色）

### 2. 止损线
- 基于ATR（平均真实波幅）计算动态止损线
- 公式: `止损线 = EMA6 - 2.5 × ATR(14)`
- 只在上升趋势时显示（黄色虚线）

### 3. 顶底背离
- **底背离**: 价格创新低但MACD的DIF指标未创新低，且DIF金叉DEA
- **顶背离**: 价格创新高但MACD的DIF指标未创新高，且DEA死叉DIF
- 底背离标记为"★底背离"（红色）
- 顶背离标记为"★顶背离"（绿色）

### 4. ZIG之字转向
- 使用5%的转向幅度识别价格的峰值和谷值
- 谷值显示"留意反转"（黄色）
- 用于捕捉趋势的重要转折点

### 5. 共振机会（强烈买入信号）
- 当谷值信号和底背离同时出现时触发
- 标记为"🔥🔥双重共振"（紫色）
- 这是最强的买入信号

### 6. 放量启动（一浪进场）
- 条件：EMA6金叉EMA18 + 成交量大于5日均量
- 标记为"🚀放量启动"（黄色）
- 适合趋势启动初期的进场

### 7. 二浪回踩（二浪进场）
- 条件：
  - 处于上升趋势（EMA6 > EMA18）
  - 最低价触及或跌破EMA6
  - 收盘价仍在止损线上方
  - 收出阳线（红K线）
  - 距离金叉超过3个周期
- 标记为"🚘"（黄色）
- 适合趋势确立后的回调进场

### 8. 离场警报
- 当价格跌破止损线时触发
- 标记为"🛑破线离场"（绿色）
- 这是明确的卖出信号

## 快速开始

### 基本使用

```python
from mai_indicator import MaiIndicator
import pandas as pd

# 1. 准备数据（DataFrame需要包含以下列）
df = pd.DataFrame({
    'open': [...],      # 开盘价
    'high': [...],      # 最高价
    'low': [...],       # 最低价
    'close': [...],     # 收盘价
    'volume': [...]     # 成交量
}, index=pd.date_range('2024-01-01', periods=100))

# 2. 创建指标计算器
indicator = MaiIndicator(df)

# 3. 计算所有指标
result = indicator.calculate_all()

# 4. 查看最新信号
indicator.print_latest_signals()
```

### 获取交易信号

```python
# 获取所有买入信号
buy_signals = indicator.get_buy_signals()
print(buy_signals)

# 输出示例:
#       date    signal     price                     description
# 2024-03-01  放量启动  105.23  金叉+放量，一浪进场机会
# 2024-03-15  二浪回踩  108.45  回踩EMA6支撑，二浪进场机会
# 2024-03-20  双重共振  102.67  谷值+底背离，强烈买入信号

# 获取所有卖出信号
sell_signals = indicator.get_sell_signals()
print(sell_signals)
```

### 获取特定日期的信号

```python
# 获取最新日期的信号
latest_signals = indicator.get_signals()

# 获取指定日期的信号
specific_signals = indicator.get_signals(date='2024-03-15')

# 信号字典包含:
# - EMA6, EMA18: 短期和长期均线值
# - 止损线: 动态止损线位置
# - 上升趋势: True/False
# - 底背离, 顶背离: True/False
# - 谷值信号, 峰值信号: True/False
# - 共振机会: True/False
# - 放量启动: True/False
# - 二浪回踩: True/False
# - 离场警报: True/False
```

### 与现有项目集成

如果你已经有股票数据获取代码，可以这样集成：

```python
from mai_indicator import MaiIndicator
import akshare as ak

# 获取股票数据
stock_code = '600000'
df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")

# 重命名列（如果需要）
df.rename(columns={
    '日期': 'date',
    '开盘': 'open',
    '最高': 'high',
    '最低': 'low',
    '收盘': 'close',
    '成交量': 'volume'
}, inplace=True)

df.set_index('date', inplace=True)

# 计算指标
indicator = MaiIndicator(df)
indicator.calculate_all()

# 查看信号
indicator.print_latest_signals()

# 获取买入机会
buy_signals = indicator.get_buy_signals()
if len(buy_signals) > 0:
    print(f"\n发现 {len(buy_signals)} 个买入信号")
    print(buy_signals.tail())
```

## 信号优先级和使用建议

### 买入信号优先级（从高到低）

1. **🔥🔥双重共振** - 最强买入信号
   - 谷值 + 底背离同时出现
   - 成功率最高，建议重点关注

2. **🚀放量启动** - 趋势启动信号
   - 金叉 + 放量
   - 适合趋势跟踪者，进场较早

3. **🚘二浪回踩** - 趋势确认后的回调买入
   - 回踩EMA6支撑
   - 风险相对较低，适合稳健投资者

4. **★底背离** - 反转机会
   - 单独的底背离信号
   - 建议结合其他信号使用

### 卖出信号

1. **🛑破线离场** - 必须执行
   - 跌破止损线
   - 强制止损信号，建议严格执行

2. **★顶背离** - 警示信号
   - 顶部背离
   - 建议减仓或观望

## 数据要求

输入的DataFrame必须包含以下列（列名不区分大小写）：

- `open` / `OPEN`: 开盘价
- `high` / `HIGH`: 最高价
- `low` / `LOW`: 最低价
- `close` / `CLOSE`: 收盘价
- `volume` / `VOL`: 成交量

建议至少有50个以上的交易日数据，以确保指标计算的准确性。

## 输出说明

### calculate_all() 返回的DataFrame包含：

| 列名 | 说明 |
|-----|------|
| EMA6 | 6日指数移动平均线 |
| EMA18 | 18日指数移动平均线 |
| VAR_SHORT | 短期均线（同EMA6） |
| VAR_LONG | 长期均线（同EMA18） |
| IS_UPTREND | 是否上升趋势 |
| MY_ATR | 平均真实波幅 |
| STOP_LOSS_LINE | 止损线 |
| 止盈红线 | 上升趋势时的止损线（下降趋势为NaN） |
| DIF | MACD的DIF线 |
| DEA | MACD的DEA线 |
| MACD_BAR | MACD柱状图 |
| 底背离 | 底背离信号 |
| 顶背离 | 顶背离信号 |
| Z_VAL | ZIG之字转向值 |
| IS_PEAK | 峰值信号 |
| IS_TROUGH | 谷值信号 |
| 共振机会 | 双重共振信号 |
| IS_VOL_UP | 放量 |
| IS_GOLD_CROSS | 金叉 |
| 放量启动 | 放量启动信号 |
| 二浪回踩 | 二浪回踩信号 |
| 离场警报 | 离场警报信号 |

## 注意事项

1. **历史数据要求**: 建议使用至少3个月的日K线数据进行计算
2. **复权数据**: 建议使用前复权数据，以保证价格的连续性
3. **信号滞后**: 某些信号（如ZIG）具有一定滞后性，需要结合实时行情判断
4. **风险控制**: 任何技术指标都不能100%准确，请结合其他分析方法并做好风险控制
5. **止损纪律**: 出现"破线离场"信号时，建议严格执行止损

## 依赖库

```bash
pip install pandas numpy
```

## 示例：批量筛选股票

```python
from mai_indicator import MaiIndicator
import pandas as pd

def scan_stocks(stock_list):
    """批量扫描股票，找出有买入信号的"""
    results = []
    
    for stock_code in stock_list:
        # 获取股票数据（这里需要你自己实现）
        df = get_stock_data(stock_code)
        
        # 计算指标
        indicator = MaiIndicator(df)
        indicator.calculate_all()
        
        # 获取最新信号
        signals = indicator.get_signals()
        
        # 检查买入信号
        if signals['共振机会']:
            results.append({
                'code': stock_code,
                'signal': '双重共振',
                'price': df['close'].iloc[-1],
                'ema6': signals['EMA6'],
                'stop_loss': signals['止损线']
            })
        elif signals['放量启动']:
            results.append({
                'code': stock_code,
                'signal': '放量启动',
                'price': df['close'].iloc[-1],
                'ema6': signals['EMA6'],
                'stop_loss': signals['止损线']
            })
        elif signals['二浪回踩']:
            results.append({
                'code': stock_code,
                'signal': '二浪回踩',
                'price': df['close'].iloc[-1],
                'ema6': signals['EMA6'],
                'stop_loss': signals['止损线']
            })
    
    return pd.DataFrame(results)

# 使用示例
stock_list = ['600000', '600036', '601318']  # 示例股票代码
opportunities = scan_stocks(stock_list)
print(opportunities)
```

## 技术支持

如有问题或建议，请参考源代码中的注释，或查看Mai语言原始指标公式。

## 版本历史

- v1.0 (2026-01-30): 初始版本，完整实现Mai指标的所有功能
