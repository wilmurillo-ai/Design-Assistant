---
name: image-compressor
description: 图片压缩和格式转换工具，支持 JPEG/PNG/WebP/AVIF/GIF。使用 rv-image-optimize 进行高质量压缩、批量处理、尺寸调整和懒加载组件集成。
version: 1.0.0
---

# Image Compressor Skill

基于 `rv-image-optimize` 的图片压缩和优化工具。

## 核心功能

- **压缩** - 有损/无损压缩，质量 1-100 可调
- **格式转换** - JPEG ↔ PNG ↔ WebP ↔ AVIF ↔ GIF
- **批量处理** - 文件夹递归压缩，支持并发
- **尺寸调整** - 最大宽高限制，自动等比缩放
- **React 组件** - LazyImage 懒加载、ProgressiveImage 渐进式加载

## 何时使用

用户提到以下需求时触发：
- "压缩图片"、"图片太大"、"减小文件大小"
- "转成 WebP/AVIF"、"格式转换"
- "批量处理图片"、"压缩整个文件夹"
- "调整图片尺寸"、"缩小图片"
- "懒加载图片组件"

## 使用方法

### CLI 命令（已全局安装）

```powershell
# 单张图片压缩
rv-image-optimize photo.jpg --quality 80

# 转换格式
rv-image-optimize input.png --output output.webp --format webp

# 批量压缩文件夹
rv-image-optimize ./images --output-dir ./compressed --format webp --quality 75

# 调整尺寸 + 压缩
rv-image-optimize photo.jpg --max-width 1920 --max-height 1080 --quality 85

# 替换原图（谨慎）
rv-image-optimize ./photos --format webp --replace-original
```

### 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--quality <1-100>` | 压缩质量 | 80 |
| `--format <fmt>` | 输出格式 (jpeg/png/webp/avif/auto) | auto |
| `--output <file>` | 单文件输出路径 | - |
| `--output-dir <dir>` | 批量输出目录 | - |
| `--max-width` | 最大宽度 | - |
| `--max-height` | 最大高度 | - |
| `--suffix` | 输出文件后缀 | .compressed |
| `--overwrite` | 覆盖已存在文件 | false |
| `--concurrency` | 并发数 | 4 |

### Node.js API

```javascript
import { compressImage } from 'rv-image-optimize/node-compress';

await compressImage({
  input: 'input.jpg',
  output: 'output.webp',
  quality: 80,
  format: 'webp',
  maxWidth: 1920
});
```

## 质量推荐

| 用途 | 格式 | 质量 |
|------|------|------|
| 网页图片 | WebP | 75-85 |
| 高质量展示 | JPEG | 85-95 |
| 缩略图 | WebP/AVIF | 60-75 |
| 透明背景 | PNG/WebP | 80-90 |
| 动画 | GIF/WebP | 70-80 |

## 相关脚本

- `scripts/batch-compress.js` - 批量压缩脚本
- `scripts/convert-format.js` - 格式转换脚本

## 依赖

- `rv-image-optimize` (全局安装)
- `sharp` (底层依赖，自动安装)
