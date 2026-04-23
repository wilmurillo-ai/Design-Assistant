---
name: xiaohongshu-content
description: >
  将文章、技术文档等内容转换为适合小红书发布的 HTML 格式，生成封面图和内容截图，配好标题和正文摘要。
  用户提供原始内容（Markdown 或纯文本）后，AI 生成适配小红书风格的多图 HTML 页面，并调用截图工具生成可直接发布的图片。
  适用于：技术博客分享、知识干货、產品介绍、营销内容等。
---

# 小红书内容生成技能

## 功能概述

将任意文章/内容转换为**小红书风格**的 HTML 页面，输出多张可截图发布的图片，并附上**标题 + 正文摘要**。

---

## 使用方式

### 方式一：发送内容给 AI

直接把你的文章内容发给我（可以是 Markdown 或纯文本），告诉我"帮我生成小红书内容"或"做成适合小红书的格式"。

**示例：**
> "帮我把这篇关于 BM25 算法的文章做成小红书风格的内容"

**我会自动：**
1. 分析内容结构，提取核心要点
2. 生成适配小红书的 HTML 页面（封面 + 多个内容区块）
3. 截图并发送给你
4. 提供标题和正文建议

### 方式二：命令行调用

```bash
# 手动执行内容生成
cd ~/.openclaw/workspace/skills/xiaohongshu-content
bash scripts/generate_content.sh "你的内容" "输出标题"
```

---

## 输出规格

| 项目 | 说明 |
|------|------|
| **图片数量** | 1张封面 + 2-5张内容图（视内容长度） |
| **图片格式** | PNG |
| **图片宽度** | 680px（小红书标准宽度） |
| **HTML输出** | 可在浏览器打开查看完整效果 |
| **截图工具** | wkhtmltoimage 或 Chromium headless |

---

## HTML 页面结构

```
┌─────────────────────────┐
│      封面 (Header)       │  ← 标题 + 副标题 + 标签
├─────────────────────────┤
│      内容卡片 1           │  ← 核心要点/问题
├─────────────────────────┤
│      内容卡片 2           │  ← 公式/原理
├─────────────────────────┤
│      内容卡片 3           │  ← 参数/应用
├─────────────────────────┤
│      总结卡片             │  ← 核心结论
└─────────────────────────┘
```

---

## HTML 模板设计规范

### 配色方案（小红书风格）

- **主色**: #FF6B6B (珊瑚红)
- **渐变**: #FF6B6B → #FF8E53 (橙红渐变)
- **背景**: #FFF5F5 / #FFF9F0 / #F0F8FF (淡粉/淡黄/淡蓝)
- **文字**: #333333 (深灰), #666666 (中灰), #FF6B6B (强调)

### 字体

- 标题: 28px, 700, sans-serif
- 副标题: 18px, 600
- 正文: 14px, 400
- 标签: 12px, 圆角背景

### 卡片样式

- 圆角: 16px
- 阴影: 0 4px 20px rgba(0,0,0,0.05)
- 内边距: 24px
- 左边框: 4px 渐变色

---

## 截图脚本用法

### Python 截图（推荐）

```bash
cd ~/.openclaw/workspace/skills/xiaohongshu-content
python3 scripts/take_screenshot.py \
    --input /path/to/content.html \
    --output /path/to/output.png \
    --width 680 \
    --height 800
```

### Chromium 截图

```bash
chromium-browser --headless \
    --disable-gpu \
    --no-sandbox \
    --screenshot=output.png \
    --window-size=680,500 \
    --crop-y=0 --crop-h=500 \
    file:///path/to/content.html
```

### wkhtmltoimage 截图

```bash
wkhtmltoimage --width 680 --quality 90 \
    /path/to/content.html /path/to/output.png
```

---

## 标题与摘要生成规则

### 标题公式

```
[符号] + [核心关键词] + [效果词] + [平台词]

示例：
🔍 一文搞懂搜索引擎背后的BM25算法
💡 5分钟理解RAG技术原理
🚀 Redis 性能优化实战总结
```

### 摘要公式

```
[一句话概括价值] + [时间/难度暗示] + [行动引导]

示例：
BM25是TF-IDF的升级版，解决了词频无上限和长度不公平两大问题！
收藏慢慢看，干货满满～
#标签1 #标签2 #标签3
```

### 标签策略

- 3-5个标签
- 结构：1个领域词 + 1-2个技术词 + 1个平台词 + 1个情绪词
- 示例：#算法 #搜索引擎 #BM25 #知识分享 #技术干货

---

## 依赖项

| 依赖 | 用途 | 安装 |
|------|------|------|
| Python3 | 截图脚本 | 系统自带 |
| imgkit | HTML转图片 | `pip install imgkit` |
| wkhtmltoimage | HTML渲染引擎 | `apt install wkhtmltopdf` |
| chromium-browser | 备选渲染引擎 | 系统安装 |

---

## 文件结构

```
xiaohongshu-content/
├── SKILL.md                    # 本技能说明
├── scripts/
│   ├── generate_content.sh     # 内容生成主脚本
│   ├── take_screenshot.py      # Python截图工具
│   └── open_preview.sh         # 浏览器打开预览
├── templates/
│   └── content_template.html   # HTML模板
└── outputs/                    # 生成的内容目录
```

---

## 注意事项

1. **图片宽度固定 680px**，适配小红书笔记宽度
2. **内容卡片控制在 500-800px 高度**，便于截取完整信息
3. **标签使用 emoji + 文字**，增加视觉吸引力
4. **摘要控制在 100 字以内**，小红书显示完整
5. **标题控制在 20 字以内**，超过会被截断

---

## 示例输出

用户提供内容 → AI 生成以下内容：

**标题：** 🔍 一文搞懂搜索引擎背后的BM25算法

**正文：**
> BM25是TF-IDF的升级版，通过词频饱和和长度归一化让搜索结果更准确！收藏慢慢看～
> #算法 #搜索引擎 #BM25 #知识分享

**图片：** 封面图 × 1 + 内容图 × 3
