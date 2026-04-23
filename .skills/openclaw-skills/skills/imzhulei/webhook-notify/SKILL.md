---
name: webhook-notify
description: 通用Webhook通知工具，支持钉钉、企业微信、飞书、Slack、Discord、Teams、Telegram、自定义HTTP等多种平台。提供统一接口、自动平台识别、配置管理、模板系统、重试机制等高级功能。适用于告警通知、自动化触发、系统监控、CI/CD通知等场景。
metadata: {"clawdbot":{"emoji":"🔔","requires":{"anyBins":["curl","powershell"]},"os":["linux","darwin","win32"]}}
---

# Webhook 通知工具

一个统一的、跨平台的 webhook 发送工具，支持多种主流平台，提供智能平台识别、统一接口、配置管理和模板系统。

## 核心特性

✅ **统一接口** - 一个函数调用所有平台  
✅ **自动识别** - 根据 URL 自动识别平台  
✅ **跨平台** - 支持 Windows、Linux、macOS  
✅ **配置管理** - 支持环境变量、配置文件  
✅ **模板系统** - 内置常用消息模板  
✅ **重试机制** - 自动重试失败请求  
✅ **错误处理** - 详细的错误信息和调试支持  

## 支持的平台

| 平台 | 消息类型 | 自动识别 | 特殊功能 |
|------|---------|---------|---------|
| **钉钉** | Text/Markdown/Link/ActionCard | ✅ | @用户、@所有人、按钮交互 |
| **企业微信** | Text/Markdown/Image/File/News | ✅ | 图文消息、@用户 |
| **飞书** | Text/Post/Interactive/ShareCard | ✅ | 富文本、卡片、按钮 |
| **Slack** | Text/Block/Attachment | ✅ | 格式化消息、按钮 |
| **Discord** | Text/Embed | ✅ | 富文本嵌入、颜色 |
| **Teams** | Text/AdaptiveCard | ✅ | 自适应卡片 |
| **Telegram** | Text/Markdown/HTML | ✅ | 格式化文本、按钮 |
| **自定义HTTP** | JSON/Form-Data/Raw | ✅ | 完全自定义请求 |

## 快速开始

### 1. 统一接口（推荐）

```powershell
# 自动识别平台并发送
Send-Webhook -Url "https://oapi.dingtalk.com/robot/send?access_token=..." -Message "告警信息"
Send-Webhook -Url "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..." -Message "告警信息"
Send-Webhook -Url "https://hooks.slack.com/services/..." -Message "告警信息"
```

### 2. 平台特定函数

```powershell
# 钉钉
Send-WebhookDingTalk -WebhookUrl $url -Message "告警" -IsAtAll $true

# 企业微信
Send-WebhookWeCom -WebhookUrl $url -Message "告警" -AtUsers @("13800138000")

# 飞书
Send-WebhookFeishu -WebhookUrl $url -Message "告警"

# Slack
Send-WebhookSlack -WebhookUrl $url -Message "System Alert"

# Discord
Send-WebhookDiscord -WebhookUrl $url -Message "Alert" -Color "red"

# Telegram
Send-WebhookTelegram -WebhookUrl $url -Message "Alert" -ParseMode "Markdown"
```

### 3. 使用模板

```powershell
# 系统告警模板
Send-WebhookTemplate -Template "system-alert" -Params @{
    Severity = "critical"
    Component = "CPU"
    Details = "使用率: 95%"
    WebhookUrl = $env:DINGTALK_WEBHOOK
}

# 部署通知模板
Send-WebhookTemplate -Template "deploy-success" -Params @{
    Project = "MyApp"
    Version = "v1.2.3"
    Environment = "production"
    WebhookUrl = $env:DINGTALK_WEBHOOK
}
```

---

## 安装与配置

### 1. 安装函数库

```powershell
# 克隆或下载函数库
git clone https://github.com/your-repo/webhook-notify.git
# 或直接复制 webhook-functions.ps1 到你的项目

# 在脚本中引用
. "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"
```

### 2. 配置环境变量

**Windows PowerShell**:
```powershell
# 临时设置（当前会话）
$env:DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=..."
$env:WECOM_WEBHOOK = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
$env:FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/..."
$env:SLACK_WEBHOOK = "https://hooks.slack.com/services/..."
$env:DISCORD_WEBHOOK = "https://discord.com/api/webhooks/..."
$env:TELEGRAM_WEBHOOK = "https://api.telegram.org/botTOKEN/sendMessage"

# 永久设置（系统环境变量）
[System.Environment]::SetEnvironmentVariable('DINGTALK_WEBHOOK', 'https://...', 'User')
```

