---
name: anyshare-mcp
description: "【配置】首次使用自动写入默认 MCP 服务地址（可改）。 【链接触发】当用户提供 anyshare.aishu.cn 分享链接（https://anyshare.aishu.cn/link/...）时，自动激活本技能；【搜索】用户提到 AnyShare、asmcp、文档库、文件管理、知识库、智能搜索 时，激活文件搜索；【读写操作】文件上传/下载、Bot 智能问答、全文写作（基于文档内容提取）。 English: Auto-apply default MCP URL on first use; then links, search, upload/download, Bot, writing."
homepage: "https://anyshare.aishu.cn"
metadata: '{"openclaw":{"category":"productivity","emoji":"📁","requires":{"bins":["agent-browser","mcporter"]},"openclawSkillsEntryFile":"openclaw.skill-entry.json"}}'
---

# AnyShare MCP 技能

## 📚 AnyShare 基础知识

> 以下为基础概念，供大模型理解 AnyShare 对象模型。

### 核心概念

| 术语 | 说明 | 示例 |
|------|------|------|
| **文档域** | 访问 AnyShare 的**站点域名**（产品用语）；各企业不同。 | `https://<贵司文档域主机>` |
| **MCP 服务地址** | MCP 网关完整 URL（`asmcp.url`）。**通常以文档域主机为前缀**，路径以运维为准；技能包默认 URL 仅为占位。 | `https://<文档域主机>/mcp`（示例） |
| **docid** | 文件库、文件夹、文件的完整唯一标识，有层级关系 | `gns://E6D15886.../A51FA4844.../2DDD46B195F24BCEB238DB59151CD15E` |
| **id** | docid 的最后一段（精简版唯一标识），部分接口文档别名 | `2DDD46B195F24BCEB238DB59151CD15E` |
| **sharedlink** | 文档库、文件夹、文件的分享链接，格式固定 | `https://anyshare.aishu.cn/link/AR0498B2639D3B4321B927A5F362600B35` |
| **namepath** | 云盘**展示用名字路径**（由 `file_convert_path` 将 gns docid 转换得到） | 如 `库名/文件夹/对象名`（以接口返回为准） |

> **别名说明**：
> 1. 因历史原因，docid 在部分接口文档中有别名：gnsid、gns目录、gns等，实际传值均同 docid（完整路径）。
> 2. id 在部分接口文档中有别名：objectid 等

### docid 与 id 的关系

```
docid = gns://<库ID>/<父目录ID>/.../<id>
                                                        ^^^^^^^^
                                                        id
```

> 例如：`gns://E6D15886.../2DDD46B195F24BCEB238DB59151CD15E`
> id 为 `2DDD46B195F24BCEB238DB59151CD15E`

### sharedlink 解析方法

分享链接点击后会重定向到带参数的 URL：
```
https://anyshare.aishu.cn/anyshare/zh-cn/link/ARXXXXX?_tb=none&belongs_to=document&item_id=gns%3A%2F%2F{编码的docid}&item_type=folder&type=realname
```

解析步骤：
1. 从 URL 中提取 `item_id` 参数（已 URL 编码）
2. 解码后得到完整 docid：`gns://E6D15886.../2DDD46B195F24BCEB238DB59151CD15E`
3. 取最后一段即为 id：`2DDD46B195F24BCEB238DB59151CD15E`
4. 根据 `item_type` 判断类型：
   - `item_type=folder` → 文件夹，用 `folder_sub_objects` 获取子文件
   - `item_type=file` 或其他 → 文件，直接用 docid 或 id 给工具

### 工具调用时 id vs docid 用法

| 工具 | 参数 | 传什么 | 说明 |
|------|------|--------|------|
| `chat_send` | `source_ranges[].id` | **id** | 只传最后一段，AnyShare 自动解析完整路径 |
| `folder_sub_objects` | `id` | **docid（完整）** | 需要完整路径 |
| `file_search` | — | — | 搜索工具，不需要手动拼接 |
| `file_osdownload` | `docid` | **docid（完整）** | 需要完整路径 |
| `file_convert_path` | `docid` | **docid（完整 gns）** | **仅用于展示**：返回 **`namepath`**（云盘名字路径）；**不**替代其它工具的 docid 传参 |

### 云盘路径（namepath）与 `file_convert_path`

- **用途**：将完整 **`gns://…` docid** 转为对话中易读的**云盘路径**（响应字段 **`namepath`**，POST `/efast/v1/file/convertpath`，与 MCP 服务实现一致）。
- **与业务工具的关系**：`folder_sub_objects`、`file_upload`、`file_osdownload` 等仍**必须**使用完整 docid 调用；**`namepath` 仅供用户阅读**，不得当作 `docid` 传给上述工具。
- **不属于搜索**：`file_convert_path` **不是** `file_search` 的替代，也**不是** RAG；仅作路径展示。

---

# AnyShare MCP 技能

> **触发**：用户请求匹配 description 中的关键词，或明确提及 AnyShare 相关操作时激活。
> **执行前必读**：**MCP 服务地址**已在 mcporter 中配置或已按默认/用户指定写入 → 认证检查（自动）→ 工具调用方式 → 安全约束 → 意图识别（按顺序）
>
> **📦 首次安装**：阅读同目录 **`setup.md`**，完成 mcporter 与 **MCP 服务地址**（默认见下）。

### 📌 MCP 服务地址 — 首次使用与变更（强制）

**MCP 服务地址** 即 AnyShare MCP 网关的 **HTTP 端点**，在技术配置中对应 `~/.mcporter/mcporter.json` 的 **`mcpServers.asmcp.url`**（与技能包 **`mcp.json`** 中 `url` 字段一致）。

