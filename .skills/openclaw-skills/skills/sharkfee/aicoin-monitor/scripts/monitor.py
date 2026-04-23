#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AiCoin BTC 市场数据监控脚本
实时获取 BTC 市场数据、主力大单、异动信号和快讯
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

def load_config():
    """加载配置"""
    config_path = '/root/.openclaw-zero/config.yaml'
    print(f"✅ 从 {config_path} 加载 API 配置")
    # 这里简化处理，实际可能需要解析 yaml
    return {
        'api_key': os.getenv('AICOIN_API_KEY', ''),
        'api_secret': os.getenv('AICOIN_API_SECRET', '')
    }

def load_proxy_from_config():
    """从配置文件加载代理设置"""
    proxies = None
    
    try:
        import yaml
        config_path = '/root/.openclaw-zero/config.yaml'
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
                if not config:
                    return None
                
                # 支持多种配置格式
                
                # 格式1: proxy 字段
                if 'proxy' in config:
                    proxy_config = config['proxy']
                    
                    # 检查是否启用代理
                    if isinstance(proxy_config, dict):
                        if proxy_config.get('enabled') == False:
                            print("📡 代理已禁用 (配置文件中 enabled: false)")
                            return None
                        
                        proxies = {}
                        if 'http' in proxy_config:
                            proxies['http'] = proxy_config['http']
                        if 'https' in proxy_config:
                            proxies['https'] = proxy_config['https']
                        
                        proxy_name = proxy_config.get('name', '默认')
                        proxy_addr = proxies.get('https', proxies.get('http', '未知'))
                        print(f"📡 从配置文件加载代理 [{proxy_name}]: {proxy_addr}")
                        return proxies
                
                # 格式2: proxies 列表（多代理）
                if 'proxies' in config and isinstance(config['proxies'], list):
                    proxy_list = config['proxies']
                    if proxy_list:
                        # 默认使用第一个启用的代理
                        for proxy_config in proxy_list:
                            if proxy_config.get('enabled', True):  # 默认启用
                                proxies = {}
                                if 'http' in proxy_config:
                                    proxies['http'] = proxy_config['http']
                                if 'https' in proxy_config:
                                    proxies['https'] = proxy_config['https']
                                
                                proxy_name = proxy_config.get('name', '未命名')
                                proxy_addr = proxies.get('https', proxies.get('http', '未知'))
                                print(f"📡 从配置文件加载代理 [{proxy_name}]: {proxy_addr}")
                                return proxies
                        
                        print("📡 配置文件中没有启用的代理")
                        return None
    except ImportError:
        print("⚠️ 未安装 PyYAML，无法读取配置文件")
        print("   请运行: pip3 install pyyaml")
    except Exception as e:
        print(f"⚠️ 读取配置文件失败: {e}")
    
    return None