**Linux/Mac (bash/zsh)**:
```bash
# ~/.bashrc 或 ~/.zshrc
export DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=..."
export WECOM_WEBHOOK="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=..."
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/..."
export SLACK_WEBHOOK="https://hooks.slack.com/services/..."
export DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
export TELEGRAM_WEBHOOK="https://api.telegram.org/botTOKEN/sendMessage"
```

### 3. 配置文件

创建 `webhook-config.json`:

```json
{
  "platforms": {
    "dingtalk": {
      "default": "${DINGTALK_WEBHOOK}",
      "monitoring": {
        "url": "${DINGTALK_MONITORING_WEBHOOK}",
        "keyword": "【openclaw】"
      },
      "alerts": {
        "url": "${DINGTALK_ALERTS_WEBHOOK}",
        "atAll": true
      }
    },
    "wecom": {
      "devTeam": "${WECOM_DEV_TEAM_WEBHOOK}",
      "alerts": "${WECOM_ALERTS_WEBHOOK}"
    },
    "feishu": {
      "default": "${FEISHU_WEBHOOK}"
    },
    "slack": {
      "alerts": "${SLACK_WEBHOOK}",
      "dev": "${SLACK_DEV_WEBHOOK}"
    },
    "discord": {
      "alerts": "${DISCORD_WEBHOOK}"
    },
    "telegram": {
      "default": "${TELEGRAM_WEBHOOK}"
    }
  },
  "templates": {
    "system-alert": {
      "title": "系统告警",
      "severity": "critical",
      "includeTimestamp": true
    },
    "deploy-success": {
      "title": "部署成功",
      "emoji": "✅"
    }
  },
  "retry": {
    "maxRetries": 3,
    "retryDelay": 2
  }
}
```

**使用配置**:
```powershell
$config = Get-WebhookConfig -Path "webhook-config.json"
Send-Webhook -Url $config.platforms.dingtalk.monitoring.url -Message "告警"
```

---

## 函数参考

### Send-Webhook（统一接口）

自动识别平台并发送消息。

**参数**:
- `Url` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型（可选，平台特定）
- `Title` (string): 消息标题（可选）
- `Content` (string): 富文本内容（可选）
- `Params` (hashtable): 平台特定参数（可选）
- `Retry` (int): 重试次数，默认 3
- `Timeout` (int): 超时秒数，默认 30
- `Debug` (bool): 启用调试输出

**示例**:

```powershell
# 自动识别平台
Send-Webhook -Url $env:DINGTALK_WEBHOOK -Message "告警信息"
Send-Webhook -Url $env:WECOM_WEBHOOK -Message "告警信息"
Send-Webhook -Url $env:SLACK_WEBHOOK -Message "Alert"

# 带参数
Send-Webhook -Url $env:DINGTALK_WEBHOOK -Message "告警" -Params @{
    IsAtAll = $true
    Keyword = "openclaw"
}

# 使用配置
Send-Webhook -Url $config.platforms.dingtalk.monitoring.url -Message "告警" -Params @{
    Keyword = $config.platforms.dingtalk.monitoring.keyword
}
```

---

### Send-WebhookDingTalk

发送钉钉webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`markdown`|`actionCard`，默认 `text`
- `Title` (string): 消息标题
- `Content` (string): markdown内容
- `Text` (string): actionCard的文本内容
- `Buttons` (array): 按钮列表
- `AtMobiles` (array): @的手机号列表
- `AtUserIds` (array): @的userId列表
- `IsAtAll` (bool): 是否@所有人
- `Keyword` (string): 添加关键字
- `Retry` (int): 重试次数
- `Timeout` (int): 超时秒数

**示例**:

```powershell
# 文本消息 @所有人
Send-WebhookDingTalk -WebhookUrl $url -Message "【openclaw】告警" -IsAtAll $true

# Markdown @指定用户
Send-WebhookDingTalk -WebhookUrl $url -Type markdown -Title "告警" -Content "系统异常" -AtMobiles @("13800138000")

# ActionCard带按钮
Send-WebhookDingTalk -WebhookUrl $url -Type actionCard -Title "告警" `
    -Text "CPU使用率：95%" `
    -Buttons @(@{title="查看详情";url="https://example.com"}, @{title="忽略";url="https://example.com/ignore"})
```

---

### Send-WebhookWeCom

发送企业微信webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`markdown`|`image`|`news`|`file`
- `Content` (string): markdown内容
- `MdId` (string): 媒体ID
- `Articles` (array): 图文消息列表
- `AtUsers` (array): @的手机号列表
- `IsAtAll` (bool): 是否@所有人
- `Retry` (int): 重试次数
- `Timeout` (int): 超时秒数

