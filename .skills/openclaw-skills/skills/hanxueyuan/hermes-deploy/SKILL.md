---
name: hermes-deploy
description: 使用 OpenClaw 部署 Hermes Agent 完整指南（含开机自启）
version: 1.0.1
tags: [hermes, deploy, openclaw, migration, yolo, autostart]
---

# hermes-deploy

使用 OpenClaw 部署 Hermes Agent，从 0 到 1 完成安装、配置迁移和 YOLO 模式开启。

## 技能描述

帮助用户在服务器上部署 Hermes Agent，包括：
- 克隆源码并安装依赖
- 从 OpenClaw 迁移配置（模型、飞书等）
- 配置飞书 WebSocket 连接
- 开启 YOLO 模式（无审批执行）

## 前置条件

- 服务器：Linux (Ubuntu/Debian)
- Python: 3.10+
- Git: 已安装
- 已有 OpenClaw 配置（可选，用于迁移）
- 飞书应用凭证（App ID / App Secret）

### 系统检查

```bash
# 检查 Python 版本
python3 --version  # 应 >= 3.10

# 检查 pip
pip3 --version

# 检查 git
git --version
```

## 使用示例

```
帮我部署 Hermes Agent
从 OpenClaw 迁移配置到 Hermes
开启 Hermes 的 YOLO 模式
配置开机自启动
```

## 部署步骤

### 1. 安装 Hermes Agent

```bash
# 方式 1: 官方安装脚本
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
source ~/.bashrc

# 方式 2: 手动克隆（网络受限时）
cd /tmp
curl -fsSL https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip -o hermes.zip
unzip -q hermes.zip
mv hermes-agent-main ~/.hermes/hermes-agent
cd ~/.hermes/hermes-agent
pip install -e .
```

### 2. 验证安装

```bash
hermes --version
# 输出：Hermes Agent v0.7.0
```

### 3. 从 OpenClaw 迁移配置（推荐：自动迁移）

#### 方式 1: 使用官方迁移命令（推荐）

Hermes 提供了自动迁移工具，可以一键迁移 OpenClaw 配置：

```bash
# 1. 预览迁移内容（不会实际执行）
hermes claw migrate --source /workspace/projects --dry-run

# 2. 执行完整迁移（包含密钥）
hermes claw migrate --source /workspace/projects --migrate-secrets -y

# 3. 仅迁移用户数据（不含密钥）
hermes claw migrate --source /workspace/projects --preset user-data -y

# 4. 迁移后清理（可选）
hermes claw cleanup
```

**迁移内容**：
- ✅ `SOUL.md` 人设文件
- ✅ `MEMORY.md` 和 `USER.md` 记忆
- ✅ 已创建的 Skills
- ✅ 命令白名单
- ✅ 消息平台配置（Telegram、飞书等）
- ✅ API Key（OpenRouter、OpenAI、Anthropic、ElevenLabs 等）

#### 方式 2: 手动迁移（备选）

如果自动迁移失败，可以手动迁移：

##### 1. 创建配置目录

```bash
mkdir -p ~/.hermes/{memories,skills,cron,sessions,logs}
```

##### 2. 迁移模型配置

从 OpenClaw 配置文件中提取模型配置：

```json
// OpenClaw 配置示例
{
  "models": {
    "providers": {
      "bailian": {
        "baseUrl": "https://coding.dashscope.aliyuncs.com/v1",
        "apiKey": "sk-YOUR_API_KEY"
      }
    }
  }
}
```

写入 Hermes 配置：

```bash
# 编辑 ~/.hermes/.env
cat >> ~/.hermes/.env << EOF
# 模型配置（百炼）
OPENAI_API_KEY=sk-YOUR_API_KEY
OPENAI_BASE_URL=https://coding.dashscope.aliyuncs.com/v1
EOF
```

#### 迁移飞书配置

```bash
# 编辑 ~/.hermes/.env
cat >> ~/.hermes/.env << EOF
# 飞书配置
FEISHU_APP_ID=YOUR_APP_ID
FEISHU_APP_SECRET=YOUR_APP_SECRET
FEISHU_DOMAIN=feishu
FEISHU_CONNECTION_MODE=websocket
GATEWAY_ALLOW_ALL_USERS=true
EOF
```

#### 创建配置文件

```bash
cat > ~/.hermes/config.yaml << 'EOF'
# Hermes Agent 配置文件

# 模型配置
model:
  default: "qwen3.5-plus"
  provider: "custom"
  base_url: "https://coding.dashscope.aliyuncs.com/v1"
  api_key: "sk-YOUR_API_KEY"

# 终端配置
terminal:
  backend: "local"
  working_dir: "~/workspace"

# 审批配置（YOLO 模式）
approvals:
  mode: false
  timeout: 60

# 安全配置
security:
  tirith_enabled: true

# 显示配置
display:
  personality: "helpful"

# 记忆配置
memory:
  enabled: true
  max_size: 2200

# 网关配置
gateway:
  enabled: true
  port: 5001
EOF
```

