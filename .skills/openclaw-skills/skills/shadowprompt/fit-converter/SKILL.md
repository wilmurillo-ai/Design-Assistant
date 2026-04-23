---
name: fit-converter
description: |
  运动健康转换工具、运动记录转换、运动记忆、运动数据转换、fitconverter、华为运动数据、小米运动数据、Zepp跑步记录、Keep数据导出、三星运动记录、Vivo运动记录、Keep训练记录、咕咚数据、悦跑圈记录、Garmin、Coros、RQrun、IGPSPOR迹驰、行者数据、Strava、运动转换
---

# FitConverter Submit

## Purpose

This skill covers:

- collecting inputs for a conversion job
- determining whether the selected source supports self-service
- building the web request
- interpreting validation and payment responses
- polling payment completion

This skill does not cover:

- manual email-based conversion
- Harmony app flow
- backend implementation details that are not visible from the page logic

## Files

- `scripts/run-flow.js`: submit, wait for payment, and poll until the flow ends
- `scripts/submit-convert.js`: submit to the online FitConverter endpoint
- `scripts/poll-payment.js`: poll the online FitConverter endpoint
- `reference.md`: quick reference for types, fields, and response handling
- `openclaw-integration.md`: how to expose this flow as an OpenClaw tool

## OpenClaw Install Notes

When copying this skill into OpenClaw, prefer a target folder named `fit-converter`.

This skill is cross-platform and should work on Windows, macOS, and Linux as long as `node` is available and the runtime can access the local zip file path.

Recommended locations:

- `<workspace>/skills/fit-converter`
- `<workspace>/.agents/skills/fit-converter`
- `~/.openclaw/skills/fit-converter`

After copying:

1. Start a new OpenClaw session or restart the gateway.
2. Run `openclaw skills list`.
3. Confirm `fit-converter` appears in the loaded skill list.

## Entry Conditions

Use this skill only when the user wants the self-service conversion flow that starts from FitConverter.

If the selected `type` is not self-service capable, do not force this workflow. Tell the user to use the manual conversion path instead.

## Self-Service Source Types

These source values support the self-service flow:

- `huawei`
- `zepp`
- `xiaomi`
- `vivo`
- `keep`
- `samsung`
- `dongdong`
- `kml`
- `gpx`
- `tcx`
- `fit`
- `zepp_sync`
- `keep_sync`
- `codoon_sync`
- `joyrun_sync`
- `xingzhe_sync`
- `garmin_sync_coros`

Do not treat `rqrun_sync` as self-service.

## Target Platforms

Supported `destination` values:

- `coros`
- `garmin`
- `strava`
- `rqrun`
- `huawei`
- `keep`
- `shuzixindong`
- `xingzhe`
- `igpsport`
- `onelap`
- `fit`
- `tcx`
- `gpx`
- `kml`

## Input Contract

Always gather:

- `address`: result delivery email
- `type`: source platform
- `destination`: target platform

Conditional requirements:

- file upload types require `zip_file`
- password-based sync types require `account` and `password`
- `joyrun_sync` requires `account` as phone number and `password` as SMS code

Optional fields:

- `fitCode`
- `doMode`
- `clientMode`
- `clientOpenID`

## Type-Specific Requirements

### File Upload Types

Require exactly one `zip_file`:

- `huawei`
- `zepp`
- `xiaomi`
- `vivo`
- `keep`
- `samsung`
- `dongdong`
- `kml`
- `gpx`
- `tcx`
- `fit`

The uploaded archive should be a password-free zip file.

### Password Sync Types

Require:

- `account`
- `password`

Types:

- `zepp_sync`
- `keep_sync`
- `codoon_sync`
- `xingzhe_sync`
- `garmin_sync_coros`

### Code Sync Types

Require:

- `account` as phone number
- `password` as SMS verification code

Types:

- `joyrun_sync`

## Client Mode Rules

Frontend logic uses these client modes:

- `PC`
- `weixin`
- `H5`

Rules:

- if running in WeChat browser and `clientOpenID` exists, use `weixin`
- else if running on mobile, use `H5`
- otherwise use `PC`

Current page flow does not support `H5` submission. If the resolved mode is `H5`, stop and report that H5 is unsupported for this workflow.

## Request Construction

Build `FormData` with these fields when present:

- `clientMode`
- `clientOpenID`
- `zip_file`
- `type`
- `address`
- `destination`
- `fileName`
- `fitCode`
- `account`
- `password`
- `paid`
- `payment`
- `recordMode`

Field rules:

- `payment` must be `wechat`
- `fileName` should follow `trial_<timestamp>`
- `recordMode` is `trial_<fitCode>` when `doMode === trial`, otherwise `prd`
- `paid` is only client-provided seed data; treat server payment data as authoritative

## Submission Workflow

Follow this sequence exactly.

