# -*- coding: utf-8 -*-
"""
A股Mai指标买入信号筛选器
根据 mai_indicator.py 中的技术指标筛选出现买入信号的股票
"""

import json
import time
import os
from datetime import datetime
import requests
import pandas as pd
from Ashare import get_price
from mai_indicator import MaiIndicator


def get_stock_list():
    """
    获取所有A股股票代码列表（主板、创业板、科创板）
    使用东方财富API获取
    """
    print("正在获取A股全部股票列表...")
    all_stocks = []
    seen_codes = set()  # 用于去重
    
    # 方法1: 尝试从东方财富获取
    try:
        print("方法1: 从东方财富API获取全部A股...")
        
        # 定义各个板块的查询参数
        markets = [
            # 沪市主板 (600, 601, 603, 605等开头)
            {'name': '沪市主板', 'fs': 'm:1+t:2,m:1+t:23', 'prefix': 'sh'},
            # 科创板 (688开头)
            {'name': '科创板', 'fs': 'm:1+t:23', 'prefix': 'sh'},
            # 深市主板 (000, 001开头)
            {'name': '深市主板', 'fs': 'm:0+t:6,m:0+t:13', 'prefix': 'sz'},
            # 深市中小板 (002, 003开头)
            {'name': '深市中小板', 'fs': 'm:0+t:7,m:0+t:13', 'prefix': 'sz'},
            # 创业板 (300开头)
            {'name': '创业板', 'fs': 'm:0+t:80', 'prefix': 'sz'},
        ]
        
        for market in markets:
            market_name = market['name']
            fs_param = market['fs']
            prefix = market['prefix']
            
            print(f"  正在获取{market_name}...")
            page = 1
            market_count = 0
            
            while True:
                try:
                    url = f'http://push2.eastmoney.com/api/qt/clist/get?pn={page}&pz=1000&po=1&np=1&fltt=2&invt=2&fid=f3&fs={fs_param}&fields=f12,f14'
                    response = requests.get(url, timeout=15)
                    data = response.json()
                    
                    if not data or 'data' not in data or not data['data']:
                        break
                    
                    if 'diff' not in data['data'] or not data['data']['diff']:
                        break
                    
                    items = data['data']['diff']
                    if not items:
                        break
                    
                    for item in items:
                        code = item['f12']
                        name = item['f14']
                        
                        # 去重
                        if code not in seen_codes:
                            seen_codes.add(code)
                            all_stocks.append({
                                'code': f'{prefix}{code}',
                                'name': name,
                                'original_code': code
                            })
                            market_count += 1
                    
                    # 如果返回的数量小于1000，说明已经是最后一页
                    if len(items) < 1000:
                        break
                    
                    page += 1
                    time.sleep(0.1)  # 避免请求过快
                    
                except Exception as e:
                    print(f"    {market_name}第{page}页获取失败: {e}")
                    break
            
            print(f"    {market_name}获取完成: {market_count} 只")
        
        if len(all_stocks) > 100:
            print(f"\n✓ 成功获取全部A股 {len(all_stocks)} 只股票")
            print(f"  包括: 沪市主板、科创板、深市主板、中小板、创业板")
            return all_stocks
            
    except Exception as e:
        print(f"\n从东方财富获取失败: {e}")
    
    # 方法2: 尝试使用akshare获取（如果已安装）
    try:
        print("\n方法2: 尝试使用akshare库获取...")
        import akshare as ak
        
        # 获取沪深A股
        df_a = ak.stock_info_a_code_name()
        
        for _, row in df_a.iterrows():
            code = row['code']
            name = row['name']
            
            # 确定前缀
            if code.startswith('6') or code.startswith('688'):
                prefix = 'sh'
            else:
                prefix = 'sz'
            
            if code not in seen_codes:
                seen_codes.add(code)
                all_stocks.append({
                    'code': f'{prefix}{code}',
                    'name': name,
                    'original_code': code
                })
        
        if len(all_stocks) > 100:
            print(f"✓ 通过akshare成功获取 {len(all_stocks)} 只股票")
            return all_stocks
            
    except ImportError:
        print("  akshare未安装，跳过")
    except Exception as e:
        print(f"  akshare获取失败: {e}")
    
    # 方法3: 生成常见的股票代码范围
    print("\n方法3: 生成A股常见代码范围...")
    try:
        # 沪市主板: 600000-605999, 601000-601999, 603000-603999
        for prefix_num in [600, 601, 603]:
            for i in range(1000):
                code = f"{prefix_num}{i:03d}"
                if code not in seen_codes:
                    seen_codes.add(code)
                    all_stocks.append({
                        'code': f'sh{code}',
                        'name': f'沪股{code}',
                        'original_code': code
                    })
        
        # 科创板: 688000-688999
        for i in range(1000):
            code = f"688{i:03d}"
            if code not in seen_codes:
                seen_codes.add(code)
                all_stocks.append({
                    'code': f'sh{code}',
                    'name': f'科创{code}',
                    'original_code': code
                })
        
        # 深市主板: 000000-001999
        for i in range(2000):
            code = f"000{i:03d}"
            if code not in seen_codes:
                seen_codes.add(code)
                all_stocks.append({
                    'code': f'sz{code}',
                    'name': f'深股{code}',
                    'original_code': code
                })
        
        # 深市中小板: 002000-002999, 003000-003999
        for i in range(2000, 4000):
            code = f"{i:06d}"
            if code not in seen_codes:
                seen_codes.add(code)
                all_stocks.append({
                    'code': f'sz{code}',
                    'name': f'中小{code}',
                    'original_code': code
                })
        
        # 创业板: 300000-301999
        for i in range(300000, 302000):
            code = f"{i}"
            if code not in seen_codes:
                seen_codes.add(code)
                all_stocks.append({
                    'code': f'sz{code}',
                    'name': f'创业{code}',
                    'original_code': code
                })
        
        print(f"✓ 生成了 {len(all_stocks)} 个潜在股票代码")
        print("  注意：包含未上市代码，筛选时会自动跳过无效股票")
        return all_stocks
        
    except Exception as e:
        print(f"生成代码范围失败: {e}")
    
    # 方法4: 使用预定义的股票列表
    print("\n使用预定义股票列表（包含精选活跃股票）...")
    return [
        # 沪市主板 - 金融
        {'code': 'sh600519', 'name': '贵州茅台', 'original_code': '600519'},
        {'code': 'sh600036', 'name': '招商银行', 'original_code': '600036'},
        {'code': 'sh601318', 'name': '中国平安', 'original_code': '601318'},
        {'code': 'sh600000', 'name': '浦发银行', 'original_code': '600000'},
        {'code': 'sh601166', 'name': '兴业银行', 'original_code': '601166'},
        {'code': 'sh601328', 'name': '交通银行', 'original_code': '601328'},
        {'code': 'sh600030', 'name': '中信证券', 'original_code': '600030'},
        {'code': 'sh600016', 'name': '民生银行', 'original_code': '600016'},
        {'code': 'sh601169', 'name': '北京银行', 'original_code': '601169'},
        {'code': 'sh601288', 'name': '农业银行', 'original_code': '601288'},
        # 沪市主板 - 消费
        {'code': 'sh600276', 'name': '恒瑞医药', 'original_code': '600276'},
        {'code': 'sh600887', 'name': '伊利股份', 'original_code': '600887'},
        {'code': 'sh603288', 'name': '海天味业', 'original_code': '603288'},
        {'code': 'sh600690', 'name': '海尔智家', 'original_code': '600690'},
        {'code': 'sh603259', 'name': '药明康德', 'original_code': '603259'},
        # 沪市主板 - 科技/制造
        {'code': 'sh601012', 'name': '隆基绿能', 'original_code': '601012'},
        {'code': 'sh600900', 'name': '长江电力', 'original_code': '600900'},
        {'code': 'sh601888', 'name': '中国中免', 'original_code': '601888'},
        {'code': 'sh688981', 'name': '中芯国际', 'original_code': '688981'},
        {'code': 'sh601766', 'name': '中国中车', 'original_code': '601766'},
        # 深市主板
        {'code': 'sz000001', 'name': '平安银行', 'original_code': '000001'},
        {'code': 'sz000002', 'name': '万科A', 'original_code': '000002'},
        {'code': 'sz000858', 'name': '五粮液', 'original_code': '000858'},
        {'code': 'sz000333', 'name': '美的集团', 'original_code': '000333'},
        {'code': 'sz000651', 'name': '格力电器', 'original_code': '000651'},
        {'code': 'sz000568', 'name': '泸州老窖', 'original_code': '000568'},
        {'code': 'sz000063', 'name': '中兴通讯', 'original_code': '000063'},
        {'code': 'sz000725', 'name': '京东方A', 'original_code': '000725'},
        {'code': 'sz000776', 'name': '广发证券', 'original_code': '000776'},
        # 创业板 - 新能源/科技
        {'code': 'sz300750', 'name': '宁德时代', 'original_code': '300750'},
        {'code': 'sz300059', 'name': '东方财富', 'original_code': '300059'},
        {'code': 'sz300014', 'name': '亿纬锂能', 'original_code': '300014'},
        {'code': 'sz300015', 'name': '爱尔眼科', 'original_code': '300015'},
        {'code': 'sz300760', 'name': '迈瑞医疗', 'original_code': '300760'},
        {'code': 'sz300122', 'name': '智飞生物', 'original_code': '300122'},
        {'code': 'sz300274', 'name': '阳光电源', 'original_code': '300274'},
        {'code': 'sz300957', 'name': '贝泰妮', 'original_code': '300957'},
        {'code': 'sz300433', 'name': '蓝思科技', 'original_code': '300433'},
        # 添加更多中小盘股
        {'code': 'sh600809', 'name': '山西汾酒', 'original_code': '600809'},
        {'code': 'sh600132', 'name': '重庆啤酒', 'original_code': '600132'},
        {'code': 'sh603486', 'name': '科沃斯', 'original_code': '603486'},
        {'code': 'sh603501', 'name': '韦尔股份', 'original_code': '603501'},
        {'code': 'sz002594', 'name': '比亚迪', 'original_code': '002594'},
        {'code': 'sz002475', 'name': '立讯精密', 'original_code': '002475'},
        {'code': 'sz002460', 'name': '赣锋锂业', 'original_code': '002460'},
        {'code': 'sz002415', 'name': '海康威视', 'original_code': '002415'},
        {'code': 'sz002129', 'name': '中环股份', 'original_code': '002129'},
        {'code': 'sz002371', 'name': '北方华创', 'original_code': '002371'},
    ]


