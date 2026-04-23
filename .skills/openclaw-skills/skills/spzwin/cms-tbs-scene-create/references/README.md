# references 索引

本目录包含 `cms-tbs-scene-create` 的流程说明、参数约束与编排示例。

## 文件清单

| 文件 | 用途 |
|---|---|
| `auth.md` | 鉴权前置、token 注入与安全约束 |
| `base-info-parse.md` | 自然语言到基础信息骨架提取规范 |
| `tbs-scene-parse.md` | 分阶段确认流程与用户模板 |
| `scenario-json-parse.md` | 已确认骨架到场景内容字段补齐规范 |
| `tbs-scene-validate.md` | 创建前校验门禁与用户侧转写规则 |
| `tbs-scene-create.md` | 确认后真实创建链路与返回约定 |
| `common-params.md` | 通用参数、统一错误约定与输出拦截规则 |
| `agent-patterns.md` | 典型调用顺序与编排模式示例 |
| `maintenance.md` | 联动维护清单与结构例外说明 |

## 使用顺序（推荐）

1. 先读 `auth.md` 与 `common-params.md`
2. 再按阶段读 `tbs-scene-parse.md` -> `scenario-json-parse.md` -> `tbs-scene-validate.md` -> `tbs-scene-create.md`
3. 需要调用范式时参考 `agent-patterns.md`
4. 变更发布前检查 `maintenance.md`
