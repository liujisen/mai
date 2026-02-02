# -*- coding: utf-8 -*-
"""
测试新浪API返回的数据
"""

import requests
import json

print("测试新浪财经API...")

url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
params = {
    'page': 1,
    'num': 20,
    'sort': 'symbol',
    'asc': 1,
    'node': 'hs_a',
    'symbol': '',
    '_s_r_a': 'page'
}

response = requests.get(url, params=params, timeout=10)
data = json.loads(response.text)

print(f"\n返回数据数量: {len(data)}")
print(f"\n前5条数据:")
for i, item in enumerate(data[:5], 1):
    print(f"{i}. {item}")
