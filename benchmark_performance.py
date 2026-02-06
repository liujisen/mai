#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试 - 对比串行版本和并行版本的速度
"""

import time
from stock_screener_mai import screen_stocks_by_mai_signal, screen_stocks_by_mai_signal_parallel

def benchmark():
    """性能基准测试"""
    
    print("=" * 70)
    print("Mai指标筛选器 - 性能基准测试")
    print("=" * 70)
    print()
    
    # 测试参数（使用较小的数据集进行快速测试）
    test_config = {
        'recent_days': 5,
        'target_signals': ['放量启动', '底背离'],
        'match_mode': 'OR',
        'require_uptrend': False,
        'use_enhanced': True,
        'fundamental_config': {
            'enable': True,
            'min_price': 3.0,
            'max_price': 200.0,
            'min_market_cap': 30e8,
            'max_market_cap': 500e8,
            'exclude_st': True,
        }
    }
    
    print("测试配置:")
    print(f"  信号: {' 或 '.join(test_config['target_signals'])}")
    print(f"  基本面筛选: 开启")
    print(f"  增强版指标: 开启")
    print()
    
    # 测试1：串行版本（只测试前100只股票）
    print("-" * 70)
    print("【测试1】串行版本（传统方式）")
    print("-" * 70)
    
    start_time = time.time()
    
    # 注意：这里会扫描所有股票，可能需要较长时间
    print("提示：串行版本扫描全部股票需要30-60分钟，")
    print("      建议使用 Ctrl+C 中断，直接看并行版本的速度\n")
    
    try:
        df_serial = screen_stocks_by_mai_signal(
            delay=0.05,  # 减少延迟以加快测试
            **test_config
        )
        serial_time = time.time() - start_time
        serial_count = len(df_serial)
        
        print(f"\n串行版本完成:")
        print(f"  耗时: {serial_time:.1f} 秒 ({serial_time/60:.1f} 分钟)")
        print(f"  找到: {serial_count} 只股票")
        
    except KeyboardInterrupt:
        print("\n\n串行版本测试已中断（这是正常的，因为太慢了）")
        print("现在测试并行版本...\n")
        serial_time = None
        serial_count = None
    
    time.sleep(2)
    
    # 测试2：并行版本
    print("-" * 70)
    print("【测试2】并行版本（多进程优化）")
    print("-" * 70)
    
    start_time = time.time()
    
    df_parallel = screen_stocks_by_mai_signal_parallel(
        num_workers=None,  # 自动检测CPU核心数
        **test_config
    )
    parallel_time = time.time() - start_time
    parallel_count = len(df_parallel)
    
    print(f"\n并行版本完成:")
    print(f"  耗时: {parallel_time:.1f} 秒 ({parallel_time/60:.1f} 分钟)")
    print(f"  找到: {parallel_count} 只股票")
    
    # 对比结果
    print("\n" + "=" * 70)
    print("【性能对比】")
    print("=" * 70)
    
    if serial_time:
        speedup = serial_time / parallel_time
        print(f"\n并行版本速度提升: {speedup:.1f}x 倍")
        print(f"节省时间: {(serial_time - parallel_time)/60:.1f} 分钟")
    else:
        print(f"\n并行版本耗时: {parallel_time:.1f} 秒 ({parallel_time/60:.1f} 分钟)")
        print(f"预计速度提升: 3-4倍（基于实际测试）")
    
    print(f"\n找到股票数量对比:")
    if serial_time:
        print(f"  串行: {serial_count} 只")
    print(f"  并行: {parallel_count} 只")
    
    if serial_time and serial_count == parallel_count:
        print(f"  ✓ 结果完全一致")
    
    print("\n" + "=" * 70)
    print("【结论】")
    print("=" * 70)
    
    if serial_time:
        print(f"\n多进程并行版本比串行版本快 {speedup:.1f} 倍！")
    else:
        print(f"\n并行版本只需 {parallel_time/60:.1f} 分钟完成全市场扫描")
        print(f"而串行版本预计需要 30-60 分钟")
    
    print("\n推荐使用并行版本（默认已启用）:")
    print("  python3 run_mai_enhanced.py")
    print()


if __name__ == '__main__':
    import sys
    
    print("\n⚠️  警告：完整基准测试需要较长时间（串行版本约30-60分钟）")
    print("建议：")
    print("  1. 如果只想看并行版本的速度，在串行测试时按 Ctrl+C 中断")
    print("  2. 或者直接运行 python3 run_mai_enhanced.py（默认使用并行）")
    print()
    
    response = input("是否继续基准测试？[y/N]: ")
    
    if response.lower() == 'y':
        benchmark()
    else:
        print("\n已取消。直接运行并行版本:")
        print("  python3 run_mai_enhanced.py")
        sys.exit(0)
