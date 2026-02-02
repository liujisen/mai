# 系统架构文档

## 📐 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    用户入口层                                │
├─────────────────────────────────────────────────────────────┤
│  run_mai_screener.py          完整版（5477只，10分钟）       │
│  run_mai_screener_small.py    测试版（100只，30秒）          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   业务逻辑层                                 │
├─────────────────────────────────────────────────────────────┤
│  stock_screener_mai.py                                      │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ get_stock_list() │  │ check_buy_signal()│               │
│  │ 获取股票列表      │  │ 检查单只股票      │               │
│  └──────────────────┘  └──────────────────┘               │
│           ↓                      ↓                          │
│  ┌────────────────────────────────────────┐                │
│  │  screen_stocks_by_mai_signal()         │                │
│  │  批量筛选 + 过滤 + 排序                │                │
│  └────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   指标计算层                                 │
├─────────────────────────────────────────────────────────────┤
│  mai_indicator.py                                           │
│                                                             │
│  MaiIndicator类                                             │
│  ├─ calculate_all()      计算所有指标                       │
│  ├─ get_signals()        获取最新信号                       │
│  ├─ get_buy_signals()    买入信号历史                       │
│  └─ get_sell_signals()   卖出信号历史                       │
│                                                             │
│  内置指标：                                                  │
│  • EMA6/EMA18 (趋势)                                        │
│  • ATR (波幅)                                               │
│  • MACD (顶底背离)                                          │
│  • ZIG (峰谷)                                               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据源层                                  │
├─────────────────────────────────────────────────────────────┤
│  Ashare.py                   akshare                        │
│  股票K线数据                  股票代码列表                   │
│  (新浪/腾讯API)              (5477只A股)                    │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 数据流程

```
开始
  ↓
[读取配置参数]
  RECENT_DAYS, TARGET_SIGNALS, MATCH_MODE, REQUIRE_UPTREND
  ↓
[获取股票列表]
  akshare → 5477只A股
  ↓
[逐个检查股票] ←─────┐
  ↓                  │
[获取K线数据]         │
  Ashare.py          │
  100天历史数据      │
  ↓                  │
[计算Mai指标]         │
  MaiIndicator       │
  计算所有信号       │
  ↓                  │
[应用筛选条件]        │
  1. 时间范围过滤    │
  2. 信号匹配检查    │
  3. 趋势状态过滤    │
  ↓                  │
[符合条件？]          │
  是 → [加入结果]    │
  否 → ──────────────┘
  ↓
[所有股票检查完毕]
  ↓
[结果排序]
  按信号强度 + 日期
  ↓
[保存CSV文件]
  ↓
[显示统计信息]
  ↓
结束
```

## 🎛️ 筛选条件逻辑

```
对每只股票:
  
  1️⃣ 获取K线数据 (100天)
      ↓
  2️⃣ 计算Mai指标
      ↓
  3️⃣ 检查最近N天
      ↓
  4️⃣ 是否有目标信号？
      ├─ OR模式: 有任意一个 → ✅
      └─ AND模式: 全部都有 → ✅
      ↓
  5️⃣ 当前趋势检查
      ├─ REQUIRE_UPTREND=True
      │   └─ EMA6 > EMA18? → ✅
      └─ REQUIRE_UPTREND=False
          └─ 不检查 → ✅
      ↓
  6️⃣ 符合条件 → 加入结果
```

## 🧩 模块依赖关系

```
run_mai_screener.py
    │
    └─→ stock_screener_mai.py
            │
            ├─→ mai_indicator.py
            │       └─→ pandas, numpy
            │
            └─→ Ashare.py
                    └─→ requests, pandas
            
            └─→ akshare (可选，推荐)
```

## 📊 信号计算逻辑

### 放量启动
```python
金叉 = EMA6上穿EMA18
放量 = 成交量 > MA5(成交量)
放量启动 = 金叉 AND 放量
```

### 底背离
```python
价格创新低 = CLOSE[i-n] > CLOSE[i]
MACD不创新低 = DIF[i] > DIF[i-n]
底背离 = 价格创新低 AND MACD不创新低 AND DIF上穿DEA
```

