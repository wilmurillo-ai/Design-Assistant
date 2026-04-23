# 脚本清单 — sfe-zone

## 共享依赖

- `../common/toon_encoder.py` — TOON 编码器，所有脚本的 API 响应必须经过此编码器转换后再输出

## 脚本列表

| 脚本                 | 对应接口                                              | 用途                       |
| -------------------- | ----------------------------------------------------- | -------------------------- |
| `project-task.py`    | `POST /bia/open/biz-service/sfe-zone/project-task`    | 查询指定区划的待办任务     |
| `project-plan.py`    | `POST /bia/open/biz-service/sfe-zone/project-plan`    | 查询指定区划的计划编制数据 |
| `project-actual.py`  | `POST /bia/open/biz-service/sfe-zone/project-actual`  | 查询指定区划的实际结果数据 |
| `project-general.py` | `POST /bia/open/biz-service/sfe-zone/project-general` | 查询指定区划的采集填报数据 |

## 使用方式

```bash
# 设置环境变量
export XG_BIZ_API_KEY="your-appkey"

# 执行脚本（通过命令行参数传入必填参数）
python3 scripts/sfe-zone/project-task.py --zoneId <区划ID> --projectId <项目ID> --periodStart <开始日期> --periodEnd <结束日期>

# 如果用户存在多个租户身份，需传入 tenantId
python3 scripts/sfe-zone/project-task.py --tenantId <租户ID> --zoneId <区划ID> --projectId <项目ID> --periodStart <开始日期> --periodEnd <结束日期>
```

## 可选参数

| 参数         | 说明                                                                                                     |
| ------------ | -------------------------------------------------------------------------------------------------------- |
| `--tenantId` | 租户 ID。默认无须传入，用户存在多个租户身份时须传入。如未传入具体 tenantId，会返回用户可选择的租户列表。 |
| `--page`     | 页码，默认为 1                                                                                           |
| `--status`   | 任务状态（仅 project-task.py 支持）                                                                      |

## 输出说明

所有脚本的输出均为 **TOON 格式**（非原始 JSON），这是一种面向 LLM 的高密度压缩格式，可大幅节省 Token 消耗。

## 注意事项

sfe-zone 模块的接口需要必填参数：

- `zoneId` — 区划 ID
- `projectId` — 项目 ID
- `periodStart` — 周期开始时间
- `periodEnd` — 周期结束时间

执行前请根据实际业务需求修改脚本中的 body 参数。

## 规范

1. **必须使用 Python** 编写
2. **必须经过 toon_encoder** 处理后再输出
3. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范
4. **入参定义以** `openapi/` 文档为准
