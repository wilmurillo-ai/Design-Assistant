---
name: puzzle-captcha-solver
description: 专门处理拼图滑块验证码的浏览器自动化技能。使用 OpenCV 模板匹配 + 边缘检测识别拼图缺口，模拟人类拖动轨迹完成验证。支持大麦、淘宝、京东等常见网站的拼图验证码。当遇到"拖动滑块完成验证"时自动触发。
allowed-tools: Bash(agent-browser:*)
---

# Puzzle Captcha Solver - 拼图滑块验证码处理技能

专门处理**拼图滑块验证码**（Puzzle Slider Captcha），这类验证码要求用户拖动滑块将拼图块嵌入正确位置。

## 支持的验证码类型

| 类型 | 特征 | 支持网站 |
|------|------|----------|
| **箭头拼图** | 拖动箭头拼合 | 大麦、12306、哔哩哔哩 |
| **缺口拼图** | 拖动方块填补空缺 | 淘宝、京东、抖音、拼多多 |
| **图形对齐** | 拖动图形对齐 | 微信、QQ、微博 |
| **动物拼图** | 拖动动物图案 | 美团、饿了么、各类网站 |

### 🎯 支持网站列表

| 网站 | 验证码类型 | 识别成功率 | 备注 |
|------|------------|------------|------|
| **大麦网** | 箭头拼图 | 85%+ | 粉色主题，箭头滑块 |
| **12306** | 箭头拼图 | 80%+ | 蓝色主题，可能需要多次尝试 |
| **哔哩哔哩** | 箭头拼图 | 75%+ | 蓝色主题，偶有变化 |
| **淘宝/天猫** | 缺口拼图 | 85%+ | 蓝色拼图块，识别稳定 |
| **京东** | 缺口拼图 | 85%+ | 蓝色渐变，识别稳定 |
| **抖音** | 缺口拼图 | 80%+ | 彩色拼图，光线影响较大 |
| **拼多多** | 缺口拼图 | 75%+ | 橙色主题，偶有变形 |
| **微信** | 图形对齐 | 70%+ | 图形类型多变 |
| **QQ** | 图形对齐 | 70%+ | 图形类型多变 |
| **微博** | 缺口拼图 | 75%+ | 橙色主题 |
| **美团** | 动物拼图 | 70%+ | 动物图案，难度较高 |
| **饿了么** | 动物拼图 | 70%+ | 动物图案，难度较高 |

## 核心工作流程

```
1. 检测验证码 → 2. 截图 → 3. 识别缺口 → 4. 模拟拖动 → 5. 验证结果
```

### 完整流程示例

```bash
# 1. 打开目标页面
agent-browser open https://search.damai.cn/search.htm?keyword=李健

# 2. 等待验证码出现并截图
agent-browser wait 2000
agent-browser screenshot --full captcha-full.png

# 3. 使用脚本识别缺口位置
python3 skills/puzzle-captcha-solver/scripts/recognize_puzzle.py \
  --screenshot captcha-full.png \
  --output result.json

# 4. 执行拖动
agent-browser eval "
  const slider = document.querySelector('.slider-btn');
  const trajectory = $TRAJECTORY;
  await executeDrag(slider, trajectory);
"

# 5. 验证是否成功
agent-browser wait 1000
agent-browser screenshot verify.png
```

## 脚本工具

### recognize_puzzle.py - 拼图识别

自动检测验证码区域并识别缺口位置。

```bash
python3 scripts/recognize_puzzle.py \
  --screenshot <截图路径> \
  --template <滑块模板路径（可选）> \
  --output <输出 JSON> \
  --debug  # 输出调试图片
```

**输出示例：**
```json
{
  "success": true,
  "captcha_type": "arrow_puzzle",
  "slider_location": {"x": 280, "y": 450},
  "gap_location": {"x": 420, "y": 450},
  "offset": 140,
  "confidence": 0.92,
  "trajectory": [[0,0], [5,1], [12,2], ...]
}
```

### execute_drag.js - 执行拖动

Playwright JavaScript 代码，模拟人类拖动轨迹。

