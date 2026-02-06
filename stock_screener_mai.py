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
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from Ashare import get_price
from mai_indicator import MaiIndicator


# ========== 基本面数据获取函数 ==========

def get_fundamental_data(stock_code):
    """
    获取股票基本面数据（市值、价格、ST标识等）
    
    参数:
        stock_code: 股票代码，格式如 'sh600519' 或 '600519'
    
    返回:
        dict: 包含基本面数据，失败返回None
    """
    try:
        # 提取纯数字代码
        if stock_code.startswith('sh') or stock_code.startswith('sz'):
            pure_code = stock_code[2:]
        else:
            pure_code = stock_code
        
        # 尝试使用akshare获取实时数据
        try:
            import akshare as ak
            
            # 获取实时行情
            df_realtime = ak.stock_zh_a_spot_em()
            stock_data = df_realtime[df_realtime['代码'] == pure_code]
            
            if len(stock_data) > 0:
                row = stock_data.iloc[0]
                
                # 提取关键数据
                name = row['名称']
                price = float(row['最新价'])
                market_cap = float(row['总市值']) if '总市值' in row else 0  # 单位：元
                circulating_market_cap = float(row['流通市值']) if '流通市值' in row else 0
                
                # 判断是否ST股
                is_st = 'ST' in name or 'st' in name or '*' in name
                
                return {
                    'code': pure_code,
                    'name': name,
                    'price': price,
                    'market_cap': market_cap,
                    'circulating_market_cap': circulating_market_cap,
                    'is_st': is_st,
                }
        except ImportError:
            pass
        except Exception:
            pass
        
        # 备用方案：从东方财富获取
        try:
            url = f'http://push2.eastmoney.com/api/qt/stock/get?secid={get_secid(stock_code)}&fields=f57,f58,f43,f60,f116,f117'
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data and 'data' in data and data['data']:
                info = data['data']
                name = info.get('f58', '')
                price = info.get('f43', 0) / 100.0  # 价格单位转换
                circulating_market_cap = info.get('f116', 0)  # 流通市值（万元）
                market_cap = info.get('f117', 0)  # 总市值（万元）
                
                is_st = 'ST' in name or 'st' in name or '*' in name
                
                return {
                    'code': pure_code,
                    'name': name,
                    'price': price,
                    'market_cap': market_cap * 10000,  # 转换为元
                    'circulating_market_cap': circulating_market_cap * 10000,
                    'is_st': is_st,
                }
        except Exception:
            pass
        
        return None
        
    except Exception:
        return None


def get_secid(stock_code):
    """将股票代码转换为东方财富的secid格式"""
    if stock_code.startswith('sh') or stock_code.startswith('6'):
        code = stock_code[2:] if stock_code.startswith('sh') else stock_code
        return f'1.{code}'
    else:
        code = stock_code[2:] if stock_code.startswith('sz') else stock_code
        return f'0.{code}'


def apply_fundamental_filters(stock_code, stock_name, price, fundamental_config=None):
    """
    应用基本面筛选条件
    
    参数:
        stock_code: 股票代码
        stock_name: 股票名称
        price: 当前价格
        fundamental_config: 筛选配置字典
    
    返回:
        tuple: (是否通过筛选, 不通过原因)
    """
    if fundamental_config is None:
        fundamental_config = {
            'enable': True,
            'min_price': 3.0,        # 最低价格
            'max_price': 200.0,      # 最高价格
            'min_market_cap': 30e8,  # 最小流通市值（30亿）
            'max_market_cap': 500e8, # 最大流通市值（500亿）
            'exclude_st': True,      # 排除ST股
        }
    
    if not fundamental_config.get('enable', True):
        return True, None
    
    # 1. 价格筛选
    min_price = fundamental_config.get('min_price', 3.0)
    max_price = fundamental_config.get('max_price', 200.0)
    if price < min_price:
        return False, f"价格过低({price:.2f}<{min_price})"
    if price > max_price:
        return False, f"价格过高({price:.2f}>{max_price})"
    
    # 2. 获取基本面数据
    fundamental = get_fundamental_data(stock_code)
    if fundamental is None:
        # 如果无法获取基本面数据，只进行简单筛选
        if fundamental_config.get('exclude_st', True):
            if 'ST' in stock_name or 'st' in stock_name or '*' in stock_name:
                return False, "ST股票"
        return True, None
    
    # 3. ST股筛选
    if fundamental_config.get('exclude_st', True):
        if fundamental['is_st']:
            return False, "ST股票"
    
    # 4. 市值筛选
    circulating_cap = fundamental['circulating_market_cap']
    if circulating_cap > 0:
        min_cap = fundamental_config.get('min_market_cap', 30e8)
        max_cap = fundamental_config.get('max_market_cap', 500e8)
        
        if circulating_cap < min_cap:
            return False, f"市值过小({circulating_cap/1e8:.1f}亿<{min_cap/1e8:.0f}亿)"
        if circulating_cap > max_cap:
            return False, f"市值过大({circulating_cap/1e8:.1f}亿>{max_cap/1e8:.0f}亿)"
    
    return True, None


