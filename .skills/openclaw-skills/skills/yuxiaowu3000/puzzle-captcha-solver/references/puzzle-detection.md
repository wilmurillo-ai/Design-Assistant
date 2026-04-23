# 拼图检测算法详解

## 拼图验证码类型

### 1. 箭头拼图（大麦网）

**特征：**
- 滑块是箭头图标（→）
- 背景通常是粉色/渐变色
- 轨道在弹窗底部
- 提示文字："Please drag the slider"

**识别方法：**
```python
# 1. 颜色检测（粉色区域）
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
lower_pink = np.array([140, 50, 50])
upper_pink = np.array([170, 255, 255])
mask = cv2.inRange(hsv, lower_pink, upper_pink)

# 2. 查找滑块轮廓
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 3. 选择底部区域的轮廓（滑块在底部）
```

### 2. 缺口拼图（淘宝、京东）

**特征：**
- 滑块是拼图块形状
- 背景是图片
- 缺口在图片右侧
- 提示文字："向右滑动填充拼图"

**识别方法：**
```python
# 1. 边缘检测
edges = cv2.Canny(image, 50, 150)

# 2. 模板匹配（滑块 vs 背景）
result = cv2.matchTemplate(bg_edges, piece_edges, cv2.TM_CCOEFF_NORMED)

# 3. 找到最佳匹配位置
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
```

### 3. 图形对齐（微信、QQ）

**特征：**
- 需要对齐两个图形
- 通常是左右拖动
- 图形可能是动物、文字等

**识别方法：**
```python
# 1. 检测两个图形的位置
# 2. 计算对齐所需的偏移量
# 3. 生成拖动轨迹
```

## 核心算法

### 边缘检测（Canny）

```python
def detect_edges(image):
    """边缘检测"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 高斯模糊（去噪）
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Canny 边缘检测
    edges = cv2.Canny(blurred, 50, 150)
    
    return edges
```

**参数说明：**
- `threshold1=50`：低阈值（弱边缘）
- `threshold2=150`：高阈值（强边缘）
- 弱边缘和强边缘之间的像素会被分类为边缘或非边缘

### 模板匹配

```python
def match_template(bg_image, piece_image):
    """模板匹配找到缺口位置"""
    
    # 边缘检测
    bg_edges = cv2.Canny(bg_image, 50, 150)
    piece_edges = cv2.Canny(piece_image, 50, 150)
    
    # 模板匹配
    result = cv2.matchTemplate(bg_edges, piece_edges, cv2.TM_CCOEFF_NORMED)
    
    # 获取最佳匹配位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    return {
        "x": max_loc[0],
        "y": max_loc[1],
        "confidence": max_val
    }
```

**匹配方法对比：**

| 方法 | 常量 | 说明 |
|------|------|------|
| 平方差 | `TM_SQDIFF` | 值越小越匹配 |
| 归一化平方差 | `TM_SQDIFF_NORMED` | 0-1，越小越匹配 |
| 相关 | `TM_CCORR` | 值越大越匹配 |
| 归一化相关 | `TM_CCORR_NORMED` | 0-1，越大越匹配 |
| 相关系数 | `TM_CCOEFF` | 值越大越匹配 |
| **归一化相关系数** | `TM_CCOEFF_NORMED` | **-1 到 1，越大越匹配（最常用）** |

### 轮廓检测

```python
def find_contours(image):
    """查找轮廓"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 阈值分割
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 查找轮廓
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 筛选轮廓
    valid_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 1000 < area < 50000:  # 面积筛选
            x, y, w, h = cv2.boundingRect(contour)
            if 0.5 < w/h < 3.0:  # 长宽比筛选
                valid_contours.append(contour)
    
    return valid_contours
```

## 缺口位置推算

对于无法直接检测缺口的情况，可以使用以下策略：

### 策略 1：基于滑块位置推算

