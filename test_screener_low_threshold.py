# -*- coding: utf-8 -*-
"""
测试筛选功能 - 使用低阈值
"""

import stock_screener

print("=" * 60)
print("测试筛选功能 - 涨幅阈值 0.5%")
print("=" * 60)

# 使用0.5%的阈值测试
df = stock_screener.screen_stocks(threshold=0.5, delay=0.1)

if not df.empty:
    print("\n找到的股票:")
    print(df.to_string(index=False))
    print(f"\n总共找到 {len(df)} 只股票")
    
    # 统计涨跌情况
    rising = len(df[df['涨幅(%)'] > 0])
    falling = len(df[df['涨幅(%)'] < 0])
    print(f"\n其中:")
    print(f"  上涨: {rising} 只")
    print(f"  下跌: {falling} 只")
    
    if rising > 0:
        print("\n✓ 筛选功能正常！")
        print("  如果需要找涨幅>5%的股票，可能需要扩大股票池或等待市场行情好转")
    else:
        print("\n今天市场整体表现不佳，所有测试股票都在下跌")
else:
    print("\n未找到任何股票，可能是数据获取问题")
