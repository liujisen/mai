# -*- coding: utf-8 -*-
"""
测试Mai指标 - 查看具体股票的信号情况
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
]

print("=" * 70)
print("Mai指标详细分析")
print("=" * 70)

for code, name in test_stocks:
    print(f"\n{'='*70}")
    print(f"股票: {name} ({code})")
    print(f"{'='*70}")
    
    try:
        # 获取100天数据
        df = get_price(code, frequency='1d', count=100)
        
        if df is None or len(df) < 50:
            print(f"❌ 数据不足")
            continue
        
        # 计算指标
        indicator = MaiIndicator(df)
        indicator.calculate_all()
        
        # 打印最新信号
        indicator.print_latest_signals()
        
        # 获取最近5天的买入信号
        buy_signals_df = indicator.get_buy_signals()
        if len(buy_signals_df) > 0:
            recent_signals = buy_signals_df.tail(5)
            print(f"\n最近的买入信号:")
            print(recent_signals.to_string(index=False))
        else:
            print(f"\n近期无买入信号")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("分析完成")
print("=" * 70)