**示例**:

```powershell
# 文本消息
Send-WebhookWeCom -WebhookUrl $url -Message "系统告警"

# Markdown
Send-WebhookWeCom -WebhookUrl $url -Type markdown -Content "**标题**`n内容"

# 图文消息
Send-WebhookWeCom -WebhookUrl $url -Type news -Articles @(
    @{title="标题";description="描述";url="http://example.com";picurl="http://example.com/img.jpg"}
)
```

---

### Send-WebhookFeishu

发送飞书webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`post`|`interactive`|`shareCard`
- `Title` (string): 卡片标题
- `Content` (array): 富文本内容元素
- `Elements` (array): 交互元素
- `AtUsers` (array): @的open_id列表
- `Retry` (int): 重试次数
- `Timeout` (int): 超时秒数

**示例**:

```powershell
# 文本消息
Send-WebhookFeishu -WebhookUrl $url -Message "【openclaw】告警"

# 富文本卡片
Send-WebhookFeishu -WebhookUrl $url -Type post -Title "系统告警" -Content @(
    @{tag="text";text="CPU使用率：95%"}
)

# 交互卡片
Send-WebhookFeishu -WebhookUrl $url -Type interactive -Title "确认操作" `
    -Elements @(@{tag="button";text=@{tag="plain_text";content="确认"};type="primary";url="https://example.com"})
```

---

### Send-WebhookSlack

发送Slack webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Type` (string): 消息类型 `text`|`block`
- `Blocks` (array): Block Kit块
- `Attachments` (array): 附件列表
- `Channel` (string): 目标频道
- `Username` (string): 发送者名称
- `IconEmoji` (string): 图标emoji
- `IconUrl` (string): 图标URL
- `Retry` (int): 重试次数
- `Timeout` (int): 超时秒数

**示例**:

```powershell
# 简单文本
Send-WebhookSlack -WebhookUrl $url -Message "System Alert"

# Block Kit
Send-WebhookSlack -WebhookUrl $url -Type block -Blocks @(
    @{type="section";text=@{type="mrkdwn";text="*Alert*`nCPU: 95%"}},
    @{type="actions";elements=@(@{type="button";text=@{type="plain_text";text="View"};url="https://example.com"})}
)
```

---

### Send-WebhookDiscord

发送Discord webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `Username` (string): 发送者名称
- `AvatarUrl` (string): 头像URL
- `Embeds` (array): 嵌入消息列表
- `Color` (string): 颜色（decimal或颜色名）
- `Title` (string): 嵌入标题
- `Description` (string): 嵌入描述
- `Url` (string): 嵌入URL
- `Fields` (array): 字段列表
- `Footer` (string): 页脚文本
- `Timestamp` (bool): 是否包含时间戳
- `Retry` (int): 重试次数
- `Timeout` (int): 超时秒数

**示例**:

```powershell
# 简单文本
Send-WebhookDiscord -WebhookUrl $url -Message "System Alert"

# 嵌入消息
Send-WebhookDiscord -WebhookUrl $url -Username "Monitor Bot" -Embeds @(@{
    title = "系统告警"
    description = "CPU使用率超过90%"
    color = 16711680  # 红色
    fields = @(
        @{name="组件";value="CPU";inline=$true},
        @{name="当前值";value="95%";inline=$true}
    )
    timestamp = $true
})
```

---

### Send-WebhookTelegram

发送Telegram webhook消息。

**参数**:
- `WebhookUrl` (string): webhook地址
- `Message` (string): 文本消息内容
- `ChatId` (string): 聊天ID（覆盖默认）
- `ParseMode` (string): 解析模式 `Markdown`|`HTML`|`MarkdownV2`
- `DisableNotification` (bool): 禁用通知
- `ReplyMarkup` (hashtable): 回复键盘
- `Retry` (int): 重试次数
- `Timeout` (int): 超时秒数

**示例**:

```powershell
# 简单文本
Send-WebhookTelegram -WebhookUrl $url -Message "System Alert"

# Markdown格式
Send-WebhookTelegram -WebhookUrl $url -Message "*Alert*`nCPU: 95%" -ParseMode "Markdown"

