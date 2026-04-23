# 自动化场景模式库

## 模式1：数据采集

### 适用场景
- 电商价格监控
- 新闻内容采集
- 产品信息抓取
- 评论数据收集

### 实现步骤

```python
from playwright.sync_api import sync_playwright
import json
import time

def scrape_products(url, pages=3):
    """采集商品列表数据"""
    data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for page_num in range(1, pages + 1):
            # 访问页面
            page.goto(f"{url}?page={page_num}")
            page.wait_for_load_state('networkidle')
            
            # 等待商品加载
            page.wait_for_selector('.product-item')
            
            # 提取数据
            products = page.query_selector_all('.product-item')
            
            for product in products:
                item = {
                    'name': product.query_selector('.product-name').inner_text(),
                    'price': product.query_selector('.product-price').inner_text(),
                    'link': product.query_selector('a').get_attribute('href'),
                }
                data.append(item)
            
            # 随机延迟
            time.sleep(2 + (page_num % 3))
        
        browser.close()
    
    return data

# 使用
results = scrape_products('https://example.com/products', pages=5)
with open('products.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### 处理动态加载

```python
def scroll_and_scrape(page, scroll_times=5):
    """滚动页面并采集动态加载内容"""
    items = []
    
    for _ in range(scroll_times):
        # 滚动到底部
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        
        # 等待新内容加载
        page.wait_for_timeout(1000)
    
    # 采集所有内容
    items = page.query_selector_all('.item')
    return items
```

---

## 模式2：表单自动填写

### 适用场景
- 批量注册账号
- 自动提交申请
- 填写调查问卷
- 自动报名活动

### 基础模板

```python
def fill_form(form_data):
    """
    form_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'phone': '13800138000',
        'agreement': True
    }
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        page.goto('https://example.com/form')
        
        # 填写文本字段
        page.fill('input[name="username"]', form_data['username'])
        page.fill('input[name="email"]', form_data['email'])
        page.fill('input[name="phone"]', form_data['phone'])
        
        # 选择下拉框
        page.select_option('select[name="country"]', 'China')
        
        # 单选按钮
        page.click('input[value="male"]')
        
        # 复选框
        if form_data.get('agreement'):
            page.click('input[name="agreement"]')
        
        # 提交
        page.click('button[type="submit"]')
        
        # 等待结果
        page.wait_for_selector('.success-message')
        
        browser.close()
```

### 复杂表单处理

```python
def fill_multi_step_form():
    """多步骤表单"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # Step 1: 基本信息
        page.goto('https://example.com/step1')
        page.fill('#name', '张三')
        page.fill('#email', 'zhangsan@example.com')
        page.click('#next-step')
        
        # 等待第二步加载
        page.wait_for_selector('#step2-form')
        
        # Step 2: 详细信息
        page.fill('#address', '北京市朝阳区')
        page.fill('#phone', '13800138000')
        page.click('#next-step')
        
        # Step 3: 确认提交
        page.wait_for_selector('#confirm-step')
        page.click('#submit')
        
        # 验证提交成功
        success = page.wait_for_selector('.success-message')
        
        browser.close()
        return success is not None
```

---

## 模式3：登录自动化

### 适用场景
- 自动签到领奖励
- 定时任务执行
- 状态监控

### 基础登录

```python
import json
import os

def login_and_save_state(username, password):
    """登录并保存状态"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        
        # 登录
        page.goto('https://example.com/login')
        page.fill('#username', username)
        page.fill('#password', password)
        page.click('#login-btn')
        
        # 等待登录成功
        page.wait_for_selector('.user-profile', timeout=10000)
        
        # 保存状态
        context.storage_state(path=f'state_{username}.json')
        
        browser.close()

def use_saved_state(username):
    """使用保存的状态"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        # 加载状态
        if os.path.exists(f'state_{username}.json'):
            context = browser.new_context(
                storage_state=f'state_{username}.json'
            )
        else:
            context = browser.new_context()
        
        page = context.new_page()
        page.goto('https://example.com/dashboard')
        
        # 执行操作...
        
        browser.close()
