---
name: esd-device-config
description: "Use when querying or modifying device configurations on ESD service, calling REST APIs with sigV2 authentication on HK baseline or STG environments"
version: 1.0.0
---

# ESD 设备配置查询与修改

## Overview

ESD（设备配置分发服务）提供设备配置的查询和修改接口。所有环境使用统一的 sigV2 签名认证，仅 Base URL 不同。

## When to Use

- 查询设备在 ESD 配置中心的当前配置
- 修改设备配置（如 webSocket support、timezone、statusLight 等）
- 排查设备消息投递问题（XMPP vs WebSocket 路由）
- 验证 Blade 双写后 ESD MySQL 中的配置值

## Quick Reference

### 环境参考

| 项目 | 香港基线 (HK) | 海外测试 (STG) |
|------|--------------|----------------|
| Base URL | `https://psh-esd.closeli.com/lecam` | `https://esd.stg.closeli.com/lecam` |
| 认证路径 | `/sigV2/` | `/sigV2/` |
| AccessKey | `42435117-1e6` | `42435117-1e6` |
| Secret | `6mCBWg13tedIsdv8A56P` | `6mCBWg13tedIsdv8A56P` |
| 测试设备 | — | `xxxxS_tjl31070009` |
| 测试 Token | — | `495f127d3b0440afa2d5693381fd32ac` |

### 认证路径对比

| 路径 | 认证方式 | 说明 |
|------|----------|------|
| `/service/*` | DES 加密 | 旧接口，需要加密 jsonObject |
| `/sigV2/*` | accessKey + signature | 推荐，无需 DES 加密 |
| `/sigV3/*` | accessKey + signature | 与 sigV2 相同认证方式 |

## 签名算法

```
signature = md5(secret + "accessKey=<accessKey>jsonObject=<jsonObject>")
```

规则：
1. 将所有参数（**排除** `signature` 本身）按 key 字母序排序
2. 拼接为 `key=value` 格式（无分隔符）
3. 在前面拼接 secret
4. 对整个字符串做 MD5

## API 1: 查询设备当前配置 (getCurrentSetting)

**端点:** `POST /sigV2/profile/app/getCurrentSetting`

**jsonObject 格式:**
```json
{"deviceid":"<设备ID>","token":"<token>"}
```

**完整调用示例:**
```bash
DEVICE_ID="xxxxS_54f29f143034"
TOKEN="4c873406fa384908a0b0c644d4a4bd05"
SECRET="6mCBWg13tedIsdv8A56P"
ACCESS_KEY="42435117-1e6"
# 根据环境选择 Base URL
BASE_URL="https://psh-esd.closeli.com/lecam"       # HK
# BASE_URL="https://esd.stg.closeli.com/lecam"      # STG

JSON="{\"deviceid\":\"${DEVICE_ID}\",\"token\":\"${TOKEN}\"}"
SIG_STRING="${SECRET}accessKey=${ACCESS_KEY}jsonObject=${JSON}"
SIGNATURE=$(echo -n "$SIG_STRING" | md5sum | awk '{print $1}')

curl -s -X POST "${BASE_URL}/sigV2/profile/app/getCurrentSetting" \
  --data-urlencode "accessKey=${ACCESS_KEY}" \
  --data-urlencode "jsonObject=${JSON}" \
  --data-urlencode "signature=${SIGNATURE}"
```

**成功响应:** `failflag: "0"`，`content` 字段包含完整设备配置 XML。

## API 2: 修改设备配置 (saveSettingByPaths)

**端点:** `POST /sigV2/profile/saveSettingByPaths`

**jsonObject 格式:**
```json
{
  "deviceid": "<设备ID>",
  "token": "<token>",
  "savetype": "3",
  "paths": [
    {
      "path": "profile/general/webSocket",
      "element": "<webSocket support=\"1\"/>"
    }
  ]
}
```

**savetype 说明:**

| savetype | 行为 |
|----------|------|
| `0` | 保存配置，不通知设备（APP 端常用） |
| `1` | 保存配置，不通知设备 |
| `2` | 保存配置，通知设备 |
| `3` | 保存配置，通知设备（直接写入，绕过队列） |

**注意:** ESD 开启 `saveSupportQueueSwitch` 时，`saveSettingAttrByPaths` 会被放入队列异步处理。使用 `saveSettingByPaths` + `savetype=3` 可直接写入。

**完整调用示例:**
```bash
DEVICE_ID="xxxxS_54f29f143034"
TOKEN="4c873406fa384908a0b0c644d4a4bd05"
SECRET="6mCBWg13tedIsdv8A56P"
ACCESS_KEY="42435117-1e6"
BASE_URL="https://psh-esd.closeli.com/lecam"

JSON="{\"deviceid\":\"${DEVICE_ID}\",\"token\":\"${TOKEN}\",\"savetype\":\"3\",\"paths\":[{\"path\":\"profile/general/webSocket\",\"element\":\"<webSocket support=\\\"1\\\"/>\"}]}"
SIG_STRING="${SECRET}accessKey=${ACCESS_KEY}jsonObject=${JSON}"
SIGNATURE=$(echo -n "$SIG_STRING" | md5sum | awk '{print $1}')

curl -s -X POST "${BASE_URL}/sigV2/profile/saveSettingByPaths" \
  --data-urlencode "accessKey=${ACCESS_KEY}" \
  --data-urlencode "jsonObject=${JSON}" \
  --data-urlencode "signature=${SIGNATURE}"
```

**成功响应:** `failflag: "0"`

## API 3: 版本查询

```bash
curl -s https://esd.stg.closeli.com/lecam/version
# 返回: ESD_3.1.0_20260316_B1491_8cbf78e7
```

## Common Mistakes

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `failflag: "1007"`, `For input string: "{"` | 使用了 `/service/` 路径（需要 DES 加密） | 改用 `/sigV2/` 路径 |
| `failflag: "9999"`, `signature error` | 签名计算错误 | 检查参数排序、secret 拼接 |
| `failflag: "1005"`, system error | `getSettingByPaths` 接口异常 | 改用 `getCurrentSetting` 查询 |
| 配置修改后未生效 | `saveSupportQueueSwitch` 开启，请求被队列化 | 使用 `saveSettingByPaths` + `savetype=3` |