# HTML格式
Send-WebhookTelegram -WebhookUrl $url -Message "<b>Alert</b>`nCPU: 95%" -ParseMode "HTML"
```

---

### Send-WebhookCustom

发送自定义HTTP请求。

**参数**:
- `Url` (string): 目标URL
- `Method` (string): HTTP方法 `GET`|`POST`|`PUT`|`DELETE`
- `Body` (object 或 string): 请求体
- `ContentType` (string): Content-Type
- `Headers` (hashtable): 请求头
- `Timeout` (int): 超时秒数
- `UseBasicAuth` (bool): 使用基础认证
- `Username` (string): 用户名
- `Password` (string): 密码
- `Retry` (int): 重试次数

**示例**:

```powershell
# JSON POST
Send-WebhookCustom -Url "https://api.example.com/webhook" `
    -Body @{event="alert";severity="high"} `
    -Headers @{"X-API-Key"="your-key"}

# 自定义Header
Send-WebhookCustom -Url "https://..." `
    -Method PUT `
    -Body "raw string body" `
    -ContentType "text/plain" `
    -Headers @{"Authorization"="Bearer token"}
```

---

### Send-WebhookTemplate

使用模板发送消息。

**参数**:
- `Template` (string): 模板名称
- `Params` (hashtable): 模板参数
- `WebhookUrl` (string): webhook地址（可选，使用配置中的默认值）
- `Platform` (string): 平台名称（可选，自动识别）

**内置模板**:
- `system-alert`: 系统告警
- `deploy-success`: 部署成功
- `deploy-failed`: 部署失败
- `es-alert`: Elasticsearch告警
- `custom`: 自定义模板

**示例**:

```powershell
# 使用内置模板
Send-WebhookTemplate -Template "system-alert" -Params @{
    Severity = "critical"
    Component = "CPU"
    Details = "使用率: 95%"
    WebhookUrl = $env:DINGTALK_WEBHOOK
}

# 使用自定义模板
Send-WebhookTemplate -Template "custom" -Params @{
    Title = "自定义告警"
    Message = "这是自定义消息"
    WebhookUrl = $env:DINGTALK_WEBHOOK
}
```

---

## 高级用法

### 1. 平台自动识别

```powershell
# 自动识别平台
function Send-Webhook {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Url,
        
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [hashtable]$Params = @{},
        [int]$Retry = 3,
        [int]$Timeout = 30,
        [bool]$Debug = $false
    )
    
    # 自动识别平台
    $platform = Get-WebhookPlatform -Url $Url
    
    if ($Debug) {
        Write-Host "识别到平台: $platform"
    }
    
    # 根据平台调用对应函数
    switch ($platform) {
        'DingTalk' {
            Send-WebhookDingTalk -WebhookUrl $Url -Message $Message @Params -Retry $Retry -Timeout $Timeout
        }
        'WeCom' {
            Send-WebhookWeCom -WebhookUrl $Url -Message $Message @Params -Retry $Retry -Timeout $Timeout
        }
        'Feishu' {
            Send-WebhookFeishu -WebhookUrl $Url -Message $Message @Params -Retry $Retry -Timeout $Timeout
        }
        'Slack' {
            Send-WebhookSlack -WebhookUrl $Url -Message $Message @Params -Retry $Retry -Timeout $Timeout
        }
        'Discord' {
            Send-WebhookDiscord -WebhookUrl $Url -Message $Message @Params -Retry $Retry -Timeout $Timeout
        }
        'Telegram' {
            Send-WebhookTelegram -WebhookUrl $Url -Message $Message @Params -Retry $Retry -Timeout $Timeout
        }
        default {
            Send-WebhookCustom -Url $Url -Body @{message=$Message} @Params -Retry $Retry -Timeout $Timeout
        }
    }
}

# 平台识别函数
function Get-WebhookPlatform {
    param([string]$Url)
    
    if ($Url -match "dingtalk\.com") { return 'DingTalk' }
    if ($Url -match "qyapi\.weixin\.qq\.com") { return 'WeCom' }
    if ($Url -match "feishu\.cn|larksuite\.com") { return 'Feishu' }
    if ($Url -match "slack\.com") { return 'Slack' }
    if ($Url -match "discord\.com") { return 'Discord' }
    if ($Url -match "telegram\.org") { return 'Telegram' }
    
    return 'Custom'
}
```

---

### 2. 配置管理

```powershell
# 加载配置
function Get-WebhookConfig {
    param(
        [string]$Path = "webhook-config.json"
    )
    
    if (-not (Test-Path $Path)) {
        Write-Warning "配置文件不存在: $Path"
        return @{}
    }
    
    $config = Get-Content $Path -Raw | ConvertFrom-Json
    
    # 展开环境变量
    $configJson = $config | ConvertTo-Json -Depth 10
    $configJson = [regex]::Replace($configJson, '\$\{([^}]+)\}', {
        param($match)
        $envName = $match.Groups[1].Value
        [System.Environment]::GetEnvironmentVariable($envName)
    })
    
    return $configJson | ConvertFrom-Json
}

