# 客户管理年度跟踪表

查询维盛专属客户管理年度跟踪表数据。

**接口地址**: `/bia/open/biz-service/sfe-ws-report/hcpManageYearlyTrackingReport`

**请求方式**: POST

---

## Headers

- `appKey` (string, 必填): 应用密钥，从环境变量 `XG_BIZ_API_KEY` 获取
- `Content-Type`: application/json

---

## 请求参数

| 参数名  | 类型   | 必填 | 说明        |
| ------- | ------ | ---- | ----------- |
| zoneId  | string | 否   | 区划ID      |
| year    | number | 否   | 年度        |
| quarter | number | 否   | 季度        |
| page    | number | 否   | 页码，默认1 |

---

## 响应参数

**data**: 数组，包含以下字段：

| 参数名                                     | 类型   | 说明                   |
| ------------------------------------------ | ------ | ---------------------- |
| id                                         | string | ID                     |
| year                                       | number | 年度                   |
| sourceType                                 | string | 来源标签               |
| regionName                                 | string | 大区名称               |
| areaName                                   | string | 地区名称               |
| territoryName                              | string | 岗位名称               |
| positionType                               | string | 岗位类型：专岗、组合岗 |
| managerName                                | string | 管理人                 |
| productName                                | string | 品种名称               |
| hcoId                                      | string | 医院id                 |
| hcoName                                    | string | 医院名称               |
| hcoCpId                                    | string | 医院云平台ID           |
| hcpId                                      | string | 医生ID                 |
| hcpName                                    | string | 医生名称               |
| hcpCpId                                    | string | 医生云平台ID           |
| deptName                                   | string | 医生科室               |
| subspecialityName                          | string | 亚专科标签名称         |
| isAdministrativeCustomer                   | string | 是否是行政客户         |
| lyRoleCount                                | number | 去年角色次数           |
| lyTargetLectureCount                       | number | 去年讲课次数           |
| cyKeyHospitalFlag                          | string | 重点医院标记           |
| lyMonthlyAverage                           | number | 去年月均量             |
| lyProductAwareness                         | string | 去年产品认知度         |
| cyMonthlyPotential                         | number | 今年月潜力量           |
| cyPotentialProductAwareness                | string | 今年潜力产品认知度     |
| cyTargetMonthlyAverage                     | number | 今年目标月均量         |
| cyTargetProductAwareness                   | string | 今年目标产品认知度     |
| cyRoleCount                                | number | 今年角色次数           |
| cyTargetLectureCount                       | number | 今年目标讲课次数       |
| cyFocusType                                | string | 年度聚焦类型           |
| cyQ1MonthlyAverageTarget                   | number | 今年Q1季度月均量       |
| cyQ2MonthlyAverageTarget                   | number | 今年Q2季度月均量       |
| cyQ3MonthlyAverageTarget                   | number | 今年Q3季度月均量       |
| cyQ4MonthlyAverageTarget                   | number | 今年Q4季度月均量       |
| cyAnnualTotalTarget                        | number | 年度总目标量           |
| cyQ1ExpenseInvestment                      | number | 今年Q1季度费用投入     |
| cyQ2ExpenseInvestment                      | number | 今年Q2季度费用投入     |
| cyQ3ExpenseInvestment                      | number | 今年Q3季度费用投入     |
| cyQ4ExpenseInvestment                      | number | 今年Q4季度费用投入     |
| cyEstimatedAnnualExpensePerBox             | number | 年度预计单盒费用       |
| cyEstimatedAnnualTotalExpense              | number | 预估年度总费用         |
| cyEstimatedAnnualAcademicConferenceExpense | number | 预估年度学术会议费用   |
| cyEstimatedAnnualAcademicLinkExpense       | number | 预估年度学术链接费用   |
| quarter                                    | string | 季度                   |
| lqMonthlyAverage                           | number | 上季度月均完成量       |
| lqProductAwareness                         | string | 上季度产品认知度       |
| cqTargetMonthlyAverage                     | number | 本季度月均目标量       |
| cqTargetProductAwareness                   | string | 本季度目标产品认知度   |
| cqHcoWorkTarget                            | string | 本季度医院工作目标     |
| cqFocusType                                | string | 本季度聚焦类型         |
| cqRoleCount                                | number | 本季度规划学术会议次数 |
| cqTargetLectureCount                       | number | 本季度规划讲课次数     |
| cqAcademicLinkCount                        | string | 本季度规划关系营销次数 |
| cqAcademicLinkExpense                      | number | 本季度关系营销费用     |
| cqAcademicConferenceExpense                | number | 本季度学术营销费用     |
| cqActualRoleCount                          | number | 本季度已覆盖角色次数   |
| cqActualLectureCount                       | number | 本季度已覆盖讲课次数   |
| w1PlanContent                              | string | W1周计划               |
| w2PlanContent                              | string | W2周计划               |
| w3PlanContent                              | string | W3周计划               |
| w4PlanContent                              | string | W4周计划               |
| w5PlanContent                              | string | W5周计划               |
| w6PlanContent                              | string | W6周计划               |
| w7PlanContent                              | string | W7周计划               |
| w8PlanContent                              | string | W8周计划               |
| w9PlanContent                              | string | W9周计划               |
| w10PlanContent                             | string | W10周计划              |
| w11PlanContent                             | string | W11周计划              |
| w12PlanContent                             | string | W12周计划              |
| w13PlanContent                             | string | W13周计划              |
| w14PlanContent                             | string | W14周计划              |
| w1VisitCnt                                 | number | W1执行拜访次数         |
| w2VisitCnt                                 | number | W2执行拜访次数         |
| w3VisitCnt                                 | number | W3执行拜访次数         |
| w4VisitCnt                                 | number | W4执行拜访次数         |
| w5VisitCnt                                 | number | W5执行拜访次数         |
| w6VisitCnt                                 | number | W6执行拜访次数         |
| w7VisitCnt                                 | number | W7执行拜访次数         |
| w8VisitCnt                                 | number | W8执行拜访次数         |
| w9VisitCnt                                 | number | W9执行拜访次数         |
| w10VisitCnt                                | number | W10执行拜访次数        |
| w11VisitCnt                                | number | W11执行拜访次数        |
| w12VisitCnt                                | number | W12执行拜访次数        |
| w13VisitCnt                                | number | W13执行拜访次数        |
| w14VisitCnt                                | number | W14执行拜访次数        |
| w1LinkCnt                                  | number | W1执行学术连接次数     |
| w2LinkCnt                                  | number | W2执行学术连接次数     |
| w3LinkCnt                                  | number | W3执行学术连接次数     |
| w4LinkCnt                                  | number | W4执行学术连接次数     |
| w5LinkCnt                                  | number | W5执行学术连接次数     |
| w6LinkCnt                                  | number | W6执行学术连接次数     |
| w7LinkCnt                                  | number | W7执行学术连接次数     |
| w8LinkCnt                                  | number | W8执行学术连接次数     |
| w9LinkCnt                                  | number | W9执行学术连接次数     |
| w10LinkCnt                                 | number | W10执行学术连接次数    |
| w11LinkCnt                                 | number | W11执行学术连接次数    |
| w12LinkCnt                                 | number | W12执行学术连接次数    |
| w13LinkCnt                                 | number | W13执行学术连接次数    |
| w14LinkCnt                                 | number | W14执行学术连接次数    |
| w1MeetingCnt                               | number | W1执行学术会议次数     |
| w2MeetingCnt                               | number | W2执行学术会议次数     |
| w3MeetingCnt                               | number | W3执行学术会议次数     |
| w4MeetingCnt                               | number | W4执行学术会议次数     |
| w5MeetingCnt                               | number | W5执行学术会议次数     |
| w6MeetingCnt                               | number | W6执行学术会议次数     |
| w7MeetingCnt                               | number | W7执行学术会议次数     |
| w8MeetingCnt                               | number | W8执行学术会议次数     |
| w9MeetingCnt                               | number | W9执行学术会议次数     |
| w10MeetingCnt                              | number | W10执行学术会议次数    |
| w11MeetingCnt                              | number | W11执行学术会议次数    |
| w12MeetingCnt                              | number | W12执行学术会议次数    |
| w13MeetingCnt                              | number | W13执行学术会议次数    |
| w14MeetingCnt                              | number | W14执行学术会议次数    |
| m1SalesVolume                              | number | 当季度第1月销量        |
| m2SalesVolume                              | number | 当季度第2月销量        |
| m3SalesVolume                              | number | 当季度第3月销量        |
| avgSalesVolume                             | number | 季度月均量             |
| isCultivationSuccessful                    | string | 是否培养成功           |
| cqExpense                                  | number | 季度花费               |

---

## 脚本调用

```bash
python3 scripts/sfe-ws/hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
```

支持参数：

- `--zoneId`: 区划ID（可选）
- `--year`: 年度
- `--quarter`: 季度
- `--page`: 页码
- `--count`: 查询总记录数

---

## 查询总记录数

在接口地址后追加 `/count`：

```
/bia/open/biz-service/sfe-ws-report/hcpManageYearlyTrackingReport/count
```

脚本使用：

```bash
python3 scripts/sfe-ws/hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --count
```