### 4. 安装飞书依赖

```bash
pip install lark-oapi websockets aiohttp -q
```

**注意**：如果自动迁移已执行，此步骤可能已完成。

### 5. 启动 Hermes Gateway

```bash
cd ~/.hermes
hermes gateway run &

# 查看日志
tail -f ~/.hermes/logs/gateway.log
```

**注意**：
- 首次启动可能需要 1-2 分钟
- 如果遇到 systemd 错误，直接运行即可（不用 `systemctl`）
- 可以使用 `nohup` 后台运行：`nohup hermes gateway run > /dev/null 2>&1 &`

### 6. 验证连接

查看日志确认飞书连接成功：

```bash
tail -20 ~/.hermes/logs/gateway.log

# 期望输出：
# [Feishu] Connected in websocket mode (feishu)
# ✓ feishu connected
# Gateway running with 1 platform(s)
```

### 7. 测试消息

在飞书中向机器人发送消息：
```
hi
```

如果收到回复，说明部署成功。

---

## YOLO 模式配置

### 开启 YOLO 模式（无审批）

编辑 `~/.hermes/config.yaml`：

```yaml
approvals:
  mode: false  # false = YOLO 模式，true = 需要审批
  timeout: 60
```

重启 Gateway：

```bash
pkill -f "hermes gateway"
sleep 2
hermes gateway run &
```

### 验证 YOLO 模式

在飞书中发送：
```
执行 ls -la ~/workspace
```

如果直接执行且无审批卡片，说明 YOLO 模式已开启。

---

## 配置对比

| 配置项 | OpenClaw | Hermes |
|--------|----------|--------|
| 配置文件 | `openclaw.json` | `config.yaml` + `.env` |
| 模型配置 | `models.providers` | `model` + `OPENAI_API_KEY` |
| 飞书配置 | `channels.feishu` | `FEISHU_*` 环境变量 |
| 审批模式 | `tools.exec.ask` | `approvals.mode` |
| 记忆系统 | `MEMORY.md` + SQLite | `memories/` + `state.db` |

---

## 常见问题

### 0. 网络问题（中国大陆）

**问题**: GitHub 连接超时或失败

**解决**:
```bash
# 使用 ZIP 下载而非 git clone
cd /tmp
curl -fsSL https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip -o hermes.zip
unzip -q hermes.zip
mv hermes-agent-main ~/.hermes/hermes-agent
```

**或者使用代理**:
```bash
export https_proxy=http://your-proxy:port
git clone https://github.com/NousResearch/hermes-agent.git ~/.hermes/hermes-agent
```

### 1. GitHub 克隆失败

**问题**: `fatal: unable to access 'https://github.com/...'`

**解决**: 使用 ZIP 下载方式：
```bash
cd /tmp
curl -fsSL https://github.com/NousResearch/hermes-agent/archive/refs/heads/main.zip -o hermes.zip
unzip -q hermes.zip
mv hermes-agent-main ~/.hermes/hermes-agent
```

### 2. 飞书连接失败

**问题**: `No messaging platforms enabled`

**解决**: 检查 `.env` 配置：
```bash
cat ~/.hermes/.env | grep FEISHU
# 确认 FEISHU_APP_ID 和 FEISHU_APP_SECRET 已配置
```

### 3. 401 认证错误

**问题**: `Error code: 401 - Missing Authentication header`

**解决**: 在 `config.yaml` 中添加 `api_key`：
```yaml
model:
  default: "qwen3.5-plus"
  base_url: "https://coding.dashscope.aliyuncs.com/v1"
  api_key: "sk-YOUR_API_KEY"  # 添加这行
```

### 5. Gateway 启动失败

**问题**: `Failed to connect to bus: No medium found`

**解决**: 直接运行，不使用 systemd：
```bash
hermes gateway run &
```

### 6. 权限问题

**问题**: `Permission denied`

**解决**:
```bash
# 确保使用正确的用户
whoami

# 如果是 root，确保路径权限正确
chmod 700 ~/.hermes
chown -R $USER:$USER ~/.hermes
```

### 7. 日志查看

```bash
# 实时查看日志
tail -f ~/.hermes/logs/gateway.log

# 查看最近 50 行
tail -50 ~/.hermes/logs/gateway.log

# 查看错误日志
grep -i error ~/.hermes/logs/gateway.log
```

### 8. 配置检查