- **企业级部署**：AnyShare **面向企业**，**各企业/租户的 MCP 服务地址通常不同**（私有化、专有云等）。技能包内默认 **`https://anyshare.aishu.cn/mcp`** 仅为**首次写入的占位**，**不能**默认等于用户所在企业的正式端点。
- **可配置**：须以**本企业 IT/运维**提供的地址为准；随时可改 **`asmcp.url`**。

#### 第一次使用本技能时（Agent 必须）

> **交互原则**：**不要**先问用户「要不要帮你检查 / 配置」——应**直接执行**下列步骤；全部做完后，**再**用简短回复告知用户**当前已配置的 MCP 服务地址**（`asmcp.url`）以及验证结果（已注册 / 连接失败及错误码）。仅在无法读写配置文件、或明确需要用户提供的私有化 URL 时，再向用户提问。

1. **自动检查**：在可读的前提下查看 `~/.mcporter/mcporter.json` 是否已有 `asmcp` 且 `url` 非空；并执行 `mcporter list` 是否含 **`asmcp`**。
2. **若尚未配置**（无文件、无 `asmcp` 或 `url` 为空）：**直接**按 **`setup.md`** 将技能包 **`mcp.json`** 中的 **`asmcp` 条目**合并写入 `~/.mcporter/mcporter.json`（默认 **`https://anyshare.aishu.cn/mcp`**），执行 `mcporter daemon restart`，再 `mcporter list` 确认 **`asmcp`** 已出现。**此首次补全默认地址属于规定动作，不属于「擅自改用户配置」**。
3. **OpenClaw 超时（与上并列，勿省略）**：按 **`setup.md`「OpenClaw 运行时环境变量」** 将技能包 **`openclaw.skill-entry.json`** 合并进 **`~/.openclaw/openclaw.json`** → **`skills.entries["anyshare-mcp"].env`**，确保 **`MCPORTER_CALL_TIMEOUT=600000`**（`chat_send` 10 分钟）。**这是运行设备上的正式配置**，不依赖用户手工在 shell 里 `export`。
4. **向用户汇报**（执行完第 1～3 步后必做）：说明**当前 `asmcp.url`**、**`openclaw.json` 是否已合并 `MCPORTER_CALL_TIMEOUT`**、daemon 是否已重启、连通性（**成功 / 503 / 401 / 超时** 等如实写出）。**无论成功与否**，须按 **`setup.md`** 提示用户：**各企业 MCP 地址通常不同**，请其确认当前地址是否为**本企业**正式端点；**连接成功也不能省略此确认**。详见 `setup.md`「企业环境」与话术示例。
5. **若连通失败**（如 **503**、连接被拒绝、DNS 失败）：**不得**立刻调用业务工具。说明失败现象，并请用户向运维索取**本企业** MCP 服务 URL 后更新 `asmcp.url`。
6. **若用户已确认**当前地址即本企业正式端点（或已按用户提供 URL 更新并重试成功），再进入认证与业务场景。

**仅在以下情况才先发问、不强行默认写入**：用户明确拒绝写入 `~/.mcporter`、无法创建/写入文件、或已声明使用与官方默认不同的网关且尚未提供 URL。

#### 修改 MCP 服务地址

当用户**明确要求**更换 **MCP 服务地址**（换环境、换网关、迁移集群或修正错误配置）时，Agent **必须**协助完成：

1. 更新 `~/.mcporter/mcporter.json` 中 **`asmcp.url`** 为用户确认的新地址（保留 `transportType`、`headers` 等字段与 **`setup.md`** 示例一致）。
2. 执行 **`mcporter daemon restart`**（若仍看不到 `asmcp` 再重启一次）。
3. 告知用户：更换 **MCP 服务地址**后，若出现未授权，需在**同一套流程**下重新完成浏览器登录与 **`auth_login`**；换账号或 Cookie 异常时可按上文删除 `~/.openclaw/skills/anyshare-mcp/asmcp-state.json` 后重登。

**禁止**在未经用户明确确认的情况下，将**已生效的非默认** `asmcp.url` **改成其它地址**（例如从用户私有化网关改回官方默认）。**首次**将**空配置**补全为技能包默认 URL **除外**。

#### 与「安装命令」的关系

`openclaw skills install` / ClawHub **不会**自动替你完成 mcporter 侧合并；**首次在对话中使用本技能时**，须按上表检查。**安装技能包**与 **本机写入 MCP 服务地址**是两件独立的事。

---

## 🔐 认证（自动执行，对用户不可见）

> 所有场景执行前必须先通过认证检查。认证失败时自动尝试恢复，无需用户主动触发。

### 前置依赖

| 依赖 | 说明 | 自动处理 |
|------|------|----------|
| agent-browser CLI | 浏览器自动化工具 | 未安装时自动 `npm install -g agent-browser` |
| Chromium/Playwright | 无头浏览器环境 | `agent-browser install` 自动补全 |

### 状态文件

```
~/.openclaw/skills/anyshare-mcp/
└── asmcp-state.json    # 浏览器 Cookie 持久化（含 AnyShare Authorization）
```

### 认证检查流程

```
第 1 步：检查 agent-browser
  which agent-browser || npm install -g agent-browser
  agent-browser install（必要时）

第 2 步：加载状态，打开浏览器，从 Cookie 获取 AnyShare Bearer token
  agent-browser state load ~/.openclaw/skills/anyshare-mcp/asmcp-state.json
  agent-browser open https://anyshare.aishu.cn/anyshare/zh-cn/
  agent-browser cookies get Authorization
  # 格式：Authorization=Bearer ory_at_xxx，提取 Bearer 后的 token 部分

第 3 步：MCP initialize（无需 Authorization 头）
  POST /mcp → { method: initialize } → 获得 Mcp-Session-Id

第 4 步：调用 auth_login 注册 token（通过 mcporter）
  mcporter call asmcp.auth_login token="<AnyShare Bearer>"
  → mcporter daemon 负责 initialize session 并注册 token
  → 此后 asmcp 的所有工具调用通过 mcporter 路由，自动携带认证状态

第 5 步：验证
  mcporter call asmcp.auth_status
  → auth_login 返回成功：检查通过，继续执行业务场景
  → auth_login 失败：触发「认证恢复」
```

