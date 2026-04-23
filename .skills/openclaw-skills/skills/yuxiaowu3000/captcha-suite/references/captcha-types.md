# 验证码类型识别指南

本文档详细介绍如何识别不同类型的验证码，帮助选择正确的处理方式。

## 验证码类型总览

| 类型 | 特征 | 处理方式 | 难度 |
|------|------|----------|------|
| 🧩 拼图滑块 | 拖动滑块拼合图片 | OpenCV 缺口识别 | ⭐⭐ |
| 🔄 旋转验证码 | 旋转图片到正确角度 | 霍夫变换测角度 | ⭐⭐ |
| 🔢 图形验证码 | 输入 4-6 位字符 | OCR 识别 | ⭐⭐⭐ |
| 👆 点击验证 | 点击特定文字/物体 | 图像识别/打码平台 | ⭐⭐⭐⭐ |
| 📱 短信/邮箱 | 接收验证码输入 | 用户手动处理 | ⭐ |

---

## 1. 拼图滑块验证码

### 视觉特征

```
┌─────────────────────────┐
│   [图片区域]            │
│   ┌───┐                 │
│   │ ▓ │  ← 缺口         │
│   └───┘                 │
│                         │
│ [▒▒▒▒] → 滑块按钮       │
└─────────────────────────┘
```

### 检测要点

1. **滑块按钮**：通常位于底部或侧面，有颜色差异
2. **缺口区域**：图片中有明显缺失部分
3. **拖动轨道**：滑块可左右移动

### 常见变体

| 变体 | 特征 | 网站 |
|------|------|------|
| 箭头拼图 | 滑块是箭头图标 | 大麦、12306、B 站 |
| 缺口拼图 | 方块拼图块 | 淘宝、京东、抖音 |
| 图形对齐 | 两个图形对齐 | 微信、QQ |

### 识别代码

```python
def detect_puzzle_captcha(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # 检测滑块颜色
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if 1000 < area < 20000:
            return True  # 检测到滑块
    
    return False
```

---

## 2. 旋转验证码

### 视觉特征

```
┌─────────────────────────┐
│      ┌───────┐          │
│     /         \         │
│    |  图片     |  ← 圆形 │
│     \         /         │
│      └───────┘          │
│                         │
│ [▒▒▒▒] → 旋转滑块       │
└─────────────────────────┘
```

### 检测要点

1. **圆形/方形区域**：居中显示，可旋转
2. **旋转滑块**：通常位于下方，可左右拖动
3. **倾斜图片**：图片内容明显倾斜

### 常见变体

| 变体 | 特征 | 网站 |
|------|------|------|
| 圆形旋转 | 圆形图片区域 | 百度地图、高德地图 |
| 方形旋转 | 方形图片区域 | 各类登录页面 |
| 图标旋转 | 旋转图标到指定方向 | 各类验证场景 |

### 识别代码

```python
def detect_rotate_captcha(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 10000:
            continue
        
        (x, y), radius = cv2.minEnclosingCircle(contour)
        circle_area = np.pi * radius * radius
        
        if area / circle_area > 0.7:  # 接近圆形
            return True
    
    return False
```

---

## 3. 图形验证码

### 视觉特征

```
┌─────────────────┐
│  A 7 K 9        │  ← 字符
│  ~~~~           │  ← 干扰线
└─────────────────┘
[________]         ← 输入框
```

### 检测要点

1. **字符区域**：4-6 个字母/数字
2. **干扰元素**：噪点、干扰线、背景纹理
3. **输入框**：下方有文本输入框

### 常见变体

| 变体 | 特征 | 难度 |
|------|------|------|
| 字母数字 | A-Z, 0-9 | ⭐⭐ |
| 中文验证码 | 汉字识别 | ⭐⭐⭐⭐ |
| 计算题 | 12+5=? | ⭐⭐ |
| 问题验证 | "点击最大的动物" | ⭐⭐⭐⭐ |

### 识别代码

```python
def detect_graphic_captcha(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    edge_density = np.sum(edges > 0) / edges.size
    
    # 图形验证码通常有中等边缘密度
    if 0.05 < edge_density < 0.3:
        return True
    
    return False
```

---

## 4. 点击验证

### 视觉特征