```

### 自动签到

```python
def auto_check_in():
    """每日自动签到"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(storage_state='auth.json')
        page = context.new_page()
        
        page.goto('https://example.com/dashboard')
        
        # 检查今日是否已签到
        if page.query_selector('.check-in-done'):
            print("今日已签到")
        else:
            # 点击签到
            page.click('.check-in-btn')
            page.wait_for_selector('.check-in-success')
            print("签到成功")
        
        browser.close()
```

---

## 模式4：价格监控

### 适用场景
- 商品价格变动提醒
- 机票酒店价格监控
- 股票价格监控

### 实现代码

```python
import time
from datetime import datetime

def monitor_price(url, selector, threshold, callback):
    """
    监控价格变化
    callback: 价格变化时的回调函数
    """
    last_price = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        while True:
            try:
                page.goto(url)
                page.wait_for_selector(selector)
                
                # 提取价格
                price_text = page.inner_text(selector)
                current_price = parse_price(price_text)
                
                if last_price is None:
                    last_price = current_price
                    print(f"[{datetime.now()}] 初始价格: {current_price}")
                
                # 检测价格变化
                change_percent = abs(current_price - last_price) / last_price
                
                if change_percent >= threshold:
                    callback({
                        'old_price': last_price,
                        'new_price': current_price,
                        'change_percent': change_percent,
                        'timestamp': datetime.now()
                    })
                    last_price = current_price
                
            except Exception as e:
                print(f"监控出错: {e}")
            
            # 等待下次检查
            time.sleep(300)  # 5分钟

def parse_price(price_text):
    """解析价格文本"""
    import re
    numbers = re.findall(r'\d+\.?\d*', price_text.replace(',', ''))
    return float(numbers[0]) if numbers else 0
```

---

## 模式5：批量下载

### 适用场景
- 批量下载文件
- 图片采集
- 文档归档

### 实现代码

```python
import os
import urllib.request

def batch_download(page, download_selector, save_dir='downloads'):
    """批量下载文件"""
    os.makedirs(save_dir, exist_ok=True)
    
    # 获取所有下载链接
    links = page.query_selector_all(download_selector)
    
    for i, link in enumerate(links):
        url = link.get_attribute('href')
        filename = link.get_attribute('download') or f"file_{i}"
        
        filepath = os.path.join(save_dir, filename)
        
        # 下载文件
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"已下载: {filename}")
        except Exception as e:
            print(f"下载失败 {filename}: {e}")
        
        # 延迟避免触发限制
        time.sleep(1)
```

---

## 模式6：内容监控

### 适用场景
- 监控页面内容变化
- 新文章检测
- 库存监控

### 实现代码

```python
import hashlib

def monitor_content(url, selector, on_change):
    """监控内容变化"""
    last_hash = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        while True:
            page.goto(url)
            page.wait_for_selector(selector)
            
            content = page.inner_text(selector)
            current_hash = hashlib.md5(content.encode()).hexdigest()
            
            if last_hash is None:
                last_hash = current_hash
            elif current_hash != last_hash:
                on_change(content)
                last_hash = current_hash
            
            time.sleep(600)  # 10分钟检查一次
```

---

## 模式7：验证码处理流程

### 人工辅助

```python
def handle_captcha_manual(page, captcha_selector):
    """人工处理验证码"""
    # 截图验证码
    captcha_element = page.query_selector(captcha_selector)
    captcha_element.screenshot(path='captcha.png')
    
    # 提示用户输入
    print("请查看 captcha.png 并输入验证码:")
    captcha_text = input("验证码: ")
    
    # 填写验证码
    page.fill('#captcha-input', captcha_text)
```

### 自动识别（2Captcha）

```python
import requests

def solve_captcha_2captcha(api_key, image_path):
    """使用2Captcha服务"""
    # 上传图片
    with open(image_path, 'rb') as f:
        response = requests.post('http://2captcha.com/in.php', 
            files={'file': f},
            data={'key': api_key, 'method': 'post'}
        )
    
    captcha_id = response.text.split('|')[1]
    
    # 获取结果
    for _ in range(30):  # 最多等待30秒
        time.sleep(1)
        result = requests.get(
            f'http://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}'
        )
        if 'OK|' in result.text:
            return result.text.split('|')[1]
    
    return None
```

---

## 模式8：错误处理与重试

### 健壮性模板

```python
from functools import wraps
import time

def retry_on_error(max_retries=3, delay=2):
    """错误重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"尝试 {attempt + 1} 失败: {e}，{delay}秒后重试...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_error(max_retries=3, delay=2)
def scrape_with_retry(url):
    """带重试的数据采集"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        data = extract_data(page)
        browser.close()
        return data
```

---

*这些模式可以根据具体需求组合和定制。*
