# 📚 A股Mai指标筛选器 - 完整索引

> **快速开始**：运行 `python3 run_mai_screener_small.py` （30秒测试）

---

## 🎯 项目状态

**版本**：v4.0 ✅  
**状态**：生产就绪  
**最后更新**：2026-02-02  
**测试状态**：✅ 通过  

**当前筛选条件**：
```
最近3天 + (放量启动 或 底背离) + EMA6在EMA18上方
```

**测试结果**：前100只找到3只符合条件的股票 ✅

---

## 📖 文档导航

### 🚀 新手入门
1. **[README_CN.md](README_CN.md)** - 项目介绍，快速开始
2. **[QUICK_START.md](QUICK_START.md)** - 详细使用指南
3. **[CHEATSHEET.md](CHEATSHEET.md)** - 快速参考卡片 ⭐推荐

### 📊 深入了解
4. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 完整项目总结 ⭐必读
5. **[ARCHITECTURE.md](ARCHITECTURE.md)** - 系统架构设计
6. **[MAI_SCREENER_README.md](MAI_SCREENER_README.md)** - Mai指标详解

### 🔧 进阶使用
7. **[FULL_ASTOCK_GUIDE.md](FULL_ASTOCK_GUIDE.md)** - 全市场筛选指南

---

## 🗂️ 代码文件索引

### 📌 必读代码（核心逻辑）
- `stock_screener_mai.py` (568行) - 筛选核心
- `mai_indicator.py` (435行) - 指标计算
- `Ashare.py` (70行) - 数据获取

### ▶️ 运行脚本（选一个运行）
- `run_mai_screener.py` - 全市场筛选（10分钟）⭐
- `run_mai_screener_small.py` - 测试版（30秒）⭐
- `run_mai_flexible.py` - 多配置测试

### 🧪 测试脚本（验证功能）
- `test_mai_signals.py` - 测试单股信号
- `test_get_all_stocks.py` - 测试股票列表
- `check_individual_signals.py` - 检查信号频率
- `test_basic.py` - 基础功能测试

---

## 🎯 使用场景导航

### 我想...

#### 快速测试功能
→ 运行 `python3 run_mai_screener_small.py`  
→ 阅读 [QUICK_START.md](QUICK_START.md)

#### 完整扫描全市场
→ 运行 `python3 run_mai_screener.py`  
→ 阅读 [FULL_ASTOCK_GUIDE.md](FULL_ASTOCK_GUIDE.md)

#### 理解系统设计
→ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md)  
→ 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

#### 修改筛选条件
→ 编辑 `run_mai_screener.py`  
→ 参考 [CHEATSHEET.md](CHEATSHEET.md)

#### 了解Mai指标
→ 阅读 [MAI_SCREENER_README.md](MAI_SCREENER_README.md)  
→ 查看 `mai_indicator.py` 代码

#### 继续开发迭代
→ 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) "待优化功能"章节  
→ 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) "扩展开发指南"章节

---

## 📋 功能检查清单

### ✅ 已实现功能

- [x] Mai指标计算（EMA、ATR、MACD、ZIG）
- [x] 四种买入信号（放量启动、底背离、二浪回踩、共振机会）
- [x] 全A股支持（5477只，主板+创业板+科创板）
- [x] 多种信号组合（OR/AND模式）
- [x] 时间范围灵活配置
- [x] 趋势过滤（EMA6 > EMA18）
- [x] 自动获取股票列表（akshare）
- [x] CSV结果导出
- [x] 进度实时显示
- [x] 异常处理机制
- [x] 小规模测试版本
- [x] 完整文档系统

### 📝 待实现功能

- [ ] 多线程并发处理
- [ ] 数据缓存机制
- [ ] 断点续传功能
- [ ] 历史回测系统
- [ ] Web可视化界面
- [ ] 实时监控提醒
- [ ] 更多技术指标

---

## 🎨 配置速查表

