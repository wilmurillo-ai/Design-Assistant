---
name: zl-claw-pay
version: 1.0.0
description: |
  Use when users need to query sub-wallet binding status, bind sub-wallet, generate QR code, check payment status, query balance or transaction history.
  Trigger words: query sub-wallet, bind wallet, QR code, check balance, transaction records, payment status.
  Not applicable for: non-payment scenarios, batch operations, historical data export.
author: zlpay Team
license: MIT
tags:
  - payment
  - wallet
  - finance
skill_type: api
execution_mode: llm_driven
has_server: false
has_install_scripts: true
requires:
  - python>=3.6
security_level: high
environment_variables:
  required:
    - ZLPAY_APP_ID
    - ZLPAY_GM_CLIENT_PRIVATE_KEY (or ZLPAY_GM_CLIENT_PRIVATE_KEY_PATH)
    - ZLPAY_GM_SERVER_PUBLIC_KEY (or ZLPAY_GM_SERVER_PUBLIC_KEY_PATH)
  optional:
    - ZLPAY_API_KEY (supports command line, interactive input, or request body)
    - ZLPAY_LOG_LEVEL
---

# ZL Claw Pay Skill

ZL Pay Skill provides sub-wallet management, payment collection, and Token payment functions, building a dual-track payment system of "Fiat + Token".

##  Key Protocols 

1. **Never expose credentials**: Do not display API Key, Wallet ID or any sensitive information in chat responses.
2. **Explicit confirmation**: Must ask for "yes/no" confirmation before executing payments.
   *Format*: "I am about to send **[amount] sat** to **[recipient/note]**. Continue? (y/n)"
3. **Check balance first**: Verify balance before payment to prevent errors.
4. **Always include QR code**: When generating QR code: (a) display QR image, (b) output `MEDIA:` + `qr_file` path on same line. Never skip.

## Execution Mode: LLM Driven

This Skill uses LLM-driven mode. The agent interacts with backend via command-line calls to `skill.py`.

### Core Principles

- **Stateless design**: Each call starts a new process, exits immediately after execution
- **Agent manages context**: Session memory managed by agent, not dependent on local state
- **Command-line driven**: Execute all operations via `skill.py` commands
- **Dual command support**: `call` for HTTP APIs and local interfaces

### Command Format

```bash
# Unified calling method
python {baseDir}/scripts/skill.py call -interfaceId=<INTERFACE_ID> [--param1=value1] ...
```

**Command Design Principles**:
- **Unified command**: `call` for all interface calls (HTTP and local)
- **Parameter passthrough**: Control params via `-key=value`, data params via `--key=value`
- **Auto authentication**: Python code handles GM SM2/SM4 encryption and signing automatically
- **Interface code**: All calls must pass `-interfaceId` parameter

### Interface Types

| Type | Code | Command | Description |
|------|------|------|------|
| HTTP API | C prefix | `call` | Requires network request to backend |
| Local Interface | L prefix | `call` | Direct local storage operation |

### Documentation Guide

When processing user requests, consult documents in this order:

1. **Consult `references\api-spec.md`**: Get interface codes, trigger keywords, guidance phrases, request/response parameters
2. **Consult `assets\request-examples.md`**: Get command-line calling examples
3. **Execute command**: Construct and execute commands according to documentation

### CLI Command Examples

**Local Interface (Query Binding Status)**:
```bash
python {baseDir}/scripts/skill.py call -interfaceId=L00001
```

**HTTP API (Generate QR Code)**:
```bash
python {baseDir}/scripts/skill.py call -interfaceId=C00004 --amount=100
```

More examples in `assets\request-examples.md`.

---

## Trigger Conditions

Activate when users need to handle payment-related business:
- **Query binding status**: User asks "Have I bound my wallet", "Query sub-wallet"
- **Bind sub-wallet**: User says "Bind wallet", "Open account", "Create wallet"
- **Collect payment**: User says "Generate QR code", "Collect money", "Receive payment"
- **Query payment status**: User asks "Payment successful", "Check order status"
- **Query balance**: User says "Check balance", "How much money left"
- **Query transactions**: User says "Transaction records", "Bill", "Collection details"

Not applicable for: non-payment scenarios, batch operations, historical data export.

---

## Execution Steps

1. **Consult interface documentation**: Based on user intent, consult `references\api-spec.md` for interface codes and parameters
2. **Consult calling examples**: Get command format from `assets\request-examples.md`
3. **Construct command**: Use `call` command:
   - Local interface (L prefix): `call -interfaceId=L00001`
   - HTTP interface (C prefix): `call -interfaceId=C00003`
