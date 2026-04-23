---
name: gzh-official-account-title-generator
description: 基于用户输入生成公众号爆款标题的专业工具，适用于标题创作、热点趋势参考与传播效果优化场景。
dependency:
  python:
    - requests>=2.28.0
---

# 公众号爆款标题生成器

## 使用说明（入口）

本技能完整执行规范已抽离到引用文档，执行前必须先读取并严格遵循：

- `references/priority_rules.md`（最高优先级规则）
- `references/workflow.md`（完整流程与步骤约束）
- `references/output_template.md`（输出模板与格式要求）

## 强制要求

- 不得跳过引用文档中的流程与校验项。
- 爆款数据仅允许通过脚本接口获取。
- 统一使用脚本：`scripts/fetch_official_account_trends.py`。

## 资源索引

- 数据查询脚本：`scripts/fetch_official_account_trends.py`
