# Puzzle Captcha Solver

拼图滑块验证码自动识别技能 - 专门处理大麦、淘宝、京东等网站的拼图验证码

## 安装

### 1. 安装 Python 依赖

```bash
cd ~/.openclaw/skills/puzzle-captcha-solver
pip install -r requirements.txt
```

### 2. 验证安装

```bash
python3 scripts/recognize_puzzle.py --help
```

## 使用示例

### 示例 1：大麦网验证码

```bash
# 1. 打开大麦网并截图
agent-browser open "https://search.damai.cn/search.htm?keyword=李健"
agent-browser wait 3000
agent-browser screenshot --full captcha.png

# 2. 识别验证码
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json \
  --debug

# 3. 查看结果
cat result.json

# 4. 执行拖动（使用识别出的轨迹）
agent-browser eval "$(jq -r '.trajectory_js' result.json)"
```

### 示例 2：批量处理

```bash
# 对多个截图进行识别
for img in captchas/*.png; do
    python3 scripts/recognize_puzzle.py \
        --screenshot "$img" \
        --output "results/${img%.png}.json"
done
```

## 输出格式

```json
{
  "success": true,
  "offset": 142,
  "confidence": 0.85,
  "slider_location": {
    "x": 280,
    "y": 450,
    "w": 50,
    "h": 50
  },
  "trajectory": [[0,0], [5,1], [12,2], ...],
  "error": null
}
```

## 成功率

| 网站 | 识别成功率 | 备注 |
|------|------------|------|
| 大麦网 | 85%+ | 箭头拼图，相对简单 |
| 淘宝 | 75%+ | 缺口拼图 |
| 京东 | 75%+ | 缺口拼图 |
| 其他 | 60-80% | 取决于验证码复杂度 |

## 故障排除

### 问题 1：无法检测验证码弹窗

**解决：**
```bash
# 使用全屏截图
agent-browser screenshot --full captcha.png

# 增加等待时间
agent-browser wait --load networkidle
agent-browser wait 3000
```

### 问题 2：识别准确率低

**解决：**
```bash
# 使用 debug 模式查看检测结果
python3 scripts/recognize_puzzle.py --screenshot captcha.png --debug

# 查看 debug_captcha/ 目录下的标记图片
```

### 问题 3：拖动后验证失败

**解决：**
1. 增加轨迹随机性
2. 延长拖动时间（修改 `generate_trajectory` 的 `duration` 参数）
3. 检查滑块起始位置是否正确

## 调试

### 查看调试图片

```bash
# 运行后会在 debug_captcha/ 目录生成图片
ls debug_captcha/
# original.png  - 原图
# marked.png    - 标记检测区域的图
```

### 可视化轨迹

```python
# 使用 matplotlib 可视化轨迹
import matplotlib.pyplot as plt
import json

with open('result.json') as f:
    result = json.load(f)

trajectory = result['trajectory']
xs = [p[0] for p in trajectory]
ys = [p[1] for p in trajectory]

plt.plot(xs, ys)
plt.scatter(xs[0], ys[0], c='green', label='Start')
plt.scatter(xs[-1], ys[-1], c='red', label='End')
plt.legend()
plt.show()
```

## 注意事项

⚠️ **合规使用**
- 仅用于合法用途
- 遵守目标网站服务条款
- 不要用于恶意爬虫

⚠️ **成功率限制**
- 无法保证 100% 识别
- 新型验证码可能无法处理
- 建议准备手动处理方案

⚠️ **性能**
- 识别耗时：1-3 秒
- 拖动耗时：1.5-2.5 秒
- 建议设置总超时 10 秒

## 参考文档

- [拼图检测算法](references/puzzle-detection.md)
- [轨迹优化技巧](references/trajectory-optimization.md)
- [网站验证码特征](references/website-patterns.md)

## 支持

遇到问题？查看参考文档或提交 Issue。
