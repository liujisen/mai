# 🎯 从这里开始

## 欢迎使用 A股Mai指标筛选器！

---

## ⚡ 30秒快速测试

```bash
cd /Users/insilicomedicine/demo/A
python3 run_mai_screener_small.py
```

✅ 刚才测试结果：找到3只符合条件的股票！

---

## 🎮 现在你可以...

### 1️⃣ 运行完整筛选（10分钟）

```bash
python3 run_mai_screener.py
```

将筛选全部5477只A股，找出所有符合条件的股票。

### 2️⃣ 修改筛选条件

编辑 `run_mai_screener.py`：

```python
RECENT_DAYS = 3      # 改为 5, 10 等
TARGET_SIGNALS = ['放量启动', '底背离']  # 改信号
REQUIRE_UPTREND = True   # 改为 False
```

### 3️⃣ 查看结果

```bash
cat mai_buy_signals_*.csv
```

或直接用Excel打开CSV文件。

---

## 📖 了解更多

### 快速查阅
- **[CHEATSHEET.md](CHEATSHEET.md)** - 2分钟掌握所有命令 ⭐

### 完整文档
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 项目总结（15分钟）⭐
- **[INDEX.md](INDEX.md)** - 文档索引（5分钟）

### 按需查阅
- [QUICK_START.md](QUICK_START.md) - 详细使用指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构
- [CHANGELOG.md](CHANGELOG.md) - 版本历史

---

## 🎯 当前配置一览

| 参数 | 值 | 说明 |
|------|---|------|
| 时间范围 | 3天 | 最近3天 |
| 信号条件 | 放量启动 或 底背离 | OR模式 |
| 趋势要求 | EMA6 > EMA18 | 上升趋势 |
| 股票池 | 5477只 | 全A股 |

---

## ✨ 项目亮点

1. ⚡ **快速**：10分钟扫描5477只股票
2. 🎯 **准确**：基于成熟的Mai技术指标
3. 🔧 **灵活**：多种参数可配置
4. 📊 **全面**：覆盖主板+创业板+科创板
5. 💾 **方便**：结果自动保存CSV

---

## 🆘 遇到问题？

1. 📖 查看 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 的"常见问题"章节
2. 🧪 运行测试脚本：`python3 test_mai_signals.py`
3. 📊 检查结果文件是否生成

---

## 🎓 学习建议

### 5分钟入门
1. 运行测试版 ✅ （你已完成）
2. 查看结果CSV
3. 阅读 CHEATSHEET.md

### 30分钟掌握
1. 阅读 PROJECT_SUMMARY.md
2. 尝试修改配置
3. 运行完整版

### 深入学习
1. 阅读 ARCHITECTURE.md
2. 研究代码实现
3. 尝试添加新功能

---

## 📋 下一步行动

### 立即行动
- [ ] 运行完整版筛选全市场
- [ ] 查看并分析结果
- [ ] 尝试不同配置参数

### 可选优化
- [ ] 安装akshare（如果还没装）
- [ ] 设置每日定时运行
- [ ] 记录结果进行回测

---

## 🎉 祝贺！

你已经拥有了一个功能完善的A股筛选系统！

**准备好了？开始筛选吧！** 🚀

```bash
python3 run_mai_screener.py
```

---

**需要帮助？** 查看 [INDEX.md](INDEX.md) 找到所有文档 📚
