#!/usr/bin/env python3
"""
数据采集模板
适用于：电商价格监控、新闻采集、产品信息抓取等
"""

import json
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

class DataScraper:
    def __init__(self, headless=True, delay_range=(1, 3)):
        self.headless = headless
        self.delay_range = delay_range
        self.browser = None
        self.page = None
        self.data = []
    
    def start(self):
        """启动浏览器"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = context.new_page()
    
    def random_delay(self):
        """随机延迟"""
        time.sleep(random.uniform(*self.delay_range))
    
    def scroll_page(self, times=3):
        """滚动页面加载更多内容"""
        for _ in range(times):
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.5)
    
    def extract_data(self, items_selector, fields):
        """
        提取数据
        
        items_selector: 列表项的选择器
        fields: {
            'name': '.product-name',
            'price': '.product-price',
            'link': ('a', 'href'),  # (选择器, 属性名)
        }
        """
        items = self.page.query_selector_all(items_selector)
        
        for item in items:
            data_item = {
                'scraped_at': datetime.now().isoformat(),
            }
            
            for field_name, selector in fields.items():
                try:
                    if isinstance(selector, tuple):
                        # 提取属性值
                        sel, attr = selector
                        element = item.query_selector(sel)
                        data_item[field_name] = element.get_attribute(attr) if element else None
                    else:
                        # 提取文本
                        element = item.query_selector(selector)
                        data_item[field_name] = element.inner_text().strip() if element else None
                except Exception as e:
                    data_item[field_name] = None
                    print(f"提取 {field_name} 失败: {e}")
            
            self.data.append(data_item)
        
        return len(items)
    
    def scrape_list_page(self, url, items_selector, fields, scroll=False):
        """
        采集列表页面
        
        url: 页面URL
        items_selector: 列表项选择器
        fields: 字段映射
        scroll: 是否滚动加载更多
        """
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')
        self.random_delay()
        
        # 等待元素加载
        self.page.wait_for_selector(items_selector, timeout=10000)
        
        # 滚动加载
        if scroll:
            self.scroll_page()
        
        # 提取数据
        count = self.extract_data(items_selector, fields)
        print(f"从 {url} 提取了 {count} 条数据")
        
        return count
    
    def scrape_multiple_pages(self, base_url, total_pages, items_selector, fields, page_param='page'):
        """采集多页数据"""
        for page_num in range(1, total_pages + 1):
            url = f"{base_url}?{page_param}={page_num}"
            print(f"正在采集第 {page_num} 页...")
            
            try:
                self.scrape_list_page(url, items_selector, fields)
                self.random_delay()
            except Exception as e:
                print(f"采集第 {page_num} 页失败: {e}")
                continue
    
    def save_data(self, filename):
        """保存数据到JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filename}，共 {len(self.data)} 条")
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()


# 使用示例
if __name__ == '__main__':
    scraper = DataScraper(headless=False, delay_range=(2, 4))
    
    try:
        scraper.start()
        
        # 定义采集规则
        fields = {
            'title': '.product-title',
            'price': '.product-price',
            'rating': '.product-rating',
            'link': ('a.product-link', 'href'),
        }
        
        # 采集单页
        scraper.scrape_list_page(
            url='https://example.com/products',
            items_selector='.product-item',
            fields=fields,
            scroll=True
        )
        
        # 或者采集多页
        # scraper.scrape_multiple_pages(
        #     base_url='https://example.com/products',
        #     total_pages=5,
        #     items_selector='.product-item',
        #     fields=fields
        # )
        
        # 保存数据
        scraper.save_data('scraped_data.json')
        
    finally:
        scraper.close()
