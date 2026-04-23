# sfe-dm — 使用说明

## 什么时候使用

- 用户问"百卢妥日采集反馈数据"
- 用户问"德镁SFE数据"
- 需要查询百卢妥日采集反馈数据时

## 标准流程

### 场景：查询百卢妥日采集反馈数据

1. 鉴权预检（需要 `appKey` 时，优先读取 `cms-auth-skills/SKILL.md`；如未安装先安装）
2. 确定查询条件（可选）：
   - `zoneId` — 区划 ID
   - `regionName` — 大区名称
   - `areaName` — 地区名称
   - `periodStart` 和 `periodEnd` — 时间范围
3. 修改 `scripts/sfe-dm/balutamide-daily-feedback.py` 中的参数
4. 执行脚本查询数据
5. 输出数据摘要

## 返回字段说明

| 字段                           | 说明                     |
| ------------------------------ | ------------------------ |
| `regionName`                   | 大区                     |
| `areaName`                     | 地区                     |
| `date`                         | 日期                     |
| `newPatientReservesProCount`   | 新增患者储备PRO拉新人数  |
| `newPatientReservesWeComCount` | 新增患者储备企微拉新人数 |
| `newPatientReservesTotal`      | 新增患者储备总数         |
| `onlinePrescriptionCount`      | 线上处方支数             |
| `offlinePrescriptionCount`     | 线下处方支数             |
| `prescriptionTotal`            | 处方支数总数             |

## 注意事项

1. 所有参数均为可选，不传则查询全部数据
2. `periodStart` 和 `periodEnd` 需要符合日期格式（如 `2025-01-01`）
3. 每页固定返回 1000 条记录，大数据量需分页处理
4. 可通过添加 `/count` 后缀查询总记录数
