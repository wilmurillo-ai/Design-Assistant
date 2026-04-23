#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
唯品会商品搜索脚本
根据关键词搜索商品列表
"""

import sys
import json
import re
import urllib.parse
import requests


def extract_json_from_jsonp(response_text, callback_name):
    """
    从JSONP响应中提取JSON数据
    :param response_text: JSONP响应文本
    :param callback_name: 回调函数名
    :return: JSON对象
    """
    # 匹配 callback_name(...) 格式
    pattern = rf'^{callback_name}\s*\(\s*(.+)\s*\)\s*$'
    match = re.match(pattern, response_text.strip(), re.DOTALL)
    
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return None
    else:
        # 尝试直接解析（可能不是JSONP格式）
        try:
            return json.loads(response_text)
        except:
            print(f"Cannot parse response as JSON or JSONP")
            return None


def search_products(keyword, page_offset=0, batch_size=120):
    """
    搜索商品
    :param keyword: 搜索关键词
    :param page_offset: 分页偏移量
    :param batch_size: 每页数量
    :return: 搜索结果
    """
    # 构建请求URL
    base_url = "https://mapi-pc.vip.com/vips-mobile/rest/shopping/pc/search/product/rank"
    
    params = {
        'callback': 'getMerchandiseIds',
        'app_name': 'shop_pc',
        'app_version': '4.0',
        'warehouse': 'VIP_NH',
        'fdc_area_id': '104104101',
        'client': 'pc',
        'mobile_platform': '1',
        'province_id': '104104',
        'api_key': '70f71280d5d547b2a7bb370a529aeea1',
        'user_id': '302134333',
        'mars_cid': '1717465638168_f77af888f9f775b14e0d8044dc768fdc',
        'wap_consumer': 'c',
        'is_default_area': '1',
        'standby_id': 'nature',
        'keyword': keyword,
        'lv3CatIds': '',
        'lv2CatIds': '',
        'lv1CatIds': '',
        'brandStoreSns': '',
        'props': '',
        'priceMin': '',
        'priceMax': '',
        'vipService': '',
        'sort': '0',
        'pageOffset': page_offset,
        'channelId': '1',
        'gPlatform': 'PC',
        'batchSize': batch_size,
        'tfs_fp_token': 'BWEc3MGHin4cCE%2BU49YWSljqu8RWoLSJp0nadQu59E7xViD%2Bt85BkIR7cTER81ke9b1wj7V8sK1MdFGD3gKbr5g%3D%3D',
        '_': '1770874412242'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.vip.com/',
        'Accept': '*/*',
    }
    
    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        # Save raw response
        with open('search_response.json', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("Raw response saved to search_response.json")
        
        # Parse JSONP
        data = extract_json_from_jsonp(response.text, 'getMerchandiseIds')
        
        if data is None:
            print("Failed to parse response")
            return None
            
        return data
        
    except requests.RequestException as e:
        print(f"Request error: {e}")
        return None


def extract_product_ids(data):
    """
    从搜索结果中提取商品ID列表
    :param data: API响应数据
    :return: 商品ID列表
    """
    if not data:
        return []
    
    # Check response code
    code = data.get('code', -1)
    if code not in [0, 1]:
        print(f"API returned error code: {code}")
        return []
    
    # Get products array
    products = data.get('data', {}).get('products', [])
    
    if not products:
        print("No products found in response")
        return []
    
    product_ids = []
    
    for product in products:
        pid = product.get('pid')
        if pid:
            product_ids.append(str(pid))
    
    # Get total count
    total = data.get('data', {}).get('total', 0)
    print(f"Total products available: {total}")
    
    return product_ids


if __name__ == "__main__":
    # Get keyword from command line
    if len(sys.argv) < 2:
        print("Usage: python query_search_products.py <keyword>")
        print("Example: python query_search_products.py nike")
        sys.exit(1)
    
    keyword = sys.argv[1]
    
    print(f"Searching for: {keyword}")
    print("="*50)
    
    # Search products
    data = search_products(keyword)
    
    if data:
        # Extract product IDs
        product_ids = extract_product_ids(data)
        
        if product_ids:
            print(f"\n=== Search Results ===")
            print(f"Keyword: {keyword}")
            print(f"Products found: {len(product_ids)}")
            print(f"\nProduct ID list: {product_ids[:10]}{'...' if len(product_ids) > 10 else ''}")
            
            # Print first 5 product IDs
            print(f"\nTop 5 Product IDs:")
            for i, pid in enumerate(product_ids[:5], 1):
                print(f"  [{i}] {pid}")
            
            # Save results
            result = {
                'keyword': keyword,
                'totalProducts': len(product_ids),
                'productIds': product_ids
            }
            
            with open('search_products.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"\nKey info saved to search_products.json")
            print(f"\nUse these product IDs to analyze with vipshop-product-consultant:")
            print(f"  {product_ids[:5]}")
            print("\nSearch completed successfully!")
            sys.exit(0)
        else:
            print("No products found")
            sys.exit(1)
    else:
        print("Search failed")
        sys.exit(1)
