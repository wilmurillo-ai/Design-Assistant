# OpenClaw Integration

## Goal

Connect the FitConverter skill to OpenClaw as a structured tool call, instead of asking the user to type shell commands in chat.

Recommended shape:

- OpenClaw skill: decides when to use the conversion flow
- OpenClaw tool: receives structured parameters
- local runner: maps tool parameters to `scripts/run-flow.js`

## Skill Packaging

Recommended copied folder name:

- `fit-converter`

Recommended `SKILL.md` frontmatter:

```markdown
---
name: fit-converter
description: Submit FitConverter self-service conversion jobs through the `/convert/do` workflow. Use when the task is to collect conversion inputs, validate required fields, call `/api/convertSubmit`, handle validation failures, present payment QR or WeChat payment info, and wait for `/api/payStatusQuery` to confirm completion.
metadata: {"openclaw":{"requires":{"bins":["node"]}}}
---
```

Recommended install targets:

- `<workspace>/skills/fit-converter`
- `<workspace>/.agents/skills/fit-converter`
- `~/.openclaw/skills/fit-converter`

After copying:

1. Start a new OpenClaw session or restart the gateway.
2. Run `openclaw skills list`.
3. Confirm `fit-converter` is loaded.

Platform note:

- this skill is intended to work on Windows, macOS, and Linux
- the main runtime requirement is `node` on `PATH`
- the zip file path must match the host OS path format

## Recommended Tool Name

- `fitconverter_run_flow`

## When To Call This Tool

Call this tool when the user wants to submit a FitConverter self-service conversion task and enough inputs have been collected.

Do not call this tool when:

- the source type is not self-service capable
- required inputs are still missing
- the user is asking only for explanation, not execution

## Tool Input Schema

Use a JSON input shape like this:

```json
{
  "type": "huawei",
  "destination": "garmin",
  "address": "user@example.com",
  "zip_file": "D:/path/to/file.zip",
  "do_mode": "trial",
  "fit_code": "",
  "account": "",
  "password": "",
  "client_mode": "PC",
  "client_openid": "",
  "interval_ms": 3000,
  "max_attempts": 120,
  "include_qr_data": false
}
```

## Required Fields

Always required:

- `type`
- `destination`
- `address`

Conditionally required:

- `zip_file` for file upload types
- `account` and `password` for password-based sync types
- `account` as phone number and `password` as SMS code for `joyrun_sync`

Recommended defaults:

- `do_mode`: `do`
- `client_mode`: `PC`
- `client_openid`: `""`
- `interval_ms`: `3000`
- `max_attempts`: `120`
- `include_qr_data`: `false`

## Valid Enum Values

### `type`

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

### `destination`

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

### `do_mode`

- `trial`
- `do`

### `client_mode`

- `PC`
- `weixin`
- `H5`

## Chat Collection Rules

OpenClaw should collect missing fields conversationally before calling the tool.

Suggested order:

1. `type`
2. `destination`
3. `address`
4. `zip_file` or `account` and `password`
5. optional `do_mode`

Suggested prompts:

- `你要转换哪种来源平台的数据？`
- `要导入到哪个目标平台？`
- `转换结果发到哪个邮箱？`
- `请提供 zip 文件路径。`
- `请提供账号和密码。`
- `要走试用模式还是正式付费模式？`

## Attachment Handling

Best option:

- let the user upload a zip file in OpenClaw
- save it to a local temporary path
- pass that local path as `zip_file`

Fallback option:

- ask the user for a local file path

Do not pass raw file bytes in chat text.

## CLI Mapping

Map tool input to:

```bash
node "{baseDir}/scripts/run-flow.js" \
  --type <type> \
  --destination <destination> \
  --address <address> \
  [--zip-file <zip_file>] \
  [--account <account>] \
  [--password <password>] \
  [--do-mode <do_mode>] \
  [--fit-code <fit_code>] \
  [--client-mode <client_mode>] \
  [--client-openid <client_openid>] \
  [--interval-ms <interval_ms>] \
  [--max-attempts <max_attempts>] \
  [--include-qr-data]
```

Windows `bash` note:

- prefer `"D:/path/to/file.zip"` or `"/d/path/to/file.zip"`
- avoid unquoted `D:\path\to\file.zip`

macOS and Linux note:

- use normal POSIX paths such as `/Users/name/file.zip` or `/home/name/file.zip`

## Execution Model

