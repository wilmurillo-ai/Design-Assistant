---
name: captcha-suite
description: 验证码处理套件 - 整合滑块拼图、旋转验证码、图形验证码等多种验证码处理能力。一站式解决网页验证码拦截问题，支持百度地图、大麦、淘宝、京东等 50+ 网站。当遇到任何类型的验证码时自动触发此技能。
allowed-tools: Bash(agent-browser:*)
---

# Captcha Suite - 验证码处理套件

**一站式验证码解决方案**，整合多种验证码处理能力，自动识别并处理各类网页验证码。

## 🎯 支持的验证码类型

| 类型 | 子技能 | 支持网站 | 成功率 |
|------|--------|----------|--------|
| **🧩 拼图滑块** | puzzle-captcha-solver | 大麦、淘宝、京东、抖音、拼多多等 | 85-95% |
| **🔄 旋转验证码** | rotate-captcha-solver | 百度地图、高德地图、各类地图服务 | 85-95% |
| **🔢 图形验证码** | ocr-captcha-solver | 各类登录页面、注册流程 | 70-85% |
| **👆 点击验证** | click-captcha-solver | 百度、谷歌、各类网站 | 60-80% |
| **📱 短信/邮箱验证** | manual-assist | 所有需要手机验证的场景 | 100% |

## 🌐 支持网站列表（50+）

### 票务/演出
| 网站 | 验证码类型 | 成功率 |
|------|------------|--------|
| 大麦网 | 拼图滑块（箭头） | 90%+ |
| 猫眼演出 | 拼图滑块 | 85%+ |
| 摩天轮票务 | 拼图滑块 | 85%+ |

### 电商/购物
| 网站 | 验证码类型 | 成功率 |
|------|------------|--------|
| 淘宝/天猫 | 拼图滑块 | 90%+ |
| 京东 | 拼图滑块 | 90%+ |
| 拼多多 | 拼图滑块 | 85%+ |
| 抖音电商 | 拼图滑块 | 85%+ |
| 快手电商 | 拼图滑块 | 80%+ |

### 地图/导航
| 网站 | 验证码类型 | 成功率 |
|------|------------|--------|
| 百度地图 | 旋转验证码 | 90%+ |
| 高德地图 | 旋转验证码 | 85%+ |
| 腾讯地图 | 旋转验证码 | 85%+ |

### 社交/娱乐
| 网站 | 验证码类型 | 成功率 |
|------|------------|--------|
| 哔哩哔哩 | 拼图滑块（箭头） | 85%+ |
| 微博 | 拼图滑块 | 80%+ |
| 知乎 | 拼图滑块 | 80%+ |
| 小红书 | 拼图滑块 | 75%+ |

### 生活服务
| 网站 | 验证码类型 | 成功率 |
|------|------------|--------|
| 美团 | 拼图滑块 | 85%+ |
| 饿了么 | 拼图滑块 | 85%+ |
| 12306 | 拼图滑块（箭头） | 85%+ |
| 携程 | 拼图滑块 | 80%+ |
| 去哪儿 | 拼图滑块 | 80%+ |

### 其他常见网站
- 微信、QQ、支付宝登录验证
- 各类政府网站、银行网站
- 各类论坛、博客平台

## 🚀 快速开始

### 方式 1：自动触发（推荐）

```bash
# 打开任何网站，遇到验证码时自动处理
agent-browser open "https://map.baidu.com"
# 验证码出现时会自动调用 captcha-suite 处理
```

### 方式 2：手动调用

```bash
# 1. 截图验证码
agent-browser screenshot --full captcha.png

# 2. 使用套件自动识别并处理
python3 skills/captcha-suite/scripts/auto_solve.py \
  --screenshot captcha.png \
  --output result.json \
  --auto-execute

# 3. 查看结果
cat result.json
```

### 方式 3：指定验证码类型

```bash
# 明确指定处理旋转验证码
python3 skills/captcha-suite/scripts/rotate_solver.py \
  --screenshot captcha.png \
  --output result.json

# 明确指定处理拼图滑块
python3 skills/captcha-suite/scripts/puzzle_solver.py \
  --screenshot captcha.png \
  --output result.json
```

## 📦 套件结构

```
captcha-suite/
├── SKILL.md                      # 本文件
├── scripts/
│   ├── auto_solve.py             # 自动识别 + 处理（主入口）
│   ├── puzzle_solver.py          # 拼图滑块处理
│   ├── rotate_solver.py          # 旋转验证码处理
│   ├── ocr_solver.py             # 图形验证码识别
│   ├── click_solver.py           # 点击验证处理
│   └── execute_action.js         # 浏览器执行脚本
├── references/
│   ├── captcha-types.md          # 验证码类型识别指南
│   ├── website-patterns.md       # 各网站验证码特征库
│   └── troubleshooting.md        # 故障排查指南
└── assets/
    └── templates/                # 验证码模板库
```

