#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mai指标筛选器 - 增强版运行脚本
包含: OBV能量潮 + 量比分析 + 基本面筛选
"""

from stock_screener_mai import main

if __name__ == '__main__':
    # ========== 增强版配置 ==========
    
    # 基本面筛选配置
    fundamental_config = {
        'enable': True,              # 启用基本面筛选
        'min_price': 3.0,           # 最低价格 3元（排除垃圾股）
        'max_price': 200.0,         # 最高价格 200元
        'min_market_cap': 30e8,     # 最小流通市值 30亿
        'max_market_cap': 500e8,    # 最大流通市值 500亿（排除超大盘股）
        'exclude_st': True,         # 排除ST股
    }
    
    # 技术信号配置
    recent_days = 5              # 查看最近5天内的信号
    target_signals = [           # 目标信号列表
        '放量启动',              # 金叉+放量
        '底背离',                # MACD底背离
        '隐蔽吸筹',              # OBV创新高但价格横盘
    ]
    match_mode = 'OR'            # OR: 满足任意一个即可, AND: 必须同时满足
    require_uptrend = False      # 是否要求当前处于上升趋势
    use_enhanced = True          # 使用增强版指标（OBV+量比）
    
    # ========== 运行筛选 ==========
    
    print("\n" + "="*70)
    print("Mai指标增强版选股系统")
    print("="*70)
    print("\n【增强功能】")
    print("  ✓ OBV能量潮 - 识别主力资金流向")
    print("  ✓ 量比分析 - 避免爆量陷阱（1.2-3.5倍为温和放量）")
    print("  ✓ 基本面筛选 - 市值、价格、ST股过滤")
    print("  ✓ MA18角度 - 避免震荡市假金叉")
    print("  ✓ 布林带收敛 - 捕捉变盘前夜")
    print("  ✓ 隐蔽吸筹 - 价格横盘但OBV创新高")
    
    print("\n【筛选条件】")
    print(f"  价格范围: {fundamental_config['min_price']}-{fundamental_config['max_price']}元")
    print(f"  市值范围: {fundamental_config['min_market_cap']/1e8:.0f}-{fundamental_config['max_market_cap']/1e8:.0f}亿")
    print(f"  排除ST股: {'是' if fundamental_config['exclude_st'] else '否'}")
    print(f"  信号组合: {' 或 '.join(target_signals)}")
    print(f"  上升趋势: {'必须' if require_uptrend else '不要求'}")
    print("\n" + "="*70 + "\n")
    
    # 运行主程序
    main(
        recent_days=recent_days,
        target_signals=target_signals,
        match_mode=match_mode,
        require_uptrend=require_uptrend,
        use_enhanced=use_enhanced,
        fundamental_config=fundamental_config
    )
    
    print("\n" + "="*70)
    print("增强版选股完成！")
    print("="*70)
    print("\n【结果说明】")
    print("  OBV向上 ✓: 资金持续流入（好）")
    print("  温和放量 ✓: 1.2-3.5倍量比（好）")
    print("  MA18向上 ✓: 均线向上（好）")
    print("  量比 > 3.5: 可能是爆量陷阱（警惕）")
    print("  隐蔽吸筹: 主力偷偷吸筹（重点关注）")
    print("\n【风控提示】")
    print("  1. 严格设置止损（按止损线执行）")
    print("  2. 关注板块联动效应")
    print("  3. 控制单只仓位不超过20%")
    print("  4. 出现'顶背离'或'离场警报'及时止盈")
    print()
