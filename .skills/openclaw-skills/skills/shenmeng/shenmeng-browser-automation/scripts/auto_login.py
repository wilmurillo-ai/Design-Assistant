#!/usr/bin/env python3
"""
登录自动化模板
适用于：自动签到、保持登录状态、定时任务等
"""

import json
import os
from playwright.sync_api import sync_playwright

class AutoLogin:
    def __init__(self, headless=False, state_file='auth_state.json'):
        self.headless = headless
        self.state_file = state_file
        self.browser = None
        self.context = None
        self.page = None
    
    def start(self, use_saved_state=True):
        """启动浏览器，可选择加载保存的状态"""
        playwright = sync_playwright().start()
        
        # 检查是否有保存的状态
        storage_state = None
        if use_saved_state and os.path.exists(self.state_file):
            storage_state = self.state_file
            print(f"加载已保存的登录状态: {self.state_file}")
        
        self.browser = playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        if storage_state:
            self.context = self.browser.new_context(
                storage_state=storage_state,
                viewport={'width': 1920, 'height': 1080}
            )
        else:
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
        
        self.page = self.context.new_page()
    
    def login(self, login_url, username_selector, password_selector, 
              submit_selector, username, password, success_selector=None):
        """
        执行登录
        
        参数:
            login_url: 登录页面URL
            username_selector: 用户名输入框选择器
            password_selector: 密码输入框选择器
            submit_selector: 提交按钮选择器
            username: 用户名
            password: 密码
            success_selector: 登录成功后的页面元素（用于验证）
        """
        self.page.goto(login_url)
        self.page.wait_for_load_state('networkidle')
        
        # 填写登录信息
        self.page.fill(username_selector, username)
        self.page.fill(password_selector, password)
        
        # 点击登录
        self.page.click(submit_selector)
        
        # 等待登录完成
        if success_selector:
            self.page.wait_for_selector(success_selector, timeout=10000)
        else:
            self.page.wait_for_load_state('networkidle')
        
        print("登录成功")
        
        # 保存登录状态
        self.save_state()
    
    def save_state(self):
        """保存浏览器状态（包含登录态）"""
        self.context.storage_state(path=self.state_file)
        print(f"登录状态已保存到: {self.state_file}")
    
    def check_login_status(self, profile_url, login_indicator):
        """
        检查登录状态
        
        参数:
            profile_url: 需要登录才能访问的页面
            login_indicator: 登录后才会出现的元素选择器
        
        返回:
            bool: 是否已登录
        """
        self.page.goto(profile_url)
        self.page.wait_for_load_state('networkidle')
        
        try:
            self.page.wait_for_selector(login_indicator, timeout=5000)
            print("登录状态有效")
            return True
        except:
            print("登录状态已失效，需要重新登录")
            return False
    
    def auto_check_in(self, check_in_url, check_in_button_selector, 
                      success_indicator=None, already_done_indicator=None):
        """
        自动签到
        
        参数:
            check_in_url: 签到页面URL
            check_in_button_selector: 签到按钮选择器
            success_indicator: 签到成功后的元素选择器
            already_done_indicator: 已签到标识选择器
        
        返回:
            dict: 签到结果
        """
        self.page.goto(check_in_url)
        self.page.wait_for_load_state('networkidle')
        
        # 检查是否已签到
        if already_done_indicator:
            if self.page.query_selector(already_done_indicator):
                return {'success': True, 'message': '今日已签到', 'already_done': True}
        
        # 点击签到按钮
        try:
            self.page.click(check_in_button_selector)
            
            # 等待签到完成
            if success_indicator:
                self.page.wait_for_selector(success_indicator, timeout=10000)
            else:
                self.page.wait_for_timeout(2000)
            
            return {'success': True, 'message': '签到成功', 'already_done': False}
            
        except Exception as e:
            return {'success': False, 'message': f'签到失败: {e}', 'already_done': False}
    
    def perform_task(self, task_url, actions):
        """
        执行一系列操作
        
        actions: [
            {'type': 'click', 'selector': '#button'},
            {'type': 'fill', 'selector': '#input', 'value': 'text'},
            {'type': 'wait', 'timeout': 2000},
        ]
        """
        self.page.goto(task_url)
        self.page.wait_for_load_state('networkidle')
        
        for action in actions:
            action_type = action.get('type')
            
            if action_type == 'click':
                self.page.click(action['selector'])
            
            elif action_type == 'fill':
                self.page.fill(action['selector'], action['value'])
            
            elif action_type == 'wait':
                timeout = action.get('timeout', 1000)
                self.page.wait_for_timeout(timeout)
            
            elif action_type == 'wait_for':
                self.page.wait_for_selector(action['selector'])
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()


# 使用示例
if __name__ == '__main__':
    auth = AutoLogin(headless=False, state_file='my_auth.json')
    
    try:
        auth.start(use_saved_state=True)
        
        # 如果需要重新登录
        # auth.login(
        #     login_url='https://example.com/login',
        #     username_selector='#username',
        #     password_selector='#password',
        #     submit_selector='#login-btn',
        #     username='your_username',
        #     password='your_password',
        #     success_selector='.user-profile'
        # )
        
        # 检查登录状态
        is_logged_in = auth.check_login_status(
            profile_url='https://example.com/profile',
            login_indicator='.user-name'
        )
        
        if is_logged_in:
            # 执行自动签到
            result = auth.auto_check_in(
                check_in_url='https://example.com/check-in',
                check_in_button_selector='.check-in-btn',
                success_indicator='.check-in-success',
                already_done_indicator='.already-checked'
            )
            print(f"签到结果: {result}")
        else:
            print("请先登录")
        
    finally:
        auth.close()
