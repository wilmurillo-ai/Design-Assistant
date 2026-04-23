# ZLPay Skill API Specification

> **Document Version**: v1.0  
> **Updated**: 2026-03-26  
> **Maintainer**: ZLPay Team

---

## Quick Index

| Interface Code | Interface Name | Trigger Keywords | Request Method |
|---------|---------|-----------|---------|
| L00001 | Query Sub-wallet | query sub-wallet, wallet info, check binding | local |
| L00002 | Unbind Sub-wallet | unbind wallet, delete wallet | local |
| C00003 | Bind Sub-wallet | bind wallet, open account, create wallet | POST |
| C00004 | Generate QR Code | collect, receive, QR code | POST |
| C00005 | Query Payment Status | query payment, payment status, order status | POST |
| C00006 | Query Balance | balance, check balance | POST |
| C00007 | Query Receipt List | transactions, records, bill | POST |

---

## 1. Query Sub-wallet (L00001)

### 1.1 Basic Information

| Item | Content |
|------|------|
| **Interface Code** | L00001 |
| **Request Method** | local |
| **Interface Address** | None (local call) |
| **Function** | Query current bound sub-wallet info, return subWalletId and basic info |

### 1.2 Request Parameters

None (subWalletId auto-retrieved from session context)

### 1.3 Response Parameters

| Parameter | Type | Description |
|--------|------|------|
| subWalletId | string | Sub-wallet identifier (internal use only) |
| sub_wallet_name | string | Sub-wallet name |
| bindStatus | string | Binding status: bound/not bound |

### 1.4 AI Usage Guide

#### Trigger Keywords

- "query sub-wallet"
- "wallet info"
- "check binding"
- "check status"

#### Usage Scenarios

1. **Pre-check**: Before collection or balance query, verify if user has bound sub-wallet
2. **Status confirmation**: When user asks "Have I bound wallet" 
3. **Info display**: When user wants to view current sub-wallet info

#### Guidance Phrases

**Pre-check - Not Bound**:
> "You have not bound a sub-wallet. Please bind first to use collection features. Provide your API Key to complete binding."

**Pre-check - Already Bound**:
> "Confirmed you have bound sub-wallet [sub_wallet_name], can proceed with collection."

**User Asks Status**:
> "Let me check your current sub-wallet binding status..."

**Query Success - Bound**:
> "You have bound sub-wallet:
> - Name: [sub_wallet_name]
> - Status: Bound
> You can use collection, balance query and other features."

**Query Success - Not Bound**:
> "You have not bound a sub-wallet. Please use bind wallet function first."

#### Full Process

1. **Preparation**: Confirm session_id exists
2. **Initiate request**: Call local interface (pass interfaceId=L00001)
3. **Process response**:
   - Success and bound: Continue business operation
   - Success but not bound: Guide user to bind first
   - Failed: Show error info
4. **Follow-up**: Guide user next steps based on binding status

#### Calling Example

```bash
python {baseDir}/scripts/skill.py call -interfaceId=L00001
```

---

## 2. Unbind Sub-wallet (L00002)

### 2.1 Basic Information

| Item | Content |
|------|------|
| **Interface Code** | L00002 |
| **Request Method** | local |
| **Interface Address** | None (local call) |
| **Function** | Unbind current sub-wallet, clear local binding |

### 2.2 Request Parameters

None (subWalletId auto-retrieved from session context)

### 2.3 Response Parameters

| Parameter | Type | Description |
|--------|------|------|
| subWalletId | string | Unbound sub-wallet identifier |
| unbindStatus | string | Unbind status: unbound/failed |
| resMsg | string | Result description |

### 2.4 AI Usage Guide

#### Trigger Keywords

- "unbind wallet"
- "delete wallet"
- "remove wallet"

#### Usage Scenarios

1. **User-initiated unbind**: User no longer needs wallet
2. **Switch wallet**: User needs to bind new sub-wallet
3. **Security exit**: User concerned about security

#### Guidance Phrases

**Before Unbind Confirm**:
> "After unbinding, you cannot use collection features and need to re-bind to restore. Confirm unbind?"

**Unbind Success**:
> "Successfully unbound sub-wallet [sub_wallet_name]. Re-bind when needed."

**Unbind Failed**:
> "Failed to unbind wallet. Please retry later or contact support."

