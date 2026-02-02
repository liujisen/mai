# 项目文件清单

> 所有文件用途一览表

## 📂 目录结构

```
/Users/insilicomedicine/demo/A/
├── 🎯 入口文档
│   └── START_HERE.md                 ⭐ 新手从这里开始
│
├── 📖 文档系统（7个）
│   ├── INDEX.md                      文档总索引
│   ├── PROJECT_SUMMARY.md            完整项目总结 ⭐必读
│   ├── CHEATSHEET.md                 快速参考卡片
│   ├── QUICK_START.md                快速开始指南
│   ├── ARCHITECTURE.md               系统架构设计
│   ├── FULL_ASTOCK_GUIDE.md          全市场筛选指南
│   ├── MAI_SCREENER_README.md        Mai指标说明
│   ├── CHANGELOG.md                  版本更新日志
│   ├── FILES_MANIFEST.md             文件清单（本文档）
│   └── README_CN.md                  中文说明（旧版）
│
├── 💻 核心代码（4个）
│   ├── stock_screener_mai.py         筛选核心（568行）⭐
│   ├── mai_indicator.py              Mai指标（435行）⭐
│   ├── Ashare.py                     数据获取（70行）⭐
│   └── requirements.txt              依赖列表
│
├── ▶️ 运行脚本（3个）
│   ├── run_mai_screener.py           完整版 ⭐推荐
│   ├── run_mai_screener_small.py     测试版 ⭐首次使用
│   └── run_mai_flexible.py           多配置测试
│
├── 🧪 测试脚本（10个）
│   ├── test_mai_signals.py           测试单股信号
│   ├── test_get_all_stocks.py        测试股票列表
│   ├── test_basic.py                 基础功能测试
│   ├── test_api.py                   API测试
│   ├── test_ashare.py                Ashare库测试
│   ├── test_screener_low_threshold.py 低阈值测试
│   ├── test_signal_combo.py          信号组合测试
│   ├── check_individual_signals.py   信号频率检查
│   ├── debug_check.py                调试检查
│   └── test_small_batch.py           小批量测试
│
├── 📊 结果输出
│   ├── results/                      CSV目录
│   │   ├── mai_buy_signals_*.csv    Mai信号结果
│   │   └── stocks_above_5percent_*.csv 涨幅结果（旧）
│   └── mai_buy_signals_*.csv         最新结果（根目录）
│
└── 🗑️ 旧版文件（可选删除）
    ├── stock_screener.py             v1.0涨幅筛选（已废弃）
    ├── run_screener.py               v1.0运行脚本（已废弃）
    └── Demo*.py                      Ashare示例（参考）
```

---

## 📋 文件详细说明

### 🎯 入口文档（新手必看）

#### START_HERE.md ⭐⭐⭐
- **用途**：项目入口，30秒了解全貌
- **适合**：首次使用者
- **内容**：快速命令、文档导航、下一步建议

---

### 📖 文档系统

#### INDEX.md
- **用途**：文档总索引和导航
- **适合**：快速找到需要的文档
- **内容**：所有文档链接、使用场景导航

#### PROJECT_SUMMARY.md ⭐⭐⭐
- **用途**：完整项目总结（最全面）
- **适合**：理解整个项目、后续迭代开发
- **内容**：架构、功能、配置、FAQ、待优化

#### CHEATSHEET.md ⭐⭐
- **用途**：快速参考卡片
- **适合**：日常使用查阅
- **内容**：常用命令、配置模板、速查表

#### QUICK_START.md
- **用途**：详细使用指南
- **适合**：想深入了解使用方法
- **内容**：三种运行方式、配置说明、问题排查

#### ARCHITECTURE.md
- **用途**：系统架构设计文档
- **适合**：开发者、二次开发
- **内容**：架构图、数据流、扩展指南

#### FULL_ASTOCK_GUIDE.md
- **用途**：全市场筛选详细指南
- **适合**：需要扫描全部A股
- **内容**：三种获取方式、时间估算、优化建议

#### MAI_SCREENER_README.md
- **用途**：Mai指标详细说明
- **适合**：理解技术指标含义
- **内容**：指标解释、配置示例、使用技巧

