# -*- coding: utf-8 -*-
"""
测试获取全部A股股票列表
"""

from stock_screener_mai import get_stock_list

print("=" * 70)
print("测试获取A股全部股票")
print("=" * 70)

stocks = get_stock_list()

print(f"\n总计获取: {len(stocks)} 只股票")

# 按板块统计
sh_main = [s for s in stocks if s['original_code'].startswith('60')]
sh_kcb = [s for s in stocks if s['original_code'].startswith('688')]
sz_main = [s for s in stocks if s['original_code'].startswith('000') or s['original_code'].startswith('001')]
sz_small = [s for s in stocks if s['original_code'].startswith('002') or s['original_code'].startswith('003')]
sz_gem = [s for s in stocks if s['original_code'].startswith('300')]

print("\n板块分布:")
print(f"  沪市主板 (600/601/603): {len(sh_main)} 只")
print(f"  科创板 (688): {len(sh_kcb)} 只")
print(f"  深市主板 (000/001): {len(sz_main)} 只")
print(f"  深市中小板 (002/003): {len(sz_small)} 只")
print(f"  创业板 (300): {len(sz_gem)} 只")

print("\n示例股票:")
if len(stocks) >= 10:
    for stock in stocks[:5]:
        print(f"  {stock['name']} ({stock['original_code']})")
    print("  ...")
    for stock in stocks[-5:]:
        print(f"  {stock['name']} ({stock['original_code']})")