```bash
# 检查 Hermes 配置
hermes config

# 检查 .env 文件
cat ~/.hermes/.env

# 检查配置有效性
hermes config check
```

### 9. 自动迁移失败

**问题**: `hermes claw migrate` 命令失败

**解决**:
1. 确保 Hermes 已正确安装
2. 检查 OpenClaw 配置路径是否正确

---

## 🔧 配置开机自启动（重要！）

为了保证 Hermes Gateway 持续运行，建议配置开机自启动和自动恢复机制。

### Linux (systemd + cron)

#### 1️⃣ 创建 systemd 服务

```bash
# 创建服务文件
sudo tee /etc/systemd/system/hermes-gateway.service > /dev/null << 'EOF'
[Unit]
Description=Hermes Gateway Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/.hermes
ExecStart=/usr/bin/python3 /usr/local/bin/hermes gateway run
Restart=always          # 崩溃自动重启
RestartSec=10           # 重启延迟 10 秒
TimeoutStartSec=180     # 启动超时 3 分钟
TimeoutStopSec=120      # 停止超时 2 分钟

[Install]
WantedBy=multi-user.target  # 开机自启
EOF
```

#### 2️⃣ 启用并启动服务

```bash
# 重新加载 systemd 配置
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable hermes-gateway.service

# 启动服务
sudo systemctl start hermes-gateway.service

# 查看状态
systemctl status hermes-gateway.service
```

#### 3️⃣ 配置 cron 定时任务（双重保护）

```bash
# 编辑 crontab
crontab -e

# 添加以下内容：
# 每 5 分钟检查，服务停止则自动启动
*/5 * * * * systemctl is-active hermes-gateway >/dev/null || systemctl start hermes-gateway

# 每天凌晨 3 点预防性重启（防止内存泄漏）
0 3 * * * systemctl restart hermes-gateway
```

#### 4️⃣ 验证配置

```bash
# 检查服务状态
systemctl is-enabled hermes-gateway.service  # 应显示 "enabled"
systemctl is-active hermes-gateway.service   # 应显示 "active"

# 查看 Gateway 状态
cat /root/.hermes/gateway_state.json

# 查看 systemd 日志
journalctl -u hermes-gateway -f
```

### Windows (任务计划程序)

#### 1️⃣ 创建启动脚本

创建 `C:\hermes\start_gateway.bat`：

```batch
@echo off
cd /d %USERPROFILE%\.hermes\hermes-agent
hermes gateway run
```

#### 2️⃣ 创建任务计划

**方法 1: 使用 PowerShell（推荐）**

```powershell
# 以管理员身份运行 PowerShell

# 创建任务计划
$action = New-ScheduledTaskAction -Execute "C:\hermes\start_gateway.bat" -WorkingDirectory "C:\hermes"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "Hermes Gateway" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Hermes Gateway Service - Auto restart on failure"

# 启动任务
Start-ScheduledTask -TaskName "Hermes Gateway"

# 查看任务状态
Get-ScheduledTask -TaskName "Hermes Gateway" | Select-Object TaskName, State, Status
```

**方法 2: 使用图形界面**

1. 打开 **任务计划程序** (taskschd.msc)
2. 点击 **创建任务**（不是"创建基本任务"）
3. **常规** 选项卡：
   - 名称：`Hermes Gateway`
   - 勾选 **不管用户是否登录都要运行**
   - 勾选 **使用最高权限运行**
   - 配置：选择 **Windows 10/Server 2016**
4. **触发器** 选项卡：
   - 新建 → 开始任务：**启动时**
   - 勾选 **已启用**
5. **操作** 选项卡：
   - 新建 → 启动程序
   - 程序/脚本：`C:\hermes\start_gateway.bat`
   - 起始于：`C:\hermes`
6. **条件** 选项卡：
   - 取消勾选 **只有在计算机使用交流电源时才启动此任务**
7. **设置** 选项卡：
   - 勾选 **如果任务失败，重新启动每隔**：`1 分钟`
   - **尝试重新启动次数**：`3`
   - 勾选 **如果运行时间超过以下时间，停止任务**：取消勾选
8. 点击 **确定**，输入管理员密码

#### 3️⃣ 验证配置

```powershell
# 查看任务状态
Get-ScheduledTask -TaskName "Hermes Gateway" | Select-Object TaskName, State, Status, LastRunTime, NextRunTime

# 查看任务历史
Get-ScheduledTaskInfo -TaskName "Hermes Gateway"

# 手动触发测试
Start-ScheduledTask -TaskName "Hermes Gateway"
```

### macOS (launchd)

#### 1️⃣ 创建 launchd 配置文件