### 认证恢复（自动执行）

> 仅有在第 5 步检查失败时触发。触发时告知用户：「检测到登录状态已过期，正在重新登录…」，全程无头浏览器对用户透明。

**步骤：**

```bash
# 1. 打开登录页
agent-browser open https://anyshare.aishu.cn/anyshare/zh-cn/

# 2. 获取表单 refs 并填表（snapshot -i = 无障碍树 refs，禁止用 screenshot 识图）
agent-browser snapshot -i
# refs: e10=账号框, e11=密码框, e12=登录按钮
agent-browser fill @e10 "<账号>"
agent-browser fill @e11 "<密码>"
agent-browser click @e12
agent-browser wait --load networkidle

# 3. 从 Cookie 提取 AnyShare Bearer token
agent-browser cookies get Authorization
# 格式：Authorization=Bearer ory_at_xxx，提取 Bearer 后的 token

# 4. 通过 mcporter 调用 auth_login 注册 token
mcporter call asmcp.auth_login token="<AnyShare Bearer>"
# mcporter daemon 负责与 asmcp 建立 session 并注册 token

# 5. 保存浏览器状态供后续复用
mkdir -p ~/.openclaw/skills/anyshare-mcp
agent-browser state save ~/.openclaw/skills/anyshare-mcp/asmcp-state.json

# 7. 关闭浏览器
agent-browser close
```

> 认证恢复全程无头运行（`agent-browser` 默认无 UI），不会弹出窗口。
> 账号密码仅用于 fill 操作，不记录日志。

### Token 刷新（小时级）

MCP access_token 有效期约 1 小时。失效后：
1. 从浏览器 Cookie 重新获取新的 AnyShare Bearer token
2. 在 mcporter daemon session 内再次调用 `auth_login`（`mcporter call asmcp.auth_login token="<新token>"`）
3. **不需要重启网关**，继续执行业务

### 401 自动处理

MCP 请求返回 401 或认证错误时：
1. 重新执行「认证恢复」流程（步骤 1-5）
2. 更新 token 后重试原业务场景
3. 若恢复后仍失败，向用户报告

---

## 🔌 工具调用方式

**按顺序尝试，成功即锁定，后续全部使用同一方式，禁止来回切换。**

| 顺序 | 尝试方式 | 成功判断 | 失败则 |
|:----:|----------|----------|--------|
| ① | `mcporter list asmcp` | 返回 asmcp 工具列表 | ② |
| ② | `mcporter call asmcp.tools/list` | 返回工具列表 | ③ |
| ③ | HTTP POST JSON-RPC | 返回 JSON | 报告环境异常 |

**mcporter 参数格式**：`key=value`，**不是** `--key value`
- ✅ `mcporter call asmcp.file_search keyword="文档" type="doc" start=0 rows=25`
- ❌ `mcporter call asmcp.file_search --keyword 文档`

**mcporter 单次调用超时（`chat_send` 需 10 分钟）**：

