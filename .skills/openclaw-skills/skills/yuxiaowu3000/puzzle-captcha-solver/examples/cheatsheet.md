# 快速参考卡片 / Cheatsheet

一页纸速查 puzzle-captcha-solver 的所有常用命令和参数。

---

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 截图
agent-browser screenshot captcha.png

# 3. 识别
python3 scripts/recognize_puzzle.py --screenshot captcha.png --output result.json

# 4. 执行拖动
agent-browser eval "$(jq -r '.trajectory_js' result.json)"
```

---

## 📋 命令参数

### 基本参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--screenshot` | | 截图路径（必需） | `--screenshot captcha.png` |
| `--output` | | 输出 JSON 路径 | `--output result.json` |
| `--debug` | | 生成调试图片 | `--debug` |
| `--verbose` | `-v` | 详细日志 | `--verbose` |

### 识别模式

| 参数 | 说明 | 速度 | 精度 | 使用场景 |
|------|------|------|------|----------|
| `--fast` | 快速模式 | ⚡⚡⚡ | ⭐⭐ | 时间敏感 |
| *(无)* | 标准模式 | ⚡⚡ | ⭐⭐⭐ | 默认推荐 |
| `--high-precision` | 高精度 | ⚡ | ⭐⭐⭐⭐ | 复杂验证码 |
| `--benchmark` | 性能测试 | - | - | 性能分析 |

---

## 🎯 常用命令组合

### 标准识别

```bash
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json
```

### 快速识别（抢票）

```bash
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json \
  --fast
```

### 高精度识别（关键流程）

```bash
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json \
  --high-precision
```

### 调试模式（排查问题）

```bash
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json \
  --debug \
  --verbose
```

### 性能分析

```bash
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --benchmark
```

---

## 📊 输出结果格式

### 成功结果

```json
{
  "success": true,
  "offset": 142,
  "confidence": 0.85,
  "slider_location": {"x": 100, "y": 300},
  "trajectory": [[0,0], [5,1], [12,2], ...],
  "trajectory_js": "async function...",
  "steps": [...]
}
```

### 失败结果

```json
{
  "success": false,
  "error": "未检测到验证码弹窗",
  "suggestions": [
    "增加页面等待时间",
    "使用全屏截图",
    "检查验证码是否已加载"
  ],
  "steps": [...]
}
```

---

## 🔧 故障排除命令

### 检查安装

```bash
# 快速测试
python3 tests/quick_test.py

# 单元测试
python3 tests/test_recognize.py

# 性能测试
python3 tests/benchmark.py
```

### 查看调试图片

```bash
# 生成调试图片
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --debug

# 查看生成的图片
ls debug_captcha/
# original.png  - 原图
# marked.png    - 标记检测区域
```

### 查看详细日志

```bash
# 启用详细日志
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --verbose

# 或简写
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  -v
```

---

## 🌐 网站特定参数

### 大麦网（箭头拼图）

```bash
# 通常使用标准模式即可
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json

# 抢票时使用快速模式
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --fast
```

### 淘宝/京东（缺口拼图）

```bash
# 标准模式
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json
```

### 抖音（彩色拼图）

```bash
# 光线复杂时使用高精度
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --high-precision
```

### 12306（箭头拼图）

```bash
# 验证码较难，推荐高精度
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --high-precision
```

---

## 📁 文件结构

```
puzzle-captcha-solver/
├── scripts/
│   ├── recognize_puzzle.py    # 主识别脚本
│   └── execute_drag.js        # 拖动执行
├── tests/
│   ├── quick_test.py          # 快速测试
│   ├── test_recognize.py      # 单元测试
│   └── benchmark.py           # 性能测试
├── examples/
│   └── use-cases.md           # 使用案例
├── references/
│   └── performance-optimization.md  # 性能优化
├── SKILL.md                   # 完整文档
├── README.md                  # 快速开始
├── README.en.md               # English docs
└── package.json               # 元数据
```

---

## ⚡ 一键命令

### 完整流程（单行）

```bash
agent-browser screenshot captcha.png && python3 scripts/recognize_puzzle.py --screenshot captcha.png --output result.json && agent-browser eval "$(jq -r '.trajectory_js' result.json)"
```

### 批量识别

```bash
for img in captchas/*.png; do
    python3 scripts/recognize_puzzle.py --screenshot "$img" --output "${img%.png}.json"
done
```

### 清理调试文件

```bash
rm -rf debug_captcha/ && rm -f captcha_*.png captcha_*.json
```

---

## 📞 获取帮助

```bash
# 查看帮助
python3 scripts/recognize_puzzle.py --help

# 查看版本
cat package.json | jq '.version'

# 查看完整文档
cat SKILL.md
```

---

## 🔗 相关链接

| 资源 | 链接 |
|------|------|
| ClawHub | https://clawhub.com/skills/puzzle-captcha-solver |
| 完整文档 | SKILL.md |
| 使用案例 | examples/use-cases.md |
| 性能优化 | references/performance-optimization.md |
| 更新日志 | CHANGELOG.md |
| Issue 反馈 | https://github.com/openclaw/skills/issues |

---

## 💡 提示技巧

### 提高成功率

1. ✅ 使用全屏截图：`--full`
2. ✅ 等待页面加载：`agent-browser wait --load networkidle`
3. ✅ 选择合适模式：简单用 `--fast`，复杂用 `--high-precision`
4. ✅ 启用调试：失败时用 `--debug` 查看原因

### 优化性能

1. ⚡ 缩小图片尺寸（<800px）
2. ⚡ 使用快速模式
3. ⚡ 关闭 debug 输出
4. ⚡ 使用 SSD 硬盘

### 避免被检测

1. 🎭 使用真实浏览器（非 headless）
2. 🎭 添加随机延迟
3. 🎭 轮换 IP 地址
4. 🎭 保存和使用 Cookie

---

**打印此卡片贴在桌边，随时参考！** 📌
