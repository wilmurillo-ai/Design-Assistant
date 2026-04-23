# Invoice Verification Service

ClawHub skill for the `invoice-api-service` v4 plugin APIs.

## 关键提示

- 技能内部注册名 `bw-invoice-verification-service`，执行命令需要在聊天框里前缀 `$bw-invoice-verification-service`（例如 `@openclaw-bot 用 $bw-invoice-verification-service init-key`），也可以说“帮我初始化”让系统追踪 `init-key` 操作。
- 如果你在聊天框里直接说“帮我安装这个技能”，系统会把意图当作安装请求，先运行 `clawhub install bw-invoice-verification-service`，再输入上述初始化语句能才能进入具体命令。
- 安装后重启 OpenClaw 保证新技能加载；遇到识别困难时直接发 `$bw-invoice-verification-service init-key` 以避免开源语义歧义。

> **安全说明**：本技能只调用官方的 `https://test.51yzt.cn/assetInnovate` 接口，并通过标准的 `node` 脚本发起 HTTPS 请求，不包含任何 `eval`/动态执行或硬编码的敏感密钥。VirusTotal Code Insight 的“可疑”提示仅是对外部 API、加密用途的泛泛检测，若需要，可将源码与安全团队共享便于人工复核。


## 安装反馈提示

安装成功后，OpenClaw 聊天框应该提示用户：

```
技能已准备就绪，请在聊天框输入“帮我初始化”或直接发 `$bw-invoice-verification-service init-key`，系统会自动调用 init-key 并保存 appKey。
若你刚才说的是“帮我安装这个技能”，请先运行 `clawhub install bw-invoice-verification-service` 完成安装，再使用上述初始化语句。
```

如果提示没有出现，也可以直接说“帮我初始化”、“帮我配置发票”，或者明确发 `$bw-invoice-verification-service init-key`，也能触发初始化操作；“帮我安装”只用于引导安装，不会直接执行 init-key。

## 四要素自动识别

本技能会根据发票代码的格式自动判断当前票种和所需的四要素：

- 12 位、第一位是 `0` 且末尾 `04/05/06/07/11/12`，以及 10 位且第 8 位是 `3` 或 `6` 的发票，默认需要填写发票代码、发票号码、开票日期、校验码后 6 位。
- 12 位、第一位是 `1`，12 位第一位是 `0` 且末尾 `17`，或 10 位第 8 位是 `1`/`5` 的发票，默认需要发票代码、发票号码、开票日期及不含税金额（二手车票点用车价合计）。
- 当发票代码为空但发票号码为 20 位（通常来自二维码），会默认使用含税金额作为第四要素。
- 这些判断结果会随 `verify`/`verify-image` 调用一起返回，方便在聊天框或表单中提示用户填写正确的四要素。

## What This Skill Does

- Initialize or rotate an `appKey` with `POST /api/v4/plugin/key/init`
- Query recharge package options with `GET /api/v4/plugin/packages`
- Query remaining quota with `GET /api/v4/plugin/quota`
- Query quota ledger with `GET /api/v4/plugin/ledger`
- Verify invoice text with `POST /api/v4/plugin/verify`
- Verify invoice images with `POST /api/v4/plugin/verify`
- Verify all invoice images in a local directory and save JSON result files next to the source directory
- Create recharge orders with `POST /api/v4/plugin/orders`
- Query recharge order status with `GET /api/v4/plugin/orders/{orderNo}`

## Runtime Requirements

- Node.js 18 or newer
- Reachable backend base URL, for example `http://192.168.154.76:18888`

## Bundled Files

- `SKILL.md`: trigger instructions and execution workflow
- `agents/openai.yaml`: ClawHub/OpenClaw UI metadata
- `scripts/invoice_service.js`: executable helper script

## Local Usage

```bash
node "{baseDir}/scripts/invoice_service.js" config set --api-base-url http://192.168.154.76:18888
node "{baseDir}/scripts/invoice_service.js" init-key
node "{baseDir}/scripts/invoice_service.js" packages
node "{baseDir}/scripts/invoice_service.js" quota
node "{baseDir}/scripts/invoice_service.js" ledger --page 1 --page-size 20
node "{baseDir}/scripts/invoice_service.js" verify --text "发票代码 033002100611, 发票号码 12345678, 开票日期 2025-05-30, 金额 260.65, 校验码 123456" --format both
node "{baseDir}/scripts/invoice_service.js" verify-image --image-file C:\path\invoice.png --format both
node "{baseDir}/scripts/invoice_service.js" verify-image --image "data:image/png;base64,..." --format both
node "{baseDir}/scripts/invoice_service.js" verify-directory --dir C:\path\invoice-images --format json
node "{baseDir}/scripts/invoice_service.js" create-order --amount 10
node "{baseDir}/scripts/invoice_service.js" query-order --order-no ORDER123456789
```

Install the skill first, then run `init-key` once before the first real use.
`init-key` calls the backend to create and persist the `appKey`, and the backend grants the free 5-trial quota at the same time.

## Publish To ClawHub

The current `clawhub` CLI publishes a skill folder directly. `SKILL.md` is mandatory; `README.md` is recommended.

```bash
clawhub login
clawhub publish . --slug invoice-verification-service --name "Invoice Verification Service" --version 0.3.0 --changelog "Add image verify and recharge order flows for invoice-api-service v4 plugin APIs."
```

## Install From ClawHub

After the skill is published publicly:

```bash
clawhub install invoice-verification-service
node "{installDir}/scripts/invoice_service.js" init-key
```

If a specific version is needed:

```bash
clawhub install invoice-verification-service --version 0.3.0
```

## Notes

- The script stores config in `~/.openclaw/invoice-skill/config.json`.
- The script also reads the legacy plugin config from `~/.openclaw/invoice-plugin/config.json` if present.
- `verify-image` can be called with `--image-file`, `--image-base64`, or `--image` (path/base64/data-url). This lets chat-uploaded image content and local files both go through the same base64 flow to backend OCR.
- Image verification consumes `2` quota per request. The response now includes `data.quotaCost=2` and `data.quotaCostNotice`.
- `--text` is optional and is used only to supplement extracted invoice fields. For `--image-file`, the script also auto-loads a same-name sidecar text file by default when present (for example `invoice01.png` + `invoice01.txt`).
- `verify-directory` scans `.png`, `.jpg`, and `.jpeg` files in a directory. If exactly one image is found, it writes one `*.verify.json` file in the source directory. If multiple images are found, it creates an `invoice-verify-results-<timestamp>` folder under the source directory and writes one JSON per image plus `summary.json`.
- `verify-directory` reads a same-name sidecar text file by default when present, for example `invoice01.png` + `invoice01.txt`.
- When the backend reports `remainingQuota <= 3`, plugin responses may include `rechargePackages` so the caller can show package options directly in chat.
- After `create-order`, prefer `paymentPageUrl` as the payment entry. It points to the cashier page where the user can choose WeChat or Alipay. `qrCodeImageUrl` is only the QR image link.
- `create-order` now polls order status by default (`--wait-seconds`, `--poll-interval-seconds`) and returns `data.orderPolling` + `data.paymentSettled`. When settlement is detected, the response includes a direct arrival tip so the chat can immediately tell the user the recharge has arrived.
- Payment callback handling stays on the backend internal endpoint `/api/v4/internal/payment/callback`; this skill only needs order creation and order status querying.
