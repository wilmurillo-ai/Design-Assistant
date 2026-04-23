---
name: explosive-cover-generator-gzh
version: 1.1.2
description: 为公众号内容创作打造的AI封面设计工具，基于全网超过1000条的10w+文章，深度总结爆款封面规律，结合您的需求生成符合公众号平台的爆款封面。
dependency:
  python:
    - requests>=2.28.0
---

# 爆款封面生成

## 使用说明（入口）

本技能的完整执行规范已抽离到引用文档，不在本文件直接展开。

在执行任务前，必须先读取并严格遵循：

- `references/workflow.md`（完整任务流程与强制规则）
- `references/report_template.md`（HTML报告模板）
- `references/gzh_trend_data_format.md`（接口数据结构说明）

## 强制要求

- 禁止跳过引用文档中的任一步骤与校验项。
- 所有对外输出统一使用“爆款封面”术语。
- 爆款数据仅允许通过脚本接口获取，禁止使用其他来源。
