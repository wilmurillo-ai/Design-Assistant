---
name: invoice-verification-service
description: 使用发票服务后端 v4 plugin 接口完成 key 初始化、查验额度查询、额度流水查询、发票文本或图片查验。用户提到“发票查验”“剩余额度”“额度流水”“appKey 初始化/失效重绑”等需求，或需要调用 /api/v4/plugin/key/init、/api/v4/plugin/quota、/api/v4/plugin/ledger、/api/v4/plugin/verify 时使用。
metadata: {"openclaw":{"tools":["shell","read_file"],"requires":{"bins":["node"]}}}
---

# Invoice Verification Service

## Overview

用这个 skill 把原来的插件能力改成显式脚本调用。
优先执行 `{baseDir}/scripts/invoice_service.js`，不要直接改写脚本里的 HTTP 逻辑。

## Quick Start

先确认 Node.js 可用，然后按需执行以下命令：

```bash
node "{baseDir}/scripts/invoice_service.js" help
node "{baseDir}/scripts/invoice_service.js" config set --api-base-url http://localhost:8080
node "{baseDir}/scripts/invoice_service.js" init-key
node "{baseDir}/scripts/invoice_service.js" quota
node "{baseDir}/scripts/invoice_service.js" ledger --page 1 --page-size 20
node "{baseDir}/scripts/invoice_service.js" verify --text "发票代码 033002100611, 发票号码 12345678, 开票日期 2025-05-30, 金额 260.65, 校验码 123456" --format both
```

安装完成后，先执行一次 `init-key`。
这一步会调用后端 `/api/v4/plugin/key/init`，生成并保存 `appKey`，同时拿到后端发放的免费 5 次额度。

## Workflow

1. 配置 `apiBaseUrl`。
如果还没有可用配置，先运行 `config set --api-base-url ...`。

2. 直接执行目标动作。
脚本会在没有 `appKey` 时自动调用 `/api/v4/plugin/key/init` 初始化，并把 `appKey`、`clientInstanceId`、`deviceFingerprint` 写入 `~/.openclaw/invoice-skill/config.json`。

3. 当接口返回 `INVALID_KEY` 或同义错误时，重试一次。
脚本会删除旧 `appKey`，轮换 `clientInstanceId` 后重新初始化并再次发起请求。

4. 把脚本返回的 JSON 摘要化后再回复用户。
保留关键字段，例如剩余额度、额度预警、流水列表、查验结果、状态码和错误信息。

## Supported Actions

### `config`

- `config show`
- `config set --api-base-url <url>`
- `config set --app-key <key>`
- `config set --client-instance-id <id>`
- `config set --device-fingerprint <id>`
- `config clear-app-key`

只在需要初始化或排查配置时使用。

### `init-key`

主动初始化 key。

```bash
node "{baseDir}/scripts/invoice_service.js" init-key
```

推荐在 skill 安装完成后立刻执行一次，再开始 `quota`、`ledger` 或 `verify`。

需要轮换客户端标识时：

```bash
node "{baseDir}/scripts/invoice_service.js" init-key --rotate-client-instance-id
```

### `quota`

查询剩余额度。

```bash
node "{baseDir}/scripts/invoice_service.js" quota
```

### `ledger`

查询额度流水。

```bash
node "{baseDir}/scripts/invoice_service.js" ledger --page 1 --page-size 20
```

### `verify`

用于文本查验。把完整文本放进 `--text`，脚本会尽量提取结构化字段并同时上送原文。

```bash
node "{baseDir}/scripts/invoice_service.js" verify --text "<发票文本>" --format both
```

`--format` 仅允许 `json`、`base64`、`base64+json`、`both`。

### `verify-image`

当前后端没有独立 OCR 入口时，只做图片预检，不会从图片里自动识别字段。
要继续查验，必须同时提供 `--text` 补充发票字段。

```bash
node "{baseDir}/scripts/invoice_service.js" verify-image --image-file C:\path\invoice.png --text "<发票文本>"
```

或：

```bash
node "{baseDir}/scripts/invoice_service.js" verify-image --image-base64 "<base64>" --mime-type image/png --text "<发票文本>"
```

## Response Handling

- 优先读取 JSON 中的 `ok`、`action`、`data`、`meta`。
- 如果 `ok` 为 `false`，直接提炼 `error.message`、`error.code`、`error.status`。
- 如果执行了自动绑定，向用户说明已自动注册并复用新的 `appKey`。
- `data` 中真正的业务字段来自后端统一返回体：`success`、`code`、`message`、`remainingQuota`、`validUntil`、`quotaAlert`、`data`。

## Notes

- 新 skill 配置文件路径是 `~/.openclaw/invoice-skill/config.json`。
- 为兼容插件迁移，脚本会自动读取旧路径 `~/.openclaw/invoice-plugin/config.json` 作为回退配置。
- 只在确有需要时才执行 `config set --app-key ...`；常规情况下优先依赖 `/api/v4/plugin/key/init` 自动初始化。
- 当前 `invoice-api-service` 仓库中未看到充值、续费、订单查询 controller；不要再调用旧的 `/api/orders/*` 接口。