- **不属于** `~/.mcporter/mcporter.json` 或 MCP 网关配置项；由 **mcporter 客户端**对每次 `call` 设上限（默认约 **60s**）。**与「用户是否手动 export」无关**：在 **OpenClaw 上跑本技能**时，须在 **`~/.openclaw/openclaw.json`** 注入环境变量（见官方 [Skills Config](https://docs.openclaw.ai/tools/skills-config) 的 **`skills.entries.<技能名>.env`**）。
- **运行设备上的正式配置（优先）**：技能包内提供 **`openclaw.skill-entry.json`**（与 `SKILL.md` frontmatter 中 **`metadata.openclaw.openclawSkillsEntryFile`** 一致）。首次使用或排障时，Agent **必须**将该文件内容**合并**进 **`~/.openclaw/openclaw.json`** 的 **`skills.entries`**：键名为技能名 **`anyshare-mcp`**（若技能定义了 **`metadata.openclaw.skillKey`** 则以官方文档为准），**合并 `env`** 时勿覆盖用户在该条目下的其它字段；合并后 **`MCPORTER_CALL_TIMEOUT`** 为 **`600000`**（毫秒，即 10 分钟），使 **OpenClaw 代理进程**在调用 `mcporter` 时继承该变量。**具体合并步骤见 `setup.md`「OpenClaw 运行时环境变量」。**
- **沙箱会话**：若 Agent 在 **Docker 沙箱**中运行且**不继承宿主机 env**，须按官方文档在 **`agents.defaults.sandbox.docker.env`**（或对应 agent 项）中同样设置 **`MCPORTER_CALL_TIMEOUT=600000`**，或采用团队规定的沙箱镜像/编排方式。
- **兜底（单次命令）**：若某次调用仍超时，可在该次 `mcporter call` 末尾追加 **`--timeout 600000`**（覆盖当次环境变量）。
- **`mcporter list`** 另有独立默认（约 **30s**），慢启动时可设 **`MCPORTER_LIST_TIMEOUT`**（毫秒），一般与本技能业务调用无关。

**HTTP 方式示例（③ 备选）**：

```bash
# 将下方 URL 替换为你的 MCP 服务地址（与 setup.md / mcporter 中 asmcp.url 一致；默认官方见上文）
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' \
  "https://anyshare.aishu.cn/mcp"
```

> `auth_login` 之后 mcporter 路由的所有工具调用均携带认证状态，无需额外 Authorization 头。

---

## ⛔ 安全约束（强制）

### 目标确认规则（上传 / 下载适用）

**写入操作（`file_upload`）**：必须用户明确确认目标 `docid`，禁止代选。
**下载操作（`file_osdownload`）**：必须用户明确确认待下载对象 `docid`，禁止代选。

**`docid` 确认的唯一合法路径：**

```
1. 用 file_search 按用户关键词搜索
2. 搜索结果中每条必须展示：文档类型、名称、大小，以及**云盘路径**：对条目的完整 `doc_id` 调用 `file_convert_path`，展示返回的 `namepath`
3. 用户明确确认目标及其 docid（不是序号，不是 docid 字符串本身）
4. 禁止：
   - 用目录树逐层展开定位 docid
   - 用 doc_lib_list / doc_lib_owned 作为定位路径
   - 从网页/外链解析 docid（用户无法直接提供）
```

### 禁止规则（以下行为绝对禁止）

1. 在搜索结果中**代用户选定**上传或下载目标
2. 凭文件名称「看起来像」就决定写入位置或下载对象
3. 未确认目标即执行上传或下载
4. 调用 `ecosearch_slice_search`、`search_both`、`kc_search_wiki_docs`、RAG 类工具做文件搜索
5. 换账号时**不清理**浏览器状态文件直接登录

> **`file_convert_path` 例外说明**：仅用于把已定位对象的 docid 转为 `namepath` **展示给用户**，**不**构成「未确认目标即操作」，也**不**替代第 2～3 步的确认流程。

### 只读操作白名单

- `auth_status` — 查询登录状态（可选）
- `file_search` — 全局统一搜索（**唯一允许的搜索工具**）
- `file_convert_path` — gns docid → 展示用 **`namepath`**（只读，**非**搜索类工具）
- `chat_send` — Bot 问答

---

## 🎯 意图识别

### 书写类诉求：先确认是否全文写作

> **说明**：**并非**把「书写类」置于搜索、上传等其它意图之上。仅当用户话术中**已能判断存在书写类诉求**时，在**进入具体业务场景之前**，须**先**完成下面这一次确认（是否走全文写作）；其它意图仍按各场景照常识别。

**书写类**指：用户要**生成、撰写、改写、续写、润色较长内容**，或明确要**文章 / 报告 / 文案 / 推广稿 / 大纲 / 材料**，或表述为「基于这篇/这个文档写…」「参考文档写…」等**以写作为目的**的请求（**不含**仅搜索、仅列目录、仅上传下载、仅问一句事实类问题）。

**一旦识别为书写类**（无论是否已带分享链接、文档关键词或 docid），**必须先**向用户确认是否进行 **全文写作**，**不得**直接调用场景四或场景五里的写作类 `chat_send` 并跳过本确认。

**询问话术（可微调，须包含要点）：**

```
检测到您希望进行「书写/生成类」操作。是否按 AnyShare **全文写作**流程执行？

全文写作包含固定步骤：选数据源文档 → 生成大纲 → 您确认大纲 → 基于大纲生成正文 → 全文确认。

请回复：
- **是** — 走全文写作（对应场景四）
- **否** — 不需要完整流程（请说明：例如只要简短要点、普通问答、或其它）
```

- 用户回复 **是** / 确认全文写作 → 跳转 **「场景四：全文写作」**（数据源获取按该场景第 1 步；若用户已贴分享链接，解析步骤**复用场景五**第 1～2 步得到的 `docid` / `id`）。
- 用户回复 **否** 或说明只要短答、问答 → **不**强制场景四；可按用户说明使用 `chat_send` 其它能力或简短回复，**不**在本条中展开枚举。

> **与分享链接**：用户**只贴链接**并说「写一篇…」等时，仍属书写类 → **先**完成上文确认；确认全文写作后再进入场景四（链接解析见场景五，见该场景文首说明）。

### 明确触发（本技能直接执行）

- 用户明确提到：AnyShare、asmcp、文档库、文件管理、知识库、智能搜索
- 提供 anyshare.aishu.cn 链接或 docid
- 用户此前已确认使用 AnyShare

### 需要确认的模糊场景

**何时使用**：用户意图**不清晰**、无法判断是否在 AnyShare 上操作或要做哪类事时；且**当前不属于**上文「书写类」、或书写类已结束「是否全文写作」确认之后仍需澄清时。

**与「书写类」的关系**：若已识别为书写类且**尚未**完成「是否全文写作」的确认，**只**做该确认，**不要**再叠套下方模板；避免同一轮里两套问卷并行。

**向用户展示下方确认模板，不猜测：**

```
请确认：
1. 目标系统：是否在 AnyShare 操作？
   1) 是
   2) 其他系统

2. 具体操作：
   1) 搜索 / 查看文件
   2) 上传或下载文件
   3) 智能问答 / 全文写作
   4) 其他（文档库浏览、换账号等）

回复方式：第一题选 1 或 2；第二题选 1～4 中一项。示例：「1 2」表示在 AnyShare 上、上传或下载。
```

### 用户回复 → 执行路径映射

| 回复 / 条件 | 执行场景 |
|-------------|----------|
| **书写类**（见上文）且用户**确认全文写作** | **「场景四：全文写作」**（数据源见场景四第 1 步；链接解析可复用场景五） |
| **书写类**且用户**明确不要**全文写作 | 按用户说明处理，**不**强制场景四 |
| `1 + 1` | 跳转「文件/关键词搜索」 |
| `1 + 2`（上传） | 跳转「上传文件」 |
| `1 + 2`（下载） | 跳转「下载文件」 |
| `1 + 3` | 跳转「全文写作」（场景四） |
| `1 + 4` | 澄清子意图 |
| 分享链接（**且无书写类**，或已完成书写类确认） | 跳转「分享链接读取」（场景五） |
| `2` | 不走本技能 |

---

## 📂 场景一：文件/关键词搜索

**场景 ID**：`file-search`
**唯一允许的搜索工具**：`file_search`（禁止 RAG 类工具）

### 意图分流（必读）

- **按文件夹名 + 列目录**：用户表述含「某某文件夹」「这个文件夹里有哪些」「搜一下某某文件夹看看里面有什么」等 → 目标是**定位名为该称呼的文件夹并列举子文件**，不是全文搜文档内容。
- **泛关键词找资料**：用户要找「提到某概念的文档」「相关资料」→ 仍用下文 `file_search`，但**不要**与「按文件夹名列目录」混用同一套关键词拆解方式。

### 执行习惯（防漏步）

快速执行时容易把流程**心理压缩**成「搜到结果 → 直接汇报」，从而跳过**感觉像额外步骤**的环节。**在本技能中以下不是可选项**：`file_search` 出结果后，**每条展示前**须先对该条 `doc_id` 调 **`file_convert_path`** 再写进汇报；若要**列目录**，须先对**目标父文件夹**调**一次** `file_convert_path` 展示 `namepath`，**再**调 `folder_sub_objects`。**未完成上述工具调用就向用户输出列表或结论，视为流程错误**（不是「少调一次无所谓」）。

### 子场景：按文件夹名查看目录内容（优先匹配时）

1. **`keyword`**：使用用户给出的**完整文件夹名称**原样作为检索词，**禁止**擅自拆词、替换成多个零散关键词，或扩写成概念检索，除非用户明确要求换词。
2. **固定模板不可省略**：调用 `file_search` 时必须带齐 `dimension: ["basename"]` 与 `model: "phrase"`（与下方 JSON 一致）。省略会导致结果偏向**正文/多字段命中**（例如某篇长文档里零散命中多个词），与「按名找文件夹」不符。
3. **结果解读**：在 `result.files` 中**优先**查找 `size = -1`（文件夹）且 `basename` 与用户所述一致的项；**禁止**仅因排序靠前就把**普通文档**当作目标文件夹。
4. **列目录**：确认目标文件夹的 `doc_id` 后，**仅对该文件夹（父目录）的 docid 调用一次 `file_convert_path`**，向用户展示**当前目录**的云盘路径（`namepath`）；再调用 **`folder_sub_objects`**（传**完整 docid**）列举子对象。**不要**对子列表中每个子文件/子文件夹再逐个调用 `file_convert_path`。若 basename 搜索无合适命中或结果杂乱：如实说明，再建议缩小 `range`、补充文档库/路径、分页或让用户确认名称后重试。

   <!-- checkpoint: 列目录 — 未对父文件夹 docid 成功执行 file_convert_path 并得到 namepath，不得调用 folder_sub_objects，不得向用户输出子列表/汇总 -->
   **顺序硬约束**：**禁止**在父目录 **`file_convert_path` 已成功返回 `namepath` 之前**调用 **`folder_sub_objects`** 或向用户展示子对象列表（含「文件夹里有哪些文件」类汇总）。

### 步骤

<!-- checkpoint: 场景一 — 仅允许 file_search；列目录须先父目录 file_convert_path 再 folder_sub_objects；转场景二/三/四前须用户确认 docid，禁止代选 -->

**第 1 步：从用户描述中提炼 `keyword`**
必要时确认搜索范围：目录 **`range`**（`gns://…` 字符串数组，空或不传表示全目录）；标签筛选用 **`condition.tags`**（字符串数组，通常从上次搜索响应的 `condition` 中取回后收窄）。

**第 2 步：调用 `file_search`**

```json
{
  "name": "file_search",
  "arguments": {
    "keyword": "<用户关键词>",
    "type": "doc",
    "start": 0,
    "rows": 25,
    "range": [],
    "dimension": ["basename"],
    "model": "phrase"
  }
}
```

> **传参规范**：仅传 `keyword`、`start`、`rows`、`range`（上述4个动态变化），其余字段固定不变。额外参数如 `condition`、`custom`、`delimiter` 等可能导致服务端报错，一律不传。

**响应结构**：返回内容在 `result.files` 数组（不是 `data`），每项含 `basename`、`size`、`extension`、`doc_id`、`parent_path`、`highlight` 等字段。

> `rows` 单次上限 **25**；分页用 **`start`**（首页为 0），下一页将 **`start`** 设为上次响应中的 **`next`**。

<!-- checkpoint: 第 3 步 — 每条结果须先 file_convert_path(doc_id) 得到 namepath，再写入对用户的展示；禁止仅用 basename/size/doc_id/序号汇报 -->

**第 3 步：展示搜索结果（必须包含三要素 + 云盘路径）+ 判断是否满意**

每条必须展示：

- **名称**：`basename`
- **大小**：`size`（字节）
  - `size = -1` → **文件夹**，展示为「目录/未统计」
  - `size >= 0` → **文件**，展示实际字节数
- **类型辅助**：`extension`（`""` 常为文件夹；`.docx` / `.pdf` 等为文件）
- **云盘路径**：对该条目的完整 **`doc_id`** 调用 **`file_convert_path`**，展示返回的 **`namepath`**（与 `basename`、大小一并展示，便于用户辨认位置）

> **判断文件夹 vs 文件最可靠的依据是 `size`**，非 `doc_type`。`size = -1` 即为文件夹，无论 `extension` 和 `doc_type` 如何展示。

**本步卡点**：在**本条**的 **`file_convert_path` 调用完成并拿到 `namepath` 之前**，**不得**把该条作为「已展示结果」写入对用户的回复（禁止用「第 N 条」等替代路径）。

禁止只展示 `docid` 或序号让用户盲选；**展示 `namepath` 时仍须保留名称与大小**（路径为补充信息）。

**结果不满意时的处理（hits >= 25 时强制执行）：**

> 找到 **X** 条结果（已展示前 25 条），是否需要：
> 1. **查看更多** — 调整 `start` 继续分页
> 2. **更换关键词** — 重新提炼 `keyword` 搜索
> 3. **缩小范围** — 增加 `range` 限定目录
>
> 回复序号或描述需求，未确认前不擅自翻页或换词搜索。

**第 4 步（需要操作时）：用户确认 docid**

<!-- checkpoint: 上传/下载/写作 — 须用户显式点选或文字确认目标 docid；禁止凭「看起来像」代选 -->

若后续需要上传/下载，在结果中由用户确认目标 `docid`。

**第 5 步：结果不对 → 调整重试**
重新确认 `keyword`、`start`/`rows`、`range`、`condition`（含 tags 等），**仅用 `file_search` 重试**。禁止换成其它搜索工具。

### 401 处理
→ 自动执行「认证恢复」，完成后重新执行本场景。

---

## 📂 场景二：上传文件

**场景 ID**：`upload-file`

### 步骤

<!-- checkpoint: 上传 — 须先「file_search + 每条 file_convert_path + 用户按模板确认是」再 file_upload；禁止未确认即上传 -->

**第 1 步（强制确认）：搜索并展示上传目标**
1. 用 `file_search` 按用户关键词搜索目标文件夹
2. 每条结果展示「名称+大小+doc_id」，并对 `doc_id` 调用 **`file_convert_path`** 展示 **`namepath`**（云盘路径）
3. 用户选定目标目录后，以该行已展示的 **`namepath`** 为准向用户确认（**无需**对同一 docid 重复调用；若列表未含路径再补调一次）：

> 即将上传到：
> - 文件名：`<本地文件名>`
> - 云盘路径（`namepath`）：`<file_convert_path 返回>`
> - docid（完整 gns）：`gns://...`
>
> 确认继续？回复"是"确认，或提供其他目标路径。
> **用户未明确回复"是"之前，禁止调用 `file_upload`。**

**第 2 步：确认 `file_path`**
直接使用本地真实路径即可，不需要先复制到临时目录或做路径转换，只要 MCP 服务端能读到本机路径即可。

**第 3 步：调用 `file_upload`**

<!-- checkpoint: 仅当第1步用户已明确回复确认且 docid、file_path 已锁定；禁止跳过第1步模板确认 -->

```json
{
  "name": "file_upload",
  "arguments": {
    "docid": "<file_search 结果中用户确认的 docid>",
    "file_path": "<MCP 服务端可读的本地路径>"
  }
}
```

**第 4 步：检查返回，确认上传成功。**

向用户汇报「上传成功」时：

1. **docid 必须展示为 `gns://` 开头的完整路径**（与「AnyShare 基础知识」中 docid 定义一致）。**禁止**只展示 `id`（docid 最后一段）或单独一段十六进制串并标成 docid。
2. 若接口返回里仅有新对象的 **`id`**（最后一段）：用**本次 `file_upload` 传入的目标目录 docid**（完整 `gns://...`）作为父路径，按层级拼出**新文件的完整 docid**（父目录 docid + `/` + 新 `id`）再展示；若返回中已含完整 `doc_id` / `docid` / `gns` 字段，**优先**直接使用该完整值。
3. 对**新文件的完整 docid** 调用 **`file_convert_path`**，向用户展示 **`namepath`**（云盘路径），与完整 docid **一并**展示（路径为主读信息，docid 为精确标识）。

### 401 处理
→ 自动执行「认证恢复」，完成后重新执行本场景。

---

## 📂 场景三（下载）：下载文件

**场景 ID**：`download-file`

### 步骤

<!-- checkpoint: 下载 — 须先「file_search + 每条 file_convert_path + 用户按模板确认是」再 file_osdownload；禁止未确认即下载 -->

**第 1 步（强制确认）：搜索并展示下载目标**
1. 用 `file_search` 按用户关键词搜索目标文件
2. 每条结果展示「名称+大小+doc_id」，并对 `doc_id` 调用 **`file_convert_path`** 展示 **`namepath`**
3. 用户明确要下载的文件后，用该条已展示的 **`namepath`** 填入确认模板（**无需**对同一 docid 重复调用；若列表未含路径再补调一次）：

> 即将下载：
> - 文件名：`<basename>`
> - 文件大小：`<size 字节>`
> - 云盘路径（`namepath`）：`<步骤 2 已展示或补调得到>`
> - docid（完整 gns）：`gns://...`
>
> 确认继续？回复"是"确认，或提供其他文件。
> **用户未明确回复"是"之前，禁止调用 `file_osdownload`。**

**第 2 步：调用 `file_osdownload`**

<!-- checkpoint: 仅当第1步模板已获用户「是」；禁止跳过确认 -->

```json
{
  "name": "file_osdownload",
  "arguments": {
    "docid": "<file_search 结果中用户确认的 docid>"
  }
}
```

**第 3 步：返回下载链接，请用户确认保存位置。**

若需再次说明文件所在位置，可对已确认的完整 docid 调用 **`file_convert_path`** 展示 **`namepath`**（与下载链接一并给出即可）。

### 401 处理
→ 自动执行「认证恢复」，完成后重新执行本场景。

---

## 📂 场景四：全文写作

**场景 ID**：`full-text-writing`

> **入口**：除确认模板 `1 + 3` 外，凡在「意图识别 → 书写类诉求」中**确认全文写作**的用户，**必须**进入本场景。

> **【强制】流程约束**：AnyShare 全文写作是固定流程：选数据源 → 生成大纲 → 大纲确认 → 基于大纲写作 → 全文确认。**禁止跳步、禁止合并步骤、禁止省略任一步骤**。
>
> - ❌ 禁止：跳过"生成大纲"直接写全文
> - ❌ 禁止：大纲和正文一步生成
> - ❌ 禁止：省略"选数据源"直接生成
>
> **用户反馈处理**：
> - 大纲不满意 → 把修改意见加在 `query` 里，重新调用 `__全文写作__2`（保持 `conversation_id`）
> - 正文不满意 → 把修改意见加在 `query` 里，重新调用 `__大纲写作__1`

### ⚠️ source_ranges 强制约束

> AnyShare 自动提取文档全文，大模型不需要读取文件内容。
>
> `source_ranges[].id` **必须传 id**（docid 的最后一段）。
>
> - ✅ 正确：`"id": "<文档的 id>"`
> - ❌ 错误：传完整 docid（如 `gns://...`）、传文件夹 ID
>
> `type` 固定为 `"doc"`。

### 步骤

**第 1 步：获取文档 id**

用户提供分享链接 → 解析出 docid（见场景五）。
用户提供文档关键词 → 用 `file_search` 搜索确认文档 id。

**第 2 步：生成大纲（`__全文写作__2`）**

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "<用户写作任务描述>",
    "selection": "",
    "times": 1,
    "skill_name": "__全文写作__2",
    "web_search_mode": "off",
    "datasource": [],
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "template_id": 1,
    "interrupted_parent_qa_id": ""
  }
}
```

返回大纲 → 展示给用户 → 等待确认。

<!-- checkpoint: 大纲门闩 — 用户未在对话中明确确认大纲（或按上文「用户反馈处理」修改后再确认）前，禁止调用第3步 __大纲写作__1；禁止凭「默认继续」臆断 -->

> `version`、`temporary_area_id` **不要传**（无法从响应可靠获取）。

**第 3 步：生成正文（`__大纲写作__1`）**

<!-- checkpoint: 仅当大纲门闩已满足且 conversation_id 来自第2步响应；禁止跳过大纲确认 -->

大纲确认后，调用：

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "基于大纲生成文档",
    "selection": "<已确认的大纲全文>",
    "conversation_id": "<步骤2返回的 conversation_id>",
    "times": 1,
    "skill_name": "__大纲写作__1",
    "web_search_mode": "off",
    "datasource": [],
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "interrupted_parent_qa_id": ""
  }
}
```