```bash
# 创建配置文件
cat > ~/Library/LaunchAgents/com.hermes.gateway.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.hermes.gateway</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/hermes</string>
        <string>gateway</string>
        <string>run</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/$USER/.hermes</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
        <key>Crashed</key>
        <true/>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/hermes-gateway.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/hermes-gateway-error.log</string>
</dict>
</plist>
EOF
```

#### 2️⃣ 加载并启动

```bash
# 加载配置
launchctl load ~/Library/LaunchAgents/com.hermes.gateway.plist

# 启动服务
launchctl start com.hermes.gateway

# 查看状态
launchctl list | grep hermes
```

---

## 🛡️ 保护机制对比

| 平台 | 组件 | 崩溃恢复 | 开机自启 | 健康检查 | 预防性重启 |
|------|------|---------|---------|---------|-----------|
| **Linux** | systemd | 10 秒内 | ✅ | cron 每 5 分钟 | 每天 3:00 |
| **Windows** | 任务计划 | 1 分钟内 | ✅ | ❌ | ❌ |
| **macOS** | launchd | 立即 | ✅ | KeepAlive | ❌ |

---

## 🔍 管理命令速查

### Linux

```bash
# 查看状态
systemctl status hermes-gateway

# 重启
systemctl restart hermes-gateway

# 停止
systemctl stop hermes-gateway

# 查看日志
journalctl -u hermes-gateway -f

# 查看内存
systemctl show hermes-gateway --property=MemoryCurrent
```

### Windows

```powershell
# 查看任务状态
Get-ScheduledTask -TaskName "Hermes Gateway"

# 启动任务
Start-ScheduledTask -TaskName "Hermes Gateway"

# 停止任务
Stop-ScheduledTask -TaskName "Hermes Gateway"

# 查看任务历史
Get-ScheduledTaskInfo -TaskName "Hermes Gateway"
```

### macOS

```bash
# 加载配置
launchctl load ~/Library/LaunchAgents/com.hermes.gateway.plist

# 启动服务
launchctl start com.hermes.gateway

# 停止服务
launchctl stop com.hermes.gateway

# 卸载配置
launchctl unload ~/Library/LaunchAgents/com.hermes.gateway.plist
```

---

## ✅ 验证清单

部署完成后，请检查以下项目：

- [ ] Hermes 已安装 (`hermes --version`)
- [ ] Gateway 正在运行 (`ps aux \| grep hermes`)
- [ ] 飞书已连接 (检查 `gateway_state.json`)
- [ ] 开机自启已配置 (systemd/任务计划/launchd)
- [ ] 自动恢复已启用 (Restart=always 或 KeepAlive)
- [ ] 日志正常 (无 error/critical 错误)
- [ ] 内存使用正常 (<500MB)

---

## 📖 相关文档

- **Hermes 官方文档**: https://github.com/NousResearch/hermes-agent
- **OpenClaw 文档**: https://docs.openclaw.ai
- **systemd 配置**: `/etc/systemd/system/hermes-gateway.service`
- **配置总结**: `/workspace/projects/hermes/AUTOSTART_SUMMARY.md`
3. 使用 `--dry-run` 先预览
4. 如果仍失败，使用手动迁移方式

---

## 常用命令

### Gateway 管理

```bash
# 查看状态
hermes gateway status

# 启动
cd ~/.hermes && hermes gateway run &

# 停止
pkill -f "hermes gateway"

# 重启
pkill -f "hermes gateway" && sleep 2 && hermes gateway run &

# 查看日志
tail -f ~/.hermes/logs/gateway.log
```

### 配置管理

```bash
# 查看配置
hermes config

# 编辑配置
hermes config edit

# 设置配置项
hermes config set <key> <value>

# 检查配置
hermes config check
```

### 迁移命令

```bash
# 预览迁移
hermes claw migrate --source <openclaw-path> --dry-run

# 执行迁移
hermes claw migrate --source <openclaw-path> --migrate-secrets -y

# 清理
hermes claw cleanup
```

---

## 安全检查清单

部署完成后，检查以下项目：

- [ ] Hermes 版本 >= 0.7.0
- [ ] 飞书连接成功（查看日志）
- [ ] 模型配置正确（`hermes config`）
- [ ] YOLO 模式已开启（`approvals.mode: false`）
- [ ] 能够正常回复消息
- [ ] 命令执行无需审批
- [ ] 日志无错误信息

---

## 参考链接

- [Hermes Agent GitHub](https://github.com/NousResearch/hermes-agent)
- [Hermes 文档](https://hermesagent.agency/)
- [OpenClaw 文档](https://docs.openclaw.ai/)

---

## 版本历史

- **v1.0.0** (2026-04-05): 初始版本，包含完整部署流程和 YOLO 模式配置
