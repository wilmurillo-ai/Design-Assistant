#!/usr/bin/env python3
"""
网页内容监控工具

用法:
    # 监控价格变化
    python page_monitor.py --url https://example.com/product --selector ".price" --interval 3600
    
    # 监控内容更新
    python page_monitor.py --url https://example.com/news --selector ".content" --condition "contains:关键字"
    
    # 监控并通知
    python page_monitor.py --url https://example.com --selector ".status" --webhook https://hooks.slack.com/...
"""

import argparse
import json
import time
import hashlib
from datetime import datetime
from playwright.sync_api import sync_playwright
import requests


class PageMonitor:
    """网页内容监控器"""
    
    def __init__(self):
        self.last_content = None
        self.last_hash = None
    
    def get_content_hash(self, content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def check_page(self, url: str, selector: str, condition: str = None) -> dict:
        """
        检查网页内容
        
        Args:
            url: 目标URL
            selector: CSS选择器
            condition: 条件表达式 (如 "<100", "contains:关键字")
        
        Returns:
            检查结果
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            try:
                page.goto(url, wait_until='networkidle')
                time.sleep(2)
                
                # 获取元素内容
                element = page.query_selector(selector)
                if not element:
                    return {
                        'success': False,
                        'error': f'未找到元素: {selector}',
                        'timestamp': datetime.now().isoformat()
                    }
                
                content = element.inner_text().strip()
                current_hash = self.get_content_hash(content)
                
                result = {
                    'success': True,
                    'url': url,
                    'selector': selector,
                    'content': content,
                    'hash': current_hash,
                    'timestamp': datetime.now().isoformat(),
                    'changed': current_hash != self.last_hash if self.last_hash else False
                }
                
                # 检查条件
                if condition:
                    condition_met = self.check_condition(content, condition)
                    result['condition'] = condition
                    result['condition_met'] = condition_met
                
                # 更新状态
                self.last_content = content
                self.last_hash = current_hash
                
                return result
                
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            finally:
                browser.close()
    
    def check_condition(self, content: str, condition: str) -> bool:
        """检查条件是否满足"""
        try:
            # 尝试提取数字
            import re
            numbers = re.findall(r'[\d,]+\.?\d*', content)
            if numbers:
                value = float(numbers[0].replace(',', ''))
                
                # 解析条件
                if condition.startswith('<'):
                    threshold = float(condition[1:])
                    return value < threshold
                elif condition.startswith('>'):
                    threshold = float(condition[1:])
                    return value > threshold
                elif condition.startswith('<='):
                    threshold = float(condition[2:])
                    return value <= threshold
                elif condition.startswith('>='):
                    threshold = float(condition[2:])
                    return value >= threshold
            
            # 文本包含检查
            if condition.startswith('contains:'):
                keyword = condition[9:]
                return keyword in content
            
            return False
            
        except Exception as e:
            print(f"[警告] 条件检查失败: {e}")
            return False
    
    def send_notification(self, webhook_url: str, message: str):
        """发送通知"""
        try:
            payload = {'text': message}
            response = requests.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[警告] 通知发送失败: {e}")
            return False
    
    def start_monitoring(self, url: str, selector: str, interval: int,
                         condition: str = None, webhook: str = None,
                         max_checks: int = None):
        """
        开始持续监控
        
        Args:
            url: 目标URL
            selector: CSS选择器
            interval: 检查间隔(秒)
            condition: 条件表达式
            webhook: 通知webhook URL
            max_checks: 最大检查次数(无限循环为None)
        """
        print(f"[*] 开始监控: {url}")
        print(f"[*] 选择器: {selector}")
        print(f"[*] 检查间隔: {interval}秒")
        if condition:
            print(f"[*] 条件: {condition}")
        print("-" * 60)
        
        check_count = 0
        
        try:
            while max_checks is None or check_count < max_checks:
                check_count += 1
                print(f"\n[{check_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                result = self.check_page(url, selector, condition)
                
                if result['success']:
                    content = result['content']
                    print(f"  内容: {content[:100]}...")
                    
                    # 检查变化
                    if result.get('changed'):
                        print(f"  [✓] 内容已变化!")
                        
                        # 发送通知
                        if webhook:
                            message = f"🔄 页面内容变化\n\nURL: {url}\n内容: {content[:200]}"
                            self.send_notification(webhook, message)
                    
                    # 检查条件
                    if condition and result.get('condition_met'):
                        print(f"  [✓] 条件满足: {condition}")
                        
                        # 发送通知
                        if webhook:
                            message = f"✅ 条件满足\n\nURL: {url}\n条件: {condition}\n内容: {content[:200]}"
                            self.send_notification(webhook, message)
                else:
                    print(f"  [×] 检查失败: {result.get('error')}")
                
                # 等待下一次检查
                if max_checks is None or check_count < max_checks:
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n[*] 监控已停止")


def main():
    parser = argparse.ArgumentParser(description='网页内容监控工具')
    parser.add_argument('--url', type=str, required=True, help='监控的URL')
    parser.add_argument('--selector', type=str, required=True, help='CSS选择器')
    parser.add_argument('--interval', type=int, default=3600, help='检查间隔(秒)')
    parser.add_argument('--condition', type=str, help='条件表达式 (如 "<100", "contains:关键字")')
    parser.add_argument('--webhook', type=str, help='通知webhook URL')
    parser.add_argument('--max-checks', type=int, help='最大检查次数')
    
    args = parser.parse_args()
    
    monitor = PageMonitor()
    monitor.start_monitoring(
        url=args.url,
        selector=args.selector,
        interval=args.interval,
        condition=args.condition,
        webhook=args.webhook,
        max_checks=args.max_checks
    )


if __name__ == '__main__':
    main()