返回全文 → 展示给用户确认。

**第 4 步：导出**

<!-- checkpoint: 导出上传若走上传 — 须完整复用场景二（确认门闩），禁止跳过 file_search/用户确认 -->

- **保存本地**：用户提供路径
- **上传到 AnyShare**：复用「场景二：上传文件」

### 401 处理
→ 自动执行「认证恢复」，完成后回到步骤 1 重做。

---

## 📂 场景五：分享链接读取

**场景 ID**：`share-link-read`
**触发**：用户提供 AnyShare 分享链接（如 `https://anyshare.aishu.cn/link/AR...`）

> **书写类 + 全文写作**：若用户属「意图识别 → 书写类诉求」且**已确认全文写作**，应以 **场景四** 为主流程；本场景负责**打开链接、登录、解码 `item_id` 得到 docid/id**，供场景四「第 1 步：获取文档 id」使用。**禁止**仅用下文「第 3 步B」的简化 `chat_send` 代替场景四的完整大纲 → 正文流程。  
> **书写类未确认或选择不做全文写作**：再按用户后续说明决定是否使用「第 3 步B」等简化调用。

> **URL 解析规则**：见「核心概念 → sharedlink 解析方法」，不重复写。

### 步骤

<!-- checkpoint: 场景五 — item_id 仅来自 get url 解析；禁止 screenshot/图像认参；全文写作须回场景四，禁止用 3 步B 顶替大纲流程 -->

