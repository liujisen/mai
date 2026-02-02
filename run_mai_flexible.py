# -*- coding: utf-8 -*-
"""
A股Mai指标买入信号筛选器 - 灵活版本
可以查看不同的信号组合
"""

from stock_screener_mai import main

print("=" * 80)
print("Mai指标筛选器 - 多种信号组合测试")
print("=" * 80)

# 配置
RECENT_DAYS = 3  # 最近3天

# ========== 测试1: 放量启动 + 底背离（您要求的组合） ==========
print("\n\n【测试1】最近3天: 放量启动 + 底背离（同时满足）")
print("=" * 80)
main(recent_days=RECENT_DAYS, required_signals=['放量启动', '底背离'])

# ========== 测试2: 只要放量启动 ==========
print("\n\n【测试2】最近3天: 放量启动")
print("=" * 80)
main(recent_days=RECENT_DAYS, required_signals=['放量启动'])

# ========== 测试3: 只要底背离 ==========
print("\n\n【测试3】最近3天: 底背离")
print("=" * 80)
main(recent_days=RECENT_DAYS, required_signals=['底背离'])

# ========== 测试4: 共振机会（谷值+底背离） ==========
print("\n\n【测试4】最近3天: 共振机会（谷值+底背离）")
print("=" * 80)
main(recent_days=RECENT_DAYS, required_signals=['共振机会'])

print("\n\n" + "=" * 80)
print("所有测试完成！")
print("=" * 80)
print("\n说明：")
print("  - '放量启动 + 底背离' 同时出现的情况非常罕见")
print("  - '共振机会' 是Mai指标中预定义的强烈买入信号（谷值+底背离）")
print("  - 如果需要更多结果，建议：")
print("    1. 单独使用'放量启动'或'底背离'")
print("    2. 增加时间范围（如改为10天或20天）")
print("    3. 使用'共振机会'信号")