def check_buy_signal(stock_code, data_days=100, recent_days=5, target_signals=['放量启动', '底背离'], match_mode='OR', require_uptrend=False):
    """
    检查股票是否有买入信号
    
    参数:
        stock_code: 股票代码，格式如 'sh600519'
        data_days: 获取多少天的历史数据用于计算指标
        recent_days: 查看最近多少天内的买入信号（1表示只看今天，5表示最近5天）
        target_signals: 目标信号列表，如 ['放量启动', '底背离']
        match_mode: 'OR' 表示满足任意一个即可，'AND' 表示必须同时满足
        require_uptrend: 是否要求当前必须处于上升趋势（EMA6 > EMA18）
    
    返回:
        dict: 包含信号信息，如果没有信号返回None
    """
    try:
        # 获取历史数据（需要足够的数据来计算指标）
        df = get_price(stock_code, frequency='1d', count=data_days)
        
        if df is None or len(df) < 50:  # 至少需要50天数据
            return None
        
        # 创建Mai指标计算器
        indicator = MaiIndicator(df)
        
        # 计算所有指标
        result = indicator.calculate_all()
        
        # 获取最新的趋势状态
        latest_signals = indicator.get_signals()
        is_uptrend = latest_signals['上升趋势']
        
        # 如果要求上升趋势，但当前不是上升趋势，直接返回None
        if require_uptrend and not is_uptrend:
            return None
        
        # 检查最近N天是否有买入信号
        recent_results = result.tail(recent_days)
        
        found_signals = []
        signal_date = None
        
        # 从最新的日期开始检查
        for i in range(len(recent_results) - 1, -1, -1):
            row = recent_results.iloc[i]
            row_date = recent_results.index[i]
            
            temp_signals = []
            
            # 检查各种信号
            if row['放量启动']:
                temp_signals.append('放量启动')
            
            if row['二浪回踩']:
                temp_signals.append('二浪回踩')
            
            if row['共振机会']:
                temp_signals.append('共振机会')
                
            if row['底背离']:
                temp_signals.append('底背离')
            
            # 根据匹配模式检查是否符合条件
            if match_mode == 'AND':
                # AND模式：必须包含所有目标信号
                has_match = all(sig in temp_signals for sig in target_signals)
            else:
                # OR模式：包含任意一个目标信号即可
                has_match = any(sig in temp_signals for sig in target_signals)
            
            # 如果找到符合条件的信号，使用最新的
            if has_match and not found_signals:
                found_signals = temp_signals
                signal_date = row_date
        
        # 如果有买入信号，返回详细信息
        if found_signals:
            latest_price = df['close'].iloc[-1]
            ema6 = latest_signals['EMA6']
            ema18 = latest_signals['EMA18']
            stop_loss = latest_signals['止损线']
            
            return {
                'price': latest_price,
                'signals': found_signals,
                'signal_date': signal_date,
                'EMA6': ema6,
                'EMA18': ema18,
                'stop_loss': stop_loss,
                'is_uptrend': is_uptrend,
                'latest_date': df.index[-1],
                'has_底背离': latest_signals['底背离'],
                'has_顶背离': latest_signals['顶背离']
            }
        
        return None
        
    except Exception as e:
        # 静默处理错误
        return None