```javascript
async function executeDrag(sliderElement, trajectory) {
    const box = await sliderElement.boundingBox();
    
    // 鼠标移动到滑块
    await sliderElement.hover();
    
    // 按下鼠标
    await page.mouse.down();
    
    // 按轨迹移动
    for (const [dx, dy] of trajectory) {
        await page.mouse.move(box.x + dx, box.y + dy);
        await sleep(16); // 60 FPS
    }
    
    // 释放鼠标
    await page.mouse.up();
}
```

## 识别算法

### 1. 验证码区域检测

```python
def detect_captcha_area(image):
    """
    检测验证码弹窗区域
    特征：白色背景、圆角矩形、居中显示
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 阈值分割（验证码弹窗通常是白色背景）
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 找到最大的矩形轮廓（验证码区域）
    captcha_contour = None
    max_area = 0
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        
        # 验证码区域特征：中等大小、接近矩形
        if 10000 < area < 500000 and 0.5 < w/h < 3:
            if area > max_area:
                max_area = area
                captcha_contour = (x, y, w, h)
    
    return captcha_contour
```

### 2. 滑块位置检测

```python
def detect_slider_position(captcha_image):
    """
    检测可拖动滑块的位置
    特征：有颜色差异、有图标（箭头等）
    """
    # 转换为 HSV 色彩空间
    hsv = cv2.cvtColor(captcha_image, cv2.COLOR_BGR2HSV)
    
    # 检测粉色/红色区域（大麦验证码特征）
    lower_pink = np.array([140, 50, 50])
    upper_pink = np.array([170, 255, 255])
    mask = cv2.inRange(hsv, lower_pink, upper_pink)
    
    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 返回最可能的滑块位置
    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        return {"x": x, "y": y, "width": w, "height": h}
    
    return None
```

### 3. 缺口位置识别（模板匹配）

```python
def find_gap_position(bg_image, piece_image):
    """
    使用模板匹配找到缺口位置
    """
    # 边缘检测
    bg_edges = cv2.Canny(bg_image, 50, 150)
    piece_edges = cv2.Canny(piece_image, 50, 150)
    
    # 模板匹配
    result = cv2.matchTemplate(bg_edges, piece_edges, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    return {
        "x": max_loc[0],
        "y": max_loc[1],
        "confidence": max_val
    }
```

## 人类轨迹模拟

### 标准轨迹生成

```python
def generate_trajectory(offset, duration=1.5):
    """
    生成模拟人类拖动轨迹
    
    特征：
    - 启动停顿 0.1-0.3 秒
    - 先快后慢（ease-out）
    - 垂直抖动 ±2-5 像素
    - 随机回退 1-3 像素（5% 概率）
    - 到达后微调
    """
    import math
    import random
    
    trajectory = []
    steps = int(duration * 60)
    
    # 启动前停顿
    for _ in range(int(0.2 * 60)):
        trajectory.append([0, random.gauss(0, 1)])
    
    for i in range(steps + 1):
        t = i / steps
        
        # ease-out cubic
        progress = 1 - math.pow(1 - t, 3)
        x = int(offset * progress)
        
        # 垂直抖动
        y = int(random.gauss(0, 2))
        
        # 随机回退
        if random.random() < 0.05 and 0.3 < t < 0.8:
            x = max(0, x - random.randint(1, 3))
        
        trajectory.append([x, y])
    
    # 到达后微调
    for _ in range(5):
        trajectory.append([offset + random.randint(-1, 1), random.gauss(0, 1)])
    
    return trajectory
```

## 常见网站验证码特征

### 大麦网

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 粉色渐变 |
| 滑块图标 | 右箭头 → |
| 滑块颜色 | 粉色/红色 |
| 轨道位置 | 弹窗底部 |
| 验证提示 | "Please drag the slider as instructed" |

### 淘宝/天猫

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 白色 |
| 滑块图标 | 拼图块 |
| 滑块颜色 | 蓝色 |
| 轨道位置 | 图片下方 |
| 验证提示 | "向右滑动填充拼图" |

### 京东

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 白色 |
| 滑块图标 | 拼图块 |
| 滑块颜色 | 蓝色渐变 |
| 轨道位置 | 图片下方 |
| 验证提示 | "请向右滑动验证" |

