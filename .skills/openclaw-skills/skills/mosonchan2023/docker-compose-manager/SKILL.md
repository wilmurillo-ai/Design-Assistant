---
name: docker-compose-manager
description: Manage docker-compose services - start, stop, restart, logs, and scale containers. Each call charges 0.001 USDT via SkillPay.
version: 1.0.0
author: moson
tags:
  - docker
  - docker-compose
  - containers
  - devops
  - orchestration
  - deployment
homepage: https://github.com/moson/docker-compose-manager
metadata:
  clawdbot:
    requires:
      env:
        - SKILLPAY_API_KEY
triggers:
  - "docker compose"
  - "docker-compose"
  - "docker up"
  - "docker down"
  - "docker restart"
  - "docker logs"
  - "容器管理"
  - "docker 启动"
  - "docker 停止"
  - "compose services"
  - "scale containers"
---

# Docker Compose Manager

## 功能

### 核心功能

- **Start Services**: docker-compose up
- **Stop Services**: docker-compose down
- **Restart**: Restart services
- **Logs**: View service logs
- **Scale**: Scale service replicas
- **Build**: Build images before starting

## 使用方法

```json
{
  "action": "up",
  "file": "docker-compose.yml",
  "detached": true
}
```

## 输出示例

```json
{
  "success": true,
  "action": "up",
  "file": "docker-compose.yml",
  "services": ["web", "api", "db"],
  "message": "Docker Compose services started"
}
```

## 支持的操作

| Action | Description |
|--------|-------------|
| up | 启动所有服务 |
| down | 停止并删除所有服务 |
| restart | 重启所有服务 |
| logs | 查看服务日志 |
| scale | 扩展服务副本数 |
| build | 构建镜像 |

## 价格

每次调用: 0.001 USDT

## 使用场景

- 微服务管理
- 本地开发环境
- 测试环境部署
- 多容器编排
