# -*- coding: utf-8 -*-
"""
调试脚本 - 检查数据获取情况
"""

from Ashare import get_price
import stock_screener

print("=" * 60)
print("调试检查：数据获取情况")
print("=" * 60)

# 1. 检查股票列表
stocks = stock_screener.get_stock_list()
print(f"\n获取到股票数量: {len(stocks)}")
print(f"前5只股票: {stocks[:5]}")

# 2. 随机检查几只股票的数据
test_stocks = stocks[:10]  # 测试前10只

print("\n" + "=" * 60)
print("检查前10只股票的数据获取情况:")
print("=" * 60)

for i, stock in enumerate(test_stocks, 1):
    code = stock['code']
    name = stock['name']
    
    try:
        result = stock_screener.calculate_change_pct(code)
        if result:
            print(f"{i}. {name}({code})")
            print(f"   昨日收盘: {result['yesterday_close']:.2f}")
            print(f"   今日收盘: {result['today_close']:.2f}")
            print(f"   涨幅: {result['change_pct']:.2f}%")
            print(f"   日期: {result['date']}")
        else:
            print(f"{i}. {name}({code}) - 数据获取失败")
    except Exception as e:
        print(f"{i}. {name}({code}) - 错误: {e}")

# 3. 直接测试一些活跃股票
print("\n" + "=" * 60)
print("测试一些活跃股票:")
print("=" * 60)

active_stocks = [
    ('sh600519', '贵州茅台'),
    ('sh600036', '招商银行'),
    ('sz000858', '五粮液'),
    ('sz300750', '宁德时代'),
    ('sh601318', '中国平安'),
]

for code, name in active_stocks:
    try:
        result = stock_screener.calculate_change_pct(code)
        if result:
            status = "✓" if result['change_pct'] > 5.0 else "✗"
            print(f"{status} {name}: 涨幅 {result['change_pct']:.2f}%")
        else:
            print(f"✗ {name}: 无法获取数据")
    except Exception as e:
        print(f"✗ {name}: 错误 - {e}")

print("\n分析：")
print("如果所有股票涨幅都小于5%，可能是今天市场整体表现不佳")
print("建议：可以降低阈值到2-3%来测试筛选功能")
