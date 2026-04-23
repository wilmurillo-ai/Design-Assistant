# 反检测与防封指南

## 检测机制原理

### 网站如何识别自动化工具

**1. JavaScript 检测**
- `navigator.webdriver` 属性
- Chrome DevTools Protocol 检测
- 插件和扩展检测

**2. 行为分析**
- 鼠标移动轨迹（直线移动 vs 曲线移动）
- 点击速度（机器快 vs 人类慢）
- 滚动模式（瞬间滚动 vs 渐进滚动）
- 页面停留时间

**3. 浏览器指纹**
- Canvas 指纹
- WebGL 指纹
- 字体列表
- 屏幕分辨率 + 颜色深度
- 时区和语言

**4. IP 和行为关联**
- 同一IP多账号
- 请求频率异常
- 地理位置与行为不符

## 基础反检测策略

### 1. 浏览器配置

**禁用自动化标志：**
```python
# Playwright
browser = p.chromium.launch(
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process',
    ]
)
```

**设置真实 User-Agent：**
```python
context = browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)
```

### 2. 行为模拟

**随机延迟：**
```python
import random
import time

def random_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

# 使用
page.click('#button')
random_delay(1, 3)  # 1-3秒随机延迟
```

**人类化鼠标移动：**
```python
from playwright.sync_api import sync_playwright
import random

def human_like_click(page, selector):
    # 获取元素位置
    box = page.locator(selector).bounding_box()
    
    # 随机偏移（不点击正中心）
    x = box['x'] + random.randint(5, box['width'] - 5)
    y = box['y'] + random.randint(5, box['height'] - 5)
    
    # 移动鼠标（贝塞尔曲线）
    page.mouse.move(x, y, steps=random.randint(5, 10))
    
    # 随机延迟后点击
    time.sleep(random.uniform(0.1, 0.3))
    page.mouse.click(x, y)
```

**自然滚动：**
```python
def smooth_scroll(page, distance):
    """模拟人类滚动行为"""
    steps = random.randint(5, 15)
    step_distance = distance // steps
    
    for _ in range(steps):
        page.mouse.wheel(0, step_distance)
        time.sleep(random.uniform(0.1, 0.3))
```

### 3. 浏览器指纹管理

**使用指纹浏览器：**

| 工具 | 特点 | 价格 |
|------|------|------|
| **AdsPower** | 中文支持好，功能全面 | $10/月起 |
| **Dolphin Anty** | 俄罗斯产品，性价比高 | $10/月起 |
| **Multilogin** | 老牌工具，稳定可靠 | $99/月起 |
| **GoLogin** | 云端方案，便携 | $49/月起 |

**指纹浏览器核心功能：**
- Canvas/ WebGL 指纹随机化
- 时区和地理位置模拟
- 屏幕分辨率多样化
- 字体和插件列表定制
- Cookie 和缓存隔离

## 高级反检测策略

### 1. 代理IP管理

**代理类型选择：**

| 类型 | 匿名性 | 速度 | 价格 | 适用场景 |
|------|--------|------|------|---------|
| 数据中心 | 低 | 快 | 低 | 低安全性网站 |
| 静态住宅 | 中 | 中 | 中 | 中等安全性 |
| 动态住宅 | 高 | 中 | 高 | 高安全性网站 |
| 移动代理 | 极高 | 慢 | 极高 | 最高安全性 |

**IP轮换策略：**
```python
# 每个账号固定IP（推荐）
account_ip_map = {
    'account_1': 'http://proxy1:port',
    'account_2': 'http://proxy2:port',
}

# 请求失败时切换IP
def get_proxy(account):
    return account_ip_map.get(account)
```

### 2. 请求频率控制

**自适应速率限制：**
```python
import time
import random

class RateLimiter:
    def __init__(self, base_delay=2):
        self.base_delay = base_delay
        self.last_request = 0
    
    def wait(self):
        elapsed = time.time() - self.last_request
        delay = self.base_delay + random.uniform(0, 2)
        
        if elapsed < delay:
            time.sleep(delay - elapsed)
        
        self.last_request = time.time()

# 使用
limiter = RateLimiter(base_delay=3)
limiter.wait()  # 每次请求前调用
```

### 3. Cookie和缓存管理

**真实浏览痕迹：**
```python
# 先访问相关页面建立痕迹
page.goto('https://google.com')
page.goto('https://target-site.com')

# 随机点击几个页面
links = page.query_selector_all('a')
for link in random.sample(links, min(3, len(links))):
    link.click()
    time.sleep(random.uniform(2, 5))
    page.go_back()
```

### 4. 验证码处理

**常见验证码类型：**

| 类型 | 处理方式 | 工具 |
|------|---------|------|
| 图片验证码 | OCR识别 | Tesseract、2Captcha |
| reCAPTCHA v2 | 点击验证 | 2Captcha、Anti-Captcha |
| reCAPTCHA v3 | 分数绕过 | 行为优化、指纹管理 |
| hCaptcha | 类似reCAPTCHA | 同上 |
| 滑块验证码 | 轨迹模拟 | 自定义算法 |

**验证码服务价格：**
- 2Captcha: $0.5-3/千次
- Anti-Captcha: $2-10/千次

## 检测与反制案例

### 案例1：Cloudflare 5秒盾

**检测原理：**
- JavaScript挑战
- 浏览器指纹验证
- TLS指纹检测

**解决方案：**
```python
# 使用undetected-chromedriver或类似工具
# 等待挑战完成
page.wait_for_selector('.cf-browser-verification', state='hidden')
```

### 案例2：DataDome Bot检测

**检测原理：**
- 行为指纹分析
- 设备指纹验证
- 挑战-响应机制

**解决方案：**
1. 使用高质量住宅代理
2. 指纹浏览器环境
3. 人类化操作间隔

### 案例3：PerimeterX (Human)

**检测原理：**
- 机器学习行为分析
- 传感器数据收集
- 多维度风险评估

**解决方案：**
1. 真实设备/虚拟机
2. 完整浏览器环境
3. 渐进式交互建立信任

## 最佳实践

### 开发阶段

1. **本地开发**
   - 使用无头模式加快速度
   - 添加详细日志
   - 保存错误截图

2. **测试阶段**
   - 小规模测试账号
   - 监控封禁率
   - 调整参数

3. **生产阶段**
   - 逐步增加账号
   - 实时监控异常
   - 备用方案准备

### 运维监控

**关键指标：**
- 成功率
- 封禁率
- 验证码触发率
- 平均响应时间

**告警阈值：**
```python
# 封禁率超过5%告警
if ban_rate > 0.05:
    send_alert("封禁率过高，需要调整策略")

# 成功率低于90%告警
if success_rate < 0.9:
    send_alert("成功率下降，检查目标网站变更")
```

## 法律和道德边界

### 允许的行为
- 自动化自己的网站
- 公开数据的合理采集
- 授权访问的系统
- 遵守robots.txt的网站

### 禁止的行为
- 未经授权的大规模数据采集
- 破坏网站正常运营
- 自动化攻击
- 侵犯隐私或版权

---

*提示：反检测技术应与良好的网络礼仪相结合，尊重目标网站的服务条款。*