#### Calling Example

```bash
python {baseDir}/scripts/skill.py call -interfaceId=L00002
```

---

## 3. Bind Sub-wallet (C00003)

### 3.1 Basic Information

| Item | Content |
|------|------|
| **Interface Code** | C00003 |
| **Interface Address** | /post/claw/bind-sub-wallet |
| **Request Method** | POST |

#### Request Parameters

| Parameter | Type | Required | Description |
|--------|------|------|------|
| sub_wallet_name | string | Yes | Sub-wallet name |
| apiKey | string | Yes | API Key (user provides) |

#### Response Parameters

| Parameter | Type | Description |
|--------|------|------|
| subWalletId | string | Sub-wallet identifier |

### 3.2 AI Usage Guide

#### Trigger Keywords

- "bind wallet"
- "open account"
- "create wallet"

#### Usage Scenarios

When user first uses ZLPay and needs to bind their sub-wallet. Prerequisite for other features.

#### Guidance Phrases

**Ask for apiKey**:
> "To complete sub-wallet binding, I need your API Key. Please provide:"

**Confirm Info**:
> "I will bind sub-wallet [sub_wallet_name] with apiKey [apiKey]. Continue?"

**Bind Success**:
> "Sub-wallet binding successful! You can now use collection and balance query."

**Bind Failed**:
> "Binding failed: [reason]. Check apiKey or retry later."

#### Calling Example

```bash
python {baseDir}/scripts/skill.py call -method=POST -endpoint=/post/claw/bind-sub-wallet -interfaceId=C00003 --sub_wallet_name="Wallet Name" --apiKey="user apiKey"
```

---

## 4. Generate QR Code (C00004)

### 4.1 Basic Information

| Item | Content |
|------|------|
| **Interface Code** | C00004 |
| **Interface Address** | /post/claw/create-qr-code |
| **Request Method** | POST |

#### Request Parameters

| Parameter | Type | Required | Description |
|--------|------|------|------|
| amount | string | Yes | Amount (CNY) |
| remark | string | No | Product name/payment note |

#### Response Parameters

| Parameter | Type | Description |
|--------|------|------|
| qrCode | string | QR code link |
| seqId | string | Transaction ID (**must save to session**) |

### 4.2 AI Usage Guide

#### Trigger Keywords

- "collect"
- "receive"
- "QR code"
- "generate QR code"

#### Usage Scenarios

When user needs to collect payment from others. User shares QR to payer who scans and pays.

#### Guidance Phrases

**Confirm Amount**:
> "Please tell me the amount to collect (CNY):"

**Generate Success**:
> "QR code generated! Transaction ID is `seqId`. Scan to pay or share to payer."

**Generate Failed**:
> "Failed: [reason]. Check amount or retry later."

#### Important Notes

- **Must save seqId**: Key for querying payment status
- Generate QR image from qrCode link
- Output format must include `MEDIA:./qr_code.png`

#### Calling Example

```bash
python {baseDir}/scripts/skill.py call -method=POST -endpoint=/post/claw/create-qr-code -interfaceId=C00004 --amount="100.00" --remark="Product name"
```

---

## 5. Query Payment Status (C00005)

### 5.1 Basic Information

| Item | Content |
|------|------|
| **Interface Code** | C00005 |
| **Interface Address** | /post/claw/query-pay-status |
| **Request Method** | POST |

#### Request Parameters

| Parameter | Type | Required | Description |
|--------|------|------|------|
| orgSeqId | string | Yes | Original transaction ID (seqId from QR generation) |

#### Response Parameters

| Parameter | Type | Description |
|--------|------|------|
| orderStatus | string | Payment status: success/processing/failed |

### 5.2 AI Usage Guide

#### Trigger Keywords

- "query payment"
- "payment status"
- "order status"
- "paid successfully"

#### Usage Scenarios

After generating QR code, user wants to know if payment completed.

#### Guidance Phrases

**Query Success - Different Status**:
- Success: "Transaction [seqId] paid successfully! Amount [amount] CNY received."
- Processing: "Transaction [seqId] is processing, please query later."
- Failed: "Transaction [seqId] failed, reason: [reason]."

#### Calling Example

```bash
python {baseDir}/scripts/skill.py call -method=POST -endpoint=/post/claw/query-pay-status -interfaceId=C00005 --orgSeqId="transaction ID"
```

