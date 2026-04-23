# FitConverter Submit Reference

## Online Endpoints

- submit: `https://www.fitconverter.com/api/convertSubmit`
- payment status: `https://www.fitconverter.com/api/payStatusQuery`

## Required Inputs

Always required:

- `type`
- `destination`
- `address`

Require `zip_file`:

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

Require `account` and `password`:

- `zepp_sync`
- `keep_sync`
- `codoon_sync`
- `xingzhe_sync`
- `garmin_sync_coros`

Require phone number plus SMS code:

- `joyrun_sync`

## Request Fields

The page sends these `FormData` keys to `/api/convertSubmit`:

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

## Response Interpretation

### `res.code === 1`

Validation passed and payment initialization succeeded.

Possible payment branches:

- `res.data.code_url`: PC QR payment
- `res.data.h5_url`: H5 redirect payment
- `res.data.prepay_id`: WeChat JSAPI payment

Also capture:

- `res.orderId`
- `res.paid`

## `res.code === 0`

Validation failed.

User-facing message:

- with `res.message`: `提交的${res.message}，请按照说明重新整理后上传`
- without `res.message`: `提交压缩包结构不正确，请按照说明重新整理后上传`

## Payment Status Query

`/api/payStatusQuery` expects:

```json
{
  "orderId": "..."
}
```

Key field:

- `data.trade_state`

Meaning:

- `NOTPAY`: keep polling
- `SUCCESS`: payment confirmed, conversion should continue server-side
- any other non-empty value: stop polling and treat as ended but not successful

## Scripts

Run full flow:

```bash
node "{baseDir}/scripts/run-flow.js" \
  --do-mode trial \
  --type huawei \
  --destination garmin \
  --address user@example.com \
  --zip-file "D:/sample-data/sample.zip"
```

Include `qr_data_url` in final JSON:

```bash
node "{baseDir}/scripts/run-flow.js" \
  --do-mode trial \
  --type huawei \
  --destination garmin \
  --address user@example.com \
  --zip-file "D:/sample-data/sample.zip" \
  --include-qr-data
```

Git Bash alternative:

```bash
node "{baseDir}/scripts/run-flow.js" \
  --do-mode trial \
  --type huawei \
  --destination garmin \
  --address user@example.com \
  --zip-file "/d/sample-data/sample.zip"
```

Submit conversion:

```bash
node "{baseDir}/scripts/submit-convert.js" \
  --type huawei \
  --destination garmin \
  --address user@example.com \
  --zip-file "D:/sample-data/sample.zip"
```

Git Bash alternative:

```bash
node "{baseDir}/scripts/submit-convert.js" \
  --type huawei \
  --destination garmin \
  --address user@example.com \
  --zip-file "/d/sample-data/sample.zip"
```

Poll payment:

```bash
node "{baseDir}/scripts/poll-payment.js" \
  --order-id ORDER_ID_FROM_SUBMIT
```

Quiet polling:

```bash
node "{baseDir}/scripts/poll-payment.js" \
  --order-id ORDER_ID_FROM_SUBMIT \
  --quiet
```

## Notes

- The scripts default to the online host `https://www.fitconverter.com`.
- The scripts are intended to run on Windows, macOS, or Linux with `node` available.
- `run-flow.js` is the preferred entry point for the full user flow.
- `run-flow.js` renders a terminal QR code when `code_url` is returned.
- `run-flow.js` prints payment progress to stderr and returns final JSON on stdout.
- `submit-convert.js` returns machine-friendly JSON.
- `poll-payment.js` prints progress logs by default and does not declare success until `trade_state === SUCCESS`.
- The server starts conversion after confirmed payment. QR generation alone is not completion.
- See `openclaw-integration.md` for tool wrapping and chat collection guidance.