def screen_stocks_by_mai_signal(recent_days=5, target_signals=['放量启动', '底背离'], match_mode='OR', require_uptrend=False, delay=0.1):
    """
    筛选出现Mai买入信号的股票
    
    参数:
        recent_days: 查看最近多少天内的买入信号（默认5天）
        target_signals: 目标信号列表，如 ['放量启动', '底背离']
        match_mode: 'OR' 表示满足任意一个即可，'AND' 表示必须同时满足
        require_uptrend: 是否要求当前必须处于上升趋势（EMA6 > EMA18）
        delay: 请求延迟（秒），避免请求过快
    
    返回:
        pd.DataFrame: 筛选结果
    """
    # 获取股票列表
    stock_list = get_stock_list()
    
    if not stock_list:
        print("无法获取股票列表")
        return pd.DataFrame()
    
    if match_mode == 'AND':
        signal_desc = ' + '.join(target_signals)
        condition_desc = f"同时出现 {signal_desc}"
    else:
        signal_desc = ' 或 '.join(target_signals)
        condition_desc = f"出现 {signal_desc}"
    
    if require_uptrend:
        condition_desc += " + EMA6 > EMA18（上升趋势）"
    
    print(f"\n开始筛选最近{recent_days}天内{condition_desc}的股票...")
    print(f"共需检查 {len(stock_list)} 只股票，请耐心等待...\n")
    
    results = []
    total = len(stock_list)
    
    for idx, stock in enumerate(stock_list, 1):
        code = stock['code']
        name = stock['name']
        original_code = stock['original_code']
        
        # 显示进度
        if idx % 10 == 0 or idx == 1:
            print(f"进度: {idx}/{total} ({idx/total*100:.1f}%)")
        
        # 检查买入信号
        signal_info = check_buy_signal(code, recent_days=recent_days, target_signals=target_signals, match_mode=match_mode, require_uptrend=require_uptrend)
        
        if signal_info is not None:
            # 将信号列表转为字符串
            signal_str = '+'.join(signal_info['signals'])
            
            # 判断信号强度（有底背离且有其他信号的都算强信号）
            if '共振机会' in signal_info['signals']:
                signal_strength = '⭐⭐⭐ 强烈'
            elif '底背离' in signal_info['signals'] and len(signal_info['signals']) >= 2:
                signal_strength = '⭐⭐⭐ 强烈'
            elif len(signal_info['signals']) >= 2:
                signal_strength = '⭐⭐ 较强'
            else:
                signal_strength = '⭐ 一般'
            
            results.append({
                '股票代码': original_code,
                '股票名称': name,
                '最新价': round(signal_info['price'], 2),
                'EMA6': round(signal_info['EMA6'], 2),
                'EMA18': round(signal_info['EMA18'], 2),
                '止损线': round(signal_info['stop_loss'], 2),
                '买入信号': signal_str,
                '信号强度': signal_strength,
                '信号日期': signal_info['signal_date'].strftime('%Y-%m-%d'),
                '趋势': '上升' if signal_info['is_uptrend'] else '下降',
                '更新日期': signal_info['latest_date'].strftime('%Y-%m-%d')
            })
            
            print(f"✓ 发现: {name}({original_code}) - {signal_str} {signal_strength} [{signal_info['signal_date'].strftime('%m-%d')}]")
        
        # 添加延迟，避免请求过快
        time.sleep(delay)
    
    print(f"\n筛选完成！共找到 {len(results)} 只符合条件的股票")
    
    # 转换为DataFrame并按信号强度和信号日期排序
    if results:
        df = pd.DataFrame(results)
        # 按信号强度排序（共振机会优先），然后按信号日期排序（越新越靠前）
        signal_order = {'⭐⭐⭐ 强烈': 0, '⭐⭐ 较强': 1, '⭐ 一般': 2}
        df['_sort_key'] = df['信号强度'].map(signal_order)
        df = df.sort_values(['_sort_key', '信号日期'], ascending=[True, False]).drop('_sort_key', axis=1)
        return df
    else:
        return pd.DataFrame()