#### CHANGELOG.md
- **用途**：版本更新历史
- **适合**：了解项目演进
- **内容**：v1.0-v4.0的所有变更

---

### 💻 核心代码

#### stock_screener_mai.py (568行) ⭐⭐⭐
- **用途**：筛选器核心逻辑
- **核心函数**：
  - `get_stock_list()` - 获取股票列表
  - `check_buy_signal()` - 检查单只股票
  - `screen_stocks_by_mai_signal()` - 批量筛选
  - `save_to_csv()` - 保存结果
  - `main()` - 主函数

#### mai_indicator.py (435行) ⭐⭐⭐
- **用途**：Mai技术指标计算库
- **核心类**：MaiIndicator
- **核心方法**：
  - `calculate_all()` - 计算所有指标
  - `get_signals()` - 获取最新信号
  - `get_buy_signals()` - 买入信号历史
  - `get_sell_signals()` - 卖出信号历史

#### Ashare.py (70行) ⭐⭐⭐
- **用途**：股票行情数据获取
- **核心函数**：`get_price()` - 获取K线数据
- **数据源**：新浪财经、腾讯财经
- **支持周期**：1d日线、1w周线、1M月线、5m/15m/30m/60m分钟线

#### requirements.txt
- **用途**：Python依赖包列表
- **内容**：pandas, requests
- **安装**：`pip3 install -r requirements.txt --user`

---

### ▶️ 运行脚本

#### run_mai_screener.py (38行) ⭐⭐⭐
- **用途**：主运行脚本（全市场筛选）
- **配置项**：RECENT_DAYS, TARGET_SIGNALS, MATCH_MODE, REQUIRE_UPTREND
- **运行时间**：10分钟（5477只）
- **使用场景**：日常筛选、完整扫描

#### run_mai_screener_small.py (90行) ⭐⭐
- **用途**：小规模测试版
- **范围**：前100只股票
- **运行时间**：30秒
- **使用场景**：快速测试、验证配置

#### run_mai_flexible.py (46行)
- **用途**：多种配置对比测试
- **功能**：一次运行测试多种信号组合
- **使用场景**：配置选择、效果对比

---

### 🧪 测试脚本

#### test_mai_signals.py
- **用途**：测试单个股票的Mai信号
- **输出**：详细的信号分析

#### test_get_all_stocks.py
- **用途**：测试股票列表获取
- **输出**：股票数量、板块分布

#### check_individual_signals.py
- **用途**：检查各种信号的出现频率
- **输出**：每只股票最近10天的信号情况

#### 其他测试脚本
- `test_basic.py` - 基础功能测试
- `test_api.py` - API连接测试
- `test_ashare.py` - Ashare库测试
- `debug_check.py` - 调试检查

---

## 📊 输出文件

### mai_buy_signals_YYYYMMDD.csv
- **位置**：根目录 + results/目录
- **格式**：CSV（UTF-8-BOM）
- **字段**：11列（代码、名称、价格、指标、信号等）
- **用途**：筛选结果，可用Excel打开

### stocks_above_5percent_*.csv（旧版）
- **用途**：v1.0涨幅筛选结果
- **状态**：已废弃，建议删除

---

## 🎨 文件使用频率

### 每天使用
- ⭐⭐⭐ `run_mai_screener.py` - 运行筛选
- ⭐⭐⭐ `CHEATSHEET.md` - 查阅命令
- ⭐⭐⭐ 结果CSV文件 - 查看结果

### 首次使用
- ⭐⭐⭐ `START_HERE.md` - 入门
- ⭐⭐⭐ `PROJECT_SUMMARY.md` - 了解全貌
- ⭐⭐ `run_mai_screener_small.py` - 测试

### 修改配置时
- ⭐⭐ `CHEATSHEET.md` - 配置示例
- ⭐⭐ `MAI_SCREENER_README.md` - 信号说明

### 二次开发时
- ⭐⭐⭐ `ARCHITECTURE.md` - 架构设计
- ⭐⭐⭐ 核心代码文件 - 理解实现
- ⭐⭐ `CHANGELOG.md` - 版本历史

