---
name: xhs-publisher
version: 1.0.0
description: |
  小红书笔记创作与发布完整工作流。包含：Humanizer去AI味文案写作、
  Pexels正版图配图、文泉驿字体卡片渲染、审核-发布双流程。
  当用户需要创建、审核、发布小红书笔记时使用。
---

# 小红书笔记创作与发布技能

## 核心能力

1. **文案写作** — 小红书风格口语化内容，附 Humanizer 去AI味处理
2. **配图生成** — Pexels正版图 + 文泉驿字体渲染三张卡片
3. **审核流程** — 飞书卡片预览 → 用户回复「通过」或「修改」→ 发布
4. **隐私发布** — 支持 `--private` 私密发布

## 工作流程

```
用户需求 → 文案Humanizer → 配图(Pexels) → 飞书卡片审核
                                              ↓
                                       「通过」→ 发布
                                       「修改」→ 调整 → 重新审核
```

## SKILL.md 速查

### 发布命令

```bash
cd ~/.openclaw/workspace/skills/xhs-publisher
XHS_COOKIE=$(cat ~/.config/xiaohongshu/cookie.txt) \
XHS_COOKIE="$XHS_COOKIE" python3 scripts/publish.py \
  --title "标题" \
  --desc "正文内容" \
  --images card1.jpg card2.jpg card3.jpg \
  --private
```

### 卡片渲染

```bash
python3 scripts/render_cards.py \
  --template "modern" \
  --theme "dark" \
  --font "wqy" \
  --images pexels_photo.jpg \
  --texts "标题|副标题|标签"
```

### 配图获取

```bash
python3 scripts/fetch_image.py --query "coffee latte" --count 5
```

## 依赖

```bash
pip install Pillow requests python-dotenv qrcode
```

## 配置

Cookie 保存在 `~/.config/xiaohongshu/cookie.txt`

## 审核规则

- 每次发布前必须发飞书卡片给用户审核
- 用户回复「通过」→ 执行发布
- 用户回复「修改」→ 根据意见修改后重新发卡片
- 禁止跳过审核直接发布