1. Confirm the selected `type` supports self-service.
2. Gather all required inputs for that `type`.
3. Validate `address` as an email.
4. Reject the flow early if `clientMode === H5`.
5. Prefer running `scripts/run-flow.js` for the full end-to-end flow.
6. Use `scripts/submit-convert.js` plus `scripts/poll-payment.js` only when the two-step flow is explicitly needed.
7. Interpret the script JSON response using the rules below.
8. Stop only when the workflow reaches a terminal state.

## Utility Scripts

### Run Full Flow

Run:

```bash
node "{baseDir}/scripts/run-flow.js" \
  --type <type> \
  --destination <destination> \
  --address <email> \
  [--zip-file <path>] \
  [--account <value>] \
  [--password <value>] \
  [--do-mode <trial|do>] \
  [--fit-code <value>] \
  [--client-mode <PC|weixin|H5>] \
  [--client-openid <value>] \
  [--interval-ms 3000] \
  [--max-attempts 120] \
  [--include-qr-data]
```

Windows `bash` path note:

- prefer `"D:/path/to/file.zip"` or `"/d/path/to/file.zip"`
- avoid unquoted `D:\path\to\file.zip` in `bash`

On macOS and Linux, use normal POSIX file paths such as `/Users/name/data.zip` or `/home/name/data.zip`.

Script behavior:

- calls `submit-convert.js`
- prints payment information to stderr as soon as submission succeeds
- renders a terminal QR code when `code_url` is returned
- automatically starts `poll-payment.js` when an `orderId` is available
- shows polling progress in stderr while waiting for payment
- returns final JSON only after the payment flow reaches a terminal state
- adds `--skip-qr` by default to keep JSON output compact
- use `--include-qr-data` if the final JSON should also include `qr_data_url`

Use this script by default when the user wants the same behavior as the page flow.

### Submit Conversion

Run:

```bash
node "{baseDir}/scripts/submit-convert.js" \
  --type <type> \
  --destination <destination> \
  --address <email> \
  [--zip-file <path>] \
  [--account <value>] \
  [--password <value>] \
  [--do-mode <trial|do>] \
  [--fit-code <value>] \
  [--client-mode <PC|weixin|H5>] \
  [--client-openid <value>]
```

Windows `bash` path note:

- prefer `"D:/path/to/file.zip"` or `"/d/path/to/file.zip"`
- avoid unquoted `D:\path\to\file.zip` in `bash`

Script behavior:

- calls `https://www.fitconverter.com/api/convertSubmit`
- validates inputs before the request
- returns machine-friendly JSON
- includes `code_url` and a QR data URL when the server returns PC QR payment data
- exits immediately after payment initialization, without automatic polling

### Poll Payment

Run:

```bash
node "{baseDir}/scripts/poll-payment.js" \
  --order-id <orderId> \
  [--interval-ms 3000] \
  [--max-attempts 120] \
  [--quiet]
```

Script behavior:

- calls `https://www.fitconverter.com/api/payStatusQuery`
- keeps polling while `trade_state === NOTPAY`
- prints attempt count, current status, and elapsed time to stderr by default
- returns `submitted` only when `trade_state === SUCCESS`
- use `--quiet` to suppress progress logs and keep only the final JSON result

## Response Handling

### Success Path: `res.code === 1`

Treat this as submission accepted and payment initialized.

Then branch by returned payment data:

- if `res.data.code_url` exists:
  - generate a QR code from `code_url`
  - store `orderId`
  - if `res.paid` exists, convert cents to yuan for display
  - return status `payment_required`
- else if `res.data.h5_url` exists:
  - redirect user to `h5_url`
  - return status `payment_required`
- else if `res.data.prepay_id` exists:
  - invoke WeChat JSAPI payment with the returned payload
  - store `orderId`
  - return status `payment_required`
- else:
  - return status `error`
  - user message: `支付初始化成功，但未返回可用的支付信息`

### Validation Failure: `res.code === 0`

Treat this as data validation failure.

User-facing message rules:

- if `res.message` exists:
  - `提交的${res.message}，请按照说明重新整理后上传`
- else:
  - `提交压缩包结构不正确，请按照说明重新整理后上传`

Return status `validation_failed`.

### Other Response Codes

Return status `error`.

Default user-facing message:

- `其它异常`

### Network or Request Failure

Return status `error`.

Default user-facing message:

- `出错啦`

## Payment Polling

When `orderId` exists, poll:

- `POST /api/payStatusQuery`

Request body:

- `orderId`

Polling rules:

- if `trade_state === NOTPAY`, wait 3 seconds and poll again
- if `trade_state === SUCCESS`, finish with:
  - status `submitted`
  - user message: `提交成功，转换结果随后将以邮件形式通知`
- if `trade_state` is any other non-empty value, stop polling and close the payment flow

Do not claim conversion is complete immediately after QR generation. The server starts conversion after confirmed payment.

## Agent Output Contract

Always summarize the current state using exactly one of these statuses:

- `missing_inputs`
- `unsupported_flow`
- `validation_failed`
- `payment_required`
- `submitted`
- `error`

When reporting a result, include:

- `status`
- `user_message`
- `missing_fields` if any
- `request_summary`
- `payment_summary` when payment is active

