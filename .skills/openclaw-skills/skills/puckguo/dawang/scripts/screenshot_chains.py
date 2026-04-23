#!/usr/bin/env python3
"""使用 Playwright 截取 Google Maps 餐厅截图"""

from playwright.sync_api import sync_playwright
import os
import time

# 创建输出目录
output_dir = "/Users/godspeed/.openclaw/workspaces/dawang/chains_screenshots"
os.makedirs(output_dir, exist_ok=True)

# 餐厅搜索链接
restaurants = [
    ("panda_express", "https://www.google.com/maps/search/Panda+Express+Los+Angeles+Figueroa+St"),
    ("pf_changs", "https://www.google.com/maps/search/P.F.+Chang's+Washington+DC"),
    ("pei_wei", "https://www.google.com/maps/search/Pei+Wei+Asian+Kitchen+Los+Angeles"),
    ("pick_up_stix", "https://www.google.com/maps/search/Pick+Up+Stix+Los+Angeles"),
    ("china_wok", "https://www.google.com/maps/search/China+Wok+Los+Angeles"),
    ("jade_wok", "https://www.google.com/maps/search/Jade+Wok+Los+Angeles"),
]

def take_screenshot(page, url, name):
    """截取页面截图"""
    print(f"正在截取 {name}...")
    page.goto(url, timeout=30000)
    time.sleep(3)  # 等待页面加载
    screenshot_path = f"{output_dir}/{name}.png"
    page.screenshot(path=screenshot_path, full_page=False)
    print(f"已保存: {screenshot_path}")
    return screenshot_path

with sync_playwright() as p:
    # 连接到已运行的 Chrome
    browser = p.chromium.connect_over_cdp("http://localhost:9222")
    
    # 创建新标签页
    context = browser.new_context()
    page = context.new_page()
    
    for name, url in restaurants:
        try:
            take_screenshot(page, url, name)
        except Exception as e:
            print(f"截图失败 {name}: {e}")
    
    context.close()
    browser.close()

print("完成!")
