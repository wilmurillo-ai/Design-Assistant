# 医院管理年度跟踪表

查询维盛专属医院管理年度跟踪表数据。

**接口地址**: `/bia/open/biz-service/sfe-ws-report/hcoManageYearlyTrackingReport`

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
| year          | string | 否   | 年度                   |
| page          | number | 否   | 页码，默认1            |

---

## 响应参数

**data**: 数组，包含以下字段：

| 参数名                   | 类型   | 说明                                       |
| ------------------------ | ------ | ------------------------------------------ |
| id                       | string | ID                                         |
| year                     | number | 年                                         |
| region                   | string | 大区名称                                   |
| area                     | string | 地区名称                                   |
| territory                | string | 岗位名称                                   |
| positionType             | string | 岗位类型                                   |
| jobState                 | string | 在职状态                                   |
| managerName              | string | 负责人名称                                 |
| hcoCpId                  | string | 医院云平台ID                               |
| productName              | string | 产品名称                                   |
| hcoName                  | string | 医院名称                                   |
| hcoCollectionType        | string | 集合类别                                   |
| hcoNatureType            | string | 医院性质                                   |
| hcoGradeType             | string | 医院级别                                   |
| hqName                   | string | 集团归属                                   |
| hcoManageType            | string | 医院类别                                   |
| cyHcoWorkTarget          | string | 年度医院工作目标                           |
| cyYearlyM3Amount         | string | 年度M3目标量                               |
| blyCompleted             | number | 前年完成                                   |
| lyCompleted              | number | 去年完成                                   |
| lyYoy                    | number | 去年同比                                   |
| lyQ1Flow                 | number | 去年Q1流向                                 |
| lyQ2Flow                 | number | 去年Q2流向                                 |
| lyQ3Flow                 | number | 去年Q3流向                                 |
| lyQ4Flow                 | number | 去年Q4流向                                 |
| cyM2Task                 | number | 今年M2任务                                 |
| cyFlow                   | number | 今年流向                                   |
| m01Flow                  | number | 今年1月流向                                |
| m02Flow                  | number | 今年2月流向                                |
| m03Flow                  | number | 今年3月流向                                |
| q1Flow                   | number | 今年1季度流向                              |
| q1Yoy                    | number | 今年1季度流向同比                          |
| q1Mom                    | number | 今年1季度流向环比                          |
| q1M2Progress             | number | 今年1季度M2进度                            |
| m04Flow                  | number | 今年4月流向                                |
| m05Flow                  | number | 今年5月流向                                |
| m06Flow                  | number | 今年6月流向                                |
| q2Flow                   | number | 今年2季度流向                              |
| q2Yoy                    | number | 今年2季度流向同比                          |
| q2Mom                    | number | 今年2季度流向环比                          |
| q2M2Progress             | number | 今年2季度M2进度                            |
| h1Flow                   | number | 今年上半年流向                             |
| h1Yoy                    | number | 今年上半年流向同比                         |
| h1M2Progress             | number | 今年上半年M2进度                           |
| m07Flow                  | number | 今年7月流向                                |
| m08Flow                  | number | 今年8月流向                                |
| m09Flow                  | number | 今年9月流向                                |
| q3Flow                   | number | 今年3季度流向                              |
| q3Yoy                    | number | 今年3季度流向同比                          |
| q3Mom                    | number | 今年3季度流向环比                          |
| q3M2Progress             | number | 今年3季度M2进度                            |
| m10Flow                  | number | 今年10月流向                               |
| m11Flow                  | number | 今年11月流向                               |
| m12Flow                  | number | 今年12月流向                               |
| q4Flow                   | number | 今年4季度流向                              |
| q4Yoy                    | number | 今年4季度流向同比                          |
| q4Mom                    | number | 今年4季度流向环比                          |
| q4M2Progress             | number | 今年4季度M2进度                            |
| h2Flow                   | number | 今年下半年流向                             |
| h2Yoy                    | number | 今年下半年流向同比                         |
| h2M2Progress             | number | 今年下半年M2进度                           |
| cyYtdCompleted           | number | 今年ytd完成                                |
| cyYtdM2Progress          | number | 今年YTD完成进度                            |
| cqTask                   | number | 当前季度M2任务                             |
| cqHcoWorkTarget          | string | 当前季度医院工作目标                       |
| cqLockedCustCnt          | string | 当前季度锁定客户数                         |
| cqLockedKeyUpgIncCustCnt | string | 当前季度锁定提级+增量客户数                |
| cqLockedMntDosageCustCnt | string | 当前季度锁定维持用量客户数                 |
| hcoLockedMeetingCnt      | number | 当前季度医院锁定客户的季度规划学术会议次数 |
| hcoLockedMeetingAmt      | number | 当前季度医院锁定客户的季度规划学术会议金额 |
| hcoLockedLinkCnt         | number | 当前季度医院锁定客户的季度规划学术链接次数 |
| hcoLockedLinkAmt         | number | 当前季度医院锁定客户的季度规划学术链接金额 |
| cmW1Flow                 | number | 当月第1周流向                              |
| cmW2Flow                 | number | 当月第2周流向                              |
| cmW3Flow                 | number | 当月第3周流向                              |
| cmW4Flow                 | number | 当月第4周流向                              |
| cmW5Flow                 | number | 当月第5周流向                              |
| cmW6Flow                 | number | 当月第6周流向                              |
| cmFlow                   | number | 当月流向代表填报                           |
| cmFlowSync               | number | 当月流向系统带入                           |
| cmActVisitCnt            | number | 当月实际执行学术拜访次数                   |
| cmActLinkCnt             | number | 当月实际执行学术链接次数                   |
| cmActMeetingCnt          | number | 当月实际执行学术会议次数                   |
| cqActVisitCnt            | number | 当前季度实际执行学术拜访次数               |
| cqActLinkCnt             | number | 当前季度实际执行学术链接次数               |
| cqActMeetingCnt          | number | 当前季度实际执行学术会议次数               |
| monthlyAverageRate       | number | 季度锁定客户上季度用量占比                 |
| cqCost                   | number | 当季度费用使用                             |

---

## 脚本调用

```bash
python3 scripts/sfe-ws/hco-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
```

支持参数：

- `--zoneId`: 区划ID（必填）
- `--year`: 年度
- `--page`: 页码
- `--count`: 查询总记录数

---

## 查询总记录数

在接口地址后追加 `/count`：

```
/bia/open/biz-service/sfe-ws-report/hcoManageYearlyTrackingReport/count
```

脚本使用：

```bash
python3 scripts/sfe-ws/hco-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --count
```
