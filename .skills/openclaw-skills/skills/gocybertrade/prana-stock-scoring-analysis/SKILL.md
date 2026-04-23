---
name: A股财务分析助手
description: 通过调用Prana平台上的远程 agent 执行 A股财务分析助手，并将结果返回给调用方
required_env:
  - PRANA_SKILL_API_FLAG
network_requests:
  - method: POST
    url: https://claw-uat.ebonex.io/api/v2/api-keys
  - method: POST
    url: https://claw-uat.ebonex.io/api/claw/agent-run
  - method: POST
    url: https://claw-uat.ebonex.io/api/claw/agent-result
  - method: GET
    url: https://claw-uat.ebonex.io/api/claw/skill-purchase-history-url
---


当客户提出需要对指定A股股票的股财务分析时，可以使用本技能。
例如：帮我分析茅台股票的盈利能力、帮我分析中国平安的营运能力

# 一、获取标识：从 Prana 平台获取 api_key（需先与用户郑重确认，且以用户触发运行为准配置环境变量）

1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若环境变量已存在，直接进入运行流程；

- 若任一环境变量不存在，执行第2步获取prana平台请求标识。

2. 调用接口 `GET /api/v2/api-keys`，获取 `api_key` 的值（本标识仅用于 Prana 平台相关接口，不作用于任何其他数据）。

接口调用命令：

```bash
curl -sS "https://claw-uat.ebonex.io/api/v2/api-keys"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "api_key": "af:XXXXX"
  }
}
```

3. 将接口返回的 `api_key` 配置到 OpenClaw 环境变量：

- 接口返回的api_key → 环境变量PRANA_SKILL_API_FLAG；

**补充说明（OpenClaw环境变量配置规范）：**

需通过OpenClaw专属配置命令设置环境变量，确保配置全局生效：

```bash
openclaw config set env.PRANA_SKILL_API_FLAG "af_..."
```
# 二、运行流程：调用 Prana 平台接口获取数据

**OpenClaw 执行者须知（必须遵守，否则视为未完整执行本技能）**  
本技能依赖「会话目录 + 文本文件」保存 `thread_id`；**客户端脚本不会自动创建或写入** `workspace/<session_id>/`。必须由执行本技能的 OpenClaw/宿主在跑脚本**之前**读文件、在拿到接口结果**之后**写文件。

1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止整个流程；

- 若环境变量检测成功，进入第2步。

2. **必须先解析会话 ID，再跑脚本**  
   - **必须**从 OpenClaw 当前会话上下文取得 `<session_id>`（与 `workspace/<session_id>/` 目录一一对应；若平台以其他字段命名，仍以实际会话唯一标识为准）。**不得**在未确定 `<session_id>` 的情况下假定路径。  
   - **必须**保证目录 `workspace/<session_id>/` 存在：若不存在则**先创建**该目录，再执行后续读写。  
   - 脚本参数 `question`：用户要执行的需求任务（例如：帮我分析茅台股票的盈利能力、帮我分析中国平安的营运能力）。不要包含账号密码、付款信息、个人隐私等敏感内容。  
   - 脚本参数 `thread_id`：**必须**先尝试读取 `workspace/<session_id>/prana-stock-scoring-analysis.txt` 的**整文件内容**（去首尾空白）作为 `-t` 的值；仅当文件不存在、为空或读取失败时，`-t` 才传空（或不传 `-t`）。  
   - 根据本机已安装的客户端选择运行方式，默认优先使用 `Node.js`；若未安装 Node.js 或无法使用时再选用 `Python 3`。  
   - **执行脚本后必须立即执行步骤 3**；仅执行脚本而不维护 `prana-stock-scoring-analysis.txt` **不算**完成本技能。

- **Node.js 18+（默认）**
  ```bash
  NODE_OPTIONS=--experimental-default-type=module node scripts/prana_skill_client.js -q "帮我分析茅台股票的盈利能力" [-t thread_id]
  ```

- **Python 3（备选）**
  `python3 scripts/prana_skill_client.py -q "帮我分析茅台股票的盈利能力" [-t thread_id]`

3. **必须写回 `thread_id`（与步骤 2 同一会话）**  
   - 使用与步骤 2 **相同**的 `<session_id>`。  
   - 从步骤 2 的脚本/接口响应中解析出 `thread_id`；若成功取得非空 `thread_id`，**必须**将其**仅写入**（覆盖写入即可）`workspace/<session_id>/prana-stock-scoring-analysis.txt`，文件内容**仅为**该字符串，不要附加说明或 JSON。  
   - 若本次响应中无有效 `thread_id`，则**不要**删除已有文件（保留上次值便于续聊），除非业务明确要求新开会话（此时应清空或删除该文件后再传空 `-t`）。
  

# 三、获取历史请求地址

用于获取可在浏览器中打开的 **历史请求（技能获取记录）** 页面链接。
1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止整个流程；

- 若环境变量检测成功，进入第2步（调用接口）。

2. 调用接口 `GET /api/claw/skill-purchase-history-url`。

- **成功时**：从响应体 `data.url` 取出链接。不要把返回的完整链接写进日志以及存储；把完整链接直接发给用户即可。

接口调用命令（成功时返回执行结果 JSON；请求头中的x-api-key从环境变量PRANA_SKILL_API_FLAG获取）：

```bash
curl -sS -H "x-api-key:af..." "https://claw-uat.ebonex.io/api/claw/skill-purchase-history-url"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "url": "https://claw-uat.ebonex.io/skill-purchase-history-url?pay_token=xxxxxxx"
  }
}
```

# 四、安全与审计说明

1. 本技能的远程执行步骤只调用 `https://claw-uat.ebonex.io` 的 claw agent 接口（例如 `POST /api/claw/agent-run`）。
2. 为什么必须调用远程 `https://claw-uat.ebonex.io`？只有https://claw-uat.ebonex.io中才提供了完成本技能分析所需要的相关数据源和agent。
3. 为什么必须写入“全局持久化环境变量”？持久化变量的目的之一是减少重复握手/调用次数，从而尽可能降低对平台每日资源消耗的影响（具体策略以平台实际计费/配额为准）。
4. prana服务公网首页地址:https://claw-uat.ebonex.io/
5. 关于 `/api/v2/api-keys` 的授权语义：不同环境/平台策略可能导致该接口在当前调用方式下无需额外认证。接口返回的令牌类型（共享令牌或用户专属令牌）及具体原因，请以平台文档/接口说明为准，以满足审计要求。
 
