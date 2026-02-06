"""
Mai指标Python实现
将富途牛牛Mai语言的自定义指标转换为Python代码
包含：趋势通道、平均波幅、顶底背离、共振机会、放量启动、二浪回踩、离场警报
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional


class MaiIndicator:
    """Mai指标计算类"""
    
    def __init__(self, df: pd.DataFrame):
        """
        初始化指标计算器
        
        Args:
            df: 包含股票数据的DataFrame，需要有以下列：
                - open/OPEN: 开盘价
                - high/HIGH: 最高价
                - low/LOW: 最低价
                - close/CLOSE: 收盘价
                - volume/VOL: 成交量
        """
        self.df = df.copy()
        self._normalize_columns()
        self.result = pd.DataFrame(index=df.index)
        
    def _normalize_columns(self):
        """统一列名为大写"""
        column_mapping = {
            'open': 'OPEN',
            'high': 'HIGH',
            'low': 'LOW',
            'close': 'CLOSE',
            'volume': 'VOL'
        }
        self.df.rename(columns={k: v for k, v in column_mapping.items() if k in self.df.columns}, inplace=True)
        
    def calculate_ema(self, series: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线EMA"""
        return series.ewm(span=period, adjust=False).mean()
    
    def calculate_ma(self, series: pd.Series, period: int) -> pd.Series:
        """计算简单移动平均线MA"""
        return series.rolling(window=period).mean()
    
    def ref(self, series: pd.Series, n: int) -> pd.Series:
        """返回N周期前的值"""
        return series.shift(n)
    
    def cross(self, series1: pd.Series, series2: pd.Series) -> pd.Series:
        """判断series1上穿series2"""
        return (series1 > series2) & (self.ref(series1, 1) <= self.ref(series2, 1))
    
    def barslast(self, condition: pd.Series) -> pd.Series:
        """返回距离上次条件成立的周期数"""
        result = pd.Series(index=condition.index, dtype=float)
        last_true_idx = -1
        
        for i in range(len(condition)):
            if condition.iloc[i]:
                last_true_idx = i
                result.iloc[i] = 0
            elif last_true_idx >= 0:
                result.iloc[i] = i - last_true_idx
            else:
                result.iloc[i] = np.nan
                
        return result
    
    def zig(self, series: pd.Series, turn_rate: float) -> pd.Series:
        """
        ZIG函数实现 - 之字转向
        turn_rate: 转向幅度百分比
        """
        if len(series) < 2:
            return pd.Series(index=series.index, dtype=float)
        
        zig_values = pd.Series(index=series.index, dtype=float)
        threshold = turn_rate / 100.0
        
        # 初始化
        direction = 0  # 0=未定，1=上升，-1=下降
        last_pivot_idx = 0
        last_pivot_value = series.iloc[0]
        zig_values.iloc[0] = last_pivot_value
        
        for i in range(1, len(series)):
            current_value = series.iloc[i]
            
            if direction == 0:
                # 确定初始方向
                if current_value > last_pivot_value * (1 + threshold):
                    direction = 1
                    zig_values.iloc[i] = current_value
                    last_pivot_idx = i
                    last_pivot_value = current_value
                elif current_value < last_pivot_value * (1 - threshold):
                    direction = -1
                    zig_values.iloc[i] = current_value
                    last_pivot_idx = i
                    last_pivot_value = current_value
                else:
                    zig_values.iloc[i] = last_pivot_value
                    
            elif direction == 1:  # 上升趋势
                if current_value > last_pivot_value:
                    # 继续上升
                    last_pivot_value = current_value
                    last_pivot_idx = i
                    zig_values.iloc[i] = current_value
                elif current_value < last_pivot_value * (1 - threshold):
                    # 转向下降
                    direction = -1
                    zig_values.iloc[i] = current_value
                    last_pivot_idx = i
                    last_pivot_value = current_value
                else:
                    zig_values.iloc[i] = last_pivot_value
                    
            else:  # direction == -1，下降趋势
                if current_value < last_pivot_value:
                    # 继续下降
                    last_pivot_value = current_value
                    last_pivot_idx = i
                    zig_values.iloc[i] = current_value
                elif current_value > last_pivot_value * (1 + threshold):
                    # 转向上升
                    direction = 1
                    zig_values.iloc[i] = current_value
                    last_pivot_idx = i
                    last_pivot_value = current_value
                else:
                    zig_values.iloc[i] = last_pivot_value
        
        return zig_values
    
    def calculate_obv(self) -> pd.Series:
        """
        计算OBV能量潮指标
        OBV是通过累计成交量来判断资金流向的指标
        价格上涨时加上当日成交量，价格下跌时减去当日成交量
        """
        obv = pd.Series(0.0, index=self.df.index)
        obv.iloc[0] = self.df['VOL'].iloc[0]
        
        for i in range(1, len(self.df)):
            if self.df['CLOSE'].iloc[i] > self.df['CLOSE'].iloc[i-1]:
                # 价格上涨，加上成交量
                obv.iloc[i] = obv.iloc[i-1] + self.df['VOL'].iloc[i]
            elif self.df['CLOSE'].iloc[i] < self.df['CLOSE'].iloc[i-1]:
                # 价格下跌，减去成交量
                obv.iloc[i] = obv.iloc[i-1] - self.df['VOL'].iloc[i]
            else:
                # 价格持平，OBV不变
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def calculate_volume_ratio(self) -> pd.Series:
        """
        计算量比（当日成交量/5日平均成交量）
        用于判断成交量的放大程度
        """
        vol_ma5 = self.calculate_ma(self.df['VOL'], 5)
        volume_ratio = self.df['VOL'] / vol_ma5
        return volume_ratio
    
    def calculate_ma_slope(self, ma_series: pd.Series) -> pd.Series:
        """
        计算均线的斜率（角度）
        正值表示向上，负值表示向下
        """
        slope = (ma_series - self.ref(ma_series, 1)) / self.ref(ma_series, 1)
        return slope
    
    def calculate_bollinger_bands(self) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        计算布林带
        返回：上轨、中轨、下轨、带宽
        """
        ma20 = self.calculate_ma(self.df['CLOSE'], 20)
        std20 = self.df['CLOSE'].rolling(20).std()
        
        upper = ma20 + 2 * std20
        lower = ma20 - 2 * std20
        bandwidth = (upper - lower) / ma20
        
        return upper, ma20, lower, bandwidth
    
    def calculate_all(self) -> pd.DataFrame:
        """计算所有指标"""
        
        # ========== 1. 趋势通道 ==========
        self.result['EMA6'] = self.calculate_ema(self.df['CLOSE'], 6)
        self.result['EMA18'] = self.calculate_ema(self.df['CLOSE'], 18)
        self.result['VAR_SHORT'] = self.result['EMA6']
        self.result['VAR_LONG'] = self.result['EMA18']
        
        # 趋势判断
        self.result['IS_UPTREND'] = self.result['VAR_SHORT'] >= self.result['VAR_LONG']
        
        # ========== 2. 平均波幅（ATR）和止损线 ==========
        TR1 = self.df['HIGH'] - self.df['LOW']
        TR2 = abs(self.df['HIGH'] - self.ref(self.df['CLOSE'], 1))
        TR3 = abs(self.df['LOW'] - self.ref(self.df['CLOSE'], 1))
        TR_VAL = pd.concat([TR1, TR2, TR3], axis=1).max(axis=1)
        self.result['MY_ATR'] = self.calculate_ma(TR_VAL, 14)
        self.result['STOP_LOSS_LINE'] = self.result['EMA6'] - 2.5 * self.result['MY_ATR']
        
        # 止盈红线（只在上升趋势显示）
        self.result['止盈红线'] = np.where(
            self.result['VAR_SHORT'] > self.result['VAR_LONG'],
            self.result['STOP_LOSS_LINE'],
            np.nan
        )
        
        # ========== 3. 顶底背离（基于MACD） ==========
        DIF = self.calculate_ema(self.df['CLOSE'], 12) - self.calculate_ema(self.df['CLOSE'], 26)
        DEA = self.calculate_ema(DIF, 9)
        MACD_BAR = (DIF - DEA) * 2
        
        self.result['DIF'] = DIF
        self.result['DEA'] = DEA
        self.result['MACD_BAR'] = MACD_BAR
        
        # 底背离
        cross_dif_dea = self.cross(DIF, DEA)
        A1 = self.barslast(self.ref(cross_dif_dea, 1))
        
        底背离_condition = pd.Series(False, index=self.df.index)
        for i in range(len(self.df)):
            if pd.notna(A1.iloc[i]) and A1.iloc[i] > 0:
                ref_idx = int(A1.iloc[i]) + 1
                if i >= ref_idx:
                    cond1 = self.df['CLOSE'].iloc[i - ref_idx] > self.df['CLOSE'].iloc[i]
                    cond2 = DIF.iloc[i] > DIF.iloc[i - ref_idx]
                    cond3 = cross_dif_dea.iloc[i]
                    底背离_condition.iloc[i] = cond1 and cond2 and cond3
        
        self.result['底背离'] = 底背离_condition
        
        # 顶背离
        cross_dea_dif = self.cross(DEA, DIF)
        A2 = self.barslast(self.ref(cross_dea_dif, 1))
        
        顶背离_condition = pd.Series(False, index=self.df.index)
        for i in range(len(self.df)):
            if pd.notna(A2.iloc[i]) and A2.iloc[i] > 0:
                ref_idx = int(A2.iloc[i]) + 1
                if i >= ref_idx:
                    cond1 = self.df['CLOSE'].iloc[i - ref_idx] < self.df['CLOSE'].iloc[i]
                    cond2 = DIF.iloc[i] < DIF.iloc[i - ref_idx]
                    cond3 = cross_dea_dif.iloc[i]
                    顶背离_condition.iloc[i] = cond1 and cond2 and cond3
        
        self.result['顶背离'] = 顶背离_condition
        
        # ========== 4. ZIG之字转向（峰谷检测） ==========
        TURN_RATE = 5
        Z_VAL = self.zig(self.df['CLOSE'] * 3, TURN_RATE)  # 乘以3是Mai的ZIG(3, TURN_RATE)
        self.result['Z_VAL'] = Z_VAL
        
        IS_PEAK = self.cross(self.ref(Z_VAL, 1), Z_VAL)  # 峰值
        IS_TROUGH = self.cross(Z_VAL, self.ref(Z_VAL, 1))  # 谷值
        
        self.result['IS_PEAK'] = IS_PEAK
        self.result['IS_TROUGH'] = IS_TROUGH
        
        # ========== 5. 共振机会 ==========
        self.result['共振机会'] = IS_TROUGH & 底背离_condition
        
        # ========== 6. OBV能量潮（新增）==========
        self.result['OBV'] = self.calculate_obv()
        self.result['OBV_MA30'] = self.calculate_ma(self.result['OBV'], 30)
        self.result['OBV向上'] = self.result['OBV'] > self.result['OBV_MA30']
        
        # OBV斜率（判断资金流入速度）
        obv_slope = (self.result['OBV'] - self.ref(self.result['OBV'], 1)) / (self.ref(self.result['OBV'], 1).abs() + 1)
        self.result['OBV斜率'] = obv_slope
        self.result['OBV加速'] = obv_slope > 0
        
        # 隐蔽吸筹：价格横盘但OBV创新高（主力悄悄吸筹）
        obv_high_20 = self.result['OBV'].rolling(20).max()
        price_high_10 = self.df['HIGH'].rolling(10).max()
        price_low_10 = self.df['LOW'].rolling(10).min()
        price_range = (price_high_10 - price_low_10) / self.df['CLOSE']
        
        self.result['隐蔽吸筹'] = (
            (self.result['OBV'] >= obv_high_20) &  # OBV创新高
            (price_range < 0.10)  # 价格波动小于10%
        )
        
        # ========== 7. 量比分析（新增）==========
        self.result['量比'] = self.calculate_volume_ratio()
        
        # 温和放量：1.2 < 量比 < 3.5（避免爆量陷阱）
        self.result['温和放量'] = (
            (self.result['量比'] > 1.2) & 
            (self.result['量比'] < 3.5)
        )
        
        # 放量过猛警告（可能是出货）
        self.result['放量过猛'] = self.result['量比'] > 4.0
        
        # ========== 8. MA18角度分析（新增）==========
        ma18_slope = self.calculate_ma_slope(self.result['EMA18'])
        self.result['MA18斜率'] = ma18_slope
        self.result['MA18向上'] = ma18_slope > 0
        self.result['MA18走平'] = (ma18_slope >= -0.001) & (ma18_slope <= 0.001)
        
        # ========== 9. 布林带分析（新增）==========
        upper, middle, lower, bandwidth = self.calculate_bollinger_bands()
        self.result['布林上轨'] = upper
        self.result['布林中轨'] = middle
        self.result['布林下轨'] = lower
        self.result['布林带宽'] = bandwidth
        
        # 极限收敛（变盘前夜）
        self.result['极限收敛'] = (
            (bandwidth < 0.10) &  # 带宽极窄
            (self.df['CLOSE'] > middle)  # 站上中轨
        )
        
        # ========== 10. 放量启动（优化版）==========
        IS_VOL_UP = self.df['VOL'] > self.calculate_ma(self.df['VOL'], 5)
        IS_GOLD_CROSS = self.cross(self.result['VAR_SHORT'], self.result['VAR_LONG'])
        
        # 原版放量启动（保留兼容性）
        REAL_BUY = IS_GOLD_CROSS & IS_VOL_UP
        
        # 增强版放量启动（更严格的条件）
        REAL_BUY_V2 = (
            IS_GOLD_CROSS &  # 金叉
            self.result['温和放量'] &  # 温和放量（非爆量）
            self.result['OBV向上'] &  # OBV向上
            (self.result['MA18向上'] | self.result['MA18走平'])  # MA18向上或走平
        )
        
        self.result['IS_VOL_UP'] = IS_VOL_UP
        self.result['IS_GOLD_CROSS'] = IS_GOLD_CROSS
        self.result['放量启动'] = REAL_BUY  # 原版
        self.result['放量启动_增强'] = REAL_BUY_V2  # 增强版
        
        # ========== 11. 二浪回踩 ==========
        IS_BULL = self.result['VAR_SHORT'] > self.result['VAR_LONG']
        IS_DIP = (self.df['LOW'] <= self.result['VAR_SHORT']) & (self.df['CLOSE'] > self.result['STOP_LOSS_LINE'])
        IS_RED_CANDLE = self.df['CLOSE'] > self.df['OPEN']
        bars_since_gold = self.barslast(IS_GOLD_CROSS)
        
        BUY_DIP = IS_BULL & IS_DIP & IS_RED_CANDLE & (bars_since_gold > 3)
        self.result['二浪回踩'] = BUY_DIP
        
        # ========== 12. 离场警报 ==========
        IS_STOP = self.cross(self.result['STOP_LOSS_LINE'], self.df['CLOSE']) & (self.result['VAR_SHORT'] > self.result['VAR_LONG'])
        self.result['离场警报'] = IS_STOP
        
        return self.result
    
    def get_signals(self, date: Optional[str] = None) -> Dict:
        """
        获取指定日期的信号
        
        Args:
            date: 日期，格式如'2024-01-01'，如果为None则返回最新的信号
            
        Returns:
            包含各种信号的字典
        """
        if len(self.result) == 0:
            self.calculate_all()
        
        if date:
            row = self.result.loc[date]
        else:
            row = self.result.iloc[-1]
        
        signals = {
            'EMA6': row['EMA6'],
            'EMA18': row['EMA18'],
            '止损线': row['STOP_LOSS_LINE'],
            '上升趋势': row['IS_UPTREND'],
            '底背离': row['底背离'],
            '顶背离': row['顶背离'],
            '谷值信号': row['IS_TROUGH'],
            '峰值信号': row['IS_PEAK'],
            '共振机会': row['共振机会'],
            '放量启动': row['放量启动'],
            '放量启动_增强': row['放量启动_增强'],
            '二浪回踩': row['二浪回踩'],
            '离场警报': row['离场警报'],
            # 新增OBV指标
            'OBV': row['OBV'],
            'OBV向上': row['OBV向上'],
            'OBV加速': row['OBV加速'],
            '隐蔽吸筹': row['隐蔽吸筹'],
            # 新增量比指标
            '量比': row['量比'],
            '温和放量': row['温和放量'],
            '放量过猛': row['放量过猛'],
            # 新增MA18角度
            'MA18向上': row['MA18向上'],
            # 新增布林带
            '极限收敛': row['极限收敛'],
        }
        
        return signals
    
    def get_buy_signals(self) -> pd.DataFrame:
        """获取所有买入信号的日期"""
        if len(self.result) == 0:
            self.calculate_all()
        
        buy_dates = []
        
        # 放量启动
        for date in self.result[self.result['放量启动']].index:
            buy_dates.append({
                'date': date,
                'signal': '放量启动',
                'price': self.df.loc[date, 'CLOSE'],
                'description': '金叉+放量，一浪进场机会'
            })
        
        # 二浪回踩
        for date in self.result[self.result['二浪回踩']].index:
            buy_dates.append({
                'date': date,
                'signal': '二浪回踩',
                'price': self.df.loc[date, 'CLOSE'],
                'description': '回踩EMA6支撑，二浪进场机会'
            })
        
        # 共振机会
        for date in self.result[self.result['共振机会']].index:
            buy_dates.append({
                'date': date,
                'signal': '双重共振',
                'price': self.df.loc[date, 'CLOSE'],
                'description': '谷值+底背离，强烈买入信号'
            })
        
        return pd.DataFrame(buy_dates)
    
    def get_sell_signals(self) -> pd.DataFrame:
        """获取所有卖出信号的日期"""
        if len(self.result) == 0:
            self.calculate_all()
        
        sell_dates = []
        
        # 离场警报
        for date in self.result[self.result['离场警报']].index:
            sell_dates.append({
                'date': date,
                'signal': '破线离场',
                'price': self.df.loc[date, 'CLOSE'],
                'description': '跌破止损线，需要离场'
            })
        
        # 顶背离
        for date in self.result[self.result['顶背离']].index:
            sell_dates.append({
                'date': date,
                'signal': '顶背离',
                'price': self.df.loc[date, 'CLOSE'],
                'description': '顶部背离，注意风险'
            })
        
        return pd.DataFrame(sell_dates)
    
    def print_latest_signals(self):
        """打印最新的信号"""
        signals = self.get_signals()
        latest_date = self.df.index[-1]
        latest_close = self.df['CLOSE'].iloc[-1]
        
        print(f"\n========== 最新信号 ({latest_date}) ==========")
        print(f"收盘价: {latest_close:.2f}")
        print(f"EMA6: {signals['EMA6']:.2f}")
        print(f"EMA18: {signals['EMA18']:.2f}")
        print(f"止损线: {signals['止损线']:.2f}")
        print(f"趋势: {'上升' if signals['上升趋势'] else '下降'}")
        print("\n----- 信号 -----")
        
        if signals['放量启动']:
            print("🚀 放量启动 - 金叉+放量，一浪进场机会")
        if signals['二浪回踩']:
            print("🚘 二浪回踩 - 回踩支撑，二浪进场机会")
        if signals['共振机会']:
            print("🔥🔥 双重共振 - 谷值+底背离，强烈买入信号")
        if signals['底背离']:
            print("★ 底背离 - 注意反转机会")
        if signals['顶背离']:
            print("★ 顶背离 - 注意顶部风险")
        if signals['谷值信号']:
            print("留意反转 - ZIG谷值")
        if signals['离场警报']:
            print("🛑 破线离场 - 跌破止损线")
        
        if not any([signals['放量启动'], signals['二浪回踩'], signals['共振机会'], 
                   signals['底背离'], signals['顶背离'], signals['谷值信号'], signals['离场警报']]):
            print("暂无明显信号")


def demo_usage():
    """演示如何使用"""
    # 创建示例数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # 生成模拟K线数据
    close_prices = 100 + np.cumsum(np.random.randn(100) * 2)
    high_prices = close_prices + np.random.rand(100) * 3
    low_prices = close_prices - np.random.rand(100) * 3
    open_prices = close_prices + np.random.randn(100) * 1.5
    volumes = np.random.randint(1000000, 5000000, 100)
    
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    }, index=dates)
    
    # 创建指标计算器
    indicator = MaiIndicator(df)
    
    # 计算所有指标
    result = indicator.calculate_all()
    
    # 打印最新信号
    indicator.print_latest_signals()
    
    # 获取所有买入信号
    print("\n========== 买入信号 ==========")
    buy_signals = indicator.get_buy_signals()
    if len(buy_signals) > 0:
        print(buy_signals.to_string(index=False))
    else:
        print("无买入信号")
    
    # 获取所有卖出信号
    print("\n========== 卖出信号 ==========")
    sell_signals = indicator.get_sell_signals()
    if len(sell_signals) > 0:
        print(sell_signals.to_string(index=False))
    else:
        print("无卖出信号")
    
    return indicator, result


if __name__ == '__main__':
    # 运行演示
    indicator, result = demo_usage()
    
    # 保存结果到CSV
    result.to_csv('mai_indicator_result.csv')
    print("\n结果已保存到 mai_indicator_result.csv")
