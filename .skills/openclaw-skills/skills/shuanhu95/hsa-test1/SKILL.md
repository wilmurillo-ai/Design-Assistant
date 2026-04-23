---
name: device-capture
description: 萤石设备批量抓图技能。支持多设备同时抓图，只需配置 appKey 和 appSecret。Use when: 需要获取多个摄像头实时画面、批量抓图存档、监控画面采集、定时抓图任务。
metadata:
  {
    "openclaw":
      {
        "emoji": "📸",
        "requires": { "env": ["EZVIZ_APP_KEY", "EZVIZ_APP_SECRET", "EZVIZ_DEVICE_SERIAL"], "pip": ["requests"] },
        "primaryEnv": "EZVIZ_APP_KEY"
      }
  }
---

# Device Capture (设备抓图)

批量获取萤石摄像头实时画面，支持多设备同时抓图。

## 快速开始

安装依赖：
```bash
pip install requests
```

设置环境变量：
```bash
export EZVIZ_APP_KEY="your_app_key"
export EZVIZ_APP_SECRET="your_app_secret"
export EZVIZ_DEVICE_SERIAL="dev1,dev2,dev3"
```

可选环境变量：
```bash
export EZVIZ_CHANNEL_NO="1"        # 通道号，默认 1
export EZVIZ_DOWNLOAD_PATH="./captures"  # 下载路径（可选）
export EZVIZ_TOKEN_CACHE="1"       # Token 缓存：1=启用 (默认), 0=禁用
```

**注意**: 不需要设置 `EZVIZ_ACCESS_TOKEN`！技能会自动获取 Token（有效期 7 天）。

**Token 缓存说明**:
- ✅ **默认启用**: 首次获取后自动缓存到系统临时目录
- ✅ **有效期**: Token 缓存 7 天，到期前 5 分钟自动刷新
- ⚠️ **禁用缓存**: 设置 `EZVIZ_TOKEN_CACHE=0` 可禁用缓存（每次运行重新获取）
- 🔒 **安全**: 缓存文件权限 600，仅当前用户可读写

运行：
```bash
python3 {baseDir}/scripts/device_capture.py
```

命令行参数：
```bash
# 单个设备
python3 {baseDir}/scripts/device_capture.py appKey appSecret dev1 1

# 多个设备（逗号分隔）
python3 {baseDir}/scripts/device_capture.py appKey appSecret "dev1,dev2,dev3" 1

# 指定通道号
python3 {baseDir}/scripts/device_capture.py appKey appSecret "dev1:1,dev2:2" 1

# 带下载路径
python3 {baseDir}/scripts/device_capture.py appKey appSecret "dev1,dev2" 1 ./captures
```

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken, 有效期 7 天)
       ↓
2. 设备抓图 (accessToken + deviceSerial → picUrl, 有效期 2 小时)
       ↓
3. 可选下载 (picUrl → 本地文件)
       ↓
4. 输出结果 (JSON + 控制台)
```

## Token 自动获取说明

**你不需要手动获取或配置 `EZVIZ_ACCESS_TOKEN`！**

技能会自动处理 Token 的获取：

```
首次运行:
  appKey + appSecret → 调用萤石 API → 获取 accessToken (有效期 7 天)
  ↓
保存到缓存文件（临时目录）
  ↓
后续运行:
  检查缓存 Token 是否过期
  ├─ 未过期 → 直接使用缓存 Token ✅
  └─ 已过期 → 重新获取新 Token
```

**Token 管理特性**:
- ✅ **自动获取**: 首次运行自动调用萤石 API 获取
- ✅ **有效期 7 天**: 获取的 Token 7 天内有效
- ✅ **智能缓存**: Token 有效期内不重复获取，提升效率
- ✅ **安全缓冲**: 到期前 5 分钟自动刷新，避免边界问题
- ✅ **无需配置**: 不需要手动设置 `EZVIZ_ACCESS_TOKEN` 环境变量
- ✅ **安全存储**: 缓存文件存储在系统临时目录

**缓存优势**:
- ⚡ **更快**: 避免重复 API 调用，减少等待时间
- 🌐 **稳定**: 减少 API 调用次数，降低网络失败风险
- 💰 **节省**: 减少 API 调用频率，避免触发限流

## 输出示例

```
============================================================
Device Capture Skill (设备抓图技能)
============================================================
[Time] 2026-03-13 17:00:00
[INFO] Target devices: 2
       - dev1 (Channel: 1)
       - dev2 (Channel: 1)

