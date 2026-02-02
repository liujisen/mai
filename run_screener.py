# -*- coding: utf-8 -*-
"""
A股涨幅筛选器 - 便捷运行脚本
可以快速调整参数
"""

import stock_screener

# ============ 配置参数 ============
THRESHOLD = 2.0      # 涨幅阈值（%），可改为 1.0, 2.0, 3.0, 5.0 等
DELAY = 0.05         # 请求延迟（秒），避免请求过快
# ==================================

print("=" * 60)
print(f"A股涨幅筛选器")
print(f"筛选条件: 今日涨幅 > {THRESHOLD}%")
print("=" * 60)
print()

# 运行筛选
df = stock_screener.screen_stocks(threshold=THRESHOLD, delay=DELAY)

# 显示和保存结果
if not df.empty:
    print("\n" + "=" * 60)
    print(f"筛选结果: 找到 {len(df)} 只符合条件的股票")
    print("=" * 60)
    print(df.to_string(index=False))
    
    # 保存到CSV
    stock_screener.save_to_csv(df)
    
    # 统计信息
    avg_change = df['涨幅(%)'].mean()
    max_change = df['涨幅(%)'].max()
    print(f"\n统计信息:")
    print(f"  平均涨幅: {avg_change:.2f}%")
    print(f"  最大涨幅: {max_change:.2f}%")
else:
    print(f"\n未找到涨幅超过 {THRESHOLD}% 的股票")
    print("\n建议：")
    print("  1. 降低阈值（修改本文件中的 THRESHOLD 参数）")
    print("  2. 等待市场行情好转后再运行")
    print("  3. 扩大股票池范围")

print("\n程序执行完毕！")
