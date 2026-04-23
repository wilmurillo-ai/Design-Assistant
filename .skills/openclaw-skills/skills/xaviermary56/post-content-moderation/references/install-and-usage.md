# Install and Usage

Use this reference when the user asks how to install, import, share, or operate the `post-content-moderation` skill.

## Files

- Skill folder: `skills/post-content-moderation`
- Packaged file: `skills/dist/post-content-moderation.skill`

## Installation ideas

Choose the method that matches the user's environment:

### Method 1: copy the unpacked folder into a workspace

Place the folder under a workspace skill directory such as:

```text
skills/post-content-moderation
```

Required file structure:

```text
post-content-moderation/
├── SKILL.md
├── references/
└── scripts/
```

### Method 2: distribute the packaged `.skill` file

Share this file:

```text
skills/dist/post-content-moderation.skill
```

Import it using the target environment's skill import/install flow.

## What this skill does after installation

- reviews title and body with a default ad/contact blocking policy
- can be used as a moderation prompt/policy skill for multimodal review tasks
- supports whitelist exceptions
- supports custom project rules
- supports strict full-auto mode and balanced mode
- can return human-readable output or JSON output
- includes optional PHP demo scripts for remote pull + callback workflows

## Important safety note

This skill is **not** a purely local moderation pack if you use the bundled PHP demos.

The demo scripts can:
- call external model APIs
- pull pending moderation items from a remote service
- send moderation results to a remote callback service
- expose text fields and media URLs to third-party services depending on your integration

Also note:
- the bundled media inspector is currently a placeholder only
- image/video moderation claims require your own verified OCR / QR / ASR / frame extraction pipeline before production use
- you should not present this demo as a complete media-audit implementation without those additions

## Recommended operating pattern

Provide moderation input in this shape:

```text
审核模式：严格全自动 / 平衡模式
标题：
正文：
图片：<number / description / attached images>
视频：<description / transcript / key frames>
白名单：
自定义规则：
输出要求：普通文本 / JSON
```

## Suggested rollout checklist

Before using this skill in production, confirm:
- whitelist is defined narrowly
- callback contract is fixed
- strict full-auto vs balanced mode is chosen
- media URLs are readable by the audit service
- timeout / retry / fail-close policy is agreed
- sample pass/reject cases were tested
- outbound hosts are allowlisted
- secrets are injected only through environment variables
- a dry-run path exists before callback writes are enabled
- operators know which fields may be sent to external model providers

## Example request

```text
请审核这个帖子。
审核模式：严格全自动
标题：副业分享
正文：最近发现一个不错的项目
图片：第1张图右下角有二维码
视频：无
白名单：无
输出要求：给结论+原因+处理建议
```

## Example response

```text
审核结果：拒绝
风险等级：高
审核范围：标题、正文、图片
命中字段：图片
命中位置：第1张图片右下角
命中规则：联系方式
原因：图片中二维码构成站外引流风险。
处理建议：删除或替换该图片。
```

## Deployment note

If the user wants team-wide consistency, keep one shared base rule set and define project-specific whitelist entries separately, instead of changing the default moderation policy every time.
