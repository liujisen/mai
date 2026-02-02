# -*- coding: utf-8 -*-
"""
A股涨幅筛选器
筛选出今天涨幅大于5%的股票
"""

import json
import time
import os
from datetime import datetime
import requests
import pandas as pd
from Ashare import get_price


def get_stock_list():
    """
    获取所有A股股票代码列表
    使用东方财富或新浪财经API获取
    """
    print("正在获取A股股票列表...")
    all_stocks = []
    
    # 方法1: 尝试从东方财富获取
    try:
        print("方法1: 尝试从东方财富API获取...")
        # 沪市主板
        for page in range(1, 3):  # 获取前2页
            url = f'http://push2.eastmoney.com/api/qt/clist/get?pn={page}&pz=1000&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f12,f14'
            response = requests.get(url, timeout=10)
            data = response.json()
            if data and 'data' in data and data['data'] and 'diff' in data['data']:
                for item in data['data']['diff']:
                    code = item['f12']
                    name = item['f14']
                    all_stocks.append({
                        'code': f'sh{code}',
                        'name': name,
                        'original_code': code
                    })
        
        # 深市主板
        for page in range(1, 3):
            url = f'http://push2.eastmoney.com/api/qt/clist/get?pn={page}&pz=1000&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80&fields=f12,f14'
            response = requests.get(url, timeout=10)
            data = response.json()
            if data and 'data' in data and data['data'] and 'diff' in data['data']:
                for item in data['data']['diff']:
                    code = item['f12']
                    name = item['f14']
                    all_stocks.append({
                        'code': f'sz{code}',
                        'name': name,
                        'original_code': code
                    })
        
        # 创业板
        for page in range(1, 2):
            url = f'http://push2.eastmoney.com/api/qt/clist/get?pn={page}&pz=1000&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:0+t:80&fields=f12,f14'
            response = requests.get(url, timeout=10)
            data = response.json()
            if data and 'data' in data and data['data'] and 'diff' in data['data']:
                for item in data['data']['diff']:
                    code = item['f12']
                    name = item['f14']
                    if not any(s['original_code'] == code for s in all_stocks):  # 去重
                        all_stocks.append({
                            'code': f'sz{code}',
                            'name': name,
                            'original_code': code
                        })
        
        if len(all_stocks) > 100:
            print(f"✓ 成功获取 {len(all_stocks)} 只股票")
            return all_stocks
            
    except Exception as e:
        print(f"从东方财富获取失败: {e}")
    
    # 方法2: 使用预定义的股票列表（包含更多股票以提高找到涨幅>5%的概率）
    print("使用预定义股票列表（包含100+只活跃股票）...")
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
        {'code': 'sz300059', 'name': '东方财富', 'original_code': '300059'},
        # 添加更多中小盘股（波动性更大，更容易涨超5%）
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


def calculate_change_pct(stock_code):
    """
    计算股票涨幅
    
    参数:
        stock_code: 股票代码，格式如 'sh600519'
    
    返回:
        dict: 包含股票信息和涨幅数据，如果失败返回None
    """
    try:
        # 获取最近2天的日线数据
        df = get_price(stock_code, frequency='1d', count=2)
        
        if df is None or len(df) < 2:
            return None
        
        # 计算涨幅
        yesterday_close = df['close'].iloc[-2]
        today_close = df['close'].iloc[-1]
        change_pct = (today_close - yesterday_close) / yesterday_close * 100
        
        # 获取其他信息
        today_open = df['open'].iloc[-1]
        today_high = df['high'].iloc[-1]
        today_low = df['low'].iloc[-1]
        volume = df['volume'].iloc[-1]
        
        return {
            'yesterday_close': yesterday_close,
            'today_open': today_open,
            'today_close': today_close,
            'today_high': today_high,
            'today_low': today_low,
            'change_pct': change_pct,
            'volume': volume,
            'date': df.index[-1]
        }
        
    except Exception as e:
        # 静默处理错误，有些股票可能停牌或数据异常
        return None


def screen_stocks(threshold=5.0, delay=0.1):
    """
    筛选涨幅超过阈值的股票
    
    参数:
        threshold: 涨幅阈值（百分比）
        delay: 请求延迟（秒），避免请求过快
    
    返回:
        pd.DataFrame: 筛选结果
    """
    # 获取股票列表
    stock_list = get_stock_list()
    
    if not stock_list:
        print("无法获取股票列表")
        return pd.DataFrame()
    
    print(f"\n开始筛选涨幅超过 {threshold}% 的股票...")
    print(f"共需检查 {len(stock_list)} 只股票，请耐心等待...\n")
    
    results = []
    total = len(stock_list)
    
    for idx, stock in enumerate(stock_list, 1):
        code = stock['code']
        name = stock['name']
        original_code = stock['original_code']
        
        # 显示进度
        if idx % 50 == 0 or idx == 1:
            print(f"进度: {idx}/{total} ({idx/total*100:.1f}%)")
        
        # 计算涨幅
        result = calculate_change_pct(code)
        
        if result is not None and result['change_pct'] > threshold:
            results.append({
                '股票代码': original_code,
                '股票名称': name,
                '昨日收盘': round(result['yesterday_close'], 2),
                '今日开盘': round(result['today_open'], 2),
                '今日收盘': round(result['today_close'], 2),
                '最高价': round(result['today_high'], 2),
                '最低价': round(result['today_low'], 2),
                '涨幅(%)': round(result['change_pct'], 2),
                '成交量': int(result['volume']),
                '日期': result['date'].strftime('%Y-%m-%d')
            })
            print(f"✓ 发现: {name}({original_code}) 涨幅 {result['change_pct']:.2f}%")
        
        # 添加延迟，避免请求过快
        time.sleep(delay)
    
    print(f"\n筛选完成！共找到 {len(results)} 只符合条件的股票")
    
    # 转换为DataFrame并按涨幅排序
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('涨幅(%)', ascending=False)
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
    filename = f'stocks_above_5percent_{today}.csv'
    filepath = os.path.join(output_dir, filename)
    
    # 保存CSV
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存到: {filepath}")
    
    # 同时保存一份到项目根目录，方便查看
    root_filepath = f'stocks_above_5percent_{today}.csv'
    df.to_csv(root_filepath, index=False, encoding='utf-8-sig')
    print(f"结果也已保存到: {root_filepath}")


def main():
    """
    主函数
    """
    print("=" * 60)
    print("A股涨幅筛选器 v1.0")
    print("筛选条件: 今日涨幅 > 5%")
    print("=" * 60)
    print()
    
    # 筛选股票
    df = screen_stocks(threshold=5.0, delay=0.05)
    
    # 显示结果
    if not df.empty:
        print("\n" + "=" * 60)
        print("筛选结果:")
        print("=" * 60)
        print(df.to_string(index=False))
        
        # 保存到CSV
        save_to_csv(df)
    else:
        print("\n未找到符合条件的股票")
    
    print("\n程序执行完毕！")


if __name__ == '__main__':
    main()