============================================================
[Step 1] Getting access token...
[SUCCESS] Token obtained, expires: 2026-03-20 17:00:00

============================================================
[Step 2] Capturing images...
============================================================

[Device] dev1 (Channel: 1)
[SUCCESS] Image captured: https://opencapture.ys7.com/...

[Device] dev2 (Channel: 1)
[SUCCESS] Image captured: https://opencapture.ys7.com/...
[INFO] Downloaded: ./captures/dev2_20260313_170000.jpg (145KB)

============================================================
CAPTURE SUMMARY
============================================================
  Total devices:  2
  Success:        2
  Failed:         0
============================================================
```

## 多设备格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 单设备 | `dev1` | 默认通道 1 |
| 多设备 | `dev1,dev2,dev3` | 全部使用默认通道 |
| 指定通道 | `dev1:1,dev2:2` | 每个设备独立通道 |
| 混合 | `dev1,dev2:2,dev3` | 部分指定通道 |

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://openai.ys7.com/help/81 |
| 设备抓图 | `POST /api/lapp/device/capture` | https://openai.ys7.com/help/687 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `openai.ys7.com` | 萤石开放平台 API（Token、抓图） |

## 格式代码

**返回字段**:
- `picUrl` - 抓拍图片 URL（有效期 2 小时）
- `expire_hours` - URL 有效期（2 小时）

**错误码**:
- `200` - 操作成功
- `10002` - accessToken 过期
- `10028` - 抓图次数超限
- `20007` - 设备不在线
- `20008` - 设备响应超时

## Tips

- **多设备**: 逗号分隔 `dev1,dev2,dev3`
- **指定通道**: 冒号分隔 `dev1:1,dev2:2`
- **Token 有效期**: 7 天（每次运行自动获取）
- **图片有效期**: 2 小时
- **频率限制**: 设备间自动间隔 4 秒，避免限流
- **定时任务**: 建议 ≥5 分钟
- **下载路径**: 设置 `EZVIZ_DOWNLOAD_PATH` 自动下载图片

## 注意事项

⚠️ **频率限制**: 萤石抓图接口建议间隔 4 秒以上。技能已自动在设备间等待 4 秒，避免触发限流（错误码 10028）

⚠️ **隐私合规**: 使用摄像头监控可能涉及隐私问题，确保符合当地法律法规

⚠️ **设备要求**: 设备必须在线且支持抓图功能（`support_capture=1`）

⚠️ **Token 安全**: Token 会缓存到系统临时目录（自动管理），不写入日志，不发送到非萤石端点

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| appKey/appSecret | `openai.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `openai.ys7.com` (萤石) | 请求抓图 | ✅ 必需 |
| 抓拍图片 URL | `openai.ys7.com` (萤石) | 返回图片地址 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`openai.ys7.com`): Token 请求、设备抓图 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务
- ❌ **图片不上传**: 图片存储在萤石服务器，技能只获取 URL

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（设备抓图）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 缓存到系统临时目录（`/tmp/ezviz_global_token_cache/`），权限 600
- ✅ Token 有效期 7 天，到期前 5 分钟自动刷新
- ✅ 可禁用缓存：设置 `EZVIZ_TOKEN_CACHE=0` 环境变量
- ✅ 不记录完整 API 响应
- ✅ 图片 URL 只显示前 50 字符
- ✅ 可选下载图片到本地（默认不下载）

## 定时任务示例

**Linux Crontab** (每 5 分钟):
```bash
*/5 * * * * cd /path/to/device-capture && python3 scripts/device_capture.py >> /var/log/capture.log 2>&1
```

**macOS Launchd**:
```xml
<key>StartInterval</key>
<integer>300</integer>
```
