# -*- coding: utf-8 -*-
"""
A股Mai指标买入信号筛选器 - 小规模测试版
只筛选前100只股票，用于快速测试
"""

from stock_screener_mai import screen_stocks_by_mai_signal, get_stock_list, save_to_csv,send_wechat_msg

# ============ 配置参数 ============
RECENT_DAYS = 3
TARGET_SIGNALS = ['放量启动', '底背离']
MATCH_MODE = 'OR'
REQUIRE_UPTREND = True   # 要求EMA6在EMA18上方
TEST_LIMIT = 100  # 只测试前100只股票
# ==================================

trend_desc = " + EMA6在EMA18上方" if REQUIRE_UPTREND else ""
print("=" * 70)
print("A股Mai指标买入信号筛选器 - 小规模测试")
print(f"筛选条件: 最近{RECENT_DAYS}天内出现 {' 或 '.join(TARGET_SIGNALS)}{trend_desc}")
print(f"测试范围: 前{TEST_LIMIT}只股票")
print("=" * 70)
print()

# 获取股票列表
all_stocks = get_stock_list()
test_stocks = all_stocks[:TEST_LIMIT]

print(f"从 {len(all_stocks)} 只股票中选取前 {TEST_LIMIT} 只进行测试\n")

# 临时替换股票列表
import stock_screener_mai
original_get_list = stock_screener_mai.get_stock_list
stock_screener_mai.get_stock_list = lambda: test_stocks

# 运行筛选
df = screen_stocks_by_mai_signal(
    recent_days=RECENT_DAYS, 
    target_signals=TARGET_SIGNALS, 
    match_mode=MATCH_MODE,
    require_uptrend=REQUIRE_UPTREND,
    delay=0.05  # 测试时可以用更短的延迟
)

# 恢复原函数
stock_screener_mai.get_stock_list = original_get_list

# 显示结果
if not df.empty:
    print("\n" + "=" * 70)
    print("筛选结果:")
    print("=" * 70)
    print(df.to_string(index=False))
    
    # 统计信息
    print("\n" + "=" * 70)
    print("统计信息:")
    print("=" * 70)
    
    # 按信号类型统计
    signal_counts = {}
    for signals_str in df['买入信号']:
        for signal in signals_str.split('+'):
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
    
    print("\n信号类型分布:")
    for signal, count in signal_counts.items():
        print(f"  {signal}: {count} 只")
    
    # 按信号强度统计
    print("\n信号强度分布:")
    strength_counts = df['信号强度'].value_counts()
    for strength, count in strength_counts.items():
        print(f"  {strength}: {count} 只")
    
    # 保存到CSV
    save_to_csv(df)
    
    print("\n" + "=" * 70)
    print("💡 提示：测试成功！如需筛选全部A股，请运行:")
    print("   python3 run_mai_screener.py")
    print("=" * 70)
else:
    print(f"\n未找到符合条件的股票")
    print("\n💡 这是正常的，可能的原因：")
    print(f"  - 前{TEST_LIMIT}只股票中确实没有符合条件的")
    print(f"  - 建议运行全量筛选: python3 run_mai_screener.py")
# 在 main() 执行完之后加上这一行
if not df.empty:
    send_wechat_msg(df)
    
print("\n程序执行完毕！")
