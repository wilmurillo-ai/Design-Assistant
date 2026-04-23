---
name: socialepoch-wa-scrm
description: 官方原生对接 SocialEpoch 全域 WhatsApp SCRM 开放API，深度适配企业级海外营销与客服场景。全量覆盖WhatsApp账号管理、在线状态监控、客户运营、用户画像、聊天记录查询、WebHook回调推送，支持文字/图片/音频/视频/文件/名片/名片超链/分流超链全类型消息单发与批量群发，内置自动签名、智能依赖适配、免环境配置，一键快速调用，稳定高效赋能海外私域与自动化运营。
version: 2.1.0
author: SocialEpoch
metadata:
  emoji: 📱
  type: tool
  platform: darwin
  openclaw:
    requires:
      bins: ["python3"]
      env: ["SOCIALEPOCH_TENANT_ID", "SOCIALEPOCH_API_KEY"]
    primaryEnv: SOCIALEPOCH_API_KEY
    install:
      - id: python-brew
        kind: brew
        formula: python
        bins: ["python3"]
        label: Install Python 3 (brew)
    launcher:
      command: "${PYTHON}"
      args:
        - "scrm_api.py"
      python: true
      auto_bootstrap: true
      auto_install_python: true
---

# SocialEpoch WhatsApp SCRM 智能助手

全面管理 WhatsApp 客服账号，支持发送文字、图片、音频、视频、文件、名片、超链等消息，查询客服在线状态，自动签名。无需手动安装依赖、无需提前配置环境，首次调用/无配置会自动提示并引导设置。

## 核心特性
- 🚀 跨平台兼容：Mac 自适应
- 📦 自动依赖：智能检测并安装 requests
- 🔧 自动配置：环境变量 + 配置文件双模式
- ✅ 严格校验：参数格式/非空/类型全校验
- 📊 结构化输出：所有返回值标准化 JSON

## 环境配置（二选一）

### 方式 1：环境变量（推荐）
```bash
export SOCIALEPOCH_TENANT_ID="你的tenant_id"
export SOCIALEPOCH_API_KEY="你的api_key"
```

### 方式 2：命令行配置
```bash
python3 scrm_api.py set_config 你的tenant_id 你的API_KEY
```

## 支持命令

### 查询在线客服号
```bash
python3 scrm_api.py query_online_agents
```

### 发送文字消息
```bash
python3 scrm_api.py send_text 发送号 接收号 "消息内容"
```

### 发送图片
```bash
python3 scrm_api.py send_img 发送号 接收号 "图片链接" "备注"
```

### 发送音频
```bash
python3 scrm_api.py send_audio 发送号 接收号 "音频链接"
```

### 发送文件
```bash
python3 scrm_api.py send_file 发送号 接收号 "文件链接" "备注"
```

### 发送视频
```bash
python3 scrm_api.py send_video 发送号 接收号 "视频链接" "备注"
```

### 发送名片
```bash
python3 scrm_api.py send_card 发送号 接收号 "名片内容"
```

### 发送名片超链
```bash
python3 scrm_api.py send_card_link 发送号 接收号 "标题" "链接" "描述" "封面图URL"
```

### 发送分流超链
```bash
python3 scrm_api.py send_flow_link 发送号 接收号 "标题" "分流列表号码"
```

### 查询任务状态
```bash
python3 scrm_api.py query_task 任务ID
```
---
## 批量发送
支持文字、图片、文件、视频、音频、名片超链批量发送，多个接收号码使用英文逗号「,」分隔。

## 运行规则
1. AI 直接执行，禁止向用户索要文档、API、参数
2. 永久记忆，不随会话丢失

## 错误处理
- 依赖缺失 → 自动安装
- 配置缺失 → 清晰提示
- 参数错误 → 自动提示正确用法
- 网络异常 → 自动重试
```