```python
def estimate_gap_from_slider(slider_x, captcha_width):
    """
    基于滑块位置推算缺口位置
    
    经验法则：
    - 缺口通常在滑块的右侧
    - 缺口在验证码区域的 60-80% 位置
    """
    # 缺口在验证码区域的 65% 位置
    gap_x = int(captcha_width * 0.65)
    
    # 计算偏移量
    offset = gap_x - slider_x
    
    return offset
```

### 策略 2：基于常见模式

```python
COMMON_OFFSETS = {
    "damai": (120, 180),    # 大麦网常见偏移范围
    "taobao": (100, 200),   # 淘宝常见偏移范围
    "jd": (150, 250),       # 京东常见偏移范围
}

def get_common_offset_range(website):
    """获取常见偏移范围"""
    return COMMON_OFFSETS.get(website, (100, 200))
```

## 调试技巧

### 1. 可视化检测结果

```python
def visualize_detection(image, captcha_area, slider_area, gap_area):
    """可视化检测结果"""
    marked = image.copy()
    
    # 验证码区域（绿色）
    if captcha_area:
        cv2.rectangle(marked, 
                     (captcha_area["x"], captcha_area["y"]),
                     (captcha_area["x"]+captcha_area["w"], 
                      captcha_area["y"]+captcha_area["h"]),
                     (0, 255, 0), 2)
    
    # 滑块区域（蓝色）
    if slider_area:
        cv2.rectangle(marked,
                     (slider_area["x"], slider_area["y"]),
                     (slider_area["x"]+slider_area["w"],
                      slider_area["y"]+slider_area["h"]),
                     (255, 0, 0), 2)
    
    # 缺口区域（红色）
    if gap_area:
        cv2.rectangle(marked,
                     (gap_area["x"], gap_area["y"]),
                     (gap_area["x"]+gap_area["w"],
                      gap_area["y"]+gap_area["h"]),
                     (0, 0, 255), 2)
    
    cv2.imwrite("debug_result.png", marked)
```

### 2. 保存中间结果

```python
# 保存各阶段图片
cv2.imwrite("debug_original.png", image)
cv2.imwrite("debug_gray.png", gray)
cv2.imwrite("debug_edges.png", edges)
cv2.imwrite("debug_mask.png", mask)
```

### 3. 打印调试信息

```python
print(f"图片尺寸：{width}x{height}")
print(f"验证码区域：{captcha_area}")
print(f"滑块位置：{slider_area}")
print(f"缺口位置：{gap_area}")
print(f"计算偏移量：{offset}")
```

## 常见问题

### Q1: 检测不到验证码弹窗

**可能原因：**
- 截图时机不对（页面未加载完成）
- 弹窗样式变化
- 背景颜色不是白色

**解决方法：**
```python
# 1. 增加等待时间
agent-browser wait --load networkidle
agent-browser wait 3000

# 2. 调整阈值
_, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
# 改为
_, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)

# 3. 使用边缘检测
edges = cv2.Canny(gray, 50, 150)
```

### Q2: 滑块位置检测错误

**可能原因：**
- 滑块颜色与背景接近
- 有多个相似颜色区域

**解决方法：**
```python
# 1. 限制搜索区域（底部）
bottom_mask = mask[int(height*0.4):, :]

# 2. 增加面积筛选
if 500 < area < 20000:
    # 有效滑块

# 3. 使用模板匹配
result = cv2.matchTemplate(image, arrow_template, cv2.TM_CCOEFF_NORMED)
```

### Q3: 偏移量计算不准确

**可能原因：**
- 缺口位置检测错误
- 滑块起始位置计算错误

**解决方法：**
```python
# 1. 验证偏移量范围
if offset < 50 or offset > 400:
    print(f"警告：偏移量异常 {offset}")

# 2. 使用多次检测取平均
offsets = []
for _ in range(3):
    offset = calculate_offset()
    if 50 < offset < 400:
        offsets.append(offset)

final_offset = int(np.mean(offsets))
```