```
┌─────────────────────────┐
│  请点击所有的"红绿灯"    │  ← 提示
│                         │
│  [图 1] [图 2] [图 3]   │
│  [图 4] [图 5] [图 6]   │  ← 九宫格
│  [图 7] [图 8] [图 9]   │
│                         │
│  [确认]                 │
└─────────────────────────┘
```

### 检测要点

1. **文字提示**：要求点击特定物体
2. **九宫格/多图片**：多个小图片排列
3. **确认按钮**：点击后提交

### 常见变体

| 变体 | 特征 | 难度 |
|------|------|------|
| 文字点击 | "点击所有汉字" | ⭐⭐⭐ |
| 物体识别 | "点击所有汽车" | ⭐⭐⭐⭐ |
| 顺序点击 | "按顺序点击 1-5" | ⭐⭐⭐ |
| 滑块 + 点击 | 组合验证 | ⭐⭐⭐⭐ |

---

## 5. 短信/邮箱验证

### 视觉特征

```
┌─────────────────────────┐
│  请输入验证码           │
│  [______]               │  ← 输入框
│  [获取验证码]           │  ← 按钮
│                         │
│  已发送到 138****1234   │
└─────────────────────────┘
```

### 检测要点

1. **手机号/邮箱显示**：部分隐藏的联系方式
2. **获取验证码按钮**：可点击发送
3. **输入框**：4-6 位数字输入

### 处理方式

这类验证码**无法自动处理**，需要：
1. 截图通知用户
2. 用户查看手机/邮箱
3. 用户输入验证码
4. 继续自动化流程

---

## 识别流程图

```
开始
  ↓
截图分析
  ↓
┌─────────────────────┐
│ 检测圆形/方形区域？  │
└─────────────────────┘
         ↓ 是
    🔄 旋转验证码
         ↓ 否
┌─────────────────────┐
│ 检测滑块按钮？       │
└─────────────────────┘
         ↓ 是
    🧩 拼图滑块
         ↓ 否
┌─────────────────────┐
│ 检测字符区域？       │
└─────────────────────┘
         ↓ 是
    🔢 图形验证码
         ↓ 否
┌─────────────────────┐
│ 检测点击提示？       │
└─────────────────────┘
         ↓ 是
    👆 点击验证
         ↓ 否
┌─────────────────────┐
│ 检测短信/邮箱输入？  │
└─────────────────────┘
         ↓ 是
    📱 手动处理
         ↓ 否
    ❓ 未知类型
```

---

## 置信度评估

### 高置信度（>0.8）

- 检测到明显圆形/方形区域
- 检测到彩色滑块按钮
- 有明确的验证提示文字

### 中置信度（0.5-0.8）

- 边缘特征符合但不明显
- 颜色差异较小
- 需要进一步分析

### 低置信度（<0.5）

- 特征模糊
- 新型验证码
- 建议降级处理（通知用户）

---

## 调试技巧

### 1. 保存检测中间结果

```python
# 保存边缘检测结果
cv2.imwrite("debug_edges.png", edges)

# 保存标记图
marked = image.copy()
cv2.circle(marked, (cx, cy), radius, (0, 255, 0), 2)
cv2.imwrite("debug_marked.png", marked)
```

### 2. 多尺度检测

```python
scales = [0.5, 0.75, 1.0, 1.25]
for scale in scales:
    resized = cv2.resize(image, None, fx=scale, fy=scale)
    # 在每个尺度上检测
```

### 3. 多方法融合

```python
# 同时使用多种方法检测
rotate_score = detect_by_circle(image)
puzzle_score = detect_by_slider(image)

# 选择得分最高的
if rotate_score > puzzle_score:
    return "rotate"
else:
    return "puzzle"
```

---

## 性能优化

### 1. ROI 裁剪

```python
# 只处理验证码区域，不处理整页
x, y, w, h = detect_captcha_area(image)
roi = image[y:y+h, x:x+w]
```

### 2. 图像缩放

```python
# 大图先缩小
if image.shape[0] > 600:
    scale = 600 / image.shape[0]
    image = cv2.resize(image, None, fx=scale, fy=scale)
```

### 3. 缓存结果

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def detect_type(image_hash):
    # 检测逻辑
    pass
```

---

## 参考资源

- [OpenCV 文档](https://docs.opencv.org/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [2Captcha API](https://2captcha.com/api)
