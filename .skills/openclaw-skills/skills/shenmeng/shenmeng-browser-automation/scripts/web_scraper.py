#!/usr/bin/env python3
"""
网页数据抓取器 - 使用Playwright抓取网页内容

用法:
    # 基本抓取
    python web_scraper.py --url https://example.com --selector ".item" --output data.json
    
    # 抓取表格
    python web_scraper.py --url https://example.com --table --output table.csv

    # 多页面抓取
    python web_scraper.py --urls urls.txt --selector ".product" --output products.json

    # 需要登录
    python web_scraper.py --url https://example.com --cookies cookies.json --selector ".content"
"""

import argparse
import json
import csv
import time
from playwright.sync_api import sync_playwright
from typing import List, Dict, Optional


class WebScraper:
    """网页数据抓取器"""
    
    def __init__(self, headless: bool = True, proxy: str = None):
        self.headless = headless
        self.proxy = proxy
        self.browser = None
        self.context = None
        self.page = None
    
    def start(self):
        """启动浏览器"""
        playwright = sync_playwright().start()
        
        browser_args = {}
        if self.proxy:
            browser_args['proxy'] = {'server': self.proxy}
        
        self.browser = playwright.chromium.launch(
            headless=self.headless,
            **browser_args
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.page = self.context.new_page()
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
    
    def scrape_elements(self, url: str, selector: str, wait_time: int = 3) -> List[Dict]:
        """
        抓取指定CSS选择器的元素
        
        Args:
            url: 目标网页URL
            selector: CSS选择器
            wait_time: 等待页面加载时间(秒)
        
        Returns:
            抓取的数据列表
        """
        self.page.goto(url, wait_until='networkidle')
        time.sleep(wait_time)
        
        elements = self.page.query_selector_all(selector)
        data = []
        
        for i, element in enumerate(elements):
            try:
                text = element.inner_text()
                html = element.inner_html()
                
                data.append({
                    'index': i,
                    'text': text.strip() if text else '',
                    'html': html[:500] if html else ''
                })
            except Exception as e:
                print(f"[警告] 抓取第{i}个元素时出错: {e}")
        
        return data
    
    def scrape_table(self, url: str, table_selector: str = 'table') -> List[Dict]:
        """抓取表格数据"""
        self.page.goto(url, wait_until='networkidle')
        time.sleep(2)
        
        table = self.page.query_selector(table_selector)
        if not table:
            return []
        
        headers = []
        header_cells = table.query_selector_all('thead th, tr:first-child td, tr:first-child th')
        for cell in header_cells:
            headers.append(cell.inner_text().strip())
        
        rows = []
        data_rows = table.query_selector_all('tbody tr, tr:not(:first-child)')
        for row in data_rows:
            cells = row.query_selector_all('td')
            row_data = {}
            for i, cell in enumerate(cells):
                key = headers[i] if i < len(headers) else f'column_{i}'
                row_data[key] = cell.inner_text().strip()
            rows.append(row_data)
        
        return rows
    
    def load_cookies(self, cookies_file: str):
        """加载cookies实现登录状态"""
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
        self.context.add_cookies(cookies)
    
    def save_cookies(self, cookies_file: str):
        """保存cookies"""
        cookies = self.context.cookies()
        with open(cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)


def save_to_json(data: List[Dict], filepath: str):
    """保存为JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] 已保存 {len(data)} 条数据到 {filepath}")


def save_to_csv(data: List[Dict], filepath: str):
    """保存为CSV"""
    if not data:
        print("[X] 没有数据可保存")
        return
    
    fields = set()
    for item in data:
        fields.update(item.keys())
    fields = sorted(fields)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"[OK] 已保存 {len(data)} 条数据到 {filepath}")


def main():
    parser = argparse.ArgumentParser(description='网页数据抓取器')
    parser.add_argument('--url', type=str, help='目标URL')
    parser.add_argument('--urls', type=str, help='URL列表文件')
    parser.add_argument('--selector', type=str, help='CSS选择器')
    parser.add_argument('--table', action='store_true', help='抓取表格')
    parser.add_argument('--table-selector', type=str, default='table', help='表格选择器')
    parser.add_argument('--output', type=str, default='scraped_data.json', help='输出文件')
    parser.add_argument('--format', type=str, choices=['json', 'csv'], default='json', help='输出格式')
    parser.add_argument('--cookies', type=str, help='Cookies文件路径')
    parser.add_argument('--save-cookies', type=str, help='保存Cookies到文件')
    parser.add_argument('--wait', type=int, default=3, help='等待时间(秒)')
    parser.add_argument('--headful', action='store_true', help='显示浏览器窗口')
    parser.add_argument('--proxy', type=str, help='代理服务器')
    
    args = parser.parse_args()
    
    if not args.url and not args.urls:
        print("[X] 请提供 --url 或 --urls")
        return
    
    if not args.table and not args.selector:
        print("[X] 请提供 --selector 或使用 --table")
        return
    
    scraper = WebScraper(headless=not args.headful, proxy=args.proxy)
    scraper.start()
    
    try:
        if args.cookies:
            scraper.load_cookies(args.cookies)
            print(f"[OK] 已加载cookies: {args.cookies}")
        
        if args.table:
            data = scraper.scrape_table(args.url, args.table_selector)
        elif args.urls:
            with open(args.urls, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            data = []
            for url in urls:
                print(f"[OK] 正在抓取: {url}")
                page_data = scraper.scrape_elements(url, args.selector, args.wait)
                data.extend(page_data)
        else:
            data = scraper.scrape_elements(args.url, args.selector, args.wait)
        
        if args.format == 'json':
            save_to_json(data, args.output)
        else:
            save_to_csv(data, args.output)
        
        if args.save_cookies:
            scraper.save_cookies(args.save_cookies)
            print(f"[OK] 已保存cookies: {args.save_cookies}")
        
        print(f"\n[OK] 抓取完成! 总数据量: {len(data)}")
    
    finally:
        scraper.close()


if __name__ == '__main__':
    main()
