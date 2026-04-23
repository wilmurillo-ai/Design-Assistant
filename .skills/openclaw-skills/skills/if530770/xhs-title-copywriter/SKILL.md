---
name: xhs-explosive-content-suite
description: 基于用户输入的任何信息生成小红书爆款标题的专业工具。无论用户输入什么，最终目标都是生成小红书爆款标题。任务只在主agent执行，不在子agent执行。
dependency:
  python:
    - requests>=2.28.0
  system:
---

# 小红书爆款标题生成器

触发本技能并需要执行完整流程时，**必须先读取**与本技能同目录下的 `references/core_workflow.md`，并**完整遵循**其中的触发规则、术语规范、数据来源约束、完整操作步骤、自检清单与注意事项。脚本路径相对于技能目录：`scripts/fetch_xhs_trends.py`。