**第 1 步：用无头浏览器（agent-browser）跟随重定向并读取落地 URL**

> **必须建立正确心智**：使用 **`agent-browser` 无头 Chromium**（默认无 UI，见上文「认证恢复」）。**禁止**使用 **`screenshot`**（像素截图）或**任何基于图像/视觉**的手段去「认页面、猜参数」——**对分享落地与 `item_id` 的解析以 URL 字符串为唯一可靠来源**，图像**必然不准**。本步**仅**通过 **`get url` / `eval` 读 `location.href`** 取得地址栏等价信息并解析 query（见「核心概念 → sharedlink 解析方法」）。若需判断是否仍停在登录页等，用 **`get url`、`get title`、`eval`** 等**文本/结构化**信息，**不要**截图。

1. `open` 分享链接，等待重定向与网络空闲（`sleep` 或 `agent-browser wait --load networkidle`，以实际 CLI 为准）。
2. **读取当前页 URL**：重定向稳定后执行 **`agent-browser get url`**，得到含 **`item_id`、`item_type`** 等 query 的完整地址（也可用 **`agent-browser eval`** 读取 `location.href`，与 `get url` 等价即可）。
3. **无有效 URL 时不得臆造 `item_id`**；**不得**用截图或看图识字代替 URL 解析。

