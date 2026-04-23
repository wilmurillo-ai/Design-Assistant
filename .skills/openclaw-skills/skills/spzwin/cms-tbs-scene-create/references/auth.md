### cms-auth-skills：access-token 获取与注入（强制）

这份规则用于约束 Agent：任何需要执行本 Skill 真实创建链路的 `scripts/*.py`，`access-token` 获取必须通过依赖 Skill `cms-auth-skills` 完成。

#### 必须做

- 只要确定要进入真实创建链路（`exec python3 scripts/tbs-scene-create.py`），在调用目标脚本之前，**必须先调用** `cms-auth-skills` 获取 `access-token`。
- 将 `cms-auth-skills` 返回的 `access-token` **以 `--access-token`** 注入到后续执行命令：
  - `python3 scripts/tbs-scene-create.py ... --access-token "<ACCESS_TOKEN>"`
- 若使用 `--params-file` 注入参数，业务参数仍放在 JSON 中，`access-token` 继续使用命令行显式传入。

#### 必须禁止

- 禁止在未经过 `cms-auth-skills` 的情况下直接进入真实创建链路。
- 禁止向用户索要内部 token 原文。
- 禁止在 `cms-auth-skills` 未返回可用 `access-token` 时继续调用 `tbs-scene-create.py`。
- 禁止在用户可见回复、日志、报错透传中输出 token/appKey/header 原文或可逆片段。
- 禁止把 `access-token` 写入 `draftPath`、业务 payload 持久化文件或非鉴权用途字段。

#### 失败处理

- `cms-auth-skills` 获取失败或无可用 `access-token`：必须停止当前链路，并引导用户重新完成授权/登录；然后再重新尝试进入执行链路。
- 鉴权失败对用户只输出业务化提示，不暴露鉴权实现细节（如 header 名称、网关返回原文、调试栈）。

#### 环境与 Base URL（强制）

- TBS Admin 契约见仓库接口文档（以仓库最新版本为准）。
- 本 Skill 默认按**生产环境**联调：`https://sg-al-cwork-web.mediportal.com.cn/tbs-admin`（与 `tbs-scene-create.py` 的 `--base-url` 默认值一致）。
- `access-token` / appKey 必须与 `--base-url` 指向的 **同一套门户环境** 签发；跨环境混用会表现为鉴权失败或创建失败——应改用与环境一致的鉴权后再调用脚本。