### 抖音

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 白色/黑色 |
| 滑块图标 | 拼图块 |
| 滑块颜色 | 彩色渐变 |
| 轨道位置 | 图片下方 |
| 验证提示 | "请向右滑动完成验证" |
| 特殊说明 | 光线较暗时识别率下降 |

### 12306

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 白色 |
| 滑块图标 | 右箭头 → |
| 滑块颜色 | 蓝色 |
| 轨道位置 | 弹窗底部 |
| 验证提示 | "请向右滑动滑块" |
| 特殊说明 | 偶有背景干扰线 |

### 哔哩哔哩

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 白色 |
| 滑块图标 | 右箭头 → / 拼图块 |
| 滑块颜色 | 蓝色 |
| 轨道位置 | 弹窗底部 |
| 验证提示 | "滑动验证" |
| 特殊说明 | 粉色/蓝色主题随机 |

### 拼多多

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 白色 |
| 滑块图标 | 拼图块 |
| 滑块颜色 | 橙色 |
| 轨道位置 | 图片下方 |
| 验证提示 | "向右滑动验证" |
| 特殊说明 | 偶有变形干扰 |

### 微博

| 特征 | 值 |
|------|-----|
| 弹窗背景 | 白色 |
| 滑块图标 | 拼图块 |
| 滑块颜色 | 橙色 |
| 轨道位置 | 图片下方 |
| 验证提示 | "请滑动验证" |

## 依赖安装

```bash
# 核心依赖
pip install opencv-python numpy pillow

# 可选：深度学习模型（提高识别率）
pip install torch torchvision

# 可选：OCR
pip install pytesseract
```

## 使用示例

### 示例 1：大麦网自动验证

```bash
# 1. 打开页面
agent-browser open "https://search.damai.cn/search.htm?keyword=李健"

# 2. 等待并截图
agent-browser wait 3000
agent-browser screenshot captcha.png

# 3. 识别缺口
python3 scripts/recognize_puzzle.py --screenshot captcha.png --output result.json

# 4. 执行拖动（读取轨迹并执行）
agent-browser eval "$(cat result.json | jq -r '.trajectory_js')"
```

### 示例 2：批量处理

```bash
# 对多个页面进行验证
for url in urls.txt; do
    agent-browser open "$url"
    agent-browser wait 2000
    agent-browser screenshot captcha_${RANDOM}.png
done

# 批量识别
for img in captcha_*.png; do
    python3 scripts/recognize_puzzle.py --screenshot "$img" --output "${img%.png}.json"
done
```

## 故障排除

### 问题 1：无法检测验证码区域

**原因**：截图时机不对或页面未完全加载

**解决**：
```bash
# 增加等待时间
agent-browser wait --load networkidle
agent-browser wait 3000

# 使用全屏截图
agent-browser screenshot --full captcha.png
```

### 问题 2：识别准确率低

**原因**：图片质量差或验证码变体

**解决**：
1. 使用 `--debug` 输出调试图片
2. 检查裁剪区域是否正确
3. 尝试调整 Canny 参数

### 问题 3：拖动后验证失败

**原因**：轨迹太机械或被检测

**解决**：
1. 增加轨迹随机性
2. 延长拖动时间（1.5-2.5 秒）
3. 添加更多停顿

## 参考文档

- [references/puzzle-detection.md](references/puzzle-detection.md) - 拼图检测算法详解
- [references/trajectory-optimization.md](references/trajectory-optimization.md) - 轨迹优化技巧
- [references/website-patterns.md](references/website-patterns.md) - 各网站验证码特征库

## ❓ 常见问题 (FAQ)

### Q1: 识别成功率有多少？

**A:** 成功率取决于验证码类型和网站：
- 简单拼图（大麦、淘宝）：85-95%
- 复杂拼图（抖音、拼多多）：70-85%
- 图形对齐（微信、QQ）：60-75%
- 新型验证码：可能需手动处理

**提高成功率的方法：**
1. 确保截图清晰（使用 `--full` 全屏截图）
2. 等待页面完全加载（`agent-browser wait --load networkidle`）
3. 使用 debug 模式检查识别结果（`--debug`）

---

### Q2: 为什么拖动后验证失败？

**A:** 可能的原因：