```bash
agent-browser open "https://anyshare.aishu.cn/link/<分享ID>"
agent-browser wait --load networkidle
agent-browser get url
# 禁止 screenshot；禁止凭图像解析 item_id
```

**第 1.5 步：遇到登录页 → 填入账号密码登录**

1. **向用户在对话中索取账号与密码**（由用户当场输入；**禁止**从本地文件、固定路径或仓库读取账号密码）。
2. 使用 **`agent-browser snapshot -i`** 获取输入框 **refs**（输出为**无障碍语义树**，**不是**像素截图；**禁止**用 **`screenshot`** 看图填表）。`fill`（或 `type`）填入账号、密码，点击登录，`wait` 至页面加载完成（与上文「认证恢复」填表方式一致）。
3. 凭据仅用于本次浏览器填表，**不得**写入日志、技能仓库或明文配置。
4. 登录成功若再次发生跳转：待加载完成后再次 **`agent-browser wait --load networkidle`**，并 **`agent-browser get url`**，以**登录后落地页**的 URL 解析 `item_id`（勿用分享短链页或登录前的 URL）。

重定向 URL 示例（已解码）：
- 文件夹：`item_id=gns://E6D15886.../2DDD46B195F24BCEB238DB59151CD15E` + `item_type=folder`
- 文件：`item_id=gns://E6D15886.../ABCD1234...` + `item_type=file`（或具体文件类型）