# 使用配置
$config = Get-WebhookConfig
Send-Webhook -Url $config.platforms.dingtalk.monitoring.url -Message "告警"
```

---

### 3. 模板系统

```powershell
# 模板定义
$Script:WebhookTemplates = @{
    'system-alert' = @{
        DingTalk = {
            param($params)
            @{
                Type = 'markdown'
                Title = "🚨 系统告警 - $($params.Severity.ToUpper())"
                Content = @"
## 组件: $($params.Component)

**当前值**: $($params.CurrentValue)
**阈值**: $($params.Threshold)
**时间**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

**详情**:
$($params.Details)

请及时处理！
"@
                IsAtAll = $true
            }
        }
        Slack = {
            param($params)
            @{
                Type = 'block'
                Blocks = @(
                    @{type="header";text=@{type="plain_text";text="🚨 System Alert - $($params.Severance.ToUpper())"}},
                    @{type="section";text=@{type="mrkdwn";text="*Component*: $($params.Component)`n*Current*: $($params.CurrentValue)`n*Threshold*: $($params.Threshold)"}},
                    @{type="section";text=@{type="mrkdwn";text="*Details*:`n$($params.Details)"}},
                    @{type="context";elements=@(@{type="mrkdwn";text="$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"})}
                )
            }
        }
    }
    'deploy-success' = @{
        DingTalk = {
            param($params)
            @{
                Type = 'actionCard'
                Title = "✅ 部署成功"
                Text = @"
项目: $($params.Project)
版本: $($params.Version)
环境: $($params.Environment)
时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@
                Buttons = @(
                    @{title="查看部署";url=$params.Url},
                    @{title="回滚";url="$($params.Url)/rollback"}
                )
            }
        }
    }
}

# 使用模板
function Send-WebhookTemplate {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Template,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Params,
        
        [string]$WebhookUrl,
        [string]$Platform
    )
    
    # 自动识别平台
    if (-not $Platform) {
        $Platform = Get-WebhookPlatform -Url $WebhookUrl
    }
    
    # 获取模板
    $template = $Script:WebhookTemplates[$Template]
    if (-not $template) {
        throw "模板不存在: $Template"
    }
    
    $platformTemplate = $template[$Platform]
    if (-not $platformTemplate) {
        throw "平台 $Platform 不支持模板 $Template"
    }
    
    # 生成消息参数
    $messageParams = & $platformTemplate $Params
    
    # 发送消息
    switch ($Platform) {
        'DingTalk' {
            Send-WebhookDingTalk -WebhookUrl $WebhookUrl @messageParams
        }
        'Slack' {
            Send-WebhookSlack -WebhookUrl $WebhookUrl @messageParams
        }
        # ... 其他平台
    }
}
```

---

### 4. 重试机制

```powershell
# 带重试的发送函数
function Send-WebhookWithRetry {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Url,
        
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [int]$MaxRetries = 3,
        [int]$RetryDelay = 2,
        [hashtable]$Params = @{},
        [int]$Timeout = 30
    )
    
    $attempt = 0
    $lastError = $null
    
    while ($attempt -lt $MaxRetries) {
        $attempt++
        
        try {
            Send-Webhook -Url $Url -Message $Message -Params $Params -Timeout $Timeout
            Write-Host "✅ 发送成功 (尝试 $attempt/$MaxRetries)"
            return $true
        }
        catch {
            $lastError = $_
            Write-Host "❌ 尝试 $attempt/$MaxRetries 失败: $($_.Exception.Message)"
            
            if ($attempt -lt $MaxRetries) {
                Write-Host "⏳ 等待 $RetryDelay 秒后重试..."
                Start-Sleep -Seconds $RetryDelay
            }
        }
    }
    
    Write-Host "❌ 所有尝试失败"
    throw $lastError
}

# 使用重试
Send-WebhookWithRetry -Url $env:DINGTALK_WEBHOOK -Message "测试消息" -MaxRetries 3
```

---

### 5. 批量发送

```powershell
# 发送到多个webhook
function Send-WebhookBatch {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$true)]
        [array]$Webhooks,
        
        [hashtable]$Params = @{}
    )
    
    $results = @()
    
    foreach ($webhook in $Webhooks) {
        $url = if ($webhook -is [string]) { $webhook } else { $webhook.url }
        $platformParams = if ($webhook -is [hashtable]) { $webhook.params } else { @{} }
        
        try {
            Send-Webhook -Url $url -Message $Message -Params ($Params + $platformParams)
            $results += @{url=$url;status="success"}
        }
        catch {
            $results += @{url=$url;status="failed";error=$_.Exception.Message}
        }
    }
    
    return $results
}

