# sfe-zone — 使用说明

## 什么时候使用

- 用户问"某个区划的待办任务有哪些"
- 用户问"某个区划的计划/实际/采集数据"
- 需要按区划维度查询数据时

## 前置条件

使用 sfe-zone 模块前，必须先获取以下信息：
1. `zoneId` — 通过 sfe-user/zone 接口获取
2. `projectId` — 通过 sfe-user/project-summary 接口获取
3. `periodStart` 和 `periodEnd` — 通过 sfe-user/project-period 接口获取

## 标准流程

### 场景：查询指定区划的任务完成情况

1. 鉴权预检（需要 `appKey` 时，优先读取 `cms-auth-skills/SKILL.md`；如未安装先安装）
2. 调用 `scripts/sfe-user/zone.py` 获取区划列表，选择目标区划获取 `zoneId`
3. 调用 `scripts/sfe-user/project-summary.py` 获取项目列表，选择目标项目获取 `projectId`
4. 调用 `scripts/sfe-user/project-period.py` 获取周期列表，确定 `periodStart` 和 `periodEnd`
5. 修改 `scripts/sfe-zone/project-task.py` 中的必填参数
6. 执行脚本查询该区划的待办任务状态
7. 根据需要调用 `project-plan.py`、`project-actual.py` 或 `project-general.py` 查询数据
8. 输出数据摘要

## 接口对比

| 维度 | sfe-user 接口 | sfe-zone 接口 |
|---|---|---|
| 数据范围 | 当前用户授权的所有数据 | 指定区划的数据 |
| 必填参数 | 通常只需 `projectId` | 需要 `zoneId`、`projectId`、`periodStart`、`periodEnd` |
| 使用场景 | 查看自己的数据 | 管理者查看下属区划数据 |

## 注意事项

1. sfe-zone 接口的必填参数较多，执行前务必确认参数完整
2. `periodStart` 和 `periodEnd` 需要符合日期格式（如 `2025-11-01`）
3. 返回的数据结构包含 `fieldValue` 字段，其结构由模板定义决定