def save_to_csv(df, output_dir='results'):
    """
    保存筛选结果到CSV文件
    
    参数:
        df: 筛选结果DataFrame
        output_dir: 输出目录
    """
    if df.empty:
        print("没有数据需要保存")
        return
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 生成文件名
    today = datetime.now().strftime('%Y%m%d')
    filename = f'mai_buy_signals_{today}.csv'
    filepath = os.path.join(output_dir, filename)
    
    # 保存CSV
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: {filepath}")
    
    # 同时保存一份到项目根目录
    root_filepath = f'mai_buy_signals_{today}.csv'
    df.to_csv(root_filepath, index=False, encoding='utf-8-sig')
    print(f"结果也已保存到: {root_filepath}")


def main(recent_days=5, target_signals=['放量启动', '底背离'], match_mode='OR', require_uptrend=False):
    """
    主函数
    
    参数:
        recent_days: 查看最近多少天内的买入信号（默认5天）
        target_signals: 目标信号列表
        match_mode: 'OR' 表示满足任意一个即可，'AND' 表示必须同时满足
        require_uptrend: 是否要求当前必须处于上升趋势（EMA6 > EMA18）
    """
    if match_mode == 'AND':
        signal_desc = ' + '.join(target_signals)
        condition_desc = f"同时出现 {signal_desc}"
    else:
        signal_desc = ' 或 '.join(target_signals)
        condition_desc = f"出现 {signal_desc}"
    
    if require_uptrend:
        condition_desc += " + EMA6在EMA18上方"
    
    print("=" * 70)
    print("A股Mai指标买入信号筛选器 v4.0")
    print(f"筛选条件: 最近{recent_days}天内{condition_desc}")
    print("=" * 70)
    print()
    
    # 筛选股票
    df = screen_stocks_by_mai_signal(recent_days=recent_days, target_signals=target_signals, match_mode=match_mode, require_uptrend=require_uptrend, delay=0.1)
    
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
    else:
        print(f"\n未找到最近{recent_days}天内{condition_desc}的股票")
        print("\n说明：")
        print(f"  - 当前市场在最近{recent_days}天内没有满足条件的股票")
        print("  - 可以尝试：")
        print("    1. 增加天数范围（修改 recent_days 参数）")
        print("    2. 修改信号组合（修改 target_signals 参数）")
        print("    3. 改变匹配模式（'OR' 或 'AND'）")
        print("    4. 等待市场调整后或趋势转好时再次运行")
    
    print("\n程序执行完毕！")


if __name__ == '__main__':
    main()
