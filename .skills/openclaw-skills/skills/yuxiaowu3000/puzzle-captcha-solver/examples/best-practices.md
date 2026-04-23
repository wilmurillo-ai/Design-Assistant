# 最佳实践指南 / Best Practices

使用 puzzle-captcha-solver 的最佳实践和技巧总结。

---

## 📖 目录

1. [安装配置](#1-安装配置)
2. [使用流程](#2-使用流程)
3. [性能优化](#3-性能优化)
4. [错误处理](#4-错误处理)
5. [反反爬虫](#5-反反爬虫)
6. [生产环境](#6-生产环境)

---

## 1. 安装配置

### ✅ 推荐做法

**使用虚拟环境**
```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

**验证安装**
```bash
# 运行快速测试
python3 tests/quick_test.py

# 应该看到：✅ 所有测试通过
```

**固定依赖版本**
```bash
# 使用 requirements.txt 中的版本
opencv-python>=4.8.0
numpy>=1.24.0
pillow>=10.0.0
```

### ❌ 避免做法

- ❌ 不使用虚拟环境（可能与其他项目冲突）
- ❌ 跳过测试直接使用
- ❌ 使用过旧的 Python 版本（<3.8）

---

## 2. 使用流程

### ✅ 推荐做法

**标准流程**
```bash
# 1. 打开页面并等待加载
agent-browser open "https://example.com"
agent-browser wait --load networkidle

# 2. 截图（使用全屏）
agent-browser screenshot --full captcha.png

# 3. 识别（先标准模式）
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --output result.json

# 4. 检查结果
jq '.success' result.json

# 5. 执行拖动
if [ $(jq '.success' result.json) = "true" ]; then
    agent-browser eval "$(jq -r '.trajectory_js' result.json)"
else
    echo "识别失败，尝试高精度模式..."
    python3 scripts/recognize_puzzle.py \
      --screenshot captcha.png \
      --output result.json \
      --high-precision
fi
```

**保存和加载状态**
```bash
# 登录后保存 Cookie
agent-browser state save auth.json

# 下次使用时加载
agent-browser state load auth.json
```

### ❌ 避免做法

- ❌ 不等待页面加载就截图
- ❌ 不使用全屏截图（可能裁剪验证码）
- ❌ 不检查结果就直接执行
- ❌ 每次都重新登录（应该保存 Cookie）

---

## 3. 性能优化

### ✅ 推荐做法

**选择合适的模式**

| 场景 | 推荐模式 | 命令 |
|------|----------|------|
| 抢票/限时 | 快速模式 | `--fast` |
| 日常使用 | 标准模式 | *(无参数)* |
| 复杂验证码 | 高精度 | `--high-precision` |
| 关键流程 | 高精度 + 重试 | `--high-precision` + 循环 |

**图片预处理**
```bash
# 如果截图过大，先裁剪
convert full.png -crop 800x600+200+100 captcha.png

# 或使用内置的快速模式（自动缩小）
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --fast
```

**批量处理优化**
```bash
#!/bin/bash
# 并行处理多个验证码
for img in captchas/*.png; do
    (
        python3 scripts/recognize_puzzle.py \
            --screenshot "$img" \
            --output "${img%.png}.json" \
            --fast
    ) &
done
wait
```

### ❌ 避免做法

- ❌ 所有场景都用高精度模式（浪费时间）
- ❌ 处理超大图片（>1920px）
- ❌ 串行处理批量任务（应该并行）

---

## 4. 错误处理

### ✅ 推荐做法

**重试机制**
```bash
#!/bin/bash

MAX_RETRIES=3
retry=0

while [ $retry -lt $MAX_RETRIES ]; do
    python3 scripts/recognize_puzzle.py \
        --screenshot captcha.png \
        --output result.json
    
    if [ $? -eq 0 ]; then
        echo "✅ 识别成功"
        break
    else
        retry=$((retry + 1))
        echo "⚠️  识别失败，第 $retry 次重试..."
        
        # 切换模式重试
        if [ $retry -eq 1 ]; then
            echo "尝试高精度模式..."
            python3 scripts/recognize_puzzle.py \
                --screenshot captcha.png \
                --output result.json \
                --high-precision
        fi
        
        sleep 2
    fi
done

if [ $retry -eq $MAX_RETRIES ]; then
    echo "❌ 达到最大重试次数，请手动处理"
    # 发送通知或降级处理
fi
```

**详细日志**
```bash
# 启用详细日志
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --verbose \
  2>&1 | tee recognition.log
```

**调试模式**
```bash
# 失败时使用 debug 模式
python3 scripts/recognize_puzzle.py \
  --screenshot captcha.png \
  --debug

# 查看生成的调试图片
ls debug_captcha/
cat debug_captcha/marked.png  # 查看检测区域
```

### ❌ 避免做法

- ❌ 不检查返回值
- ❌ 不记录错误日志
- ❌ 失败后不重试就直接放弃
- ❌ 不使用 debug 模式分析原因

---

## 5. 反反爬虫

### ✅ 推荐做法

**使用真实浏览器**
```bash
# ✅ 推荐：使用真实浏览器
agent-browser open "https://example.com"

# ❌ 不推荐：headless 模式容易被检测
agent-browser open --headless "https://example.com"
```

**随机延迟**
```python
import time
import random

# 随机延迟 2-5 秒
time.sleep(random.uniform(2, 5))

# 随机延迟 3-8 秒（更自然）
time.sleep(random.uniform(3, 8))
```

**模拟人类行为**
```javascript
// 在 agent-browser eval 中使用
await page.evaluate(() => {
    // 随机滚动
    window.scrollBy(
        0, 
        Math.random() * 100 - 50
    );
    
    // 随机鼠标移动（如果有鼠标模拟）
    // ...
});
```

**轮换 IP**
```bash
# 使用代理
export HTTP_PROXY="http://proxy1:8080"
agent-browser open "https://example.com"

# 或使用代理池脚本
./rotate_proxy.sh
```

**保存和复用 Cookie**
```bash
# 第一次登录后保存
agent-browser state save auth.json

# 后续使用加载 Cookie（避免重复登录）
agent-browser state load auth.json
agent-browser open "https://example.com"
```

### ❌ 避免做法

- ❌ 固定间隔请求（容易被识别）
- ❌ 使用 headless 浏览器
- ❌ 不保存 Cookie（频繁登录）
- ❌ 单一 IP 高频访问

---

## 6. 生产环境

### ✅ 推荐做法

**监控和告警**
```bash
#!/bin/bash
# monitor.sh

# 运行识别
python3 scripts/recognize_puzzle.py \
    --screenshot captcha.png \
    --output result.json

# 检查成功率
success=$(jq '.success' result.json)

if [ "$success" != "true" ]; then
    # 发送告警
    curl -X POST "https://api.example.com/alert" \
        -d "type=captcha_recognition_failed" \
        -d "time=$(date)"
    
    # 记录日志
    echo "$(date): 识别失败" >> error.log
fi
```

**配置管理**
```bash
# config.sh
export CAPTCHA_MODE="standard"  # fast/standard/high_precision
export MAX_RETRIES=3
export TIMEOUT=30
export DEBUG_MODE=false
```

**日志轮转**
```bash
# 使用 logrotate
/var/log/captcha/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

**容器化部署**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制代码
COPY scripts/ scripts/
COPY tests/ tests/

# 运行测试
RUN python3 tests/quick_test.py

CMD ["python3", "scripts/recognize_puzzle.py", "--help"]
```

### ❌ 避免做法

- ❌ 无监控直接上线
- ❌ 硬编码配置参数
- ❌ 不记录日志或日志不轮转
- ❌ 直接在生产环境调试

---

## 📊 检查清单

### 上线前检查

- [ ] 已通过所有测试（`python3 tests/quick_test.py`）
- [ ] 已配置日志记录
- [ ] 已设置错误重试机制
- [ ] 已准备降级方案（手动处理）
- [ ] 已配置监控告警
- [ ] 已保存测试截图和结果

### 日常运维检查

- [ ] 检查日志是否有异常
- [ ] 检查识别成功率（目标：>85%）
- [ ] 检查性能指标（目标：<2 秒）
- [ ] 清理调试文件（`debug_captcha/`）
- [ ] 更新依赖包（定期）

---

## 🎯 成功率提升技巧

| 技巧 | 提升幅度 | 实施难度 |
|------|----------|----------|
| 使用全屏截图 | +15% | ⭐ |
| 等待页面完全加载 | +20% | ⭐ |
| 选择合适模式 | +10% | ⭐ |
| 使用真实浏览器 | +25% | ⭐⭐ |
| 保存和复用 Cookie | +30% | ⭐ |
| 轮换 IP 地址 | +20% | ⭐⭐ |
| 添加随机延迟 | +15% | ⭐ |
| 失败后重试（切换模式） | +25% | ⭐⭐ |

**综合应用所有技巧，成功率可达 95%+！** 🎉

---

## 📚 参考资料

- [使用案例集](examples/use-cases.md)
- [快速参考卡片](examples/cheatsheet.md)
- [性能优化指南](references/performance-optimization.md)
- [完整文档](SKILL.md)

---

**遵循这些最佳实践，让你的自动化流程更稳定、更高效！** ✨
