# 脚本清单 — sfe-user

## 共享依赖

- `../common/toon_encoder.py` — TOON 编码器，所有脚本的 API 响应必须经过此编码器转换后再输出

## 脚本列表

| 脚本                  | 对应接口                                               | 用途                           |
| --------------------- | ------------------------------------------------------ | ------------------------------ |
| `zone.py`             | `POST /bia/open/biz-service/sfe-user/zone`             | 查询用户授权的区划             |
| `product.py`          | `POST /bia/open/biz-service/sfe-user/product`          | 查询用户授权的产品             |
| `customer.py`         | `POST /bia/open/biz-service/sfe-user/customer`         | 查询用户授权的客户             |
| `customer-profile.py` | `POST /bia/open/biz-service/sfe-user/customer-profile` | 查询用户授权客户的画像         |
| `coverage.py`         | `POST /bia/open/biz-service/sfe-user/coverage`         | 查询用户授权的覆盖分管关系     |
| `project-summary.py`  | `POST /bia/open/biz-service/sfe-user/project-summary`  | 查询用户参与的数据采集项目摘要 |
| `project-period.py`   | `POST /bia/open/biz-service/sfe-user/project-period`   | 查询项目的周期列表             |
| `project-schema.py`   | `POST /bia/open/biz-service/sfe-user/project-schema`   | 查询项目的填报模板             |
| `project-role.py`     | `POST /bia/open/biz-service/sfe-user/project-role`     | 查询项目的角色权限             |
| `project-task.py`     | `POST /bia/open/biz-service/sfe-user/project-task`     | 查询用户的待办任务状态         |
| `project-plan.py`     | `POST /bia/open/biz-service/sfe-user/project-plan`     | 查询用户的计划编制数据         |
| `project-actual.py`   | `POST /bia/open/biz-service/sfe-user/project-actual`   | 查询用户的实际结果数据         |
| `project-general.py`  | `POST /bia/open/biz-service/sfe-user/project-general`  | 查询用户的采集填报数据         |

## 使用方式

```bash
# 设置环境变量
export XG_BIZ_API_KEY="your-appkey"

# 执行脚本（无必填参数）
python3 scripts/sfe-user/zone.py

# 如果用户存在多个租户身份，需传入 tenantId
python3 scripts/sfe-user/zone.py --tenantId <租户ID>

# zone.py 支持可选 status 参数
python3 scripts/sfe-user/zone.py --status <状态>
```

## 可选参数

| 参数         | 说明                                                                                                     |
| ------------ | -------------------------------------------------------------------------------------------------------- |
| `--tenantId` | 租户 ID。默认无须传入，用户存在多个租户身份时须传入。如未传入具体 tenantId，会返回用户可选择的租户列表。 |
| `--status`   | 状态筛选（仅 zone.py 支持）                                                                              |

## 输出说明

所有脚本的输出均为 **TOON 格式**（非原始 JSON），这是一种面向 LLM 的高密度压缩格式，可大幅节省 Token 消耗。

## 规范

1. **必须使用 Python** 编写
2. **必须经过 toon_encoder** 处理后再输出
3. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范
4. **入参定义以** `openapi/` 文档为准
