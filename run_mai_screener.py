# -*- coding: utf-8 -*-
"""
A股Mai指标买入信号筛选器 - 便捷运行脚本
可以快速调整参数
"""

from stock_screener_mai import main

# ============ 配置参数 ============
RECENT_DAYS = 3      # 查看最近多少天内的买入信号
                     # 1 = 只看今天
                     # 3 = 最近3天
                     # 5 = 最近5天
                     # 10 = 最近10天

# 目标信号列表
TARGET_SIGNALS = ['放量启动', '底背离']

# 匹配模式
MATCH_MODE = 'OR'    # 'OR' = 满足任意一个即可（放量启动 或 底背离）
                     # 'AND' = 必须同时满足（放量启动 且 底背离）

# 趋势要求
REQUIRE_UPTREND = True   # True = 必须EMA6在EMA18上方（上升趋势）
                         # False = 不限制趋势

# 可选的信号组合示例：
# ['放量启动', '底背离']        - 放量启动 或/且 底背离
# ['二浪回踩', '底背离']        - 二浪回踩 或/且 底背离
# ['共振机会']                  - 谷值 + 底背离（最强信号，内置组合）
# ['放量启动']                  - 只要放量启动
# ['底背离']                    - 只要底背离
# ['放量启动', '二浪回踩']      - 放量启动 或/且 二浪回踩
# ==================================

if __name__ == '__main__':
    main(recent_days=RECENT_DAYS, target_signals=TARGET_SIGNALS, match_mode=MATCH_MODE, require_uptrend=REQUIRE_UPTREND)