### 二浪回踩
```python
上升趋势 = EMA6 > EMA18
回踩支撑 = LOW <= EMA6 AND CLOSE > 止损线
红K线 = CLOSE > OPEN
金叉后N天 = barslast(金叉) > 3
二浪回踩 = 上升趋势 AND 回踩支撑 AND 红K线 AND 金叉后N天
```

### 共振机会
```python
共振机会 = ZIG谷值 AND 底背离
```

## 🔍 筛选器配置矩阵

| 参数 | 选项 | 效果 |
|------|------|------|
| **RECENT_DAYS** | 1 | 只看今天 |
|  | 3 | 最近3天（当前） |
|  | 5-10 | 更多机会 |
| **MATCH_MODE** | OR | 任意信号（结果多） |
|  | AND | 全部信号（结果少） |
| **REQUIRE_UPTREND** | True | 只看上升趋势（当前） |
|  | False | 包含下降趋势 |
| **TARGET_SIGNALS** | ['放量启动'] | 趋势启动 |
|  | ['底背离'] | 反转机会 |
|  | ['共振机会'] | 最强信号 |
|  | ['放量启动','底背离'] | 组合（当前） |

## 🎯 推荐配置组合

### 激进型（追涨）
```python
RECENT_DAYS = 3
TARGET_SIGNALS = ['放量启动']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = True
```

### 保守型（反转）
```python
RECENT_DAYS = 5
TARGET_SIGNALS = ['底背离', '共振机会']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = False
```

### 均衡型（当前配置）
```python
RECENT_DAYS = 3
TARGET_SIGNALS = ['放量启动', '底背离']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = True
```

### 精选型（高质量）
```python
RECENT_DAYS = 10
TARGET_SIGNALS = ['共振机会']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = True
```

## 🚦 性能优化路线图

### 当前性能
- 单只股票：0.2秒
- 100只股票：30秒
- 5477只股票：10分钟

### 优化方案

#### Phase 1: 多线程（可提速3-5倍）
```python
# 使用ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(check_buy_signal, stock) 
               for stock in stock_list]
```

预期：10分钟 → 2-3分钟

#### Phase 2: 缓存机制
```python
# 当日数据缓存
@lru_cache(maxsize=10000)
def get_cached_data(code, date):
    return get_price(code, ...)
```

预期：避免重复请求，节省20-30%时间

#### Phase 3: 增量更新
```python
# 只检查新股票或有更新的股票
last_scan = load_last_scan_result()
new_stocks = get_diff(current_list, last_scan)
```

预期：每日扫描时间减少80%

## 🔧 扩展开发指南

### 添加新的买入信号

1. 在 `mai_indicator.py` 中添加计算逻辑：

```python
def calculate_all(self):
    # ... 现有代码 ...
    
    # 添加新信号
    self.result['我的信号'] = 你的计算逻辑
```

2. 在 `check_buy_signal()` 中添加检测：

```python
if row['我的信号']:
    temp_signals.append('我的信号')
```

### 添加新的过滤条件

在 `check_buy_signal()` 函数中添加：

```python
# 示例：添加成交量过滤
if require_high_volume:
    latest_volume = df['volume'].iloc[-1]
    avg_volume = df['volume'].mean()
    if latest_volume < avg_volume * 1.5:
        return None
```

### 添加新的输出字段

在 `screen_stocks_by_mai_signal()` 的结果构建中添加：

```python
results.append({
    # ... 现有字段 ...
    '新字段': 计算值,
})
```

## 📈 数据库集成（未来）

如需持久化存储：

```python
# 使用SQLite
import sqlite3

conn = sqlite3.connect('stock_signals.db')
df.to_sql('signals', conn, if_exists='append')
```

## 🌐 Web界面（未来）

可使用：
- Streamlit（最简单）
- Flask + Vue（灵活）
- Dash（数据可视化强）

## 🎓 代码质量

- ✅ 函数注释完整
- ✅ 参数类型标注
- ✅ 错误处理健壮
- ✅ 模块化设计
- ✅ 配置与逻辑分离

---

**最后更新**：2026-02-02  
**架构版本**：v4.0  
**维护者**：项目团队
