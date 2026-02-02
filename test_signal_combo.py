# -*- coding: utf-8 -*-
"""
测试信号组合 - 查看不同时间范围下的结果
"""

from stock_screener_mai import main

print("=" * 70)
print("测试不同时间范围下的筛选结果")
print("=" * 70)

# 测试10天
print("\n\n【测试1】最近10天: 放量启动 + 底背离")
print("-" * 70)
main(recent_days=10, required_signals=['放量启动', '底背离'])

print("\n\n" + "=" * 70)
print("如果10天也找不到，可能这个组合太严格了")
print("建议：")
print("1. 单独查看'放量启动'")
print("2. 单独查看'底背离'")
print("3. 查看'共振机会'（谷值+底背离，是内置的组合信号）")
print("=" * 70)
