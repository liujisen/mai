# -*- coding: utf-8 -*-
"""
检查各种信号的出现频率
"""

from Ashare import get_price
from mai_indicator import MaiIndicator

# 测试几只活跃股票
test_stocks = [
    ('sh600519', '贵州茅台'),
    ('sz000002', '万科A'),
    ('sh688981', '中芯国际'),
    ('sz300750', '宁德时代'),
    ('sz002594', '比亚迪'),
    ('sh601012', '隆基绿能'),
    ('sz000858', '五粮液'),
]

print("=" * 70)
print("检查最近10天内的信号出现情况")
print("=" * 70)

for code, name in test_stocks:
    print(f"\n{name} ({code}):")
    print("-" * 50)
    
    try:
        df = get_price(code, frequency='1d', count=100)
        if df is None or len(df) < 50:
            print("  数据不足")
            continue
        
        indicator = MaiIndicator(df)
        result = indicator.calculate_all()
        
        # 查看最近10天
        recent = result.tail(10)
        
        # 统计信号
        has_放量启动 = recent['放量启动'].any()
        has_底背离 = recent['底背离'].any()
        has_二浪回踩 = recent['二浪回踩'].any()
        has_共振机会 = recent['共振机会'].any()
        
        # 找出哪天有信号
        signals_found = []
        
        if has_放量启动:
            dates = recent[recent['放量启动']].index.strftime('%m-%d').tolist()
            signals_found.append(f"放量启动: {', '.join(dates)}")
        
        if has_底背离:
            dates = recent[recent['底背离']].index.strftime('%m-%d').tolist()
            signals_found.append(f"底背离: {', '.join(dates)}")
        
        if has_二浪回踩:
            dates = recent[recent['二浪回踩']].index.strftime('%m-%d').tolist()
            signals_found.append(f"二浪回踩: {', '.join(dates)}")
        
        if has_共振机会:
            dates = recent[recent['共振机会']].index.strftime('%m-%d').tolist()
            signals_found.append(f"共振机会: {', '.join(dates)}")
        
        if signals_found:
            for sig in signals_found:
                print(f"  ✓ {sig}")
        else:
            print("  ✗ 最近10天无信号")
            
        # 检查是否同一天有放量启动和底背离
        for idx in recent.index:
            if recent.loc[idx, '放量启动'] and recent.loc[idx, '底背离']:
                print(f"  🔥 {idx.strftime('%m-%d')}: 同时出现 放量启动+底背离！")
        
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)