# 使用批量发送
$webhooks = @(
    $env:DINGTALK_WEBHOOK,
    $env:WECOM_WEBHOOK,
    $env:SLACK_WEBHOOK
)

$results = Send-WebhookBatch -Message "批量测试消息" -Webhooks $webhooks
$results | Format-Table
```

---

### 6. Webhook测试工具

```powershell
# 测试webhook连接
function Test-Webhook {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Url,
        
        [ValidateSet('DingTalk', 'WeCom', 'Feishu', 'Slack', 'Discord', 'Telegram', 'Custom')]
        [string]$Platform,
        
        [int]$Timeout = 30
    )
    
    $platform = if ($Platform) { $Platform } else { Get-WebhookPlatform -Url $Url }
    
    $testMessage = @"
🔔 Webhook测试

- 平台: $platform
- 时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- 状态: ✅ 测试成功

如果你看到这条消息，说明webhook配置正确！
"@
    
    Write-Host "正在测试 $platform webhook..."
    Write-Host "URL: $Url"
    
    try {
        Send-Webhook -Url $Url -Message $testMessage -Timeout $Timeout
        Write-Host "✅ 测试成功！"
        return $true
    }
    catch {
        Write-Host "❌ 测试失败: $($_.Exception.Message)"
        return $false
    }
}

# 测试所有配置的webhook
function Test-AllWebhooks {
    param(
        [string]$ConfigPath = "webhook-config.json"
    )
    
    $config = Get-WebhookConfig -Path $ConfigPath
    
    foreach ($platform in $config.platforms.PSObject.Properties) {
        foreach ($webhook in $platform.Value.PSObject.Properties) {
            $url = $webhook.Value.url
            if ($url) {
                Write-Host "`n测试 $($platform.Name) - $($webhook.Name)..."
                Test-Webhook -Url $url -Platform $platform.Name
            }
        }
    }
}

# 使用
Test-Webhook -Url $env:DINGTALK_WEBHOOK -Platform DingTalk
Test-AllWebhooks
```

---

## 完整示例

### 示例1: 系统监控告警

```powershell
# 系统资源监控告警
function Send-SystemAlert {
    param(
        [string]$Severity,
        [string]$Component,
        [string]$CurrentValue,
        [string]$Threshold,
        [string]$Details,
        [string]$WebhookUrl = $env:DINGTALK_WEBHOOK
    )
    
    $status = switch ($Severity) {
        "critical" { "🚨 严重" }
        "warning"  { "⚠️ 警告" }
        "info"     { "ℹ️ 信息" }
        default   { "📌 提示" }
    }
    
    $message = @"
【openclaw】$status | $Component 异常

- 当前值: $CurrentValue
- 阈值: $Threshold
- 时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

**详情**:
$Details

请及时处理！
"@
    
    Send-WebhookWithRetry -Url $WebhookUrl -Message $message -MaxRetries 3
}

# 使用
Send-SystemAlert -Severity "critical" -Component "CPU" -CurrentValue "95%" -Threshold "85%" -Details "持续高CPU使用率"
Send-SystemAlert -Severity "warning" -Component "内存" -CurrentValue "14.5/16 GB" -Threshold "90%" -Details "内存使用率接近阈值"
```

---

### 示例2: 部署通知

```powershell
# 部署完成通知
function Send-DeployNotification {
    param(
        [string]$Project,
        [string]$Version,
        [string]$Environment,
        [string]$Url,
        [string]$Status = "success",
        [string]$WebhookUrl = $env:DINGTALK_WEBHOOK
    )
    
    $emoji = switch ($Status) {
        "success" { "✅" }
        "failed"  { "❌" }
        default   { "🔄" }
    }
    
    $title = "$emoji 部署$($Status -eq 'success' ? '成功' : '失败')"
    
    Send-WebhookDingTalk -WebhookUrl $WebhookUrl `
        -Type actionCard `
        -Title $title `
        -Text @"
项目: $Project
版本: $Version
环境: $Environment
时间: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@ `
        -Buttons @(
            @{title="查看部署";url=$Url},
            @{title="查看日志";url="$Url/logs"}
        )
}

