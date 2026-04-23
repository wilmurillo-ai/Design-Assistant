---
name: readdy
description: Interact with Readdy.ai to create and modify websites. Use when the user wants to generate a new website, modify an existing Readdy project, or manage Readdy.ai projects from the command line.
---

# Readdy Website Builder Skill

本 skill 提供通过 Readdy.ai 平台创建和管理网站的完整 CLI 能力。支持一键生成网站、AI 驱动的网站修改、项目预览与发布管理。执行时必须严格遵循以下规则。

## 脚本位置

`skills/readdy/readdy.mjs`

## 前置条件

认证 token 通过配置文件提供：

```bash
node skills/readdy/readdy.mjs config --token <your-token>
```

配置文件位置：`~/.readdy/config.json`

未配置 token 时脚本会报错退出。

## 命令参考

### 1. 项目列表

```bash
node readdy.mjs list [--page <n>] [--pageSize <n>]
```

### 2. 获取项目信息

```bash
node readdy.mjs info --id <projectId>
```

### 3. 获取项目历史消息

```bash
node readdy.mjs messages --id <projectId> [--page <n>] [--pageSize <n>]
```

### 4. 项目新建 (完整流程)

```bash
node readdy.mjs create --query "项目描述/需求" \
  [--device web|mobile] \
  [--framework <f>] [--lib <l>] [--category <c>]
```

默认值：`framework=react_v2`, `device=web`, `category=2`。项目名称由 AI 自动生成。

完整流程 (8 步)：

1. `POST /api/project/gen_section` + `POST /api/page_gen/suggest/page_title` — 并行生成页面模块列表和项目名称
2. `POST /api/project/gen_logo` — 根据 logo 提示词生成 Logo 图片
3. (项目名称已在 Step 1 并行获取)
4. `POST /api/page_gen/project` — 创建项目，获取 projectId
5. `PUT /api/page_gen/project` — 将 Logo 保存到项目
6. `POST /api/project/msg` (x2) + `POST /api/project/generate` — 创建消息记录并 SSE 流式生成项目内容（含自动 build + session 续传循环）
7. `POST /api/project/build` + `POST /api/project/build_check` — 最终构建（如果续传循环中未完成）+ `POST /api/project/set_show_id` 设置 showId
8. `PUT /api/project/msg` — 更新 AI 消息为完成状态 (recordStatus=0, showId)

### 5. 项目修改 (AI 重新生成)

```bash
node readdy.mjs modify --id <projectId> --query "修改需求描述"
```

完整流程 (6 步)：

1. `GET /api/page_gen/project?projectId=xxx` — 获取项目信息
2. `POST /api/project/msg_list` — 获取历史消息，提取最新 parentVersionID、parentShowID，构建 history JSON
3. `POST /api/project/msg` (x2) + `POST /api/project/generate` — 创建消息记录并 SSE 流式生成修改内容（含自动 build + session 续传循环）
4. `POST /api/project/build` + `POST /api/project/build_check` — 最终构建（如果续传循环中未完成）
5. `POST /api/project/set_show_id` — 设置 showId (带重试)
6. `PUT /api/project/msg` — 更新 AI 消息为完成状态 (recordStatus=0, showId)

### 6. 项目属性更新

```bash
node readdy.mjs update --id <projectId> \
  [--name <n>] [--background <b>] [--logo <url>] \
  [--businessName <bn>] [--email <e>] [--notifyEmail <e>] \
  [--introduction <t>] [--phoneNumber <p>] [--businessHour <h>] \
  [--languageStyle <s>]
```

### 7. 项目删除

```bash
node readdy.mjs delete --id <projectId>
```

### 8. 项目预览

```bash
node readdy.mjs preview --id <projectId> [--versionId <v>]
```

### 9. 验证 Resend API Key

```bash
node readdy.mjs validate-key --id <projectId> --apiKey <key>
```

### 10. 获取品牌邮件配置

```bash
node readdy.mjs email-config --id <projectId>
```

### 11. 配置管理

```bash
node readdy.mjs config --token <token>       # 保存认证 token
node readdy.mjs config                       # 查看当前配置
```

## API 端点映射

| 操作 | 方法 | 端点 |
|------|------|------|
| 项目列表 | POST | `/api/page_gen/project/list` |
| 项目信息 | GET | `/api/page_gen/project?projectId=xxx` |
| 新建项目 | POST | `/api/page_gen/project` |
| 更新项目属性 | PUT | `/api/page_gen/project` |
| 删除项目 | DELETE | `/api/page_gen/project` |
| 生成模块列表 | POST | `/api/project/gen_section` |
| 生成 Logo | POST | `/api/project/gen_logo` |
| 自动生成标题 | POST | `/api/page_gen/suggest/page_title` |
| 历史消息 | POST | `/api/project/msg_list` |
| 创建消息 | POST | `/api/project/msg` |
| 更新消息 | PUT | `/api/project/msg` |
| 生成项目 (SSE) | POST | `/api/project/generate` |
| 构建项目 | POST | `/api/project/build` |
| 构建检查 | POST | `/api/project/build_check` |
| 设置 showId | POST | `/api/project/set_show_id` |
| 获取预览链接 | GET | `/api/project/share?projectId=xxx&versionId=xxx` |
| 验证 API Key | POST | `/api/brand_email/validate_api_key` |
| 邮件配置 | GET | `/api/brand_email/config/:projectId` |

