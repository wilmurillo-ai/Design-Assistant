# Prisma SASE Claw

> Claude Code skill for Palo Alto Networks Prisma SASE API — Prisma Access, SD-WAN & Access Browser.
>
> 用于 Palo Alto Networks Prisma SASE API 的 Claude Code 技能 — 支持 Prisma Access、SD-WAN 和 Access Browser。

[![ClawHub](https://img.shields.io/badge/ClawHub-prisma--sase--claw-blue)](https://clawhub.ai/skill/prisma-sase-claw)
[![License: MIT-0](https://img.shields.io/badge/License-MIT--0-green.svg)](LICENSE)

---

## What is this? / 这是什么？

**Prisma SASE Claw** is a [Claude Code](https://claude.com/claude-code) skill that lets you manage your Palo Alto Networks Prisma SASE platform through natural language. It generates working `curl` commands and Python scripts to interact with the SASE API.

**Prisma SASE Claw** 是一个 [Claude Code](https://claude.com/claude-code) 技能，让你通过自然语言管理 Palo Alto Networks Prisma SASE 平台。它能生成可用的 `curl` 命令和 Python 脚本来调用 SASE API。

### Supported Products / 支持的产品

| Product / 产品 | Description / 描述 |
|---|---|
| **Prisma Access** | Security policies, remote networks, GlobalProtect, service connections, decryption rules / 安全策略、远程网络、GlobalProtect、服务连接、解密规则 |
| **Prisma SD-WAN** | Site configs, routing, path policies, NAT, QoS, performance monitoring / 站点配置、路由、路径策略、NAT、QoS、性能监控 |
| **Prisma Access Browser** | Browser management, policies, deployments / 浏览器管理、策略、部署 |

---

## Install / 安装

```bash
npx clawhub@latest install prisma-sase-claw
```

Or clone from GitHub / 或从 GitHub 克隆：

```bash
git clone https://github.com/leesandao/prisma-sase-claw.git ~/.claude/skills/prisma-sase-claw
```

---

## Setup / 配置

### 1. Create a Service Account / 创建服务账户

Create a service account in the [Prisma SASE Console](https://app.prismaaccess.com) and note down:

在 [Prisma SASE 控制台](https://app.prismaaccess.com) 创建服务账户，记录以下信息：

- `Client ID` — e.g. `your_account@12345.iam.panserviceaccount.com`
- `Client Secret` — shown only once / 仅显示一次
- `TSG ID` — Tenant Service Group ID / 租户服务组 ID

### 2. Store Credentials / 存储凭据

Credentials are loaded from local `.env` files — **never declared in skill metadata or passed as arguments**.

凭据从本地 `.env` 文件加载 — **不会在技能元数据中声明，也无需作为参数传递**。

```bash
# Create global config directory / 创建全局配置目录
mkdir -p ~/.sase

# Copy the template / 复制模板
cp scripts/.env.example ~/.sase/.env

# Edit with your credentials / 填入你的凭据
vi ~/.sase/.env

# Lock down permissions / 锁定文件权限（仅所有者可读写）
chmod 600 ~/.sase/.env
```

`.env` file format / 文件格式：

```env
PRISMA_CLIENT_ID=your_service_account@your_tsg.iam.panserviceaccount.com
PRISMA_CLIENT_SECRET=your_client_secret_here
PRISMA_TSG_ID=your_tsg_id_here
```

The auth helper searches credentials in this order / 凭据查找顺序：

1. **Environment variables** / 环境变量 — already exported in shell
2. **`.env` in current directory** / 当前目录 `.env` — project-level config / 项目级配置
3. **`~/.sase/.env`** — global config / 全局配置

---

## Usage / 使用

Once installed and configured, just talk to Claude Code in natural language:

安装配置完成后，直接用自然语言与 Claude Code 对话：

```
> 查看所有安全策略
> List all security rules in Mobile Users folder
> 创建一条新的安全规则，阻止访问 qq.com
> Show me the SD-WAN site configuration
> 查询过去7天的安全告警
> Push the candidate config to production
```

### Python Usage / Python 使用

```python
from sase_auth import SASEAuth

# Auto-discovers credentials from .env files
# 自动从 .env 文件发现凭据
auth = SASEAuth()

# Get a token / 获取令牌
token = auth.get_token()

# Make API calls / 调用 API
rules = auth.api_get('/sse/config/v1/security-rules', params={'folder': 'All'})

# Or specify a custom .env path / 或指定自定义 .env 路径
auth = SASEAuth(env_file="/path/to/custom/.env")
```

---

## Project Structure / 项目结构

```
prisma-sase-claw/
├── SKILL.md                          # Skill definition / 技能定义
├── README.md                         # This file / 本文件
├── scripts/
│   ├── sase_auth.py                  # Auth helper with .env auto-discovery / 认证辅助（自动发现 .env）
│   └── .env.example                  # Credential template / 凭据模板
└── references/
    ├── prisma-access.md              # Prisma Access API reference / API 参考
    ├── prisma-sdwan.md               # SD-WAN API reference / API 参考
    ├── prisma-browser.md             # Access Browser API reference / API 参考
    ├── authentication.md             # Auth & credential guide / 认证与凭据指南
    └── monitoring.md                 # Aggregate monitoring reference / 聚合监控参考
```

---

## Security / 安全

- Credentials are stored **locally** in `.env` files with `chmod 600` permissions
- No secrets are declared in skill metadata or transmitted to ClawHub
- All API calls go directly to official Palo Alto Networks endpoints (`*.paloaltonetworks.com`)
- OAuth2 tokens are short-lived (15 minutes) with automatic refresh

---

- 凭据**仅存储在本地** `.env` 文件中，权限为 `chmod 600`
- 技能元数据中不包含任何密钥，也不会传输到 ClawHub
- 所有 API 调用直接发送到 Palo Alto Networks 官方端点（`*.paloaltonetworks.com`）
- OAuth2 令牌有效期短（15 分钟），支持自动刷新

---

## Changelog / 更新日志

### v1.1.6 — Bandwidth Allocation API / 带宽分配 API

- Added full bandwidth allocation management guide: list, allocate (POST), and delete (DELETE) / 新增完整的带宽分配管理指南：列表、分配 (POST) 和删除 (DELETE)
- **Critical discovery:** The `DELETE /bandwidth-allocations` endpoint uses a **unique parameter pattern** — requires `name` + `spn_name_list` as query params, does NOT accept `folder` param or request body / **关键发现：** `DELETE /bandwidth-allocations` 端点使用**独特的参数模式** — 需要 `name` + `spn_name_list` 作为查询参数，不接受 `folder` 参数或请求体
- Documented correct DELETE syntax: `DELETE /bandwidth-allocations?name=hong-kong&spn_name_list=hong-kong-myrtle` / 记录正确的 DELETE 语法
- Documented POST syntax for new allocations: location `name` must match the `value` field from `GET /locations` / 记录新分配的 POST 语法：location `name` 必须匹配 `GET /locations` 的 `value` 字段
- Added note that bandwidth changes require config push to take effect / 备注带宽变更需要推送配置才能生效

### v1.1.5 — Service Status Page Integration / 服务状态页面集成

- Added Prisma SASE Service Status Page monitoring (`https://sase.status.paloaltonetworks.com`) / 新增 Prisma SASE 服务状态页面监控
- **Auto-check on first daily interaction:** Check status page for active incidents or scheduled maintenance before making API calls / **每日首次交互自动检查：** 调用 API 前先检查状态页面是否有活跃事件或计划维护
- **Auto-check after 2+ consecutive failures:** If Child Jobs fail 2+ times in a row (especially 502 errors), check status page before retrying / **连续 2 次以上失败自动检查：** 如果 Child Job 连续失败 2 次以上（特别是 502 错误），重试前先检查状态页面
- Added programmatic status check examples: current status, active incidents, upcoming maintenance / 新增编程式状态检查示例：当前状态、活跃事件、计划维护
- Added 502 Internal Server Error to common push failure reasons / 将 502 内部服务器错误加入常见推送失败原因

### v1.1.4 — Remote Network Site Creation Guide / Remote Network 站点创建指南

- Added complete Remote Network site creation procedure: IKE Gateway → IPSec Tunnel → Remote Network (must be created in this order) / 新增完整的 Remote Network 站点创建流程：IKE Gateway → IPSec Tunnel → Remote Network（必须按此顺序创建）
- **Critical fix:** `region` value must come from `GET /locations` API response `region` field (e.g. `asia-east2` for Hong Kong), NOT the `value` field. Using wrong codes causes sites in wrong locations / **关键修复**：`region` 值必须来自 `GET /locations` API 响应的 `region` 字段（如 Hong Kong 对应 `asia-east2`），而非 `value` 字段。使用错误代码会导致站点创建在错误位置
- Added prerequisite checks: query `/locations`, `/bandwidth-allocations`, `/ike-crypto-profiles`, `/ipsec-crypto-profiles` before creating sites — never guess parameter values / 新增前置检查：创建站点前必须查询可用的 locations、bandwidth、IKE/IPSec profiles — 不要猜测参数值
- Added common region code reference table / 新增常用 region 代码对照表
- Documented Service IP allocation behavior: `details` field is populated by cloud after push, new locations may take 10-30 minutes / 记录 Service IP 分配行为：`details` 字段在推送后由云端填充，新 location 可能需要 10-30 分钟
- Added deletion procedure (reverse order: RN → Tunnel → IKE GW) / 新增删除流程（逆序：RN → Tunnel → IKE GW）

### v1.1.3 — Config Push Job Monitoring / 配置推送任务监控

- Added Father/Child Job monitoring pattern for config push operations. The push API returns a Father Job (CommitAndPush) that only commits candidate config — the actual cloud push is performed by a Child Job (CommitAll) linked via `parent_id`. Only the Child Job's status reflects the true push result / 新增配置推送的 Father/Child Job 监控模式。推送 API 返回的 Father Job 仅提交候选配置，实际云端推送由通过 `parent_id` 关联的 Child Job 执行。只有 Child Job 的状态才能反映真实的推送结果
- Added job status reference table (`ACT/PEND`, `FIN/OK`, `PUSHFAIL/FAIL`, `PUSHSUC/OK`) / 新增 Job 状态对照表
- Added per-region push result parsing guide (Child Job `details` field contains JSON with `job_details` array) / 新增按区域解析推送结果指南（Child Job 的 `details` 字段包含带 `job_details` 数组的 JSON）
- Documented common push failure reasons and remediation steps / 记录常见推送失败原因及修复方法
- Updated `references/prisma-access.md` Configuration Push section with full monitoring procedure / 更新 `references/prisma-access.md` 配置推送章节，包含完整监控流程

### v1.1.2 — TSG Hierarchy Fix / 租户层级查询修复

- Fixed: `/children` and `/ancestors` sub-endpoints return 404 for most TSG types — documented the correct approach using `GET /tenant_service_groups` with `parent_id` filtering / 修复：`/children` 和 `/ancestors` 子端点对大多数 TSG 类型返回 404 — 改用 `GET /tenant_service_groups` 按 `parent_id` 过滤
- Added TSG hierarchy querying guide to SKILL.md and authentication.md / 在 SKILL.md 和 authentication.md 中新增 TSG 层级查询指南
- Added troubleshooting entry for 404 on `/children` endpoint / 新增 `/children` 端点 404 的排错条目
- Best practice: all API calls now use `source ~/.sase/.env` to load credentials instead of passing plaintext secrets in command-line arguments / 最佳实践：所有 API 调用现在通过 `source ~/.sase/.env` 加载凭据，避免在命令行中暴露明文密钥

### v1.1.1 — Secure Credential Management / 安全凭据管理

- Removed sensitive env vars from skill metadata / 从技能元数据中移除敏感环境变量
- Added `.env` file auto-discovery mechanism / 新增 `.env` 文件自动发现机制
- Added `scripts/.env.example` template / 新增凭据模板
- Updated auth docs / 更新认证文档

### v1.0.0 — Initial Release / 初始发布

- Prisma Access, SD-WAN, Access Browser API support / 支持 Prisma Access、SD-WAN、Access Browser API
- OAuth2 authentication helper / OAuth2 认证辅助
- Full endpoint reference documentation / 完整的端点参考文档

---

## License / 许可证

[MIT-0](LICENSE) — Free to use, modify, and redistribute. No attribution required.

自由使用、修改和再分发，无需署名。
