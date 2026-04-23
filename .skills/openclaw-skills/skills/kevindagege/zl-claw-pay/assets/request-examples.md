# Request Examples

> This document provides command-line calling examples for all interfaces for agent reference.
> **Document Version**: v1.0 | **Updated**: 2026-03-26 | **Maintainer**: ZLPay Team

---

## Command Format

All API calls use the following command format:

```bash
python {baseDir}/scripts/skill.py call \
  -method=<METHOD> \
  -endpoint=<ENDPOINT> \
  -interfaceId=<INTERFACE_CODE> \
  [--param1=value1] \
  [--param2=value2]
```

### Parameter Description

| Parameter | Description |
|------|------|
| `-method` | HTTP method (GET/POST) |
| `-endpoint` | API endpoint path |
| `-interfaceId` | Interface code (e.g., C00003, L00001), required |
| `--paramN` | Request parameters (pass according to interface docs) |

**Note**: `subWalletId` does not need to be passed, auto-injected by Python from session context.

---

## Local Interface

Local interfaces use `call` command without `-method` and `-endpoint`:

```bash
python {baseDir}/scripts/skill.py call \
  -interfaceId=<INTERFACE_CODE> \
  [--param1=value1]
```

**Features**:
- Direct local Python method call
- No HTTP network request
- No third-party (ZLPay) involved
- Interface codes start with `L` (e.g., L00001)

---

## 1. Query Sub-wallet (L00001)

Query current bound sub-wallet information.

```bash
python {baseDir}/scripts/skill.py call -interfaceId=L00001
```

**Expected Response**:
```json
{
  "subWalletId": "SW123456789",
  "sub_wallet_name": "My Wallet",
  "bindStatus": "bound"
}
```

---

## 2. Unbind Sub-wallet (L00002)

Unbind current sub-wallet.

```bash
python {baseDir}/scripts/skill.py call -interfaceId=L00002
```

**Expected Response**:
```json
{
  "subWalletId": "SW123456789",
  "unbindStatus": "unbound",
  "resMsg": "Successfully unbound"
}
```

---

## 3. Bind Sub-wallet (C00003)

Bind sub-wallet with API Key.

```bash
python {baseDir}/scripts/skill.py call \
  -method=POST \
  -endpoint=/post/claw/bind-sub-wallet \
  -interfaceId=C00003 \
  --sub_wallet_name="My Wallet" \
  --apiKey="your_api_key_here"
```

**Expected Response**:
```json
{
  "resCode": "S010000",
  "resMsg": "Success",
  "resData": {
    "subWalletId": "SW123456789"
  }
}
```

---

## 4. Generate QR Code (C00004)

Generate payment QR code.

```bash
python {baseDir}/scripts/skill.py call \
  -method=POST \
  -endpoint=/post/claw/create-qr-code \
  -interfaceId=C00004 \
  --amount="100.00" \
  --remark="Product payment"
```

**Expected Response**:
```json
{
  "resCode": "S010000",
  "resMsg": "Success",
  "resData": {
    "qrCode": "https://pay.zqpay.com/qr/xxx",
    "seqId": "SEQ202603260001"
  }
}
```

**Important**: Save `seqId` for payment status query!

---

## 5. Query Payment Status (C00005)

Query payment transaction status.

```bash
python {baseDir}/scripts/skill.py call \
  -method=POST \
  -endpoint=/post/claw/query-pay-status \
  -interfaceId=C00005 \
  --orgSeqId="SEQ202603260001"
```

**Expected Response**:
```json
{
  "resCode": "S010000",
  "resMsg": "Success",
  "resData": {
    "orderStatus": "success"
  }
}
```

---

## 6. Query Balance (C00006)

Query account balance.

```bash
python {baseDir}/scripts/skill.py call \
  -method=POST \
  -endpoint=/post/claw/query-balance \
  -interfaceId=C00006
```

**Expected Response**:
```json
{
  "resCode": "S010000",
  "resMsg": "Success",
  "resData": {
    "zlBalance": "1000.00",
    "pendSettleBalance": "500.00"
  }
}
```

---

## 7. Query Receipt List (C00007)

Query transaction history.

### Query by Preset Time Range

```bash
python {baseDir}/scripts/skill.py call \
  -method=POST \
  -endpoint=/post/claw/query-receipt-list \
  -interfaceId=C00007 \
  --dataflag="last week"
```

### Query by Custom Date Range

```bash
python {baseDir}/scripts/skill.py call \
  -method=POST \
  -endpoint=/post/claw/query-receipt-list \
  -interfaceId=C00007 \
  --startDate="20260301" \
  --endDate="20260331"
```

### Query by Amount Range

```bash
python {baseDir}/scripts/skill.py call \
  -method=POST \
  -endpoint=/post/claw/query-receipt-list \
  -interfaceId=C00007 \
  --startAmount="100" \
  --endAmount="1000"
```

**Expected Response**:
```json
{
  "resCode": "S010000",
  "resMsg": "Success",
  "resData": {
    "list": [
      {
        "seqId": "SEQ202603260001",
        "amount": "100.00",
        "orderStatus": "success",
        "createTime": "20260326143000"
      }
    ],
    "allSize": "1"
  }
}
```

---

## Common Response Codes

| Code | Description |
|------|-------------|
| S010000 | Success |
| F010001 | Business error |
| P010002 | Platform error |
| E010003 | System error |

---

**Document Version**: v1.0  
**Updated**: 2026-03-26