| 需求 | 参数配置 |
|------|---------|
| 找更多结果 | `RECENT_DAYS=10`, `MATCH_MODE='OR'` |
| 找高质量结果 | `MATCH_MODE='AND'`, `TARGET_SIGNALS=['共振机会']` |
| 包含反转机会 | `REQUIRE_UPTREND=False` |
| 只看趋势股 | `REQUIRE_UPTREND=True` |
| 最强信号 | `TARGET_SIGNALS=['共振机会']` |
| 快速测试 | 运行 `run_mai_screener_small.py` |

---

## 📊 数据统计

### 项目规模
- 代码文件：12个
- 文档文件：7个
- 总代码行数：~2000行
- 核心函数数：15个
- 支持信号数：4种

### 数据规模
- 支持股票数：5477只
- 每只数据量：100天K线
- 单次扫描请求：5477次
- CSV结果字段：11列

### 性能指标
- 单股处理：0.2秒
- 批量100只：30秒
- 全市场5477只：10分钟
- 内存占用：<500MB

---

## 🔗 快速链接

### 核心文档
- 📖 [项目总结](PROJECT_SUMMARY.md) - 最全面
- 🚀 [快速开始](QUICK_START.md) - 新手友好
- 🎯 [快速参考](CHEATSHEET.md) - 最常用

### 技术文档
- 🏗️ [系统架构](ARCHITECTURE.md) - 开发必读
- 📊 [指标说明](MAI_SCREENER_README.md) - 理解信号

### 使用指南
- 📚 [全市场指南](FULL_ASTOCK_GUIDE.md) - 高级用法
- 🌐 [中文说明](README_CN.md) - 完整说明

---

## 💻 代码快查

### 核心函数位置

```python
# stock_screener_mai.py
get_stock_list()              # Line ~17，获取股票列表
check_buy_signal()            # Line ~149，检查单股
screen_stocks_by_mai_signal() # Line ~231，批量筛选
save_to_csv()                 # Line ~312，保存结果
main()                        # Line ~338，主函数

# mai_indicator.py
class MaiIndicator            # Line ~12，指标类
calculate_all()               # Line ~141，计算所有指标
get_signals()                 # Line ~247，获取信号
get_buy_signals()            # Line ~282，买入信号

# Ashare.py
get_price()                   # Line ~49，获取K线
```

---

## 🎓 学习路径

### 第1步：运行测试
```bash
python3 run_mai_screener_small.py
```
理解基本流程

### 第2步：阅读文档
1. README_CN.md（5分钟）
2. PROJECT_SUMMARY.md（15分钟）
3. CHEATSHEET.md（2分钟）

### 第3步：修改配置
编辑 `run_mai_screener.py`，尝试不同参数

### 第4步：理解代码
阅读核心函数，理解筛选逻辑

### 第5步：扩展开发
参考ARCHITECTURE.md，添加新功能

---

## 🎁 实用脚本

### 查看最新结果
```bash
cat mai_buy_signals_*.csv | tail -20
```

### 统计信号分布
```bash
awk -F',' '{print $7}' mai_buy_signals_*.csv | sort | uniq -c
```

### 查找特定股票
```bash
grep "万科" mai_buy_signals_*.csv
```

### 按涨幅排序（如果CSV中有）
```bash
sort -t',' -k8 -rn mai_buy_signals_*.csv
```

---

## 📞 获取帮助

### 查看文档
```bash
# 项目总结
cat PROJECT_SUMMARY.md

# 快速参考
cat CHEATSHEET.md
```

### 测试功能
```bash
# 测试指标
python3 test_mai_signals.py

# 测试列表
python3 test_get_all_stocks.py
```

---

## 🎉 成功指标

项目实现了以下目标：
- ✅ 支持全A股筛选（5477只）
- ✅ Mai指标完整实现
- ✅ 灵活配置系统
- ✅ 稳定运行（测试通过）
- ✅ 完整文档体系
- ✅ 易于迭代扩展

---

**版本**：v4.0  
**更新**：2026-02-02  
**状态**：🟢 正常运行

---

💡 **提示**：将此文档保存为书签，随时查阅！