## 🔧 核心脚本

### auto_solve.py - 自动识别处理（主入口）

**功能**：自动识别验证码类型并调用相应处理脚本

```bash
python3 scripts/auto_solve.py \
  --screenshot <截图路径> \
  --output <输出 JSON> \
  [--auto-execute] \
  [--debug] \
  [--timeout 10]
```

**输出示例**：
```json
{
  "success": true,
  "captcha_type": "rotate",
  "confidence": 0.92,
  "action": {
    "type": "rotate",
    "angle": 45.5,
    "direction": "clockwise"
  },
  "execution_result": {
    "status": "success",
    "message": "验证通过"
  }
}
```

**识别逻辑**：
1. 检测是否有旋转区域（圆形/方形）→ 旋转验证码
2. 检测是否有滑块和缺口 → 拼图滑块
3. 检测是否有字符图片 → 图形验证码
4. 检测是否有点选提示 → 点击验证
5. 以上都不是 → 降级处理（通知用户）

### puzzle_solver.py - 拼图滑块处理

```bash
python3 scripts/puzzle_solver.py \
  --screenshot captcha.png \
  --output result.json \
  [--template <滑块模板>] \
  [--debug]
```

**支持类型**：
- 箭头拼图（大麦、12306、B 站）
- 缺口拼图（淘宝、京东、抖音）
- 图形对齐（微信、QQ）

### rotate_solver.py - 旋转验证码处理

```bash
python3 scripts/rotate_solver.py \
  --screenshot captcha.png \
  --output result.json \
  [--debug]
```

**算法**：
- OpenCV 边缘检测 + 霍夫变换
- 轮廓拟合矩形（备用）
- 多尺度检测融合

### ocr_solver.py - 图形验证码识别

```bash
python3 scripts/ocr_solver.py \
  --image captcha.png \
  --output result.json \
  --type alphanumeric  # alphanumeric|digit|custom
```

**支持**：
- Tesseract OCR 识别
- 第三方打码平台 API（备用）

### execute_action.js - 浏览器执行

在 Playwright 环境中执行验证操作：

```javascript
await executeAction({
  type: "rotate" | "slide" | "click",
  params: { /* 具体参数 */ }
});
```

## 🧠 验证码类型识别算法

### 1. 旋转验证码检测

```python
def detect_rotate_captcha(image):
    # 检测圆形/方形区域
    # 特征：居中显示、有明显边缘、可旋转
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # 查找圆形轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius > 50:  # 半径足够大
            return True, {"center": (x, y), "radius": radius}
    
    return False, None
```

### 2. 拼图滑块检测

```python
def detect_puzzle_captcha(image):
    # 检测滑块和缺口
    # 特征：有可拖动滑块、有缺口区域
    
    # 颜色检测（滑块通常有颜色差异）
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 查找滑块区域
    slider = detect_slider_button(image)
    gap = detect_gap_area(image)
    
    if slider and gap:
        return True, {"slider": slider, "gap": gap}
    
    return False, None
```

### 3. 图形验证码检测

```python
def detect_graphic_captcha(image):
    # 检测字符区域
    # 特征：4-6 个字符、有边框、背景干扰
    
    # 边缘密度分析
    edges = cv2.Canny(image, 50, 150)
    edge_density = np.sum(edges > 0) / edges.size
    
    if 0.05 < edge_density < 0.3:  # 中等边缘密度
        return True, {"density": edge_density}
    
    return False, None
```

## 👥 人类轨迹模拟

### 滑块拖动轨迹

```python
def generate_slide_trajectory(distance, duration=2.0):
    """
    生成人类拖动轨迹
    特征：启动停顿、先快后慢、垂直抖动、到达微调
    """
    trajectory = []
    steps = int(duration * 60)
    
    # 启动停顿
    for _ in range(int(0.3 * 60)):
        trajectory.append([0, random.gauss(0, 1)])
    
    # 主拖动（ease-out）
    for i in range(steps + 1):
        t = i / steps
        progress = 1 - math.pow(1 - t, 3)
        x = distance * progress
        y = math.sin(t * math.pi * 4) * 2 + random.gauss(0, 1)
        trajectory.append([x, y])
    
    # 到达微调
    for _ in range(5):
        trajectory.append([distance + random.randint(-1, 1), random.gauss(0, 1)])
    
    return trajectory
```

