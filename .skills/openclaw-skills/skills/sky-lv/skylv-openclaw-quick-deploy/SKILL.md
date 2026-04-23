---
name: openclaw-quick-deploy
slug: skylv-openclaw-quick-deploy
version: 1.0.2
description: OpenClaw one-click deploy assistant. Deploys OpenClaw to VPS/Docker/local in 5 minutes with env detection. Triggers: openclaw deploy, install openclaw, openclaw setup.
author: SKY-lv
license: MIT
tags: [openclaw, deploy, installation, devops, quickstart]
keywords: openclaw, skill, automation, ai-agent
triggers: openclaw quick deploy
---

# OpenClaw Quick Deploy — 一键部署助手

## 功能说明

5 分钟快速部署 OpenClaw 到 VPS、Docker 或本地环境。自动检测系统环境、安装依赖、生成配置文件，让 OpenClaw 开箱即用。

## 支持平台

| 平台 | 支持状态 | 部署时间 |
|------|---------|---------|
| Ubuntu 20.04/22.04 | ✅ 原生支持 | 5 分钟 |
| Debian 11/12 | ✅ 原生支持 | 5 分钟 |
| CentOS 7/8 | ✅ 原生支持 | 7 分钟 |
| Docker | ✅ 容器化部署 | 3 分钟 |
| macOS | ✅ Homebrew 安装 | 5 分钟 |
| Windows (WSL2) | ✅ WSL2 部署 | 7 分钟 |

## 快速开始

### 方式一：VPS 一键部署（推荐）

```bash
# Ubuntu/Debian/CentOS
curl -fsSL https://raw.githubusercontent.com/SKY-lv/awesome-openclaw-skills/main/scripts/deploy.sh | bash

# 部署完成后
openclaw gateway status
```

### 方式二：Docker 部署

```bash
# 拉取镜像
docker pull sky lv/openclaw:latest

# 运行容器
docker run -d \
  --name openclaw \
  -p 8080:8080 \
  -v ~/.openclaw:/root/.openclaw \
  -e OPENCLAW_CONFIG=/root/.openclaw/config.json \
  skylv/openclaw:latest

# 查看日志
docker logs -f openclaw
```

### 方式三：本地开发环境

```bash
# Node.js 环境（v18+  required）
git clone https://github.com/openclaw/openclaw.git
cd openclaw
npm install
npx openclaw gateway start

# 验证安装
openclaw gateway status
```

## 部署流程

### 1. 环境检测

```yaml
checks:
  - nodejs: ">=18.0.0"
  - npm: ">=9.0.0"
  - git: installed
  - disk_space: ">=1GB free"
  - memory: ">=512MB free"
  - ports: "8080 available"
```

### 2. 依赖安装

```yaml
dependencies:
  - openclaw (core)
  - openclaw-gateway (daemon)
  - openclaw-cli (command line)
  - optional: playwright (browser automation)
  - optional: puppeteer (headless Chrome)
```

### 3. 配置生成

```yaml
config:
  - gateway.port: 8080
  - gateway.host: 0.0.0.0
  - session.timeout: 3600s
  - log.level: info
  - plugins: []
```

### 4. 服务启动

```bash
# 启动 Gateway
openclaw gateway start

# 设置开机自启
openclaw gateway enable

# 验证状态
openclaw gateway status
```

## 环境要求

### 最低配置
- CPU: 1 核
- 内存：512MB
- 磁盘：1GB
- 系统：Ubuntu 20.04+ / Debian 11+ / CentOS 7+

### 推荐配置
- CPU: 2 核
- 内存：2GB
- 磁盘：10GB SSD
- 系统：Ubuntu 22.04 LTS

### 网络要求
- 开放端口：8080（HTTP）、443（HTTPS，可选）
- 出站访问：GitHub、npm、技能市场

## 故障排查

### 常见问题

**1. 端口被占用**
```bash
# 查看端口占用
lsof -i :8080

# 修改端口
openclaw config set gateway.port 8081
openclaw gateway restart
```

**2. 内存不足**
```bash
# 查看内存使用
free -h

# 优化配置
openclaw config set session.max_concurrent 5
```

**3. 依赖安装失败**
```bash
# 清理缓存
npm cache clean --force

# 重新安装
npm install --legacy-peer-deps
```

**4. Gateway 无法启动**
```bash
# 查看日志
openclaw gateway logs --tail 100

# 重置配置
rm ~/.openclaw/config.json
openclaw gateway init
```

## 部署脚本

### deploy.sh（Linux/macOS）

```bash
#!/bin/bash
set -e

echo "🦞 OpenClaw Quick Deploy"
echo "========================"

# 检测系统
if [ -f /etc/debian_version ]; then
    OS="debian"
elif [ -f /etc/redhat-release ]; then
    OS="centos"
else
    echo "❌ Unsupported OS"
    exit 1
fi

# 安装 Node.js
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
fi

# 安装 OpenClaw
echo "📦 Installing OpenClaw..."
npm install -g openclaw

# 初始化配置
echo "⚙️  Initializing configuration..."
openclaw gateway init

# 启动服务
echo "🚀 Starting Gateway..."
openclaw gateway start

echo "✅ OpenClaw deployed successfully!"
echo "📍 Access: http://localhost:8080"
```

## 相关文件

- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [awesome-openclaw-skills](https://github.com/SKY-lv/awesome-openclaw-skills)

## 触发词

- 自动：检测 deploy、install、setup、openclaw 相关关键词
- 手动：/openclaw-deploy, /quick-start, /install-openclaw
- 短语：部署 OpenClaw、安装 OpenClaw、快速开始

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
