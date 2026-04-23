---
name: "Api Gateway"
slug: skylv-api-gateway
version: 1.0.0
description: "API网关管理。配置和管理API网关，处理流量路由和限流。"
author: SKY-lv
license: MIT-0
tags: [openclaw, agent, api]
---

# API Gateway Agent Skill

> AI-powered API gateway and traffic management

## 功能

- **API代理** - 统一入口、请求转发
- **流量控制** - 限流、熔断、降级
- **认证授权** - JWT、OAuth2、API Key
- **监控统计** - 请求日志、性能指标
- **文档生成** - 自动生成API文档

## 使用场景

```
用户: 帮我配置一个API网关，限流1000/min
Agent: [调用api-gateway skill配置网关规则]
```

## 工具函数

### `create_gateway(config)`

创建API网关。

**参数:**
```python
{
    "name": "main-gateway",
    "routes": [
        {
            "path": "/api/v1/*",
            "target": "http://backend:8080",
            "methods": ["GET", "POST"]
        }
    ],
    "rate_limit": {
        "requests": 1000,
        "window": "1m"
    },
    "auth": {
        "type": "jwt",
        "secret": "${JWT_SECRET}"
    }
}
```

### `add_route(gateway_id, route_config)`

添加路由。

### `set_rate_limit(gateway_id, limit)`

设置限流。

### `get_metrics(gateway_id)`

获取监控指标。

## 配置

```json
{
    "backend": "envoy",
    "persistence": "redis",
    "monitoring": {
        "prometheus": true,
        "grafana": true
    },
    "security": {
        "cors": true,
        "https_redirect": true
    }
}
```

## 安装

```bash
clawhub install SKY-lv/api-gateway
```

## License

MIT