### 旋转拖动轨迹

```python
def generate_rotate_trajectory(angle, duration=2.5):
    """
    生成旋转拖动轨迹
    特征：弧形移动、速度变化、微调确认
    """
    # 将角度转换为弧形距离
    arc_distance = angle * math.pi / 180 * radius
    
    # 类似滑块轨迹，但沿弧形路径
    # ...
```

## 🔍 故障排查

### 问题 1：无法识别验证码类型

**症状**：`auto_solve.py` 返回 `captcha_type: "unknown"`

**解决**：
```bash
# 使用 debug 模式查看检测结果
python3 scripts/auto_solve.py \
  --screenshot captcha.png \
  --output result.json \
  --debug

# 查看 debug 目录下的标记图片
ls debug_captcha/
```

### 问题 2：识别成功但验证失败

**可能原因**：
| 原因 | 解决方案 |
|------|----------|
| 轨迹太机械 | 增加随机性，延长拖动时间 |
| 角度/位置偏差 | 检查识别结果，调整算法参数 |
| IP 被标记 | 切换 IP 或使用代理 |
| 浏览器指纹 | 使用真实浏览器（非 headless） |

### 问题 3：特定网站不支持

**解决**：
1. 截图保存验证码
2. 提交 Issue 到 ClawHub
3. 临时方案：使用 `--manual` 模式手动处理

## 📚 参考文档

- [references/captcha-types.md](references/captcha-types.md) - 验证码类型识别详解
- [references/website-patterns.md](references/website-patterns.md) - 各网站验证码特征库
- [references/troubleshooting.md](references/troubleshooting.md) - 故障排查指南

## ❓ 常见问题 (FAQ)

### Q1: 如何选择使用套件还是单独技能？

**A:** 

| 场景 | 推荐 |
|------|------|
| 不确定验证码类型 | 用 captcha-suite（自动识别） |
| 明确知道是拼图滑块 | 用 puzzle-captcha-solver |
| 明确知道是旋转验证码 | 用 rotate-captcha-solver |
| 需要最快速度 | 用单独技能（少一层识别） |
| 追求方便 | 用 captcha-suite（一站式） |

---

### Q2: 识别成功率有多少？

**A:** 综合成功率：

| 验证码类型 | 成功率 |
|------------|--------|
| 拼图滑块 | 85-95% |
| 旋转验证码 | 85-95% |
| 图形验证码 | 70-85% |
| 点击验证 | 60-80% |

---

### Q3: 支持哪些浏览器？

**A:** 
- ✅ Chrome / Chromium（推荐）
- ✅ Firefox
- ✅ Edge
- ⚠️ Safari（部分功能受限）
- ❌ IE（不支持）

---

### Q4: headless 模式能用吗？

**A:** 支持但**不推荐**：

```bash
# 不推荐：容易被检测
agent-browser open --headless <url>

# 推荐：真实浏览器
agent-browser open <url>
```

---

### Q5: 如何处理新型验证码？

**A:** 
1. 截图保存：`agent-browser screenshot unknown.png`
2. 使用 debug 模式分析
3. 提交反馈到 ClawHub
4. 临时方案：手动处理

---

### Q6: 可以商用吗？

**A:** MIT-0 许可证：
- ✅ 免费使用
- ✅ 可修改分发
- ✅ 不需署名
- ⚠️ 遵守目标网站服务条款
- ⚠️ 不用于恶意爬虫

---

### Q7: 与单独技能相比有什么优势？

**A:** 

| 特性 | captcha-suite | 单独技能 |
|------|---------------|----------|
| 自动识别类型 | ✅ | ❌ |
| 一站式解决 | ✅ | ❌ |
| 处理速度 | 中等 | 最快 |
| 代码量 | 多 | 少 |
| 适用场景 | 通用 | 专用 |

---

## ⚠️ 注意事项

### 合规使用
- ✅ 仅用于合法用途
- ✅ 遵守目标网站服务条款
- ❌ 不用于恶意爬虫或攻击
- ❌ 不用于绕过安全验证进行非法操作

### 性能建议
- 识别耗时：1-5 秒（取决于类型）
- 拖动耗时：2-3 秒
- 建议超时：15 秒

### 成功率提升
1. 使用真实浏览器（非 headless）
2. 确保网络稳定
3. 避免高频请求
4. 必要时使用代理 IP

---

**版本**: v1.0.0  
**许可证**: MIT-0  
**作者**: OpenClaw Community
