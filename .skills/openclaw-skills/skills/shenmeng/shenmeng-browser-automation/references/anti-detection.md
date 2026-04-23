# 反检测与反爬虫策略

## ⚠️ 免责声明

本指南仅供学习和技术研究使用。请遵守：
- 目标网站的 robots.txt 和 Terms of Service
- 当地法律法规
- 道德准则，不要对目标网站造成过大负载

---

## 常见的反爬虫检测手段

### 1. IP检测
- **频率限制**：同一IP请求过于频繁
- **IP黑名单**：已知爬虫IP段
- **地理位置**：与正常用户分布不符

### 2. 请求头检测
- **User-Agent**：识别爬虫特征
- **Referer**：检查来源是否合理
- **Accept-Language**：检查语言设置

### 3. 行为检测
- **请求间隔**：过于规律的请求间隔
- **鼠标轨迹**：缺乏人类特征
- **页面停留时间**：异常短或长
- **滚动行为**：不自然的滚动模式

### 4. JavaScript检测
- **浏览器指纹**：Canvas指纹、WebGL指纹
- **WebDriver标志**：检测自动化工具
- **JavaScript执行**：检测页面是否被渲染

### 5. 验证码
- **图像验证码**：OCR识别或人工打码
- **滑块验证码**：轨迹模拟
- **点击验证码**：坐标识别

---

## 反检测策略

### 1. IP代理池

```python
import random

# 代理列表
proxies = [
    'http://user:pass@host1:port',
    'http://user:pass@host2:port',
    'http://user:pass@host3:port',
]

# 随机选择代理
proxy = random.choice(proxies)
```

**代理类型：**
- 数据中心代理：便宜但易被识别
- 住宅代理：贵但更隐蔽
- 移动代理：最贵，最难检测

### 2. User-Agent轮换

```python
import random

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
]

headers = {
    'User-Agent': random.choice(user_agents),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}
```

### 3. 随机延迟

```python
import time
import random

# 随机延迟1-3秒
time.sleep(random.uniform(1, 3))

# 正态分布延迟（更自然）
delay = random.gauss(2, 0.5)  # 均值2秒，标准差0.5
time.sleep(max(0.5, delay))
```

### 4. 模拟人类行为

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # 模拟真实鼠标移动
    page.mouse.move(x, y, steps=10)  # 分10步移动
    
    # 随机点击位置偏移
    offset_x = random.randint(-5, 5)
    offset_y = random.randint(-5, 5)
    element.click(position={'x': offset_x, 'y': offset_y})
    
    # 模拟滚动
    for _ in range(random.randint(3, 8)):
        page.mouse.wheel(0, random.randint(300, 800))
        time.sleep(random.uniform(0.5, 2))
```

### 5. 禁用WebDriver标志

```python
# Playwright
context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
)

# 添加初始化脚本移除webdriver标志
page.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    
    window.chrome = { runtime: {} };
""")
```

### 6. 处理Canvas指纹

```python
page.add_init_script("""
    const originalGetContext = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function(type) {
        const context = originalGetContext.call(this, type);
        if (type === '2d') {
            const originalGetImageData = context.getImageData;
            context.getImageData = function(x, y, w, h) {
                const data = originalGetImageData.call(this, x, y, w, h);
                // 添加随机噪声
                for (let i = 0; i < data.data.length; i += 4) {
                    data.data[i] += Math.random() > 0.5 ? 1 : 0;
                }
                return data;
            };
        }
        return context;
    };
""")
```

---

## 高级反检测技巧

### 1. 使用真实浏览器配置

```python
# 从真实浏览器导出配置
# Chrome: chrome://version/
# 复制用户数据目录，配合Playwright使用

context = browser.new_context(
    storage_state='path/to/cookies.json',  # 使用真实cookies
    user_agent='真实浏览器的UA',
    viewport={'width': 1920, 'height': 1080},
    locale='zh-CN',
    timezone_id='Asia/Shanghai',
)
```

### 2. 使用无头检测绕过

```python
page.add_init_script("""
    // 覆盖Permissions API
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' 
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters)
    );
    
    // 覆盖Plugins
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            return [
                { name: 'Chrome PDF Plugin' },
                { name: 'Native Client' },
            ];
        }
    });
    
    // 覆盖Languages
    Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en']
    });
""")
```

### 3. 请求指纹随机化

```python
import random

def get_random_fingerprint():
    return {
        'screen': {
            'width': random.choice([1920, 1366, 1440, 1536]),
            'height': random.choice([1080, 768, 900, 864]),
            'colorDepth': 24,
        },
        'devicePixelRatio': random.choice([1, 1.25, 1.5, 2]),
        'hardwareConcurrency': random.choice([2, 4, 6, 8, 12]),
        'memory': random.choice([4, 8, 16]),
    }
```

---

## 检测与应对对照表

| 检测手段 | 检测方式 | 应对策略 |
|----------|----------|----------|
| IP频率 | 统计请求次数 | 使用代理池，降低频率 |
| User-Agent | 检查UA字符串 | 轮换真实UA |
| WebDriver | 检查navigator.webdriver | 重写属性为undefined |
| Canvas指纹 | Canvas渲染差异 | 添加随机噪声 |
| WebGL指纹 | GPU渲染差异 | 禁用WebGL或模拟 |
| 鼠标轨迹 | 检查移动模式 | 模拟人类移动 |
| 请求间隔 | 检查时间规律性 | 随机化间隔 |
| JavaScript | 检查执行结果 | 使用真实浏览器 |

---

## 最佳实践

1. **尊重目标网站**
   - 遵守robots.txt
   - 不要造成过大负载
   - 设置合理的请求间隔

2. **渐进式爬取**
   - 从低频开始
   - 逐步增加频率
   - 观察响应变化

3. **多维度伪装**
   - IP + UA + 行为
   - 不要只依赖单一伪装

4. **及时停止**
   - 遇到验证码立即停止
   - 被封IP立即切换
   - 不要硬刚

5. **数据备份**
   - 及时保存已抓取数据
   - 记录成功配置
   - 建立IP/UA池

---

## 道德提醒

反检测技术应当用于：
- 合法的数据采集
- 自动化测试
- 个人学习研究

**不应用于：**
- 窃取商业数据
- 恶意攻击网站
- 违反法律法规

技术无罪，但使用技术的人有责任。