---

## 6. Query Balance (C00006)

### 6.1 Basic Information

| Item | Content |
|------|------|
| **Interface Code** | C00006 |
| **Interface Address** | /post/claw/query-balance |
| **Request Method** | POST |

#### Request Parameters

None (subWalletId auto-injected by backend)

#### Response Parameters

| Parameter | Type | Description |
|--------|------|------|
| pendSettleBalance | string | Pending settlement balance (CNY) |
| zlBalance | string | Available balance (CNY) |

### 6.2 AI Usage Guide

#### Trigger Keywords

- "balance"
- "check balance"
- "how much money"

#### Usage Scenarios

When user wants to know account funds. Returns available and pending balances.

#### Guidance Phrases

**Query Success**:
> "Your account balance:
> - Available: [zlBalance] CNY
> - Pending: [pendSettleBalance] CNY
> - Total: [total] CNY"

#### Calling Example

```bash
python {baseDir}/scripts/skill.py call -method=POST -endpoint=/post/claw/query-balance -interfaceId=C00006
```

---

## 7. Query Receipt List (C00007)

### 7.1 Basic Information

| Item | Content |
|------|------|
| **Interface Code** | C00007 |
| **Interface Address** | /post/claw/query-receipt-list |
| **Request Method** | POST |

#### Request Parameters

| Parameter | Type | Required | Description |
|--------|------|------|------|
| dataflag | string | No | Preset range: today, yesterday, last week, last month, last year |
| startDate | string | No | Start date (YYYYMMDD) |
| endDate | string | No | End date (YYYYMMDD) |
| startAmount | string | No | Min amount for range query (CNY) |
| endAmount | string | No | Max amount for range query (CNY) |

#### Response Parameters

| Parameter | Type | Description |
|--------|------|------|
| list | array | Transaction list |
| totalPage | string | Total pages |
| allSize | string | Total count |

### 7.2 AI Usage Guide

#### Trigger Keywords

- "transactions"
- "records"
- "bill"
- "collection details"

#### Usage Scenarios

When user wants to view historical collection records, reconcile or track funds.

#### Guidance Phrases

**Ask Query Conditions**:
> "Which time range? Choose: today, yesterday, last week, last month, last year, or provide start/end dates."

**Query Success (With Data)**:
> "Found [allSize] records:
> 
> 1. [date] [amount]CNY [status] - ID: [seqId]
> 2. [date] [amount]CNY [status] - ID: [seqId]"

**Query Success (No Data)**:
> "No transaction records in this period."

#### Calling Examples

**Preset time range**:
```bash
python {baseDir}/scripts/skill.py call -method=POST -endpoint=/post/claw/query-receipt-list -interfaceId=C00007 --dataflag="last week"
```

**Custom date range**:
```bash
python {baseDir}/scripts/skill.py call -method=POST -endpoint=/post/claw/query-receipt-list -interfaceId=C00007 --startDate="20260301" --endDate="20260331"
```

---

## General Specifications

### Sensitive Information Handling

The following are **not** required from agent, handled automatically by Python:
- `subWalletId`: Auto-retrieved from session context and injected by backend
- `api_key`: Auto-read from OpenClaw Memory system
- Encryption keys handled by backend

**Important**: Agent **does not** need to pass `subWalletId`, auto-injected by backend.

### Parameter Rules

1. **Required**: `interfaceId`
2. **Agent obtains**: `sub_wallet_name` (via OpenClaw API from session_id)
3. **User provides**: `apiKey`, `amount`, `remark`, date ranges, etc.
4. **Auto-injected**: `subWalletId`

### seqId vs orgSeqId

**Generate QR (C00004)**: Response has `seqId`, agent must save to session.
**Query Payment (C00005)**: Request uses `orgSeqId` with saved `seqId` value.

### Error Codes

| Error Code | Description | Suggestion |
|--------|------|----------|
| Success | Request successful | Process normally |
| Param error | Invalid parameters | Check required params |
| Unauthorized | Invalid apiKey | Check apiKey |
| Not bound | Sub-wallet not bound | Guide to bind first |
| Insufficient balance | Low balance | Notify user |
| System error | Server error | Retry later |

---

**Document Version**: v1.0  
**Updated**: 2026-03-26  
**Maintainer**: ZLPay Team
