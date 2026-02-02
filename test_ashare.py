# -*- coding: utf-8 -*-
"""
直接测试Ashare库
"""

from Ashare import get_price
import traceback

test_codes = [
    'sh600519',    # 贵州茅台
    '600519',      # 不带前缀
    'sh000001',    # 上证指数
    'sz000001',    # 平安银行
    'sz300750',    # 宁德时代
]

print("测试Ashare库数据获取:\n")

for code in test_codes:
    print(f"测试 {code}:")
    try:
        df = get_price(code, frequency='1d', count=2)
        if df is not None and len(df) > 0:
            print(f"  ✓ 成功获取 {len(df)} 条数据")
            print(f"    最新收盘: {df['close'].iloc[-1]}")
            if len(df) >= 2:
                print(f"    昨日收盘: {df['close'].iloc[-2]}")
        else:
            print(f"  ✗ 返回数据为空")
    except Exception as e:
        print(f"  ✗ 错误: {e}")
        traceback.print_exc()
    print()