# 使用
Send-DeployNotification -Project "MyApp" -Version "v1.2.3" -Environment "production" -Url "https://deploy.example.com"
Send-DeployNotification -Project "MyApp" -Version "v1.2.4" -Environment "staging" -Status "failed" -Url "https://deploy.example.com"
```

---

### 示例3: Elasticsearch 异常告警

```powershell
# ES 日志监控告警
function Send-ESAlert {
    param(
        [hashtable]$Analysis,
        [string]$WebhookUrl = $env:DINGTALK_WEBHOOK
    )
    
    if (-not $Analysis['alert']) {
        return
    }
    
    $content = @"
📊 异常总数: $($Analysis['total']) 条

## 受影响设备TOP5
$($Analysis['hostname_stats'].GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value) 条" } | Out-String)

## 异常类型TOP5  
$($Analysis['brief_stats'].GetEnumerator() | ForEach-Object { "$($_.Key): $($_.Value) 条" } | Out-String)

## 最新日志
$($Analysis['recent_logs'] | ForEach-Object { "$($_.timestamp.Substring(11,8)) [$($_.hostname))] $($_.brief)`n$($_.message)`n" } | Out-String)
"@
    
    Send-WebhookDingTalk -WebhookUrl $WebhookUrl `
        -Type markdown `
        -Title "[openclaw] ES异常告警" `
        -Content $content `
        -IsAtAll $true
}

# 使用
$analysis = @{
    alert = $true
    total = 106
    hostname_stats = @{
        "server1" = 45
        "server2" = 32
        "server3" = 18
        "server4" = 8
        "server5" = 3
    }
    brief_stats = @{
        "CPU high" = 50
        "Memory low" = 30
        "Disk full" = 15
        "Network error" = 8
        "Service down" = 3
    }
    recent_logs = @(
        @{timestamp="2026-04-13 15:00:00";hostname="server1";brief="CPU high";message="CPU usage: 95%"}
        @{timestamp="2026-04-13 15:00:05";hostname="server2";brief="Memory low";message="Memory: 95%"}
    )
}

Send-ESAlert -Analysis $analysis
```

---

### 示例4: 多平台告警

```powershell
# 发送到多个平台
function Send-MultiPlatformAlert {
    param(
        [string]$Message,
        [hashtable]$Platforms = @{}
    )
    
    $results = @()
    
    # 钉钉
    if ($Platforms.DingTalk -or $env:DINGTALK_WEBHOOK) {
        $url = if ($Platforms.DingTalk) { $Platforms.DingTalk } else { $env:DINGTALK_WEBHOOK }
        try {
            Send-WebhookDingTalk -WebhookUrl $url -Message $Message
            $results += @{platform="DingTalk";status="success"}
        }
        catch {
            $results += @{platform="DingTalk";status="failed";error=$_.Exception.Message}
        }
    }
    
    # 企业微信
    if ($Platforms.WeCom -or $env:WECOM_WEBHOOK) {
        $url = if ($Platforms.WeCom) { $Platforms.WeCom } else { $env:WECOM_WEBHOOK }
        try {
            Send-WebhookWeCom -WebhookUrl $url -Message $Message
            $results += @{platform="WeCom";status="success"}
        }
        catch {
            $results += @{platform="WeCom";status="failed";error=$_.Exception.Message}
        }
    }
    
    # Slack
    if ($Platforms.Slack -or $env:SLACK_WEBHOOK) {
        $url = if ($Platforms.Slack) { $Platforms.Slack } else { $env:SLACK_WEBHOOK }
        try {
            Send-WebhookSlack -WebhookUrl $url -Message $Message
            $results += @{platform="Slack";status="success"}
        }
        catch {
            $results += @{platform="Slack";status="failed";error=$_.Exception.Message}
        }
    }
    
    return $results
}

# 使用
$results = Send-MultiPlatformAlert -Message "🚨 系统告警" -Platforms @{
    DingTalk = $env:DINGTALK_WEBHOOK
    WeCom = $env:WECOM_WEBHOOK
    Slack = $env:SLACK_WEBHOOK
}

$results | Format-Table
```

---

## 错误处理与调试

### 常见错误

#### 错误1: 关键字缺失

**错误信息**: 钉钉: `{"errcode": 310000, "errmsg": "keywords not in content"}`

**解决**:
```powershell
# 确保消息包含关键字
Send-WebhookDingTalk -WebhookUrl $url -Message "【openclaw】告警" -Keyword "openclaw"
```

---

#### 错误2: 超时

**错误信息**: 请求超时

**解决**:
```powershell
# 增加超时时间
Send-Webhook -Url $url -Message "测试" -Timeout 60
```

---

#### 错误3: IP限制

**错误信息**: `{"errcode": 310000, "errmsg": "IP not in whitelist"}`

**解决**:
在钉钉机器人设置中添加服务器IP到白名单。

---

#### 错误4: JSON格式错误

**错误信息**: `{"errcode": 40035, "errmsg": "不合法的参数"}`

**解决**:
```powershell
# 启用调试模式查看发送的JSON
Send-Webhook -Url $url -Message "测试" -Debug $true
```

---

### 调试模式

```powershell
# 启用调试输出
$env:WEBHOOK_DEBUG = $true

