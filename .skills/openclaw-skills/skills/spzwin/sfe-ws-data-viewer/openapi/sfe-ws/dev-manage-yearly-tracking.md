# 开发管理年度跟踪表

查询维盛专属开发管理年度跟踪表数据。

**接口地址**: `/bia/open/biz-service/sfe-ws-report/devManageYearlyTrackingReport`

**请求方式**: POST

---

## Headers

- `appKey` (string, 必填): 应用密钥，从环境变量 `XG_BIZ_API_KEY` 获取
- `Content-Type`: application/json

---

## 请求参数

| 参数名        | 类型   | 必填 | 说明                   |
| ------------- | ------ | ---- | ---------------------- |
| zoneId        | string | 否   | 区划ID                 |
| regionName    | string | 否   | 大区名称，支持模糊查询 |
| areaName      | string | 否   | 地区名称，支持模糊查询 |
| territoryName | string | 否   | 辖区名称，支持模糊查询 |
| year          | number | 否   | 年度                   |
| quarter       | number | 否   | 季度                   |
| page          | number | 否   | 页码，默认1            |

---

## 响应参数

**data**: 数组，包含以下字段：

| 参数名                                    | 类型   | 说明                         |
| ----------------------------------------- | ------ | ---------------------------- |
| id                                        | string | ID                           |
| year                                      | number | 年度                         |
| regionName                                | string | 大区名称                     |
| areaName                                  | string | 地区名称                     |
| territoryName                             | string | 岗位名称                     |
| positionType                              | string | 岗位类型                     |
| managerName                               | string | 负责人                       |
| productName                               | string | 品种名称                     |
| hcoId                                     | string | 医院ID                       |
| hcoName                                   | string | 医院名称                     |
| hcoCpId                                   | string | 医院云平台ID                 |
| outpatientAmount                          | number | 门诊量/年                    |
| operationAmount                           | number | 抗VEGF眼底针数/月            |
| monthlyHcoPotentialAmount                 | number | 医院月潜力                   |
| sourceType                                | string | 今年开发标记                 |
| hcoNatureType                             | string | 医院性质                     |
| hqName                                    | string | 集团归属                     |
| hcoGradeType                              | string | 医院级别                     |
| hcoManageType                             | string | 医院类别                     |
| cyStartDevelopStatus                      | string | 年初开发状态                 |
| cyDevelopStatus                           | string | 当前开发状态                 |
| cyIsDualChannelEnabled                    | string | 双通道是否已打通             |
| cyDevelopmentSelect                       | string | 院内/双通道开发选择          |
| currentYearDevelopmentPercentage          | number | 今年开发几率                 |
| currentYearTargetAmount                   | number | 今年目标量M2                 |
| currentYearProductunitPrice               | number | 今年品种单价                 |
| plannedDevelopmentQuarter                 | string | 计划开发季度                 |
| plannedDevelopmentCost                    | number | 计划开发费用/元              |
| cyClinicalClient                          | string | 锁定临床关键客户             |
| cyClinicalClientViewpoint                 | string | 临床关键客户观点             |
| cyPharmacyClient                          | string | 锁定药学关键客户             |
| cyPharmacyClientViewpoint                 | string | 药学关键客户关系             |
| cyAdministrationClient                    | string | 锁定行政关键客户             |
| cyAdministrationClientRelationship        | string | 锁定行政关键客户关系         |
| hcoDevelopmentModelsDescription           | string | 医院既往开发模式简述         |
| quarter                                   | number | 季度                         |
| cqPlannedDevelopmentQuarter               | string | 预计成功开发季度             |
| cqPlannedDevelopmentCost                  | number | 计划开发费用/元              |
| cqStartDevelopStatus                      | string | 季度初开发状态               |
| cqDevelopStatus                           | string | 当前开发状态                 |
| cqIsDualChannelEnabled                    | string | 双通道是否已打通             |
| cqDevelopmentSelect                       | string | 院内/双通道开发选择          |
| cqFollowQuarter                           | string | 跟进季度                     |
| cqClinicalClient                          | string | 锁定临床关键客户             |
| cqClinicalClientViewpoint                 | string | 临床关键客户观点             |
| cqPharmacyClient                          | string | 锁定药学关键客户             |
| cqPharmacyClientViewpoint                 | string | 药学关键客户关系             |
| cqAdministrationClient                    | string | 锁定行政关键客户             |
| cqAdministrationClientRelationship        | string | 锁定行政关键客户关系         |
| cqClinicalClientPlanningResources         | string | 临床客户规划资源             |
| cqPharmacyClientPlanningResources         | string | 药学客户规划资源             |
| cqAdministrationClientPlanningResources   | string | 行政客户规划资源             |
| cqClinicalRoleCount                       | number | 临床关键客户规划学术会议次数 |
| cqClinicalAcademicConferenceExpense       | number | 临床关键客户规划学术会议费用 |
| cqClinicalAcademicLinkCount               | number | 临床关键客户学术规划链接次数 |
| cqClinicalAcademicLinkExpense             | number | 临床关键客户学术规划链接费用 |
| cqAdministrationRoleCount                 | number | 行政关键客户学术规划会议次数 |
| cqAdministrationAcademicConferenceExpense | number | 行政关键客户规划学术会议费用 |
| cqAdministrationAcademicLinkCount         | number | 行政关键客户规划学术链接次数 |
| cqAdministrationAcademicLinkExpense       | number | 行政关键客户规划学术链接费用 |
| cqPharmacyRoleCount                       | number | 药学关键客户规划学术会议次数 |
| cqPharmacyAcademicConferenceExpense       | number | 药学关键客户规划学术会议费用 |
| cqPharmacyAcademicLinkCount               | number | 药学关键客户规划学术链接次数 |
| cqPharmacyAcademicLinkExpense             | number | 药学关键客户规划学术链接费用 |
| cqClinicalVisitCount                      | number | 临床关键客户学术拜访次数     |
| cqClinicalLinkCount                       | number | 临床关键客户学术链接次数     |
| cqClinicalMeetingCount                    | number | 临床关键客户学术会议次数     |
| cqAdministrationVisitCount                | number | 行政关键客户学术拜访次数     |
| cqAdministrationLinkCount                 | number | 行政关键客户学术链接次数     |
| cqAdministrationMeetingCount              | number | 行政关键客户学术会议次数     |
| cqPharmacyVisitCount                      | number | 药学关键客户学术拜访次数     |
| cqPharmacyLinkCount                       | number | 药学关键客户学术链接次数     |
| cqPharmacyMeetingCount                    | number | 药学关键键客户学术会议次数   |
| w1PlanContent                             | string | W1周计划                     |
| w2PlanContent                             | string | W2周计划                     |
| w3PlanContent                             | string | W3周计划                     |
| w4PlanContent                             | string | W4周计划                     |
| w5PlanContent                             | string | W5周计划                     |
| w6PlanContent                             | string | W6周计划                     |
| w7PlanContent                             | string | W7周计划                     |
| w8PlanContent                             | string | W8周计划                     |
| w9PlanContent                             | string | W9周计划                     |
| w10PlanContent                            | string | W10周计划                    |
| w11PlanContent                            | string | W11周计划                    |
| w12PlanContent                            | string | W12周计划                    |
| w13PlanContent                            | string | W13周计划                    |
| w14PlanContent                            | string | W14周计划                    |
| w1IsPlanningExecute                       | string | W1是否完全执行               |
| w2IsPlanningExecute                       | string | W2是否完全执行               |
| w3IsPlanningExecute                       | string | W3是否完全执行               |
| w4IsPlanningExecute                       | string | W4是否完全执行               |
| w5IsPlanningExecute                       | string | W5是否完全执行               |
| w6IsPlanningExecute                       | string | W6是否完全执行               |
| w7IsPlanningExecute                       | string | W7是否完全执行               |
| w8IsPlanningExecute                       | string | W8是否完全执行               |
| w9IsPlanningExecute                       | string | W9是否完全执行               |
| w10IsPlanningExecute                      | string | W10是否完全执行              |
| w11IsPlanningExecute                      | string | W11是否完全执行              |
| w12IsPlanningExecute                      | string | W12是否完全执行              |
| w13IsPlanningExecute                      | string | W13是否完全执行              |
| w14IsPlanningExecute                      | string | W14是否完全执行              |
| w1DevelopmentStatus                       | string | W1周开发状态                 |
| w2DevelopmentStatus                       | string | W2周开发状态                 |
| w3DevelopmentStatus                       | string | W3周开发状态                 |
| w4DevelopmentStatus                       | string | W4周开发状态                 |
| w5DevelopmentStatus                       | string | W5周开发状态                 |
| w6DevelopmentStatus                       | string | W6周开发状态                 |
| w7DevelopmentStatus                       | string | W7周开发状态                 |
| w8DevelopmentStatus                       | string | W8周开发状态                 |
| w9DevelopmentStatus                       | string | W9周开发状态                 |
| w10DevelopmentStatus                      | string | W10周开发状态                |
| w11DevelopmentStatus                      | string | W11周开发状态                |
| w12DevelopmentStatus                      | string | W12周开发状态                |
| w13DevelopmentStatus                      | string | W13周开发状态                |
| w14DevelopmentStatus                      | string | W14周开发状态                |
| cqActualDevelopmentQuarter                | string | 实际开发季度                 |
| cqActualDevelopmentCost                   | number | 实际开发费用/元              |

---

## 脚本调用

```bash
python3 scripts/sfe-ws/dev-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
```

支持参数：

- `--zoneId`: 区划ID（必填）
- `--year`: 年度
- `--quarter`: 季度
- `--page`: 页码
- `--count`: 查询总记录数

---

## 查询总记录数

在接口地址后追加 `/count`：

```
/bia/open/biz-service/sfe-ws-report/devManageYearlyTrackingReport/count
```

脚本使用：

```bash
python3 scripts/sfe-ws/dev-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --count
```