**第 2 步：解码 gns 路径，区分类型**

<!-- checkpoint: docid/id 须由上步 URL 解析得到；禁止无 URL 凭快照臆造 item_id -->

> 详细解析规则见「核心概念 → sharedlink 解析方法」。

根据 `item_type` 判断：

| `item_type` | 处理方式 |
|-------------|---------|
| `folder` | 用 `folder_sub_objects` 获取文件夹内子文件 |
| 其他（file/doc 等） | id 传给 `chat_send` 的 `source_ranges` |

**第 3 步A：文件夹 → `folder_sub_objects`**

<!-- checkpoint: 分享链接 folder — 须先 file_convert_path(该文件夹完整 docid) 得 namepath，再 folder_sub_objects；与场景一列目录一致；禁止颠倒或跳过 -->

对**该文件夹**的完整 docid **调用一次 `file_convert_path`**，向用户展示**当前目录**的云盘路径（`namepath`）；**不要**对即将列出的每个子项再逐个调用 `file_convert_path`。**禁止**在拿到上述 **`namepath` 之前**调用下面的 **`folder_sub_objects`** 或向用户输出子列表。

```json
{
  "name": "folder_sub_objects",
  "arguments": {
    "id": "<docid（完整路径）>",
    "limit": 1000
  }
}
```

返回子文件列表（文件名、doc_id、类型等）。如有子文件夹，递归获取所有文件。

**第 3 步B：文件 → `chat_send`（仅非「全文写作」场景四流程时）**

<!-- checkpoint: 若用户已确认场景四全文写作 — 禁止用本步代替场景四（大纲→确认→正文）；仅非全文写作简化问答可用 -->

当用户**未**走场景四全文写作（例如仅问答、或已明确不要完整大纲/正文流程）时，可用 id 构建 `source_ranges` 做简化调用（AnyShare 自动提取全文）：

```json
{
  "name": "chat_send",
  "arguments": {
    "query": "<用户的写作或问答任务>",
    "skill_name": "__全文写作__2",
    "source_ranges": [{ "id": "<文档的 id>", "type": "doc" }],
    "web_search_mode": "off"
  }
}
```

> `id` 传 id（docid 的最后一段），`type` 固定为 `"doc"`。  
> **若用户已确认全文写作**：**改走场景四**，使用场景四中的 `chat_send` 参数（`__全文写作__2` → 大纲确认 → `__大纲写作__1`），**不要**用本段单次调用替代。

**第 4 步：返回结果**
- 文件夹：已展示**该文件夹**的 `namepath`；子列表展示文件名等信息即可（**无需**为每个子文件再调 `file_convert_path`），供用户选择要操作的文档
- 文件：返回全文写作/问答结果

> **与 `file_share_path`**：若用户需要**分享链接 + 路径 + 文件名**的一站式展示，可改用 **`file_share_path`**（组合路径转换与实名链接）；仅要云盘路径时用 **`file_convert_path`** 即可。

### 401 处理
→ 自动执行「认证恢复」，完成后回到步骤 1 重做。

---

## ⚠️ 核心注意（务必遵守）

1. **搜索文件只用 `file_search`**，禁止 RAG 类工具、目录树展开；**`file_convert_path` 仅用于展示路径，不是搜索**
2. **上传/下载的 `docid` 必须经 `file_search` 结果 + 用户确认**，禁止代选
3. **认证为自动前置流程**，通过 `auth_login` 动态注册，不需要配置文件写死 Token
4. **认证后通过 mcporter 路由的所有工具调用均携带认证状态**，无需 Authorization 头
5. **`skill_name` 枚举值以 `mcporter list asmcp` 返回的 schema 为准**，不做假设
6. **Token 刷新不需要重启网关**，在 mcporter session 内重新调用 `auth_login` 即可
7. **换账号前先删除 `~/.openclaw/skills/anyshare-mcp/asmcp-state.json`**
8. **首次使用须自动完成 MCP 服务地址**（`asmcp.url`）**检查与默认写入**（见上文「第一次使用」）；完成后**向用户报告**当前地址与连通性；用户明确要求时**须**协助**修改 MCP 服务地址**（更新 `~/.mcporter/mcporter.json`、重启 daemon，见上文「**MCP 服务地址**」）
9. **`chat_send` 的 10 分钟等待**：运行 OpenClaw 的设备上须已合并 **`openclaw.skill-entry.json`** 至 **`~/.openclaw/openclaw.json`** → **`skills.entries["anyshare-mcp"].env`**（见 **`setup.md`**）；兜底时在单次 `mcporter call` 上加 **`--timeout 600000`**
10. **禁止把「搜到结果」压缩成「直接汇报」**：`file_search` / 列目录流程中，**须先 `file_convert_path` 再展示或再 `folder_sub_objects`**（见场景一「执行习惯（防漏步）」与文中 **`<!-- checkpoint -->`** 处）；跳过则视为未按技能执行
11. **各场景硬卡点**：上传/下载/全文写作/分享链接等 **以各节 `<!-- checkpoint -->` 为准**；**场景四**须遵守「大纲门闩」再调用 **`__大纲写作__1`**

---

## 📖 补充资料

- `setup.md` — 首次安装、MCP 服务地址写入与变更（`~/.mcporter/mcporter.json`）
- `references/troubleshooting.md` — 常见错误与排查（与上文流程一致）
- `LICENSE` — **MIT License**（SPDX: `MIT`）
- `SECURITY.md` — 安全使用与敏感信息

---
