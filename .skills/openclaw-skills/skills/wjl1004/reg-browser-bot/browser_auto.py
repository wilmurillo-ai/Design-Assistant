#!/usr/bin/env python3
"""
简单浏览器自动化工具
功能：登录、点击、填表、截图
基于 Selenium + Chrome
"""

import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64

class SimpleBrowser:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        self.setup()
    
    def setup(self):
        """初始化浏览器"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            print("浏览器启动成功")
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            self.driver = None
    
    def navigate(self, url):
        """打开URL"""
        if self.driver:
            self.driver.get(url)
            print(f"已打开: {url}")
            return True
        return False
    
    def click(self, selector, by='css'):
        """点击元素"""
        if not self.driver:
            return False
        
        try:
            if by == 'css':
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elif by == 'xpath':
                elem = self.driver.find_element(By.XPATH, selector)
            elif by == 'id':
                elem = self.driver.find_element(By.ID, selector)
            elif by == 'name':
                elem = self.driver.find_element(By.NAME, selector)
            
            elem.click()
            print(f"已点击: {selector}")
            return True
        except Exception as e:
            print(f"点击失败: {e}")
            return False
    
    def input(self, selector, text, by='css'):
        """输入文本"""
        if not self.driver:
            return False
        
        try:
            if by == 'css':
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elif by == 'xpath':
                elem = self.driver.find_element(By.XPATH, selector)
            elif by == 'id':
                elem = self.driver.find_element(By.ID, selector)
            elif by == 'name':
                elem = self.driver.find_element(By.NAME, selector)
            
            elem.clear()
            elem.send_keys(text)
            print(f"已输入: {text[:20]}...")
            return True
        except Exception as e:
            print(f"输入失败: {e}")
            return False
    
    def submit(self, selector, by='css'):
        """提交表单"""
        if not self.driver:
            return False
        
        try:
            if by == 'css':
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elif by == 'xpath':
                elem = self.driver.find_element(By.XPATH, selector)
            
            elem.submit()
            print(f"已提交表单")
            return True
        except Exception as e:
            print(f"提交失败: {e}")
            return False
    
    def wait(self, seconds):
        """等待"""
        time.sleep(seconds)
        print(f"等待了 {seconds} 秒")
    
    def screenshot(self, filename='screenshot.png'):
        """截图"""
        if self.driver:
            self.driver.save_screenshot(filename)
            print(f"截图已保存: {filename}")
            return filename
        return None
    
    def get_page_source(self):
        """获取页面源码"""
        if self.driver:
            return self.driver.page_source
        return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("浏览器已关闭")

def main():
    if len(sys.argv) < 2:
        print("""
浏览器自动化工具
用法:
    python browser_auto.py navigate <URL>
    python browser_auto.py click <selector> [by]
    python browser_auto.py input <selector> <text> [by]
    python browser_auto.py screenshot [filename]
    python browser_auto.py wait <seconds>
    python browser_auto.py close

示例:
    python browser_auto.py navigate https://example.com
    python browser_auto.py click "#login-btn" css
    python browser_auto.py input "#username" "myuser" id
    python browser_auto.py screenshot
    python browser_auto.py close
""")
        sys.exit(1)
    
    cmd = sys.argv[1]
    browser = SimpleBrowser()
    
    if cmd == 'navigate' and len(sys.argv) > 2:
        browser.navigate(sys.argv[2])
    elif cmd == 'click' and len(sys.argv) > 2:
        by = sys.argv[3] if len(sys.argv) > 3 else 'css'
        browser.click(sys.argv[2], by)
    elif cmd == 'input' and len(sys.argv) > 3:
        by = sys.argv[4] if len(sys.argv) > 4 else 'css'
        browser.input(sys.argv[2], sys.argv[3], by)
    elif cmd == 'screenshot':
        filename = sys.argv[2] if len(sys.argv) > 2 else 'screenshot.png'
        browser.screenshot(filename)
    elif cmd == 'wait':
        browser.wait(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    elif cmd == 'close':
        browser.close()
    else:
        print(f"未知命令: {cmd}")
    
    # 保持浏览器打开直到主动关闭
    input("按回车键关闭浏览器...")

if __name__ == "__main__":
    main()
