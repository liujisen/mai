# 快速参考卡片 🎯

## ⚡ 一键运行

```bash
cd /Users/insilicomedicine/demo/A

# 测试（30秒）
python3 run_mai_screener_small.py

# 完整（10分钟）
python3 run_mai_screener.py
```

---

## 🎛️ 当前配置

```python
# 文件：run_mai_screener.py

RECENT_DAYS = 3                          # 时间窗口
TARGET_SIGNALS = ['放量启动', '底背离']  # 信号组合
MATCH_MODE = 'OR'                        # OR/AND
REQUIRE_UPTREND = True                   # EMA6>EMA18
```

**筛选条件**：`最近3天 + (放量启动或底背离) + 上升趋势`

---

## 📊 信号速查

| 信号 | 含义 | 强度 |
|------|------|------|
| 放量启动 | 金叉+放量 | ⭐ |
| 底背离 | 反转信号 | ⭐⭐ |
| 二浪回踩 | 回踩支撑 | ⭐ |
| 共振机会 | 谷值+背离 | ⭐⭐⭐ |

---

## 🔧 常用修改

### 改时间范围
```python
RECENT_DAYS = 5  # 3→5天
```

### 改信号类型
```python
TARGET_SIGNALS = ['共振机会']  # 只看最强信号
```

### 取消趋势限制
```python
REQUIRE_UPTREND = False  # 允许下降趋势
```

### 改为同时满足
```python
MATCH_MODE = 'AND'  # 必须全部信号
```

---

## 📁 关键文件

| 文件 | 用途 |
|------|------|
| `run_mai_screener.py` | ⚙️ 配置+运行 |
| `stock_screener_mai.py` | 🔍 筛选逻辑 |
| `mai_indicator.py` | 📈 指标计算 |
| `Ashare.py` | 📊 数据获取 |
| `results/*.csv` | 💾 筛选结果 |

---

## 🎨 配置模板

### 快速复制

```python
# 激进型
RECENT_DAYS = 3
TARGET_SIGNALS = ['放量启动']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = True

# 保守型
RECENT_DAYS = 5
TARGET_SIGNALS = ['底背离', '共振机会']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = False

# 当前型（均衡）
RECENT_DAYS = 3
TARGET_SIGNALS = ['放量启动', '底背离']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = True
```

---

## 📊 结果示例

```csv
股票代码,股票名称,最新价,EMA6,EMA18,止损线,买入信号,信号强度,信号日期,趋势
000002,万科A,4.88,4.91,4.88,4.45,放量启动,⭐ 一般,2026-01-29,上升
```

---

## ⏱️ 性能参考

| 股票数 | 时间 |
|-------|------|
| 100 | 30秒 |
| 1000 | 3分钟 |
| 5477 | 10分钟 |

---

## 🆘 问题速查

| 问题 | 解决 |
|------|------|
| 结果为0 | 扩大RECENT_DAYS |
| 太慢 | 装akshare |
| 太多结果 | 改AND模式 |
| 太少结果 | 改OR模式 |

---

## 📞 联系信息

- 项目路径：`/Users/insilicomedicine/demo/A/`
- 详细文档：`PROJECT_SUMMARY.md`
- 架构说明：`ARCHITECTURE.md`

---

**保存此文档 - 随时查阅** 📌