# 或在函数中启用
Send-Webhook -Url $url -Message "测试" -Debug $true
```

---

## 安全最佳实践

### 1. 环境变量存储敏感信息

```powershell
# 不要在脚本中硬编码webhook URL
# ❌ 错误
$webhook = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"

# ✅ 正确
$webhook = $env:DINGTALK_WEBHOOK
```

---

### 2. 使用配置文件

```powershell
# webhook-config.json
{
  "platforms": {
    "dingtalk": {
      "default": "${DINGTALK_WEBHOOK}"
    }
  }
}
```

---

### 3. 签名验证（企业微信）

```powershell
function Get-WeComSignature {
    param(
        [string]$Content,
        [string]$Key
    )
    
    $hmacsha = New-Object System.Security.Cryptography.HMACSHA256
    $hmacsha.key = [Text.Encoding]::UTF8.GetBytes($Key)
    $signature = $hmacsha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Content))
    return [System.BitConverter]::ToString($signature).Replace('-', '').ToLower()
}

# 使用签名
$timestamp = [int][double]::Parse((Get-Date -UFormat %s))
$sign = Get-WeComSignature -Content $timestamp -Key $env:WECOM_KEY
$webhook = "$env:WECOM_WEBHOOK&timestamp=$timestamp&sign=$sign"
```

---

### 4. 限制IP白名单

在钉钉/企业微信机器人设置中，只允许受信任的IP地址访问webhook。

---

## 性能优化

### 1. 批量发送优化

```powershell
# 使用并行发送
function Send-WebhookParallel {
    param(
        [array]$Webhooks,
        [string]$Message
    )
    
    $jobs = @()
    
    foreach ($webhook in $Webhooks) {
        $job = Start-Job -ScriptBlock {
            param($url, $msg)
            . "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"
            Send-Webhook -Url $url -Message $msg
        } -ArgumentList $webhook, $Message
        
        $jobs += $job
    }
    
    # 等待所有任务完成
    $jobs | Wait-Job | Out-Null
    
    # 获取结果
    $results = $jobs | Receive-Job
    
    # 清理任务
    $jobs | Remove-Job
    
    return $results
}
```

---

### 2. 缓存配置

```powershell
# 缓存配置文件
$Script:WebhookConfigCache = @{}

function Get-WebhookConfig {
    param([string]$Path = "webhook-config.json")
    
    if ($Script:WebhookConfigCache.ContainsKey($Path)) {
        return $Script:WebhookConfigCache[$Path]
    }
    
    $config = Load-WebhookConfig -Path $Path
    $Script:WebhookConfigCache[$Path] = $config
    
    return $config
}
```

---

## 配置文件位置

将 webhook 函数库保存为：
- **Windows**: `E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1`
- **Linux/Mac**: `~/.local/share/webhook-notify/webhook-functions.ps1`

**引用方式**:
```powershell
. "E:\devdir\clawd\skills\webhook-notify\webhook-functions.ps1"
```

---

## 版本历史

- **v2.0** (2026-04-13): 重大更新
  - 新增统一接口 `Send-Webhook`
  - 新增自动平台识别
  - 新增 Discord、Telegram 支持
  - 新增模板系统
  - 新增配置管理
  - 新增重试机制
  - 改进错误处理和调试支持
  
- **v1.0** (2026-03-19): 初始版本
  - 支持钉钉、企业微信、飞书、Slack
  - 基础webhook发送功能

---

## 技术支持

如有问题或建议，请检查：
1. Webhook URL配置是否正确
2. 网络连接是否正常（防火墙/代理）
3. 消息格式是否符合平台要求
4. 关键字/签名等安全配置是否正确
5. 启用调试模式查看详细信息

**调试步骤**:
```powershell
# 1. 测试webhook连接
Test-Webhook -Url $env:DINGTALK_WEBHOOK -Platform DingTalk

# 2. 启用调试模式
Send-Webhook -Url $env:DINGTALK_WEBHOOK -Message "测试" -Debug $true

# 3. 查看详细错误
try {
    Send-Webhook -Url $env:DINGTALK_WEBHOOK -Message "测试"
} catch {
    $_ | Format-List *
}
```

---

## 许可证

MIT License