---

## 🔄 文件依赖关系

### 运行依赖
```
run_mai_screener.py
    ├─ 依赖: stock_screener_mai.py
    ├─ 依赖: mai_indicator.py
    ├─ 依赖: Ashare.py
    └─ 依赖: akshare (可选)
```

### 文档依赖
```
START_HERE.md (入口)
    ├─ 指向: PROJECT_SUMMARY.md (主文档)
    ├─ 指向: CHEATSHEET.md (速查)
    └─ 指向: INDEX.md (索引)
```

---

## 🗑️ 可删除文件

以下文件可以安全删除（不影响核心功能）：

### 测试脚本（功能验证后）
- `test_*.py` - 所有测试脚本
- `debug_*.py` - 调试脚本
- `check_*.py` - 检查脚本

### 旧版文件
- `stock_screener.py` - v1.0涨幅筛选
- `run_screener.py` - v1.0运行脚本
- `Demo*.py` - Ashare示例

### 冗余文档（保留核心的即可）
- 保留：PROJECT_SUMMARY.md, CHEATSHEET.md, START_HERE.md
- 可删：其他文档（如果不需要）

---

## 📊 文件统计

### 代码文件
- 核心代码：4个（1073行）
- 运行脚本：3个（174行）
- 测试脚本：10个（~800行）
- **总计**：~2050行代码

### 文档文件
- 系统文档：9个
- 总字数：~15000字

### 数据文件
- CSV结果：多个
- 总大小：<5MB

---

## 🎯 核心文件（必需）

这些文件是系统运行的必需文件，**不可删除**：

1. `stock_screener_mai.py` - 筛选逻辑
2. `mai_indicator.py` - 指标计算
3. `Ashare.py` - 数据获取
4. `run_mai_screener.py` - 运行入口
5. `requirements.txt` - 依赖声明

**最小系统**：只需这5个文件即可运行！

---

## 📚 推荐阅读顺序

### 新手路径
1. START_HERE.md (2分钟)
2. CHEATSHEET.md (3分钟)
3. PROJECT_SUMMARY.md (15分钟)

### 开发者路径
1. PROJECT_SUMMARY.md (15分钟)
2. ARCHITECTURE.md (10分钟)
3. 核心代码阅读 (30分钟)
4. CHANGELOG.md (5分钟)

### 快速参考
直接看 CHEATSHEET.md 即可

---

## 🔧 维护建议

### 定期更新
- ✅ 代码修改后更新 PROJECT_SUMMARY.md
- ✅ 新版本发布更新 CHANGELOG.md
- ✅ 配置变更更新 CHEATSHEET.md

### 版本控制
- 建议使用Git管理
- 重要版本打tag
- 保留CHANGELOG.md历史

### 文档同步
- 代码和文档保持一致
- 新增功能及时补充文档
- 废弃功能及时标注

---

## 📦 打包分发

### 最小发布包（核心功能）
```
核心文件：
- stock_screener_mai.py
- mai_indicator.py
- Ashare.py
- run_mai_screener.py
- requirements.txt

必读文档：
- START_HERE.md
- PROJECT_SUMMARY.md
- CHEATSHEET.md
```

### 完整发布包（包含测试）
```
核心文件 + 测试脚本 + 所有文档
```

---

## 🎓 文件学习建议

### 想快速使用？
→ 只看：START_HERE.md + CHEATSHEET.md

### 想深入理解？
→ 读：PROJECT_SUMMARY.md + ARCHITECTURE.md

### 想二次开发？
→ 读：所有文档 + 研究核心代码

### 想快速查阅？
→ 收藏：CHEATSHEET.md

---

## ✅ 文件完整性检查

```bash
# 检查核心文件是否存在
ls -l stock_screener_mai.py mai_indicator.py Ashare.py run_mai_screener.py

# 检查文档是否齐全
ls -l *.md | wc -l  # 应该有9个

# 检查结果目录
ls -l results/
```

---

**总文件数**：约30个  
**核心文件**：5个  
**文档文件**：9个  
**测试文件**：10个  

---

💡 **提示**：将本文档作为项目文件的总览参考！
