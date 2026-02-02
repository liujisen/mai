# A股Mai指标筛选器

> 基于Mai技术指标的A股全市场智能筛选系统

## 快速开始

```bash
# 测试运行（30秒，扫描100只股票）
python3 run_mai_screener_small.py

# 完整运行（10分钟，扫描全市场5477只股票）
python3 run_mai_screener.py
```

## 当前配置

```python
时间范围: 最近3天
信号组合: 放量启动 OR 底背离
趋势要求: EMA6 > EMA18（上升趋势）
```

## 修改配置

编辑 `run_mai_screener.py` 文件：

```python
RECENT_DAYS = 3                          # 时间窗口：1, 3, 5, 10...
TARGET_SIGNALS = ['放量启动', '底背离']  # 信号组合
MATCH_MODE = 'OR'                        # OR=满足任一，AND=全部满足
REQUIRE_UPTREND = True                   # True=上升趋势，False=不限
```

### 可用信号类型

| 信号 | 说明 | 强度 |
|------|------|------|
| 放量启动 | 金叉（EMA6上穿EMA18）+ 成交量放大 | ⭐ |
| 底背离 | 价格新低但MACD不创新低（反转信号） | ⭐⭐ |
| 二浪回踩 | 上升趋势中回踩EMA6支撑 | ⭐ |
| 共振机会 | 谷值信号 + 底背离（最强组合） | ⭐⭐⭐ |

### 配置示例

```python
# 激进型（更多结果）
RECENT_DAYS = 5
TARGET_SIGNALS = ['放量启动']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = False

# 保守型（精选结果）
RECENT_DAYS = 3
TARGET_SIGNALS = ['底背离', '共振机会']
MATCH_MODE = 'AND'
REQUIRE_UPTREND = True
```

## 查看结果

筛选结果自动保存到 `results/` 目录：

```bash
# 查看最新结果
ls results/mai_buy_signals_*.csv

# 用Excel或其他工具打开CSV文件
```

结果包含字段：
- 股票代码、股票名称
- 最新价、EMA6、EMA18、止损线
- 买入信号、信号强度、信号日期
- 趋势状态、更新日期

## 安装依赖

```bash
# 基础依赖（必需）
pip3 install pandas requests --user

# 推荐依赖（提速50%）
pip3 install akshare --user
```

## 项目结构

```
A/
├── run_mai_screener.py       主运行脚本（配置+启动）
├── stock_screener_mai.py     筛选核心逻辑（568行）
├── mai_indicator.py          Mai指标计算（435行）
├── Ashare.py                 股票数据获取（70行）
├── requirements.txt          依赖列表
└── results/                  筛选结果目录
```

## 技术说明

### Mai指标体系

- **趋势判断**: EMA6（快线）、EMA18（慢线）
- **止损线**: EMA6 - 2.5 × ATR（平均波幅）
- **背离检测**: 基于MACD指标
- **峰谷识别**: ZIG之字转向算法

### 数据源

- 首选：akshare库（5477只A股列表）
- 备用：东方财富API
- 行情：新浪财经 + 腾讯财经（双重保障）

## 常见问题

### 找不到符合条件的股票？

- 增加时间范围：`RECENT_DAYS = 5` 或 `10`
- 放宽信号限制：只使用 `['放量启动']`
- 取消趋势限制：`REQUIRE_UPTREND = False`

### 结果太多？

- 缩小时间范围：`RECENT_DAYS = 1`
- 使用AND模式：`MATCH_MODE = 'AND'`
- 要求上升趋势：`REQUIRE_UPTREND = True`

### 运行太慢？

- 安装akshare加速：`pip3 install akshare --user`
- 先用测试版验证：`python3 run_mai_screener_small.py`

### 如何测试单只股票？

```python
from Ashare import get_price
from mai_indicator import MaiIndicator

# 获取数据
df = get_price('sh600519', frequency='1d', count=100)

# 计算指标
indicator = MaiIndicator(df)
result = indicator.calculate_all()

# 打印最新信号
indicator.print_latest_signals()
```

## 性能指标

- 测试版（100只）：约30秒
- 完整版（5477只）：约10分钟
- 内存占用：<500MB
- CPU使用：单核

## 免责声明

本工具仅供学习研究使用，筛选结果不构成投资建议。投资有风险，入市需谨慎。

---

**准备好了？开始筛选！** 🚀

```bash
python3 run_mai_screener.py
```
