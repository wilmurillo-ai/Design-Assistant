# sfe-user — 使用说明

## 什么时候使用

- 用户问"查询我有权限的区划/产品/客户"等基础数据
- 用户问"我的数据采集项目有哪些"
- 用户问"我的待办任务有哪些"
- 用户问"查询我的计划/实际/采集数据"
- 需要获取用户维度的基础数据或项目数据时

## 标准流程

### 场景一：获取用户授权的基础数据

1. 鉴权预检（需要 `appKey` 时，优先读取 `cms-auth-skills/SKILL.md`；如未安装先安装）
2. 调用 `scripts/sfe-user/zone.py` 获取区划列表
3. 调用 `scripts/sfe-user/product.py` 获取产品列表
4. 调用 `scripts/sfe-user/customer.py` 获取客户列表
5. 输出摘要信息

### 场景二：查询项目数据采集任务

1. 鉴权预检
2. 调用 `scripts/sfe-user/project-summary.py` 获取项目列表，筛选目标项目获取 `projectId`
3. 调用 `scripts/sfe-user/project-period.py` 获取周期列表，选择目标周期获取 `periodCode`
4. 调用 `scripts/sfe-user/project-schema.py` 获取模板定义
5. 根据项目类型调用对应数据查询脚本：
   - 目标管理类项目：`project-plan.py` 或 `project-actual.py`
   - 普通采集项目：`project-general.py`
6. 输出数据摘要

### 场景三：查询待办任务

1. 鉴权预检
2. 调用 `scripts/sfe-user/project-summary.py` 获取项目列表
3. 调用 `scripts/sfe-user/project-task.py` 查询待办任务状态
4. 输出任务摘要（任务名称、状态、截止日期）

## 常用接口说明

| 接口 | 返回关键字段 | 后续用途 |
|---|---|---|
| zone | `id` | 作为 sfe-zone 接口的 `zoneId` |
| product | `id` | 作为 customer-profile 的 `productId` |
| customer | `id` | 作为 customer-profile 的 `customerId` |
| customer-profile | `id` | 作为 coverage 的 `customerProfileId` |
| project-summary | `id` | 作为项目相关接口的 `projectId` |
| project-period | `periods[].code` | 作为数据查询接口的 `periodCode` |
| project-schema | `schemas[].code` | 作为数据查询接口的 `schemaCode` |

## 数据流向图

```
zone → coverage ← customer-profile ← customer
  ↓
sfe-zone/project-* (需要 zoneId)
  
project-summary → project-period → project-schema
  ↓                    ↓                 ↓
project-task      periodCode        schemaCode
  ↓                    ↓                 ↓
project-plan / project-actual / project-general
```
