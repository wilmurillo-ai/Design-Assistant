#!/usr/bin/env python3
"""
表单自动填写工具

用法:
    # 使用配置文件
    python form_filler.py --config form_config.json
    
    # 命令行参数
    python form_filler.py --url https://example.com/form \
        --field "#username=myuser" \
        --field "#password=mypass" \
        --submit "#submit-btn"
    
    # 从CSV批量填写
    python form_filler.py --config form_config.json --data users.csv
"""

import argparse
import json
import csv
import time
from playwright.sync_api import sync_playwright
from typing import List, Dict


class FormFiller:
    """表单自动填写器"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
    
    def start(self):
        """启动浏览器"""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = self.context.new_page()
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
    
    def fill_field(self, selector: str, value: str, field_type: str = 'text'):
        """
        填写单个字段
        
        Args:
            selector: CSS选择器
            value: 填写值
            field_type: 字段类型 (text, select, checkbox, radio, file)
        """
        try:
            element = self.page.query_selector(selector)
            if not element:
                print(f"[警告] 未找到元素: {selector}")
                return False
            
            if field_type == 'text' or field_type == 'password':
                element.fill(value)
            elif field_type == 'select':
                element.select_option(value)
            elif field_type == 'checkbox':
                if value.lower() in ('true', '1', 'yes', 'on'):
                    element.check()
                else:
                    element.uncheck()
            elif field_type == 'radio':
                element.check()
            elif field_type == 'file':
                element.set_input_files(value)
            
            print(f"[✓] 已填写: {selector}")
            return True
            
        except Exception as e:
            print(f"[×] 填写失败 {selector}: {e}")
            return False
    
    def fill_form(self, url: str, fields: List[Dict], submit_selector: str = None,
                  wait_time: int = 2):
        """
        填写整个表单
        
        Args:
            url: 表单页面URL
            fields: 字段列表 [{'selector': '...', 'value': '...', 'type': '...'}]
            submit_selector: 提交按钮选择器
            wait_time: 提交后等待时间
        """
        self.page.goto(url, wait_until='networkidle')
        time.sleep(1)
        
        print(f"[*] 正在填写表单: {url}")
        
        # 填写所有字段
        for field in fields:
            selector = field.get('selector')
            value = field.get('value')
            field_type = field.get('type', 'text')
            
            self.fill_field(selector, value, field_type)
            time.sleep(0.5)  # 模拟人类输入间隔
        
        # 提交表单
        if submit_selector:
            print(f"[*] 正在提交表单...")
            submit_btn = self.page.query_selector(submit_selector)
            if submit_btn:
                submit_btn.click()
                time.sleep(wait_time)
                print(f"[✓] 表单已提交")
            else:
                print(f"[×] 未找到提交按钮: {submit_selector}")
        
        return self.page.url
    
    def batch_fill(self, config: Dict, data_file: str):
        """
        批量填写表单
        
        Args:
            config: 表单配置
            data_file: CSV数据文件路径
        """
        url = config['url']
        fields_template = config['fields']
        submit_selector = config.get('submit')
        
        # 读取CSV数据
        with open(data_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        print(f"[*] 准备为 {len(rows)} 条数据填写表单")
        
        results = []
        for i, row in enumerate(rows):
            print(f"\n[{i+1}/{len(rows)}] 正在填写...")
            
            # 替换模板中的变量
            fields = []
            for field_template in fields_template:
                field = field_template.copy()
                value_template = field.get('value', '')
                # 替换 {{column_name}} 为实际值
                for key, val in row.items():
                    value_template = value_template.replace(f'{{{{{key}}}}}', str(val))
                field['value'] = value_template
                fields.append(field)
            
            # 填写表单
            try:
                final_url = self.fill_form(url, fields, submit_selector)
                results.append({
                    'index': i,
                    'data': row,
                    'success': True,
                    'final_url': final_url
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'data': row,
                    'success': False,
                    'error': str(e)
                })
            
            # 间隔一段时间
            if i < len(rows) - 1:
                time.sleep(3)
        
        return results


def main():
    parser = argparse.ArgumentParser(description='表单自动填写工具')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--url', type=str, help='表单URL')
    parser.add_argument('--field', type=str, action='append', help='字段 (格式: 选择器=值)')
    parser.add_argument('--type', type=str, action='append', help='字段类型 (与--field对应)')
    parser.add_argument('--submit', type=str, help='提交按钮选择器')
    parser.add_argument('--data', type=str, help='批量数据CSV文件')
    parser.add_argument('--headless', action='store_true', help='无头模式')
    parser.add_argument('--wait', type=int, default=3, help='提交后等待时间')
    
    args = parser.parse_args()
    
    # 初始化
    filler = FormFiller(headless=args.headless)
    filler.start()
    
    try:
        if args.config:
            # 使用配置文件
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if args.data:
                # 批量填写
                results = filler.batch_fill(config, args.data)
                
                # 保存结果
                output_file = 'form_results.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                success_count = sum(1 for r in results if r['success'])
                print(f"\n[✓] 批量填写完成!")
                print(f"  成功: {success_count}/{len(results)}")
                print(f"  结果已保存: {output_file}")
            else:
                # 单次填写
                url = config['url']
                fields = config['fields']
                submit = config.get('submit')
                
                final_url = filler.fill_form(url, fields, submit, args.wait)
                print(f"[✓] 表单填写完成，当前URL: {final_url}")
        
        elif args.url:
            # 使用命令行参数
            fields = []
            if args.field:
                for i, field_str in enumerate(args.field):
                    parts = field_str.split('=', 1)
                    if len(parts) == 2:
                        field_type = args.type[i] if args.type and i < len(args.type) else 'text'
                        fields.append({
                            'selector': parts[0],
                            'value': parts[1],
                            'type': field_type
                        })
            
            final_url = filler.fill_form(args.url, fields, args.submit, args.wait)
            print(f"[✓] 表单填写完成，当前URL: {final_url}")
        
        else:
            print("[×] 请提供 --config 或 --url")
    
    finally:
        filler.close()


if __name__ == '__main__':
    main()
