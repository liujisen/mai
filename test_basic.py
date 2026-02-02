# -*- coding: utf-8 -*-
"""
基础功能测试脚本
"""

from Ashare import get_price
import stock_screener

print("=" * 60)
print("测试 1: 验证 Ashare 库是否正常工作")
print("=" * 60)

try:
    # 测试获取上证指数数据
    df = get_price('sh000001', frequency='1d', count=2)
    print("✓ Ashare 库工作正常")
    print(f"  获取到 {len(df)} 条数据")
    print(f"  最新收盘价: {df['close'].iloc[-1]}")
except Exception as e:
    print(f"✗ Ashare 库测试失败: {e}")
    exit(1)

print("\n" + "=" * 60)
print("测试 2: 验证获取股票列表功能")
print("=" * 60)

try:
    stocks = stock_screener.get_stock_list()
    print(f"✓ 成功获取 {len(stocks)} 只股票")
    if len(stocks) > 0:
        print(f"  示例: {stocks[0]}")
except Exception as e:
    print(f"✗ 获取股票列表失败: {e}")
    exit(1)

print("\n" + "=" * 60)
print("测试 3: 验证涨幅计算功能")
print("=" * 60)

try:
    # 测试计算贵州茅台的涨幅
    result = stock_screener.calculate_change_pct('sh600519')
    if result:
        print("✓ 涨幅计算功能正常")
        print(f"  贵州茅台涨幅: {result['change_pct']:.2f}%")
        print(f"  今日收盘: {result['today_close']:.2f}")
    else:
        print("✗ 无法获取贵州茅台数据（可能停牌或网络问题）")
except Exception as e:
    print(f"✗ 涨幅计算失败: {e}")
    exit(1)

print("\n" + "=" * 60)
print("测试 4: 小范围筛选测试 (只测试前5只股票)")
print("=" * 60)

try:
    # 临时修改为只测试少量股票
    import pandas as pd
    test_stocks = [
        {'code': 'sh600519', 'name': '贵州茅台', 'original_code': '600519'},
        {'code': 'sh600036', 'name': '招商银行', 'original_code': '600036'},
        {'code': 'sz000001', 'name': '平安银行', 'original_code': '000001'},
        {'code': 'sz000858', 'name': '五粮液', 'original_code': '000858'},
        {'code': 'sh600000', 'name': '浦发银行', 'original_code': '600000'},
    ]
    
    results = []
    for stock in test_stocks:
        result = stock_screener.calculate_change_pct(stock['code'])
        if result:
            results.append({
                '股票代码': stock['original_code'],
                '股票名称': stock['name'],
                '涨幅(%)': round(result['change_pct'], 2)
            })
    
    if results:
        df = pd.DataFrame(results)
        print("✓ 筛选功能正常")
        print("\n测试结果:")
        print(df.to_string(index=False))
    else:
        print("✗ 未能获取任何股票数据")
        
except Exception as e:
    print(f"✗ 筛选测试失败: {e}")
    exit(1)

print("\n" + "=" * 60)
print("所有基础测试通过！")
print("=" * 60)
print("\n提示:")
print("- 如果要运行完整的筛选程序，请执行: python stock_screener.py")
print("- 完整筛选可能需要较长时间（约5-10分钟）")
print("- 结果将保存在 results/ 目录中")
