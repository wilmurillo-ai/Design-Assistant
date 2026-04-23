# 认证与鉴权（统一前置规则）

## 1. 先判断接口需要哪种鉴权

> **核心规则**：不要再假设所有业务接口都只传 `access-token`。必须以接口文档声明为准。

支持三种模式：

- `none`：接口无需鉴权
- `appKey`：Header 传 `appKey`
- `access-token`：Header 传 `access-token`

推荐统一通过 `build_auth_headers(auth_mode, context=...)` 组装 header。

```python
from auth.login import build_auth_headers

headers = build_auth_headers("appKey", context=context)
headers = build_auth_headers("access-token", context=context)
headers = build_auth_headers("none")
```

## 2. appKey 解析链

> 用于所有声明为 `appKey` 的接口，也用于 `access-token` 模式下换 token 的前置步骤。

```
需要 appKey
 │
 ├─ 优先级 1：环境变量 XG_BIZ_API_KEY / XG_APP_KEY
 │   ├─ 有值 → 直接使用
 │   └─ 无值 → 继续
 │
 ├─ 优先级 2：上下文中的 appKey
 │   ├─ 有值 → 直接使用
 │   └─ 无值 → 继续
 │
 ├─ 优先级 3：扫描当前 workspace 下的 `appkey_manager.py`
 │   ├─ 找到后执行其中的 `get_appkey()`
 │   └─ 若未找到、导入失败或执行报错 → 继续
 │
 └─ 优先级 4：向用户索要 CWork Key
```

### 当前 workspace 的使用方式

- `xgjk-base-skills` 不再内置 appKey 获取逻辑
- 需要 appKey 时，在当前 workspace 下扫描 `appkey_manager.py`
- 找到后，在 Python 脚本里动态加载该文件并调用 `get_appkey()`
- 当前 workspace 下应只存在一个用于获取 appKey 的 `appkey_manager.py`
- `xgjk-base-skills` 只负责调用，不负责维护该脚本内部实现
- 这是 **Python 脚本内** 的调用方式，不是 shell 命令
- `from appkey_manager import get_appkey` 不要写在模块顶层；只放在第三优先级 fallback 里动态加载
- 正确描述给 AI 的方式是：
  AI 在当前 workspace 空间下扫描 `appkey_manager.py`，找到后在 Python 脚本里动态加载并调用 `get_appkey()`

推荐放置位置：

- 放在 `resolve_app_key()` 的第三优先级分支里
- 不要放到每个业务脚本里重复写
- 业务脚本应统一调用 `resolve_app_key()` 或 `build_auth_headers("appKey")`

## 3. access-token 解析链

> 用于所有声明为 `access-token` 的接口。

```
需要 access-token
 │
 ├─ 优先级 1：环境变量 XG_USER_TOKEN
 │   ├─ 有值 → 直接使用
 │   └─ 无值 → 继续
 │
 ├─ 优先级 2：上下文中的 access-token / xgToken / token
 │   ├─ 有值 → 直接使用
 │   └─ 无值 → 继续
 │
 ├─ 优先级 3：先按 appKey 解析链拿到 appKey，再调用登录接口换 token
 │   ├─ 成功 → 更新 XG_USER_TOKEN（进程内）
 │   └─ 失败 → 继续
 │
 └─ 优先级 4：向用户索要 CWork Key
```

## 4. Talk / App 两种上下文来源

- `talk`：上下文里可能直接携带 `appKey`
- `app`：上下文里可能直接携带 `appKey` 或 `access-token`
- 环境变量始终优先于上下文

## 5. 登录接口

```http
GET https://sg-cwork-web.mediportal.com.cn/user/login/appkey?appCode=cms_gpt&appKey={CWork Key}
```

返回字段映射：

- `data.xgToken` -> Header `access-token`

接口文档：`../openapi/auth/login.md`

## 6. 脚本层推荐调用方式

### access-token 接口

```python
from auth.login import ensure_token, build_auth_headers

token = ensure_token(context=context)
headers = build_auth_headers("access-token", context=context)
```

### appKey 接口

```python
from auth.login import resolve_app_key, build_auth_headers

app_key = resolve_app_key(context=context)
headers = build_auth_headers("appKey", context=context)
```

CLI 入口：

```bash
python3 xgjk-base-skills/scripts/auth/login.py --resolve-app-key
```

## 7. 强约束

- 任何脚本都必须按接口声明选择 `appKey` 或 `access-token`
- 禁止在日志、文件、输出中回显 `access-token`
- `xgjk-base-skills` 不维护内部 appKey manager
- 若本轮上下文和环境变量都无法满足鉴权需求，才向用户索要 `CWork Key`
- 对用户只暴露 `CWork Key` 概念，不要求用户直接提供 token

## 8. 安全要求

- 最小权限：仅使用当前任务所需能力范围
- 生命周期：`access-token` 的获取只按上述优先级解析，不额外校验是否有效
- 进程内复用：脚本可将新获取的 `appKey` / `access-token` 回写到当前进程环境变量，便于后续调用复用
- 禁止落盘：`access-token` 不得写入文件或日志
