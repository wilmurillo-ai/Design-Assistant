# Browser 工具使用参考

## OpenClaw Browser 工具详解

### 核心操作

#### 1. 打开网页

```javascript
browser action="open" url="https://example.com" profile="openclaw"
```

**参数：**
| 参数 | 说明 | 必填 |
|------|------|------|
| url | 目标网址 | 是 |
| profile | 浏览器配置（openclaw/user/chrome-relay） | 否 |
| loadState | 等待加载状态（load/networkidle/domcontentloaded） | 否 |

#### 2. 获取页面快照

```javascript
browser action="snapshot" refs="aria"
```

**作用：** 获取页面结构和可交互元素列表

**输出：** 元素列表，包含 ref ID、角色、名称等信息

**示例输出：**
```
[e12] button "提交"
[e15] textbox "用户名"
[e18] link "忘记密码"
```

#### 3. 元素操作

**点击：**
```javascript
browser action="act" kind="click" ref="e12"
```

**填写：**
```javascript
browser action="act" kind="fill" ref="e15" text="输入内容"
```

**输入（带提交）：**
```javascript
browser action="act" kind="type" ref="e15" text="搜索词" submit=true
```

**悬停：**
```javascript
browser action="act" kind="hover" ref="e20"
```

**等待：**
```javascript
browser action="act" kind="wait" timeMs=3000
```

#### 4. 截图

**页面截图：**
```javascript
browser action="screenshot" fullPage=true
```

**元素截图：**
```javascript
browser action="screenshot" ref="e25"
```

### 完整工作流示例

**示例1：搜索并截图**
```javascript
// 1. 打开搜索页面
browser action="open" url="https://google.com"

// 2. 获取快照找到搜索框
browser action="snapshot"

// 3. 输入搜索词并提交
browser action="act" kind="type" ref="e15" text="OpenClaw" submit=true

// 4. 等待结果加载
browser action="act" kind="wait" timeMs=2000

// 5. 截图保存
browser action="screenshot" fullPage=true
```

**示例2：表单填写**
```javascript
// 打开表单页面
browser action="open" url="https://example.com/form"

// 获取元素引用
browser action="snapshot"

// 填写各个字段
browser action="act" kind="fill" ref="e10" text="张三"
browser action="act" kind="fill" ref="e12" text="zhangsan@example.com"
browser action="act" kind="fill" ref="e14" text="13800138000"

// 选择下拉选项
browser action="act" kind="click" ref="e16"
browser action="act" kind="click" ref="e20" // 选择具体选项

// 勾选同意条款
browser action="act" kind="click" ref="e25"

// 提交表单
browser action="act" kind="click" ref="e30"

// 验证提交结果
browser action="act" kind="wait" timeMs=3000
browser action="snapshot"
```

## Playwright 使用

### 安装

```bash
pip install playwright
playwright install
```

### 基础脚本模板

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # 启动浏览器
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    )
    page = context.new_page()
    
    # 导航到页面
    page.goto('https://example.com')
    
    # 等待元素加载
    page.wait_for_selector('input[name="username"]')
    
    # 填写表单
    page.fill('input[name="username"]', '用户名')
    page.fill('input[name="password"]', '密码')
    
    # 点击按钮
    page.click('button[type="submit"]')
    
    # 等待页面跳转
    page.wait_for_load_state('networkidle')
    
    # 截图
    page.screenshot(path='result.png', full_page=True)
    
    # 获取文本
    result = page.inner_text('.result-message')
    print(result)
    
    # 关闭
    browser.close()
```

### 高级特性

**处理弹窗：**
```python
page.on('dialog', lambda dialog: dialog.accept())
```

**拦截请求：**
```python
def handle_route(route, request):
    if "ads" in request.url:
        route.abort()
    else:
        route.continue_()

page.route("**/*", handle_route)
```

**滚动页面：**
```python
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
```

## Puppeteer 使用

### 安装

```bash
npm install puppeteer
```

### 基础脚本

```javascript
const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    
    // 导航
    await page.goto('https://example.com', { waitUntil: 'networkidle2' });
    
    // 填写表单
    await page.type('input[name="username"]', '用户名', { delay: 100 });
    await page.type('input[name="password"]', '密码', { delay: 100 });
    
    // 点击并等待导航
    await Promise.all([
        page.waitForNavigation(),
        page.click('button[type="submit"]')
    ]);
    
    // 截图
    await page.screenshot({ path: 'result.png', fullPage: true });
    
    await browser.close();
})();
```

## 工具选择指南

| 需求 | 推荐工具 | 理由 |
|------|---------|------|
| 简单交互/截图 | OpenClaw Browser | 无需额外安装，即时可用 |
| 复杂流程 | Playwright | 功能全面，API现代 |
| Chrome深度控制 | Puppeteer | Chrome专属，功能丰富 |
| 企业级测试 | Selenium | 跨浏览器，生态成熟 |
| 快速原型 | OpenClaw Browser | 交互式开发 |

## 常见问题

**Q: 元素找不到怎么办？**
A: 
1. 添加等待时间 `waitUntil: 'networkidle'`
2. 使用更稳定的选择器（ID、data-testid）
3. 检查是否在iframe中

**Q: 页面加载超时？**
A:
1. 增加超时时间 `timeout: 60000`
2. 检查网络连接
3. 使用 `wait_for_selector` 等待特定元素

**Q: 被网站检测为机器人？**
A:
1. 添加随机延迟
2. 使用真实User-Agent
3. 启用JavaScript执行
4. 使用指纹浏览器

---

*提示：浏览器自动化需要考虑目标网站的负载，避免过度请求。*