## 认证机制

所有请求携带以下 headers：
- `Authorization: Bearer <token>`
- `Content-Type: application/json`
- `X-Project-ID: <projectId>`（项目级操作时）

## 异常处理规则

| 错误码 | 提示 |
|--------|------|
| 401 | 认证失败，token 已过期或无效 |
| 403 / AccessDenied | 权限不足 |
| ProjectNotFound | 项目不存在或已被删除 |
| ProjectMax | 项目数量已达上限 |
| ApiKeyInvalid | API Key 无效或已失效 |
| ImageTooLarge | 图片大小不能超过 3.5MB |
| SubscriptionInGracePeriod | 订阅处于宽限期 |
| RequestTimeout | 请求超时 |
| InvalidParameter | 参数错误（附带详情） |
| PreviewError | 预览错误（附带详情） |
| 网络不可达 | 网络连接失败，检查网络或关闭 VPN |

## 执行规则

执行本 skill 时必须严格遵循以下规则，**不得自由发挥**：

### 强制约束（违反任何一条都是错误）

1. **只能通过脚本执行** — 所有操作必须通过 `node skills/readdy/readdy.mjs <command> [options]` 执行，禁止自行编写代码调用 Readdy API、禁止用 curl/fetch 直接请求 API、禁止绕过脚本实现任何功能
2. **禁止修改脚本** — 不得修改 `readdy.mjs` 的任何代码，除非用户明确要求修改脚本本身
3. **禁止修改用户输入（全链路）** — 从用户发出消息到最终执行 `node readdy.mjs` 命令的**整个链路**中，用户的需求描述必须**逐字原样传递**，一个字都不能改。具体要求：
   - 调用 Skill tool 时，`args` 参数必须是用户的原始消息文本
   - 执行 `--query` 时，值必须是用户的原始消息文本
   - 严禁在任何环节对用户输入做改写、润色、翻译、补充、省略、重新组织、纠错、扩写或缩写
   - 例：用户说"我想制作一个卖桃子的网站"，则 args 和 --query 都必须是"我想制作一个卖桃子的网站"，不得扩展为"创建一个卖桃子的电商网站，主题是新鲜桃子销售，包含首页展示……"
4. **禁止跳过步骤** — 脚本内部的流程步骤（gen_section → gen_logo → create project → generate → build → set_show_id → update msg）由脚本自动完成，不得手动拆分或跳过
5. **禁止添加额外参数** — 只传递用户明确指定的参数和脚本文档中列出的参数，不得自行添加 `--framework`、`--device`、`--category` 等参数（除非用户要求）
6. **禁止替代实现** — 即使脚本执行失败，也不得自行编写替代代码，应报告错误并建议用户排查

### 标准规则

7. 执行前检查 token 是否已配置（配置文件或环境变量），未配置则提示用户运行 `config --token`
8. 删除操作前必须向用户确认
9. 错误发生时，根据错误码给出明确的中文提示和建议操作
10. `create` 命令只需 `--query`，框架默认 `react_v2`，项目名称由 AI 自动生成
11. `modify` 命令需要 `--id` 和 `--query`，会自动获取项目信息和历史消息
12. SSE 生成返回 `session_status: "waiting_build"` 时，脚本会自动处理 build + 续传循环，无需手动干预

### 调用示例

假设用户原始消息是："做一个宠物商城网站"

```bash
# 正确 — Skill args 和 --query 都是用户原文
# Skill tool args: "做一个宠物商城网站"
node skills/readdy/readdy.mjs create --query "做一个宠物商城网站"

# 正确 — 修改项目
node skills/readdy/readdy.mjs modify --id abc123 --query "把首页的banner换成蓝色"

# 错误 — Skill args 阶段就改写了用户输入（最常见的错误！）
# 用户说"做一个宠物商城网站"，Skill args 却写成：
# "创建一个宠物电商网站，包含首页、产品列表、购物车、现代化设计风格"
# 这是严重违规，即使意图是"帮用户补充细节"也不允许

# 错误 — 不得改写用户的 query
node skills/readdy/readdy.mjs create --query "Create a pet e-commerce website with modern design"

# 错误 — 不得自行添加参数
node skills/readdy/readdy.mjs create --query "做一个网站" --framework react_v2 --device web --category 2

# 错误 — 不得绕过脚本直接调 API
fetch('https://gbh.readdy.ai/api/project/generate', ...)
```
