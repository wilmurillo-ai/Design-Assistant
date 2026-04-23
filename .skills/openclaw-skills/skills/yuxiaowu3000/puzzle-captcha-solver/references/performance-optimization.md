# 性能优化指南

本指南介绍如何优化 puzzle-captcha-solver 的识别速度。

---

## 📊 当前性能

| 操作 | 耗时 | 占比 |
|------|------|------|
| 图片加载 | 50-100ms | 5% |
| 验证码检测 | 500-1500ms | 40% |
| 滑块检测 | 300-800ms | 25% |
| 缺口识别 | 500-1000ms | 25% |
| 轨迹生成 | 50-100ms | 5% |
| **总计** | **1.4-3.5 秒** | 100% |

---

## 🚀 优化方案

### 方案 1：图片预处理优化 ⭐⭐⭐

**原理：** 缩小图片尺寸，减少计算量

```python
# 优化前：直接处理原图
image = cv2.imread(screenshot_path)

# 优化后：先缩小到合理尺寸
image = cv2.imread(screenshot_path)
max_size = 800
if max(image.shape[:2]) > max_size:
    scale = max_size / max(image.shape[:2])
    image = cv2.resize(image, None, fx=scale, fy=scale)
```

**效果：** 速度提升 40-60%

---

### 方案 2：ROI（感兴趣区域）优化 ⭐⭐⭐

**原理：** 只处理验证码区域，不处理整图

```python
# 优化前：处理整张截图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 优化后：先裁剪到验证码可能出现的区域
# 验证码通常在图片中上部
h, w = image.shape[:2]
roi_y1, roi_y2 = int(h * 0.1), int(h * 0.7)
roi_x1, roi_x2 = int(w * 0.1), int(w * 0.9)
roi = image[roi_y1:roi_y2, roi_x1:roi_x2]
```

**效果：** 速度提升 30-50%

---

### 方案 3：算法参数优化 ⭐⭐

**原理：** 调整 OpenCV 参数，减少计算量

```python
# 优化前：标准 Canny 边缘检测
edges = cv2.Canny(gray, 50, 150)

# 优化后：使用 Sobel 近似（更快）
edges = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)

# 或者降低 Canny 精度
edges = cv2.Canny(gray, 100, 200, apertureSize=3)
```

**效果：** 速度提升 20-30%

---

### 方案 4：缓存机制 ⭐

**原理：** 缓存模板匹配结果

```python
# 对于相同网站的验证码，缓存模板
template_cache = {}

def get_template(captcha_type):
    if captcha_type not in template_cache:
        template_cache[captcha_type] = load_template(captcha_type)
    return template_cache[captcha_type]
```

**效果：** 第二次识别速度提升 80%

---

### 方案 5：多线程处理 ⭐⭐

**原理：** 并行处理独立任务

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as executor:
    future_popup = executor.submit(detect_captcha_popup)
    future_slider = executor.submit(detect_slider_button)
    
    popup_result = future_popup.result()
    slider_result = future_slider.result()
```

**效果：** 速度提升 30-40%

---

## 📈 综合优化效果

| 优化方案 | 优化前 | 优化后 | 提升 |
|---------|--------|--------|------|
| 基础版本 | 3.5 秒 | - | - |
| + 图片缩小 | - | 2.5 秒 | 29% |
| + ROI 裁剪 | - | 1.8 秒 | 49% |
| + 算法优化 | - | 1.4 秒 | 60% |
| + 多线程 | - | 1.0 秒 | 71% |

**最终目标：1 秒内完成识别！** 🎯

---

## 🔧 使用优化模式

```bash
# 标准模式（默认）
python3 scripts/recognize_puzzle.py --screenshot captcha.png

# 快速模式（降低精度，提升速度）
python3 scripts/recognize_puzzle.py --screenshot captcha.png --fast

# 高精度模式（降低速度，提升精度）
python3 scripts/recognize_puzzle.py --screenshot captcha.png --high-precision
```

---

## 📝 优化检查清单

- [ ] 图片尺寸是否合理（<800px）
- [ ] 是否使用 ROI 裁剪
- [ ] Canny 参数是否优化
- [ ] 是否启用多线程
- [ ] 是否使用缓存
- [ ] 是否关闭 debug 模式

---

## ⚠️ 优化注意事项

1. **速度 vs 精度权衡**
   - 快速模式：速度优先，精度略降
   - 标准模式：平衡速度和精度
   - 高精度模式：精度优先，速度略降

2. **图片质量影响**
   - 模糊图片需要更高精度
   - 清晰图片可以使用快速模式

3. **网站差异**
   - 简单验证码（大麦）：使用快速模式
   - 复杂验证码（抖音）：使用标准或高精度模式

---

## 🎯 性能基准测试

```bash
# 运行性能测试
python3 tests/benchmark.py

# 输出示例：
# 测试 1：大麦网验证码
#   标准模式：1.2 秒 ✅
#   快速模式：0.8 秒 ✅
#   高精度模式：2.1 秒
```

---

## 📚 参考资料

- [OpenCV 性能优化最佳实践](https://docs.opencv.org/master/d7/de5/tutorial_py_optimization.html)
- [NumPy 性能优化](https://numpy.org/devdocs/user/quickstart.html#performance)
- [Python 多线程指南](https://docs.python.org/3/library/concurrency.html)