def get_stock_list():
    """
    获取所有A股股票代码列表（主板、创业板、科创板）
    优先使用akshare库获取
    """
    print("正在获取A股全部股票列表...")
    all_stocks = []
    seen_codes = set()  # 用于去重
    
    # 方法2: 优先尝试使用akshare获取（如果已安装）
    try:
        print("方法2: 尝试使用akshare库获取...")
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
        print("  akshare未安装，尝试其他方法")
    except Exception as e:
        print(f"  akshare获取失败: {e}，尝试其他方法")
    
    # 方法1: 尝试从东方财富获取
    try:
        print("\n方法1: 从东方财富API获取全部A股...")
        
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


def check_buy_signal(stock_code, data_days=60, recent_days=5, target_signals=['放量启动', '底背离'], 
                     match_mode='OR', require_uptrend=False, use_enhanced=True, fundamental_config=None):
    """
    检查股票是否有买入信号
    
    参数:
        stock_code: 股票代码，格式如 'sh600519'
        data_days: 获取多少天的历史数据用于计算指标（优化：从100改为60）
        recent_days: 查看最近多少天内的买入信号（1表示只看今天，5表示最近5天）
        target_signals: 目标信号列表，如 ['放量启动', '底背离']
        match_mode: 'OR' 表示满足任意一个即可，'AND' 表示必须同时满足
        require_uptrend: 是否要求当前必须处于上升趋势（EMA6 > EMA18）
        use_enhanced: 是否使用增强版指标（包含OBV、量比等）
        fundamental_config: 基本面筛选配置，None表示使用默认配置
    
    返回:
        dict: 包含信号信息，如果没有信号返回None
    """
    try:
        # 获取历史数据（需要足够的数据来计算指标）
        df = get_price(stock_code, frequency='1d', count=data_days)
        
        if df is None or len(df) < 50:  # 至少需要50天数据
            return None
        
        # 获取股票名称和最新价格
        latest_price = df['close'].iloc[-1]
        stock_name = stock_code  # 默认使用代码作为名称
        
        # 应用基本面筛选（如果启用）
        if fundamental_config is None or fundamental_config.get('enable', True):
            passed, reason = apply_fundamental_filters(stock_code, stock_name, latest_price, fundamental_config)
            if not passed:
                # 基本面筛选不通过，直接返回None
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
            # 如果使用增强版，优先检查增强版信号
            if use_enhanced and '放量启动' in target_signals:
                if row['放量启动_增强']:
                    temp_signals.append('放量启动_增强')
                elif row['放量启动']:
                    temp_signals.append('放量启动')
            else:
                if row['放量启动']:
                    temp_signals.append('放量启动')
            
            if row['二浪回踩']:
                temp_signals.append('二浪回踩')
            
            if row['共振机会']:
                temp_signals.append('共振机会')
                
            if row['底背离']:
                temp_signals.append('底背离')
            
            # 增强版特有信号
            if use_enhanced:
                if row['隐蔽吸筹']:
                    temp_signals.append('隐蔽吸筹')
                if row['极限收敛']:
                    temp_signals.append('极限收敛')
            
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
            
            signal_info = {
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
            
            # 添加增强版指标信息
            if use_enhanced:
                signal_info.update({
                    'OBV向上': latest_signals['OBV向上'],
                    '量比': latest_signals['量比'],
                    '温和放量': latest_signals['温和放量'],
                    'MA18向上': latest_signals['MA18向上'],
                    '隐蔽吸筹': latest_signals['隐蔽吸筹'],
                    '极限收敛': latest_signals['极限收敛'],
                })
            
            return signal_info
        
        return None
        
    except Exception as e:
        # 静默处理错误
        return None


def screen_stocks_by_mai_signal(recent_days=5, target_signals=['放量启动', '底背离'], match_mode='OR', 
                               require_uptrend=False, delay=0.1, use_enhanced=True, fundamental_config=None):
    """
    筛选出现Mai买入信号的股票
    
    参数:
        recent_days: 查看最近多少天内的买入信号（默认5天）
        target_signals: 目标信号列表，如 ['放量启动', '底背离']
        match_mode: 'OR' 表示满足任意一个即可，'AND' 表示必须同时满足
        require_uptrend: 是否要求当前必须处于上升趋势（EMA6 > EMA18）
        delay: 请求延迟（秒），避免请求过快
        use_enhanced: 是否使用增强版指标（包含OBV、量比等）
        fundamental_config: 基本面筛选配置
    
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
        signal_info = check_buy_signal(code, recent_days=recent_days, target_signals=target_signals, 
                                      match_mode=match_mode, require_uptrend=require_uptrend,
                                      use_enhanced=use_enhanced, fundamental_config=fundamental_config)
        
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
            
            result_dict = {
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
            }
            
            # 添加增强版指标列
            if use_enhanced and 'OBV向上' in signal_info:
                result_dict['OBV向上'] = '✓' if signal_info['OBV向上'] else '✗'
                result_dict['量比'] = round(signal_info['量比'], 2)
                result_dict['温和放量'] = '✓' if signal_info['温和放量'] else '✗'
                result_dict['MA18向上'] = '✓' if signal_info['MA18向上'] else '✗'
            
            results.append(result_dict)
            
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


def _process_single_stock(args):
    """
    处理单只股票的辅助函数（用于多进程）
    
    参数:
        args: 元组，包含 (stock_dict, recent_days, target_signals, match_mode, require_uptrend, use_enhanced, fundamental_config)
    
    返回:
        tuple: (stock_dict, signal_info) 或 None
    """
    stock, recent_days, target_signals, match_mode, require_uptrend, use_enhanced, fundamental_config = args
    
    code = stock['code']
    
    # 检查买入信号
    signal_info = check_buy_signal(
        code, 
        recent_days=recent_days, 
        target_signals=target_signals, 
        match_mode=match_mode, 
        require_uptrend=require_uptrend,
        use_enhanced=use_enhanced, 
        fundamental_config=fundamental_config
    )
    
    if signal_info is not None:
        return (stock, signal_info)
    return None


def screen_stocks_by_mai_signal_parallel(recent_days=5, target_signals=['放量启动', '底背离'], match_mode='OR', 
                                        require_uptrend=False, use_enhanced=True, fundamental_config=None, 
                                        num_workers=None):
    """
    筛选出现Mai买入信号的股票（多进程并行版本，速度提升3-4倍）
    
    参数:
        recent_days: 查看最近多少天内的买入信号（默认5天）
        target_signals: 目标信号列表，如 ['放量启动', '底背离']
        match_mode: 'OR' 表示满足任意一个即可，'AND' 表示必须同时满足
        require_uptrend: 是否要求当前必须处于上升趋势（EMA6 > EMA18）
        use_enhanced: 是否使用增强版指标（包含OBV、量比等）
        fundamental_config: 基本面筛选配置
        num_workers: 进程数，默认为CPU核心数-1
    
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
    
    # 确定进程数
    if num_workers is None:
        num_workers = max(1, cpu_count() - 1)  # 留一个核心给系统
    
    print(f"\n开始筛选最近{recent_days}天内{condition_desc}的股票...")
    print(f"共需检查 {len(stock_list)} 只股票")
    print(f"🚀 使用多进程并行（{num_workers}个进程），预计速度提升3-4倍！\n")
    
    results = []
    total = len(stock_list)
    completed = 0
    
    # 准备参数列表
    tasks = [
        (stock, recent_days, target_signals, match_mode, require_uptrend, use_enhanced, fundamental_config)
        for stock in stock_list
    ]
    
    # 使用进程池并行处理
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # 提交所有任务
        future_to_stock = {executor.submit(_process_single_stock, task): task[0] for task in tasks}
        
        # 处理完成的任务
        for future in as_completed(future_to_stock):
            completed += 1
            
            # 每50个显示一次进度
            if completed % 50 == 0 or completed == 1:
                print(f"进度: {completed}/{total} ({completed/total*100:.1f}%)")
            
            try:
                result = future.result()
                if result is not None:
                    stock, signal_info = result
                    name = stock['name']
                    original_code = stock['original_code']
                    
                    # 将信号列表转为字符串
                    signal_str = '+'.join(signal_info['signals'])
                    
                    # 判断信号强度
                    if '共振机会' in signal_info['signals']:
                        signal_strength = '⭐⭐⭐ 强烈'
                    elif '底背离' in signal_info['signals'] and len(signal_info['signals']) >= 2:
                        signal_strength = '⭐⭐⭐ 强烈'
                    elif len(signal_info['signals']) >= 2:
                        signal_strength = '⭐⭐ 较强'
                    else:
                        signal_strength = '⭐ 一般'
                    
                    result_dict = {
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
                    }
                    
                    # 添加增强版指标列
                    if use_enhanced and 'OBV向上' in signal_info:
                        result_dict['OBV向上'] = '✓' if signal_info['OBV向上'] else '✗'
                        result_dict['量比'] = round(signal_info['量比'], 2)
                        result_dict['温和放量'] = '✓' if signal_info['温和放量'] else '✗'
                        result_dict['MA18向上'] = '✓' if signal_info['MA18向上'] else '✗'
                    
                    results.append(result_dict)
                    
                    print(f"✓ 发现: {name}({original_code}) - {signal_str} {signal_strength} [{signal_info['signal_date'].strftime('%m-%d')}]")
            
            except Exception as e:
                # 静默处理错误
                pass
    
    print(f"\n筛选完成！共找到 {len(results)} 只符合条件的股票")
    
    # 转换为DataFrame并按信号强度和信号日期排序
    if results:
        df = pd.DataFrame(results)
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


def main(recent_days=5, target_signals=['放量启动', '底背离'], match_mode='OR', require_uptrend=False, 
         use_enhanced=True, fundamental_config=None, use_parallel=True, num_workers=None):
    """
    主函数
    
    参数:
        recent_days: 查看最近多少天内的买入信号（默认5天）
        target_signals: 目标信号列表
        match_mode: 'OR' 表示满足任意一个即可，'AND' 表示必须同时满足
        require_uptrend: 是否要求当前必须处于上升趋势（EMA6 > EMA18）
        use_enhanced: 是否使用增强版指标（包含OBV、量比等）
        fundamental_config: 基本面筛选配置
        use_parallel: 是否使用多进程并行（默认True，速度提升3-4倍）
        num_workers: 进程数，默认为CPU核心数-1
    """
    if match_mode == 'AND':
        signal_desc = ' + '.join(target_signals)
        condition_desc = f"同时出现 {signal_desc}"
    else:
        signal_desc = ' 或 '.join(target_signals)
        condition_desc = f"出现 {signal_desc}"
    
    if require_uptrend:
        condition_desc += " + EMA6在EMA18上方"
    
    version = "v5.0" if use_enhanced else "v4.0"
    version += " [多进程优化]" if use_parallel else ""
    print("=" * 70)
    print(f"A股Mai指标买入信号筛选器 {version}")
    if use_enhanced:
        print("【增强版】包含: OBV能量潮 + 量比分析 + 基本面筛选")
    if use_parallel:
        workers = num_workers if num_workers else max(1, cpu_count() - 1)
        print(f"【性能优化】多进程并行({workers}核) + 数据天数优化(60天)")
    print(f"筛选条件: 最近{recent_days}天内{condition_desc}")
    print("=" * 70)
    print()
    
    # 筛选股票（选择串行或并行版本）
    if use_parallel:
        df = screen_stocks_by_mai_signal_parallel(
            recent_days=recent_days, 
            target_signals=target_signals, 
            match_mode=match_mode, 
            require_uptrend=require_uptrend, 
            use_enhanced=use_enhanced, 
            fundamental_config=fundamental_config,
            num_workers=num_workers
        )
    else:
        df = screen_stocks_by_mai_signal(
            recent_days=recent_days, 
            target_signals=target_signals, 
            match_mode=match_mode, 
            require_uptrend=require_uptrend, 
            delay=0.1, 
            use_enhanced=use_enhanced, 
            fundamental_config=fundamental_config
        )
    
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
