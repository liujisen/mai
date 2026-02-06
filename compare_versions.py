#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
对比测试：原版 vs 增强版
用于评估OBV和基本面筛选的效果
"""

import pandas as pd
from datetime import datetime
from stock_screener_mai import screen_stocks_by_mai_signal

def compare_versions():
    """对比原版和增强版的筛选结果"""
    
    print("=" * 80)
    print("Mai指标选股系统 - 版本对比测试")
    print("=" * 80)
    print("\n开始对比测试，请耐心等待...\n")
    
    # 共同参数
    recent_days = 5
    target_signals = ['放量启动', '底背离']
    match_mode = 'OR'
    require_uptrend = False
    delay = 0.1
    
    # 基本面筛选配置
    fundamental_config = {
        'enable': True,
        'min_price': 3.0,
        'max_price': 200.0,
        'min_market_cap': 30e8,
        'max_market_cap': 500e8,
        'exclude_st': True,
    }
    
    # ========== 运行原版 ==========
    print("\n" + "=" * 80)
    print("【第一步】运行原版（v4.0）")
    print("=" * 80)
    
    df_v1 = screen_stocks_by_mai_signal(
        recent_days=recent_days,
        target_signals=target_signals,
        match_mode=match_mode,
        require_uptrend=require_uptrend,
        delay=delay,
        use_enhanced=False,  # 不使用增强版
        fundamental_config={'enable': False}  # 不使用基本面筛选
    )
    
    # ========== 运行增强版 ==========
    print("\n" + "=" * 80)
    print("【第二步】运行增强版（v5.0 with OBV + 基本面筛选）")
    print("=" * 80)
    
    df_v2 = screen_stocks_by_mai_signal(
        recent_days=recent_days,
        target_signals=target_signals,
        match_mode=match_mode,
        require_uptrend=require_uptrend,
        delay=delay,
        use_enhanced=True,   # 使用增强版
        fundamental_config=fundamental_config  # 使用基本面筛选
    )
    
    # ========== 对比分析 ==========
    print("\n" + "=" * 80)
    print("【对比结果】")
    print("=" * 80)
    
    print(f"\n原版（v4.0）筛选结果:")
    print(f"  - 信号数量: {len(df_v1)} 只")
    
    print(f"\n增强版（v5.0）筛选结果:")
    print(f"  - 信号数量: {len(df_v2)} 只")
    
    if len(df_v1) > 0 and len(df_v2) > 0:
        reduction_rate = (len(df_v1) - len(df_v2)) / len(df_v1) * 100
        print(f"  - 过滤率: {reduction_rate:.1f}% （筛选更严格）")
    
    # 保存结果
    today = datetime.now().strftime('%Y%m%d')
    
    if not df_v1.empty:
        filepath_v1 = f'results/mai_signals_v1_original_{today}.csv'
        df_v1.to_csv(filepath_v1, index=False, encoding='utf-8-sig')
        print(f"\n原版结果已保存: {filepath_v1}")
    
    if not df_v2.empty:
        filepath_v2 = f'results/mai_signals_v2_enhanced_{today}.csv'
        df_v2.to_csv(filepath_v2, index=False, encoding='utf-8-sig')
        print(f"增强版结果已保存: {filepath_v2}")
    
    # 分析差异
    if not df_v1.empty and not df_v2.empty:
        print("\n" + "=" * 80)
        print("【筛选效果分析】")
        print("=" * 80)
        
        # 被过滤掉的股票
        v1_codes = set(df_v1['股票代码'])
        v2_codes = set(df_v2['股票代码'])
        filtered_codes = v1_codes - v2_codes
        
        print(f"\n被基本面筛选过滤的股票: {len(filtered_codes)} 只")
        if len(filtered_codes) > 0 and len(filtered_codes) <= 20:
            print("  可能原因: ST股、价格过低/过高、市值不符")
            for code in list(filtered_codes)[:10]:
                stock_name = df_v1[df_v1['股票代码']==code]['股票名称'].values[0]
                price = df_v1[df_v1['股票代码']==code]['最新价'].values[0]
                print(f"    {code} {stock_name} {price:.2f}元")
        
        # 增强版特有的指标统计
        if 'OBV向上' in df_v2.columns:
            obv_up_count = (df_v2['OBV向上'] == '✓').sum()
            obv_rate = obv_up_count / len(df_v2) * 100 if len(df_v2) > 0 else 0
            
            mild_vol_count = (df_v2['温和放量'] == '✓').sum()
            mild_vol_rate = mild_vol_count / len(df_v2) * 100 if len(df_v2) > 0 else 0
            
            ma18_up_count = (df_v2['MA18向上'] == '✓').sum()
            ma18_up_rate = ma18_up_count / len(df_v2) * 100 if len(df_v2) > 0 else 0
            
            print(f"\n增强版指标统计:")
            print(f"  OBV向上占比: {obv_rate:.1f}% ({obv_up_count}/{len(df_v2)})")
            print(f"  温和放量占比: {mild_vol_rate:.1f}% ({mild_vol_count}/{len(df_v2)})")
            print(f"  MA18向上占比: {ma18_up_rate:.1f}% ({ma18_up_count}/{len(df_v2)})")
    
    print("\n" + "=" * 80)
    print("【总结】")
    print("=" * 80)
    print("\n增强版的优势:")
    print("  ✓ OBV能量潮 - 避免假放量，识别主力吸筹")
    print("  ✓ 量比上限 - 避免爆量陷阱（量比>3.5为警告）")
    print("  ✓ 基本面筛选 - 自动过滤ST股、垃圾股")
    print("  ✓ MA18角度 - 避免震荡市假金叉")
    print("\n建议:")
    print("  1. 日常使用增强版（v5.0）提高胜率")
    print("  2. 原版可用于快速扫描（信号更多但需人工筛选）")
    print("  3. 重点关注'OBV向上 + 温和放量 + MA18向上'三项全✓的股票")
    print()

if __name__ == '__main__':
    compare_versions()
