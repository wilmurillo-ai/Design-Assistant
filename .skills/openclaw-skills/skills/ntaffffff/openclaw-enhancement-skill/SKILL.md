---
name: openclaw-enhancement
description: OpenClaw 增强模块集 - 20个可选增强模块（CLI彩色输出、分层记忆、多Agent协作、沙箱隔离、智能压缩等）。直接告诉AI你想用的功能即可。
---

# 🤖 OpenClaw 增强模块集

让 OpenClaw 更强更好用的20个增强模块。

## 安装

```bash
# 克隆到 skills 目录
git clone https://github.com/ntaffffff/openclaw-enhancement.git ~/.openclaw/workspace/openclaw-enhancement
```

或者下载 enhancer.py 放到你的工作空间：
```bash
curl -o ~/.openclaw/workspace/enhancer.py https://raw.githubusercontent.com/ntaffffff/openclaw-enhancement/main/enhancer.py
```

## 使用方法

直接告诉 AI 你想用什么功能：

| 你说 | 功能 |
|------|------|
| "用彩色输出" | CLI 彩色终端 |
| "用记忆系统" | 分层记忆 |
| "用多Agent" | 多Agent协作 |
| "用沙箱" | 安全沙箱 |
| "用错误恢复" | 自动重试 |
| "用智能压缩" | 压缩上下文 |

## 命令行用法

```bash
python3 ~/.openclaw/workspace/enhancer.py <模块> [参数]

# 示例
python3 ~/.openclaw/workspace/enhancer.py cli
python3 ~/.openclaw/workspace/enhancer.py memory
python3 ~/.openclaw/workspace/enhancer.py multi_agent "写一个计算器"
```

## 可用模块

1. **cli** - 彩色输出、表格、进度条
2. **memory** - 分层记忆系统
3. **multi_agent** - 多Agent协作
4. **sandbox** - 沙箱隔离执行
5. **error_recovery** - 错误自动恢复
6. **compression** - 智能压缩
7. **tools** - 工具系统
8. **repl** - REPL交互增强

## 示例

### 彩色输出
```
ℹ 系统消息
✓ 成功
⚠ 警告
✗ 错误
```

### 多Agent协作
```
完成 3 个任务:
  ✓ 1. 理解需求
  ✓ 2. 编写代码
  ✓ 3. 测试验证
```

---

*让 OpenClaw 更强更好用 🦀*