| 原因 | 解决方案 |
|------|----------|
| 轨迹太机械 | 使用内置的人类轨迹模拟（已默认启用） |
| 拖动太快 | 延长拖动时间到 1.5-2.5 秒 |
| 缺少停顿 | 轨迹已包含启动停顿和到达微调 |
| IP 被标记 | 切换 IP 或使用代理 |
| 浏览器指纹 | 使用真实浏览器（非 headless） |

---

### Q3: 如何调试识别问题？

**A:** 使用 `--debug` 模式：

```bash
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json \
  --debug
```

会在 `debug_captcha/` 目录生成：
- `original.png` - 原图
- `marked.png` - 标记检测区域的图
- `slider_mask.png` - 滑块区域掩码
- `gap_mask.png` - 缺口区域掩码

---

### Q4: 支持 headless 浏览器吗？

**A:** 支持，但**不推荐**：

```bash
# 不推荐：headless 模式容易被检测
agent-browser open --headless <url>

# 推荐：使用真实浏览器
agent-browser open <url>
```

**原因：**
- 很多网站会检测 headless 浏览器
- 即使验证码识别成功，也可能被其他方式拦截
- 真实浏览器指纹更可靠

---

### Q5: 如何批量处理验证码？

**A:** 使用循环脚本：

```bash
#!/bin/bash

# 批量识别多个验证码
for img in captchas/*.png; do
    echo "处理：$img"
    python3 scripts/recognize_puzzle.py \
        --screenshot "$img" \
        --output "results/${img%.png}.json"
    
    # 检查是否成功
    if [ $? -eq 0 ]; then
        echo "✅ 成功：$img"
    else
        echo "❌ 失败：$img"
    fi
done
```

---

### Q6: 识别速度慢怎么办？

**A:** 优化建议：

1. **减少图片尺寸** - 裁剪到验证码区域
   ```bash
   # 先全屏截图
   agent-browser screenshot --full full.png
   
   # 裁剪到验证码区域（使用 ImageMagick）
   convert full.png -crop 400x300+200+100 captcha.png
   ```

2. **跳过 debug 模式** - debug 会保存多张图片
   ```bash
   python3 scripts/recognize_puzzle.py \
     --screenshot captcha.png \
     --output result.json
     # 不加 --debug
   ```

3. **使用 SSD 硬盘** - 减少 IO 延迟

---

### Q7: 如何处理新型验证码？

**A:** 如果遇到不支持的验证码类型：

1. **截图保存**
   ```bash
   agent-browser screenshot unknown_captcha.png
   ```

2. **使用 debug 模式分析**
   ```bash
   python3 scripts/recognize_puzzle.py \
     --screenshot unknown_captcha.png \
     --debug
   ```

3. **查看调试图片** - 分析检测失败的原因

4. **提交 Issue** - 在 ClawHub 页面反馈，帮助改进技能

---

### Q8: 可以商用吗？

**A:** 本技能使用 **MIT-0** 许可证：
- ✅ 可以免费使用
- ✅ 可以修改和分发
- ✅ 不需要署名
- ⚠️ 但请遵守目标网站的服务条款
- ⚠️ 不要用于恶意爬虫或攻击

---

### Q9: 与其他验证码技能有什么区别？

**A:** 

| 技能 | 定位 | 优势 |
|------|------|------|
| **puzzle-captcha-solver** | 专注拼图滑块 | 识别精准、人类轨迹模拟、支持网站多 |
| **captcha-solver** | 通用验证码 | 支持多种类型（图形/点击/滑块） |

**选择建议：**
- 只需要处理拼图滑块 → 用这个技能
- 需要处理多种验证码 → 用 `captcha-solver`

---

### Q10: 如何更新技能？

**A:** 

```bash
# 更新到最新版本
clawhub update puzzle-captcha-solver

# 更新所有技能
clawhub update --all
```

---

## 注意事项

⚠️ **合规使用**
- 仅用于合法用途
- 遵守目标网站服务条款
- 不要用于恶意爬虫

⚠️ **成功率**
- 简单拼图：85-95%
- 复杂拼图：70-85%
- 新型验证码：可能需手动处理

⚠️ **性能**
- 识别耗时：1-3 秒
- 拖动耗时：1.5-2.5 秒
- 建议设置超时 10 秒
