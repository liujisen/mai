#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证增强版功能是否正常安装
快速测试OBV、量比、基本面筛选等新功能
"""

import sys
import traceback

def test_mai_indicator():
    """测试mai_indicator的新功能"""
    print("=" * 60)
    print("【测试1】mai_indicator.py - OBV和增强指标")
    print("=" * 60)
    
    try:
        from mai_indicator import MaiIndicator
        import pandas as pd
        import numpy as np
        
        # 创建测试数据
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        np.random.seed(42)
        
        close_prices = 100 + np.cumsum(np.random.randn(50) * 2)
        high_prices = close_prices + np.random.rand(50) * 3
        low_prices = close_prices - np.random.rand(50) * 3
        open_prices = close_prices + np.random.randn(50) * 1.5
        volumes = np.random.randint(1000000, 5000000, 50)
        
        df = pd.DataFrame({
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': volumes
        }, index=dates)
        
        # 测试指标计算
        indicator = MaiIndicator(df)
        result = indicator.calculate_all()
        
        # 检查新增的列
        required_columns = [
            'OBV', 'OBV_MA30', 'OBV向上', 'OBV斜率', 'OBV加速',
            '隐蔽吸筹', '量比', '温和放量', '放量过猛',
            'MA18斜率', 'MA18向上', 'MA18走平',
            '布林上轨', '布林中轨', '布林下轨', '布林带宽', '极限收敛',
            '放量启动_增强'
        ]
        
        missing_columns = [col for col in required_columns if col not in result.columns]
        
        if missing_columns:
            print(f"❌ 缺少以下列: {missing_columns}")
            return False
        
        # 获取最新信号
        signals = indicator.get_signals()
        
        # 检查新增的信号字段
        required_signals = [
            'OBV', 'OBV向上', 'OBV加速', '隐蔽吸筹',
            '量比', '温和放量', '放量过猛',
            'MA18向上', '极限收敛', '放量启动_增强'
        ]
        
        missing_signals = [sig for sig in required_signals if sig not in signals]
        
        if missing_signals:
            print(f"❌ 缺少以下信号: {missing_signals}")
            return False
        
        print("✅ mai_indicator.py 新功能正常")
        print(f"   - OBV: {signals['OBV']:.0f}")
        print(f"   - OBV向上: {signals['OBV向上']}")
        print(f"   - 量比: {signals['量比']:.2f}")
        print(f"   - 温和放量: {signals['温和放量']}")
        print(f"   - MA18向上: {signals['MA18向上']}")
        print(f"   - 极限收敛: {signals['极限收敛']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False


def test_fundamental_filters():
    """测试基本面筛选功能"""
    print("\n" + "=" * 60)
    print("【测试2】stock_screener_mai.py - 基本面筛选")
    print("=" * 60)
    
    try:
        from stock_screener_mai import apply_fundamental_filters
        
        # 测试1: 价格过低（应该被过滤）
        passed, reason = apply_fundamental_filters(
            'sz000001', '测试股票', 2.5,
            fundamental_config={
                'enable': True,
                'min_price': 3.0,
                'max_price': 200.0,
                'exclude_st': True
            }
        )
        
        if passed:
            print(f"❌ 低价股票未被过滤")
            return False
        
        print(f"✅ 低价股票正确过滤: {reason}")
        
        # 测试2: 价格过高（应该被过滤）
        passed, reason = apply_fundamental_filters(
            'sz000001', '测试股票', 250.0,
            fundamental_config={
                'enable': True,
                'min_price': 3.0,
                'max_price': 200.0,
                'exclude_st': True
            }
        )
        
        if passed:
            print(f"❌ 高价股票未被过滤")
            return False
        
        print(f"✅ 高价股票正确过滤: {reason}")
        
        # 测试3: ST股票（应该被过滤）
        passed, reason = apply_fundamental_filters(
            'sz000001', 'ST测试', 10.0,
            fundamental_config={
                'enable': True,
                'min_price': 3.0,
                'max_price': 200.0,
                'exclude_st': True
            }
        )
        
        if passed:
            print(f"❌ ST股票未被过滤")
            return False
        
        print(f"✅ ST股票正确过滤: {reason}")
        
        # 测试4: 正常价格（应该通过基本筛选）
        passed, reason = apply_fundamental_filters(
            'sz000001', '正常股票', 50.0,
            fundamental_config={
                'enable': True,
                'min_price': 3.0,
                'max_price': 200.0,
                'exclude_st': True
            }
        )
        
        if not passed:
            # 可能是获取不到基本面数据，这是正常的
            print(f"⚪ 正常股票筛选: {reason if reason else '无法获取基本面数据（正常）'}")
        else:
            print(f"✅ 正常股票通过筛选")
        
        # 测试5: 关闭筛选（应该都通过）
        passed, reason = apply_fundamental_filters(
            'sz000001', 'ST测试', 2.0,
            fundamental_config={'enable': False}
        )
        
        if not passed:
            print(f"❌ 关闭筛选后仍被过滤")
            return False
        
        print("✅ 关闭筛选功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False


def test_check_buy_signal_params():
    """测试check_buy_signal的新参数"""
    print("\n" + "=" * 60)
    print("【测试3】check_buy_signal - 新参数支持")
    print("=" * 60)
    
    try:
        from stock_screener_mai import check_buy_signal
        import inspect
        
        # 检查函数签名
        sig = inspect.signature(check_buy_signal)
        params = list(sig.parameters.keys())
        
        required_params = ['use_enhanced', 'fundamental_config']
        missing_params = [p for p in required_params if p not in params]
        
        if missing_params:
            print(f"❌ 缺少参数: {missing_params}")
            return False
        
        print("✅ check_buy_signal 参数正常")
        print(f"   参数列表: {params}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()
        return False


def test_scripts_exist():
    """测试配套脚本是否存在"""
    print("\n" + "=" * 60)
    print("【测试4】配套脚本完整性")
    print("=" * 60)
    
    import os
    
    required_files = [
        'run_mai_enhanced.py',
        'compare_versions.py',
        'test_enhanced_single.py',
        'ENHANCED_README.md',
        'IMPLEMENTATION_SUMMARY.md',
        'QUICK_START.md'
    ]
    
    missing_files = []
    for filename in required_files:
        if not os.path.exists(filename):
            missing_files.append(filename)
    
    if missing_files:
        print(f"❌ 缺少文件: {missing_files}")
        return False
    
    print("✅ 所有配套文件完整")
    for filename in required_files:
        size = os.path.getsize(filename)
        print(f"   - {filename}: {size/1024:.1f} KB")
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Mai指标增强版 - 功能验证")
    print("=" * 60)
    print()
    
    tests = [
        ("OBV和增强指标", test_mai_indicator),
        ("基本面筛选", test_fundamental_filters),
        ("新参数支持", test_check_buy_signal_params),
        ("配套脚本", test_scripts_exist),
    ]
    
    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
    
    # 总结
    print("\n" + "=" * 60)
    print("【测试总结】")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print()
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！增强版功能正常，可以使用。")
        print("\n快速开始：")
        print("  python3 run_mai_enhanced.py")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查安装。")
        return 1


if __name__ == '__main__':
    sys.exit(main())