Recommended runtime behavior:

1. Spawn `run-flow.js`
2. Stream `stderr` to the user as progress
3. Capture final `stdout`
4. Parse final `stdout` as JSON
5. Convert the JSON into the OpenClaw tool result

Why stream `stderr`:

- payment QR information is shown there
- terminal QR rendering is shown there
- payment polling progress is shown there

## Recommended OpenClaw Tool Output

Return a structured result like this:

```json
{
  "status": "submitted",
  "user_message": "提交成功，转换结果随后将以邮件形式通知",
  "step": "done",
  "submit_result": {},
  "poll_result": {}
}
```

Possible `status` values:

- `missing_inputs`
- `unsupported_flow`
- `validation_failed`
- `payment_required`
- `submitted`
- `error`

## UI Recommendations

If OpenClaw supports rich progress events, show:

- `正在创建支付订单`
- `已创建订单，等待支付`
- `请扫码支付`
- `正在查询支付状态`
- `支付成功，任务已提交`

## QR Code Delivery Through OpenClaw Channels

If OpenClaw does not support images, showing:
When the script returns `payment_summary.qr_image_path`, the agent should display the QR image via the url to the user.

is enough.

### Delivery flow
1. Parse the JSON output from `run-flow.js` (or `submit-convert.js`)
2. Extract `payment_summary.qr_image_path` (a PNG file url)
3. Use the `exec` tool to run:

```bash
openclaw message send \
  --channel <channel> \
  --target <target> \
  --media <qr_image_path> \
  --message "请扫描以下二维码完成微信支付（金额：<amount>元，订单号：<orderId>）"
```

4. If only one channel is configured, omit `--channel`
5. `--target` is the user or chat identifier from the current conversation

### Fallback chain

| Priority | Condition | Action |
|----------|-----------|--------|
| 1 | `qr_image_path` exists | Send PNG via `openclaw message send --media` |
| 2 | `qr_data_url` exists | Embed in reply as `![QR](<data_url>)` |
| 3 | `code_url` exists | Show as copyable text link |

### Example adapter with QR delivery

```js
const result = JSON.parse(stdout);
const ps = result.payment_summary || {};

if (ps.qr_image_path) {
  // Send QR image through the active channel
  exec(`openclaw message send --media "${ps.qr_image_path}" --message "请扫码支付 ${ps.amount}元"`);
} else if (ps.qr_data_url) {
  // Embed in agent reply text
  reply(`请扫描以下二维码完成支付：\n![支付二维码](${ps.qr_data_url})`);
} else if (ps.code_url) {
  // Text-only fallback
  reply(`微信扫一扫支付链接：${ps.code_url}`);
}
```

### Channel compatibility notes

- **WhatsApp**: images are resized to JPEG (max 2048px side), PNG QR codes work well
- **Telegram**: PNG images are sent natively; use `--force-document` to avoid compression if needed
- **Discord**: PNG images are embedded as attachments
- **Other channels**: `openclaw message send --media` handles format conversion automatically

## Minimal Adapter Pseudocode

```js
const args = buildCliArgsFromToolInput(input);
const child = spawn("node", [
  `${baseDir}/scripts/run-flow.js`,
  ...args,
]);

child.stderr.on("data", (chunk) => {
  streamProgress(chunk.toString());
});

let stdout = "";
child.stdout.on("data", (chunk) => {
  stdout += chunk.toString();
});

child.on("close", () => {
  const result = JSON.parse(stdout);
  returnToolResult(result);
});
```

## Execution Logs

The JSON result from all scripts contains a `logs` array with timestamped entries covering the full execution timeline. When `run-flow.js` is used, the `logs` array merges entries from both `submit-convert.js` and `poll-payment.js`.

Display `result.logs` to the user when they ask about execution details, or use it for debugging when something goes wrong:

```javascript
const result = JSON.parse(stdout);
if (result.logs && result.logs.length > 0) {
  result.logs.forEach((entry) => console.log(entry));
}
```

## Integration Checklist

- define `fitconverter_run_flow`
- implement input validation
- support file path or uploaded attachment to local temp file
- map JSON input to CLI arguments
- parse `stdout` JSON, inspect `result.logs` for execution details
- surface `status`, `user_message`, and payment progress in UI

## Related Files

- `SKILL.md`
- `reference.md`
- `scripts/run-flow.js`
- `scripts/submit-convert.js`
- `scripts/poll-payment.js`
