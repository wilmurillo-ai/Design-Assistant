# Playwright 快速指南

## 安装

```bash
# 安装playwright
pip install playwright

# 安装浏览器
playwright install chromium
playwright install firefox
playwright install webkit
```

## 基础用法

### 启动浏览器
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 启动浏览器
    browser = p.chromium.launch(headless=True)  # headless=True 无头模式
    
    # 创建新页面
    page = browser.new_page()
    
    # 访问网页
    page.goto('https://example.com')
    
    # 关闭浏览器
    browser.close()
```

### 常用操作

#### 导航
```python
# 访问页面
page.goto('https://example.com')

# 等待页面加载完成
page.goto('https://example.com', wait_until='networkidle')

# 刷新页面
page.reload()

# 后退
page.go_back()

# 前进
page.go_forward()
```

#### 元素选择
```python
# 查找单个元素
element = page.query_selector('.class-name')
element = page.query_selector('#id')
element = page.query_selector('tag[attr="value"]')

# 查找多个元素
elements = page.query_selector_all('.item')

# 等待元素出现
element = page.wait_for_selector('.dynamic-content')

# 等待元素消失
page.wait_for_selector('.loading', state='hidden')
```

#### 元素操作
```python
# 点击
element.click()

# 填写文本
element.fill('文本内容')

# 清空并填写
element.clear()
element.fill('新内容')

# 获取文本
text = element.inner_text()

# 获取HTML
html = element.inner_html()

# 获取属性
href = element.get_attribute('href')

# 检查元素是否可见
is_visible = element.is_visible()

# 检查元素是否可用
is_enabled = element.is_enabled()
```

#### 键盘操作
```python
# 按Enter
page.press('input#username', 'Enter')

# 组合键
page.keyboard.press('Control+a')
page.keyboard.press('Control+c')
```

#### 鼠标操作
```python
# 悬停
page.hover('.dropdown')

# 拖拽
page.drag_and_drop('.source', '.target')

# 滚轮
page.mouse.wheel(0, 1000)
```

## 高级功能

### 截图
```python
# 整页截图
page.screenshot(path='screenshot.png')

# 元素截图
element.screenshot(path='element.png')

# 全页面截图
page.screenshot(path='fullpage.png', full_page=True)
```

### PDF生成
```python
page.pdf(path='page.pdf', format='A4')
```

### 处理弹窗
```python
# 监听弹窗
page.on('dialog', lambda dialog: dialog.accept())

# 处理确认框
page.on('dialog', lambda dialog: dialog.dismiss() if dialog.type == 'confirm' else dialog.accept())
```

### 处理新页面
```python
# 等待新页面打开
with page.expect_popup() as popup_info:
    page.click('#open-in-new-window')
popup = popup_info.value

# 在新页面操作
popup.goto('https://example.com')
```

### 拦截请求
```python
# 拦截图片加载
def handle_route(route, request):
    if request.resource_type == 'image':
        route.abort()
    else:
        route.continue_()

page.route('**/*', handle_route)
```

### 模拟设备
```python
# 模拟iPhone
iphone = p.devices['iPhone 11 Pro']
browser = p.chromium.launch()
context = browser.new_context(**iphone)
page = context.new_page()
```

### 模拟地理位置
```python
context = browser.new_context(
    geolocation={'longitude': 116.4074, 'latitude': 39.9042},
    permissions=['geolocation']
)
```

## 等待策略

```python
# 等待元素可见
element = page.wait_for_selector('.content', state='visible')

# 等待元素隐藏
page.wait_for_selector('.loading', state='hidden')

# 等待元素从DOM中移除
page.wait_for_selector('.temp', state='detached')

# 等待网络空闲
page.wait_for_load_state('networkidle')

# 等待特定时间（不推荐）
page.wait_for_timeout(3000)

# 等待函数返回True
page.wait_for_function('() => document.title.includes("Loaded")')
```

## 反检测技巧

```python
# 修改webdriver标志
context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
)

# 添加初始化脚本
def handle_page(page):
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

context.on('page', handle_page)
```

## 错误处理

```python
try:
    page.goto('https://example.com', timeout=30000)
except TimeoutError:
    print('页面加载超时')
except Error as e:
    print(f'错误: {e}')
```

## 性能优化

```python
# 重用浏览器上下文
context = browser.new_context()

# 批量操作多个页面
for url in urls:
    page = context.new_page()
    page.goto(url)
    # 操作...
    page.close()

# 最后统一关闭
context.close()
browser.close()
```