## Preferred Response Shape

Use this format:

```markdown
status: <one of the allowed statuses>
user_message: <short user-facing summary>
missing_fields: <comma-separated list or none>
request_summary:
- type: <type>
- destination: <destination>
- address: <address>
payment_summary:
- orderId: <value or none>
- amount: <value or unknown>
- payment_channel: wechat
- next_step: <scan_qr | invoke_wechat_pay | wait_for_poll | none>
```

## Guardrails

- Do not invent backend validation codes beyond what the page handles.
- Do not mark the job as submitted before payment status confirms it.
- Do not silently continue if required inputs are missing.
- Do not use the self-service flow for unsupported source types.
- Treat server-returned payment information as authoritative.
- Prefer returning the raw `code_url` or `orderId` over describing the QR in prose.
- If script output already contains structured JSON, reuse it instead of paraphrasing away important fields.

## Source of Truth

This skill is derived from the front-end flow in:

- `src/pages/convert/do.js`
- `reference.md`

## Execution Logs

All scripts output a `logs` array in their JSON result. Each entry is a timestamped string:

```json
{
  "status": "payment_required",
  "user_message": "...",
  "logs": [
    "[2026-03-31T05:14:17.123Z] [submit] type=huawei destination=garmin address=user@example.com doMode=trial",
    "[2026-03-31T05:14:17.456Z] [submit] posting to https://www.fitconverter.com/api/convertSubmit ...",
    "[2026-03-31T05:14:18.789Z] [submit] server responded: code=1",
    "[2026-03-31T05:14:18.800Z] [submit] payment created: orderId=FIT20260331xxx, code_url available"
  ]
}
```

When using `run-flow.js`, the `logs` array merges logs from both `submit-convert.js` and `poll-payment.js`, providing a complete timeline. Display or inspect `logs` to trace the full execution process.

Logs are also written to `stderr` for direct terminal use.

## QR Code Display

1. `qr_image_local_path` - QR code image local path
2. `qr_image_path` - QR code image url
3. `qr_data_url` - QR code image data url
4. `code_url` - payment info text


### Priority order

Use the `message` tool to deliver the QR PNG file through the current channel:

```javascript
message({
  action: "send",
  channel: "<channel>",
  target: "<targetType>:<targetId>",
  media: qr_image_local_path,
  caption: "支付二维码"
})
```

**参数说明：**
- `action`: 固定为 `"send"`
- `channel`: 频道类型，如 `yuanbao`、`discord`、`telegram` 等
- `target`: 目标，群聊用 `group:<群号>`，私聊用`use:<用户ID>`
- `media`: 图片路径（本地路径或 URL）
- `caption`: 图片说明（可选）

**示例：**
```javascript
// 发送到元宝群聊
message({
  action: "send",
  channel: "yuanbao",
  target: "group:253891337",
  media: "/tmp/weixinPayQr.png",
  caption: "请扫描以下二维码完成微信支付"
})

// 发送到 Discord 频道
message({
  action: "send",
  channel: "discord",
  target: "channel:1489510983377621105",
  media: "/tmp/weixinPayQr.png",
  caption: "请扫码支付"
})
```


### Second order
Use the `exec` tool to deliver the QR PNG file through the current channel:
```bash
openclaw message send --channel <channel> --target <targetType:targetId> \
  --media <qr_image_path> \
  --message "请扫描以下二维码完成微信支付（金额：<amount>元）"
```

- `<channel>`: the channel the user is chatting on (e.g. `whatsapp`, `telegram`, `discord`)
- `<targetType>`: user or channel
- `<targetId>`: if the targetType is user, user id is the targetId; if the targetType is channel, channel id is the targetId
- `<qr_image_path>`: the value from `payment_summary.qr_image_path`
- `<amount>`: the value from `payment_summary.amount`

If only one channel is configured, `--channel` can be omitted.

example of openclaw message send
```bash
频道/群聊 用`channel:<频道ID>`
openclaw message send --channel discord --target channel:1489510983377621105 --media "/tmp/weixinPayQr.png" --message "请扫码支付"
```


```bash
DM 私聊 用 `user:<用户ID>`
openclaw message send --channel discord --target user:343677073648254988 --media "/tmp/weixinPayQr.png" --message "请扫码支付"
```

### Fallback: inline markdown image

If `qr_image_path` is unavailable, use `qr_data_url` in the reply text:

或在回复中直接展示：
```
请扫描以下二维码完成支付：
![支付二维码](qr_data_url)
```

### Last resort: text-only

If neither image format is available, provide `code_url` as copyable text:

```
微信扫一扫支付链接：<code_url>
```

## Special fallback usage
### Discord
if `openclaw message send` failed，try Discord API：
   ```bash
   curl -X POST "https://discord.com/api/v10/channels/<频道ID>/messages" \
     -H "Authorization: Bot <TOKEN>" \
     -F "content=请扫码支付" \
     -F "file=@/tmp/weixinPayQr.png"
   ```
