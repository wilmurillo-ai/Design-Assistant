# Vidu Image Generate API Reference

图片生成 API 参考，包含 Nano 生图、Vidu 参考生图功能。

## Base URL

```
https://api.vidu.cn/ent/v2
```

**域名选择规则**：
- **简体中文用户**：使用 `api.vidu.cn`
- **非简体中文用户**：使用 `api.vidu.com`

根据用户交流语言自动切换域名。

## Authentication

```
Authorization: Token YOUR_API_KEY
```

---

## 图片生成 API

### 1. Nano 生图（推荐）

**POST** `/reference2image/nano`

```json
{
  "model": "q3-fast",
  "prompt": "图片描述",
  "images": ["参考图1", "..."],
  "aspect_ratio": "16:9",
  "resolution": "2K"
}
```

**模型选择**：
| 模型 | 分辨率 | 速度 | 质量 | 参考图要求 |
|------|--------|------|------|-----------|
| q3-fast | 1K/2K/4K | 快 | 高 | 0-14张（可选） |
| q2-fast | 1K | 最快 | 中 | 0-14张（可选） |
| q2-pro | 1K/2K/4K | 慢 | 最高 | 0-14张（可选） |

**特殊比例支持（仅 q3-fast）**：
- `1:4` - 超宽横图
- `4:1` - 超长竖图
- `1:8` - 极宽横图
- `8:1` - 极长竖图

**标准比例（所有模型）**：
`9:16, 2:3, 3:4, 4:5, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9`

**特点**：
- ✅ 支持文生图（不输入参考图）
- ✅ 支持参考生图（输入参考图）
- ✅ 最多 14 张参考图

---

### 2. Vidu 参考生图

**POST** `/reference2image`

```json
{
  "model": "viduq2",
  "prompt": "图片描述",
  "images": ["参考图"],
  "aspect_ratio": "16:9",
  "resolution": "1080p"
}
```

**模型选择**：
| 模型 | 分辨率 | 参考图要求 | 说明 |
|------|--------|-----------|------|
| viduq2 | 540p/720p/1080p | 0-7张 | 支持文生图、参考生图、图片编辑 |
| viduq1 | 1080p | 1-7张（必填） | 仅支持参考生图 |

**比例支持**：
`9:16, 2:3, 3:4, 4:5, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9`

**viduq2 图片编辑功能**：
- 支持图片编辑（局部重绘、扩图等）
- 使用图片编辑时，`aspect_ratio` 必须设为 `auto`
- 示例：
```json
{
  "model": "viduq2",
  "prompt": "编辑描述",
  "images": ["待编辑图片"],
  "aspect_ratio": "auto",
  "resolution": "1080p"
}
```

**特点**：
- viduq2：支持文生图、参考生图、图片编辑
- viduq1：必须输入至少 1 张参考图（仅参考生图）
- 最多 7 张参考图

---

## 任务管理 API

### 查询任务状态

**GET** `/tasks`

返回任务列表，根据 `task_id` 查找。

### 取消任务

**DELETE** `/tasks/{task_id}`

---

## 响应格式

### 任务创建响应

```json
{
  "task_id": "xxx",
  "state": "pending",
  "model": "q3-fast",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 任务完成响应

```json
{
  "task_id": "xxx",
  "state": "success",
  "creations": [
    {
      "url": "https://...",
      "cover_url": "https://..."
    }
  ]
}
```

---

## 错误码

| 错误 | 说明 |
|------|------|
| Invalid API key | API 密钥错误 |
| Image size exceeds | 图片超过 50MB |
| Invalid aspect ratio | 不支持的比例 |
| Task failed | 生成失败 |

---

## 参数速查

### 图片参数

| 参数 | 可选值 | 默认值 |
|------|--------|--------|
| aspect_ratio | 9:16, 2:3, 3:4, 4:5, 1:1, 5:4, 4:3, 3:2, 16:9, 21:9 | 16:9 |
| resolution | 1K, 2K, 4K | 2K |
