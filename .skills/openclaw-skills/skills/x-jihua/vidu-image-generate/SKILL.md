---
name: vidu-image-generate
version: 1.0.0
description: "Vidu AI 图片生成。支持 Nano 生图、Vidu 参考生图。对话式调用，自动识别意图。"
---

# Vidu Image Generate 🖼️

Vidu AI 图片生成工具，专注于图片生成功能。

## 环境说明

**变量说明**：
- `{baseDir}` - 运行时自动替换为本 skill 目录的绝对路径
  - 实际路径：`~/.openclaw/workspace/skills/vidu-image-generate/`

**环境变量**：
- `VIDU_API_KEY` - Vidu API 密钥（必需）

## 快速开始

直接告诉我你想生成什么图片，我会自动识别并调用合适的接口：

```
"生成一只可爱的橘猫图片"
"用这张图生成一个动漫风格的人物"
"生成一张风景图，1920x1080"
```

## 支持的图片类型

| 类型 | 触发条件 | 说明 |
|------|----------|------|
| 文生图 | 纯文字描述 | 从文字生成图片 |
| 参考生图 | 提供参考图片 | 根据参考风格生成 |

## 自动识别规则

```
用户输入 → 意图识别
─────────────────────────────
"生成图片/图" → 图片生成模式
纯文字 → 文生图
参考图片 → 参考生图
```

## 模型选择策略

### Nano 生图模型（推荐）

| 模型 | 分辨率 | 速度 | 质量 | 参考图 | 特殊比例 |
|------|--------|------|------|--------|---------|
| q3-fast | 1K/2K/4K | 快 | 高 | 0-14张（可选） | ✅ 1:4, 4:1, 1:8, 8:1 |
| q2-fast | 1K | 最快 | 中 | 0-14张（可选） | ❌ |
| q2-pro | 1K/2K/4K | 慢 | 最高 | 0-14张（可选） | ❌ |

**特点**：
- ✅ 支持文生图（不输入参考图）
- ✅ 支持参考生图（输入参考图）
- ✅ q3-fast 支持特殊比例（1:4、4:1、1:8、8:1）

### Vidu 参考生图模型

| 模型 | 分辨率 | 参考图要求 | 说明 |
|------|--------|-----------|------|
| viduq2 | 540p/720p/1080p | 0-7张 | 支持文生图、参考生图、图片编辑 |
| viduq1 | 1080p | 1-7张（必填） | 仅支持参考生图 |

**viduq2 图片编辑功能**：
- ✅ 支持局部重绘、扩图等编辑功能
- ⚠️ 使用图片编辑时，`aspect_ratio` 必须设为 `auto`
- 示例：`"aspect_ratio": "auto"`

**特点**：
- viduq2：支持文生图、参考生图、图片编辑
- viduq1：必须输入至少 1 张参考图（仅参考生图）

### 场景推荐

| 场景 | 模型 | 理由 |
|------|------|------|
| 默认 | q3-fast | 最新模型，速度快，支持特殊比例 |
| 高画质 | q2-pro | 效果最好 |
| 快速生成 | q2-fast | 速度最快 |
| 参考生图 | viduq2 | 支持文生图和参考生图 |

## 分辨率与比例默认值

```
图片分辨率：2K
图片比例：16:9
```

## API 调用

内部使用 Python CLI 工具：

```bash
# 图片生成
python3 {baseDir}/scripts/vidu_cli.py nano-image --prompt "图片描述"

# 参考生图
python3 {baseDir}/scripts/vidu_cli.py nano-image --prompt "图片描述" --images ref1.jpg ref2.jpg

# Vidu 参考生图
python3 {baseDir}/scripts/vidu_cli.py text2image --prompt "图片描述" --images ref.jpg

# 查询任务状态
python3 {baseDir}/scripts/vidu_cli.py status <task_id> --download ./uploads
```

## 输出规范

1. **下载目录**: `{baseDir}/uploads/`
2. **返回格式**: Markdown 格式引用文件
3. **图片链接**: 必须返回 Vidu API 的 `creations[0].url` 字段

## 环境配置

必需环境变量：

```bash
VIDU_API_KEY=your_api_key_here
```

获取 API Key：
- Vidu 官方开放平台：https://platform.vidu.cn 或 https://platform.vidu.com
- 注册账号后在「API Keys」页面创建

## API 域名选择

**重要规则**：根据用户语言自动选择 API 域名

| 用户语言 | API 域名 | 说明 |
|---------|---------|------|
| 简体中文 | `api.vidu.cn` | 国内用户（默认） |
| 其他语言 | `api.vidu.com` | 海外用户 |

**Base URL 配置**：
```python
# 简体中文用户
BASE_URL = "https://api.vidu.cn/ent/v2"

# 非简体中文用户（英文、日文、韩文等）
BASE_URL = "https://api.vidu.com/ent/v2"
```

**判断逻辑**：
- 用户使用简体中文 → 使用 `api.vidu.cn`
- 用户使用其他语言（英文、日文、韩文等） → 使用 `api.vidu.com`

## 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| Invalid API key | API密钥错误 | 检查 VIDU_API_KEY 环境变量 |
| Image size exceeds | 图片过大 | 压缩至50MB以下 |
| Task failed | 生成失败 | 查看 error 信息重试 |

## References

- [API参考文档](references/api_reference.md) - 所有API详细参数

## Rules

1. **API Key 检查**: 调用前确认 `VIDU_API_KEY` 已设置
2. **异步任务**: 图片生成异步进行，需轮询状态
3. **下载时效**: 生成 URL 24小时内有效
4. **返回图片链接**: 必须返回图片 URL 让用户直接访问