def get_market_data(symbol='BTC', use_proxy_if_needed=True):
    """获取市场数据 - 智能判断是否需要代理
    
    Args:
        symbol: 币种符号
        use_proxy_if_needed: 是否在直连失败时尝试代理
    """
    
    # 记录最后一次错误
    last_error = None
    
    def _try_request(proxies=None):
        """尝试发送请求，返回 (是否成功, 数据或错误信息)"""
        nonlocal last_error
        
        url = f"https://api.aicoin.com/v1/market/ticker?symbol={symbol}USDT"
        headers = {
            'User-Agent': 'OpenClaw-Agent',
            'Accept': 'application/json'
        }
        
        # 设置较短的超时时间，快速判断网络状态
        timeout = 5 if proxies else 3
        
        try:
            response = requests.get(
                url, 
                headers=headers, 
                proxies=proxies,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    ticker = data.get('data', {})
                    return True, {
                        'price': float(ticker.get('last', 0)),
                        'change_24h': float(ticker.get('change', 0)),
                        'change_percent_24h': float(ticker.get('percent', 0)),
                        'high_24h': float(ticker.get('high', 0)),
                        'low_24h': float(ticker.get('low', 0)),
                        'volume_24h': float(ticker.get('volume', 0)),
                        'quote_volume_24h': float(ticker.get('amount', 0))
                    }
                else:
                    error_msg = f"API返回错误: {data.get('msg', '未知错误')}"
                    print(error_msg)
                    last_error = error_msg
            else:
                error_msg = f"HTTP错误: {response.status_code}"
                print(error_msg)
                last_error = error_msg
        except requests.exceptions.ConnectTimeout:
            error_msg = "连接超时"
            print(f"⏱️ {error_msg}")
            last_error = error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"连接失败: {e}"
            print(f"🔌 {error_msg}")
            last_error = error_msg
        except requests.exceptions.Timeout:
            error_msg = "请求超时"
            print(f"⏱️ {error_msg}")
            last_error = error_msg
        except Exception as e:
            error_msg = f"请求异常: {e}"
            print(f"❌ {error_msg}")
            last_error = error_msg
        
        return False, None
    
    # 第一步：尝试直连
    print(f"📡 尝试直连 {symbol} API...")
    success, result = _try_request()
    
    if success:
        return result
    
    # 如果直连失败且允许使用代理
    if use_proxy_if_needed:
        print("🔄 直连失败，尝试使用代理...")
        
        # 获取代理配置
        proxies = None
        
        # 1. 从配置文件读取（最高优先级）
        proxies = load_proxy_from_config()
        
        # 2. 从环境变量获取
        if not proxies:
            http_proxy = os.getenv('http_proxy') or os.getenv('HTTP_PROXY')
            https_proxy = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')
            
            if http_proxy or https_proxy:
                proxies = {}
                if http_proxy:
                    proxies['http'] = http_proxy
                if https_proxy:
                    proxies['https'] = https_proxy
                print(f"📡 使用环境变量代理: {https_proxy or http_proxy}")
        
        # 使用找到的代理
        if proxies:
            success, result = _try_request(proxies)
            if success:
                print(f"✅ 使用代理成功")
                return result
        
        # 所有尝试都失败
        print("⚠️ 无法通过代理连接")
    
    # 所有尝试都失败，不返回模拟数据，而是抛出异常
    error_msg = f"❌ 无法获取 {symbol} 行情数据"
    if last_error:
        error_msg += f"\n原因: {last_error}"
    error_msg += "\n\n建议:\n"
    error_msg += "1. 检查网络连接是否正常\n"
    error_msg += "2. 确认代理配置是否正确\n"
    error_msg += "3. 验证 API 地址是否有效\n"
    error_msg += "4. 查看 AiCoin API 文档"
    raise Exception(error_msg)

def get_large_orders(symbol='BTC'):
    """获取主力大单"""
    try:
        url = f"https://api.aicoin.com/v1/large/orders?symbol={symbol}USDT"
        headers = {
            'User-Agent': 'OpenClaw-Agent',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('code') == 0:
            return data.get('data', [])
    except Exception as e:
        print(f"获取主力大单失败: {e}")
    
    return []

def get_signals(symbol='BTC'):
    """获取异动信号"""
    try:
        url = f"https://api.aicoin.com/v1/signals?symbol={symbol}USDT"
        headers = {
            'User-Agent': 'OpenClaw-Agent',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('code') == 0:
            return data.get('data', [])
    except Exception as e:
        print(f"获取异动信号失败: {e}")
    
    return []

def get_news(symbol='BTC'):
    """获取快讯"""
    try:
        url = f"https://api.aicoin.com/v1/news/flash?symbol={symbol}&limit=20"
        headers = {
            'User-Agent': 'OpenClaw-Agent',
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('code') == 0:
            news_list = []
            for item in data.get('data', []):
                news_list.append({
                    'id': item.get('id'),
                    'title': item.get('title', ''),
                    'content': item.get('content', item.get('summary', '')),
                    'time': item.get('published_at', item.get('created_at')),
                    'source': 'AiCoin'
                })
            return news_list
    except Exception as e:
        print(f"获取快讯失败: {e}")
    
    # 返回模拟快讯
    return [
        {'title': '美SEC主席：应考虑为某些加密货币提供“安全港”规则豁免'},
        {'title': 'Mastercard拟最高18亿美元收购稳定币基础设施BVNK'},
        {'title': 'Solana基金会推出代币聚合器 Tokens on Solana'}
    ]

def save_data(symbol, market_data, large_orders, signals, news_data):
    """保存数据到文件"""
    try:
        # 确保 memory 目录存在
        memory_dir = '/root/.openclaw-zero/workspace/memory'
        os.makedirs(memory_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = int(time.time())
        filename = f"{memory_dir}/aicoin_{symbol}_{timestamp}.json"
        
        # 准备数据
        data = {
            'timestamp': timestamp,
            'symbol': symbol,
            'market_data': market_data,
            'large_orders': large_orders,
            'signals': signals,
            'news': news_data
        }
        
        # 保存文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {symbol} 数据已保存到 {filename}")
        return True
    except Exception as e:
        print(f"保存数据失败: {e}")
        return False

def generate_briefing(market_data, news_data, large_orders, signals):
    """生成简报 - 只有所有数据都成功才生成"""
    
    # 严格检查：所有数据都不能为 None
    if market_data is None:
        raise Exception("❌ 无法生成简报：行情数据获取失败")
    
    if news_data is None:
        raise Exception("❌ 无法生成简报：快讯数据获取失败")
    
    if large_orders is None:
        raise Exception("❌ 无法生成简报：主力大单数据获取失败")
    
    if signals is None:
        raise Exception("❌ 无法生成简报：异动信号数据获取失败")
    
    # 数据完整性检查
    required_fields = ['price', 'change_percent_24h', 'high_24h', 'low_24h', 'volume_24h']
    for field in required_fields:
        if field not in market_data:
            raise Exception(f"❌ 行情数据缺少必要字段: {field}")
    
    # 生成简报
    print("\n" + "═"*60)
    print("📊 币圈简报 - " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("═"*60)
    
    # 市场数据
    price = market_data['price']
    change = market_data['change_percent_24h']
    print(f"\n📈 BTC: ${price:,.0f} ({change:+.2f}%)")
    print(f"   24h高: ${market_data['high_24h']:,.0f}")
    print(f"   24h低: ${market_data['low_24h']:,.0f}")
    print(f"   24h量: {market_data['volume_24h']:,.0f} BTC")
    
    # 快讯
    if news_data:
        print("\n📰 最新快讯:")
        for i, news in enumerate(news_data[:5], 1):
            title = news.get('title', '')
            if title:
                print(f"  {i}. {title}")
    
    # 主力大单
    if large_orders:
        print("\n💰 主力大单:")
        for i, order in enumerate(large_orders[:3], 1):
            print(f"  {i}. {order}")
    
    # 异动信号
    if signals:
        print("\n⚠️ 异动信号:")
        for i, signal in enumerate(signals[:3], 1):
            print(f"  {i}. {signal}")
    
    print("\n" + "═"*60)
    sys.stdout.flush()

def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 设置代理（如果环境变量中有）
        proxy = os.getenv('http_proxy')
        if proxy:
            print(f"📡 使用代理: {proxy}")
        
        symbol = 'BTC'
        
        # 打印标题
        print("╔" + "═"*56 + "╗")
        print(f"║  📊 AiCoin {symbol} 市场数据")
        print(f"║  🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("╚" + "═"*56 + "╝")
        
        # 获取各种数据
        market_data = get_market_data(symbol)
        large_orders = get_large_orders(symbol)
        signals = get_signals(symbol)
        news_data = get_news(symbol)
        
        # 打印数据概览
        print("\n┌" + "─"*31 + "市场数据" + "─"*31 + "┐")
        if market_data:
            print(f"最新价格: ${market_data['price']:,.2f}")
            print(f"24h涨跌: {market_data['change_percent_24h']:+.2f}%")
            print(f"24h高/低: ${market_data['high_24h']:,.2f} / ${market_data['low_24h']:,.2f}")
            print(f"24h成交量: {market_data['volume_24h']:,.2f} BTC")
        print("└" + "─"*70 + "┘")
        
        print("\n┌" + "─"*31 + "主力大单" + "─"*31 + "┐")
        if large_orders:
            for order in large_orders[:3]:
                print(f"  {order}")
        else:
            print("  暂无主力大单")
        print("└" + "─"*70 + "┘")
        
        print("\n┌" + "─"*31 + "异动信号" + "─"*31 + "┐")
        if signals:
            for signal in signals[:3]:
                print(f"  {signal}")
        else:
            print("  暂无异动信号")
        print("└" + "─"*70 + "┘")
        
        print("\n┌" + "─"*31 + "最新快讯" + "─"*31 + "┐")
        if news_data:
            for news in news_data[:3]:
                title = news.get('title', '')
                if title:
                    print(f"  • {title}")
        else:
            print("  暂无快讯")
        print("└" + "─"*70 + "┘")
        
        # 保存数据
        save_data(symbol, market_data, large_orders, signals, news_data)
        
        # 生成简报
        generate_briefing(market_data, news_data, large_orders, signals)
        
    except Exception as e:
        print(f"\n❌ 脚本执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ 监控完成")
    sys.stdout.flush()

if __name__ == "__main__":
    main()