4. **Execute command**: Run the constructed command
5. **Parse response**: Process JSON response, extract `success`, `data`, `_seq_id` fields
6. **Generate reply**: Create user-friendly response based on result

---

## Output Format

**Success Response**:
```
 [Operation success description]
[Related business data display]
```

**Failure Response**:
```
 [Error description]
[Suggested action]
```

**QR Code Response** (Must include):
```
Please scan the QR code to complete [amount] collection:

MEDIA:[QR code file path]
```

---

## Security Protocols

1. **Never expose credentials**: Do not display API Key, Wallet ID or sensitive info
2. **Explicit confirmation**: Must ask "yes/no" confirmation before payment
3. **Pre-payment confirmation format**: "I am about to [operation description]. Continue? (y/n)"
4. **Sensitive info management**: All sensitive info managed by OpenClaw Memory system

Detailed security specs in "Sensitive Information Management" section of `references\api-spec.md`.

---

## Business Scenarios and Interface Mapping

| Scenario | Interface Code | Reference Document |
|------|---------|---------|
| Query binding status | L00001 | `references\api-spec.md` |
| Bind sub-wallet | C00003 | `references\api-spec.md` |
| Generate QR code | C00004 | `references\api-spec.md` |
| Query payment status | C00005 | `references\api-spec.md` |
| Query balance | C00006 | `references\api-spec.md` |

---

## Document Index

| Document | Content |
|------|------|
| `references\api-spec.md` | Interface list, trigger keywords, guidance phrases, request/response parameters |
| `assets\request-examples.md` | Command-line calling examples |

---

## Account System

### Account Types
- ** Host Wallet**: Payment account, supports deposit, withdrawal, trading, settlement
- ** Sub-wallet**: Collection account, funds aggregated to host wallet
- ** Token Account**: Lobster ecosystem account for in-ecosystem transactions

### Usage Scenarios
- **Full form**: Sub-wallet + Token account, supports full-featured payments
- **Traditional e-commerce**: Sub-wallet only, fiat collection and settlement
- **Pure AI compute**: Token account only, in-ecosystem consumption and settlement

---

## Security Notes

### Transport Security
-  Mandatory HTTPS/TLS 1.3 encryption
-  GM SM2/SM4: Request body encrypted with SM4, key encrypted with SM2
-  SM2 digital signature: Request and response use SM2 signature verification
-  Anti-replay: Timestamp + Nonce
-  Response verification: Verify server SM2 signature

### Credential Management

**API Key**
- **Source**: Multiple input methods (in priority order):
  1. Command line argument: `-api-key=xxx`
  2. Request body parameter: `api_key` (e.g., bind_sub_wallet)
  3. Environment variable: `ZLPAY_API_KEY`
  4. Memory storage: saved after successful bind_sub_wallet
- **Storage**: Optionally saved to memory after bind_sub_wallet, not written to config files
- **Display**: Never show full API Key in conversation, only show first 8 and last 4 digits
- **Security**: Use IronClaw Data Guard to check output, prevent credential leakage

**Wallet ID**
- **Source**: Provided by user during chat interaction
- **Storage**: Saved to local state file (`~/.zlpay/state.json`)
- **Usage**: Auto-retrieved from state file on subsequent API calls
- **Display**: Never show full wallet ID in chat (mask as `wallet_****5678`)

**Configuration Parameters (GM Keys, App ID, API URL, Encryption)**
- **Source**: Configured in `config/.env` file
- **Required**: `ZLPAY_APP_ID`, `ZLPAY_GM_CLIENT_PRIVATE_KEY`, `ZLPAY_GM_SERVER_PUBLIC_KEY`, `ZLPAY_API_URL`
- **Optional**: `ZLPAY_GM_ENABLE_ENCRYPTION` (default: true)
- **Alternative**: Can use file paths (`*_PATH` variants) for key files with 600 permissions
- **Security**: Keys are only used for request signing/verification, never transmitted over network

### Data Masking
Sensitive info in responses is automatically masked:
- Phone: `138****8000`
- ID Number: `110101********1234`

---

## Configuration

All settings are stored in `config/.env`:
- **Required**: `ZLPAY_APP_ID`, `ZLPAY_GM_CLIENT_PRIVATE_KEY`, `ZLPAY_GM_SERVER_PUBLIC_KEY`
- **Optional**: `ZLPAY_API_URL`, `ZLPAY_LOG_LEVEL`

**API Key**: User provides during chat (stored in OpenClaw Memory, not in config file)

**Local Files**: Creates `~/.zlpay/` directory for state storage and logs (user-only permissions).
