# SEP v2.0 - Skill Evolution Protocol Specification

## 技能进化协议规范 v2.0

**版本**: 2.0.0  
**发布日期**: 2026-03-21  
**状态**: 草案  

---

## 1. 概述

### 1.1 协议目标

SEP (Skill Evolution Protocol) 是全球AI技能协同进化的开放标准协议。它定义了技能之间如何：

- 📊 **追踪使用数据** - 标准化数据收集
- 🔍 **分析性能** - 统一性能评估方法
- 📋 **生成进化计划** - 标准化的优化建议格式
- 🚀 **执行进化** - 安全的自动更新机制
- 🔄 **技能间同步** - 跨平台知识共享

### 1.2 适用范围

本协议适用于：
- OpenClaw 技能生态系统
- 钉钉 AI 助理
- 飞书机器人/应用
- GPTs / GPT Store
- 任何符合SEP标准的AI技能平台

### 1.3 术语定义

| 术语 | 定义 |
|------|------|
| **SSE** | Skill Self-Evolution Engine，技能自进化引擎 |
| **SEP** | Skill Evolution Protocol，技能进化协议 |
| **Skill** | AI技能，具有特定功能的可执行单元 |
| **Adapter** | 平台适配器，将SEP转换为平台特定API |
| **Pattern** | 进化模式，可复用的优化策略 |
| **Sync** | 技能同步，跨技能知识迁移 |

---

## 2. 协议架构

### 2.1 分层架构

```
┌─────────────────────────────────────────────┐
│           应用层 (Application Layer)         │
│    (OpenClaw, 钉钉, 飞书, GPTs, ...)        │
├─────────────────────────────────────────────┤
│           协议层 (Protocol Layer)            │
│    ┌─────────────────────────────────────┐  │
│    │  SEP v2.0 - 技能进化协议            │  │
│    │  • 消息格式标准                      │  │
│    │  • 认证授权机制                      │  │
│    │  • 错误处理规范                      │  │
│    │  • 版本兼容性                        │  │
│    └─────────────────────────────────────┘  │
├─────────────────────────────────────────────┤
│           引擎层 (Engine Layer)              │
│    ┌──────────┐  ┌──────────┐              │
│    │ 进化内核 │  │ 数据飞轮 │              │
│    │ Kernel   │  │ Flywheel │              │
│    └──────────┘  └──────────┘              │
├─────────────────────────────────────────────┤
│           存储层 (Storage Layer)             │
│    (JSON文件, SQLite, PostgreSQL, ...)      │
└─────────────────────────────────────────────┘
```

### 2.2 核心组件

| 组件 | 职责 | 接口 |
|------|------|------|
| **EvolutionKernel** | 进化引擎核心 | 提供追踪/分析/规划/执行API |
| **SkillAdapter** | 平台适配 | 转换为平台特定调用 |
| **DataCollector** | 数据收集 | 接收并存储使用数据 |
| **PatternSync** | 模式同步 | 技能间知识共享 |
| **AuthManager** | 认证管理 | 处理API认证授权 |

---

## 3. 消息格式

### 3.1 标准消息结构

所有SEP消息使用JSON格式，遵循以下结构：

```json
{
  "version": "2.0.0",
  "timestamp": "2026-03-21T13:30:00.000Z",
  "message_id": "msg_unique_id",
  "type": "track|analyze|plan|evolve|sync|status",
  "payload": { ... },
  "meta": {
    "source": "platform_name",
    "skill_id": "skill_name",
    "auth_token": "..."
  }
}
```

### 3.2 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `version` | string | 是 | SEP协议版本 |
| `timestamp` | ISO8601 | 是 | 消息生成时间 |
| `message_id` | string | 是 | 全局唯一消息ID |
| `type` | enum | 是 | 消息类型 |
| `payload` | object | 是 | 消息负载数据 |
| `meta.source` | string | 是 | 来源平台 |
| `meta.skill_id` | string | 是 | 技能标识符 |
| `meta.auth_token` | string | 否 | 认证令牌 |

---

## 4. API端点

### 4.1 追踪技能使用

**端点**: `POST /v2/track`

**请求**:
```json
{
  "version": "2.0.0",
  "timestamp": "2026-03-21T13:30:00.000Z",
  "message_id": "track_123456",
  "type": "track",
  "payload": {
    "skill_id": "my-skill",
    "action": "start|complete|error",
    "context": {
      "user_id": "user_001",
      "session_id": "session_123",
      "input_params": { ... }
    },
    "metrics": {
      "duration_ms": 1500,
      "success": true,
      "satisfaction": 4,
      "output_quality": 0.85
    }
  },
  "meta": {
    "source": "openclaw",
    "skill_id": "my-skill",
    "auth_token": "Bearer xxx"
  }
}
```

**响应**:
```json
{
  "status": "success",
  "message_id": "track_123456",
  "data": {
    "record_id": "rec_abc123",
    "stored_at": "2026-03-21T13:30:01.000Z"
  }
}
```

### 4.2 分析技能性能

**端点**: `GET /v2/analyze/{skill_id}`

**查询参数**:
- `time_range`: 分析时间范围 (7d, 30d, 90d)
- `metrics`: 指定指标 (success_rate,duration,satisfaction)

**响应**:
```json
{
  "status": "success",
  "data": {
    "skill_id": "my-skill",
    "time_range": "30d",
    "summary": {
      "total_calls": 150,
      "success_rate": 0.92,
      "avg_duration_ms": 1200,
      "avg_satisfaction": 4.2,
      "health_score": 87
    },
    "bottlenecks": [
      {
        "type": "slow_response",
        "severity": "medium",
        "frequency": 0.15,
        "recommendation": "优化响应时间"
      }
    ],
    "trends": {
      "success_rate_trend": "stable",
      "satisfaction_trend": "improving"
    }
  }
}
```

### 4.3 生成进化计划

**端点**: `POST /v2/plan`

**请求**:
```json
{
  "version": "2.0.0",
  "message_id": "plan_789",
  "type": "plan",
  "payload": {
    "skill_id": "my-skill",
    "strategy": "aggressive|balanced|conservative",
    "focus_areas": ["performance", "reliability", "features"],
    "constraints": {
      "max_changes": 5,
      "preserve_api": true
    }
  },
  "meta": { ... }
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "plan_id": "plan_xyz",
    "skill_id": "my-skill",
    "generated_at": "2026-03-21T13:30:00.000Z",
    "priority": "high",
    "tasks": [
      {
        "id": "task_1",
        "type": "optimize",
        "target": "response_time",
        "description": "添加缓存机制减少API调用",
        "estimated_impact": "+15% 性能提升",
        "auto_apply": false
      }
    ],
    "timeline": {
      "estimated_duration": "2h",
      "phases": ["backup", "update", "test", "rollback_ready"]
    }
  }
}
```

### 4.4 执行技能进化

**端点**: `POST /v2/evolve`

**请求**:
```json
{
  "version": "2.0.0",
  "message_id": "evolve_001",
  "type": "evolve",
  "payload": {
    "skill_id": "my-skill",
    "plan_id": "plan_xyz",
    "mode": "dry_run|auto|manual",
    "backup_first": true
  },
  "meta": { ... }
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "evolution_id": "evo_123",
    "skill_id": "my-skill",
    "mode": "auto",
    "results": {
      "backup_created": "backup_20260321_133000",
      "tasks_completed": 3,
      "tasks_failed": 0,
      "new_version": "1.1.0"
    },
    "verification": {
      "tests_passed": true,
      "performance_delta": +0.12,
      "health_score_improvement": +8
    }
  }
}
```

### 4.5 技能间同步

**端点**: `POST /v2/sync`

**请求**:
```json
{
  "version": "2.0.0",
  "message_id": "sync_456",
  "type": "sync",
  "payload": {
    "source_skill": "skill-a",
    "target_skills": ["skill-b", "skill-c"],
    "sync_type": "patterns|config|knowledge",
    "pattern_filter": {
      "min_confidence": 0.8,
      "max_complexity": "medium"
    }
  },
  "meta": { ... }
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "sync_id": "sync_789",
    "patterns_discovered": 3,
    "patterns_applied": 9,
    "affected_skills": ["skill-b", "skill-c"],
    "improvements": {
      "skill-b": {"health_delta": +5},
      "skill-c": {"health_delta": +7}
    }
  }
}
```

### 4.6 获取引擎状态

**端点**: `GET /v2/status`

**响应**:
```json
{
  "status": "success",
  "data": {
    "engine": {
      "version": "2.0.0",
      "status": "running",
      "uptime_seconds": 86400
    },
    "skills": {
      "total": 20,
      "registered": 20,
      "active": 18,
      "evolving": 2
    },
    "platforms": {
      "openclaw": "connected",
      "dingtalk": "configured",
      "feishu": "configured",
      "gpts": "configured"
    },
    "metrics": {
      "total_tracks_today": 150,
      "avg_health_score": 83,
      "patterns_shared": 42
    }
  }
}
```

---

## 5. 认证机制

### 5.1 认证方式

SEP支持以下认证方式：

| 方式 | 适用场景 | 优先级 |
|------|----------|--------|
| **API Key** | 服务器端集成 | 推荐 |
| **OAuth 2.0** | 第三方应用 | 可选 |
| **JWT Token** | 微服务间通信 | 可选 |

### 5.2 API Key认证

**请求头**:
```
Authorization: Bearer {api_key}
X-SSE-Skill-ID: {skill_id}
X-SSE-Platform: {platform_name}
```

### 5.3 OAuth 2.0流程

```
1. 客户端 -> 授权服务器: 请求授权码
2. 授权服务器 -> 客户端: 返回授权码
3. 客户端 -> 令牌服务器: 用授权码换取access_token
4. 令牌服务器 -> 客户端: 返回access_token + refresh_token
5. 客户端 -> SSE API: 使用access_token调用API
```

---

## 6. 错误处理

### 6.1 错误响应格式

```json
{
  "status": "error",
  "message_id": "msg_123",
  "error": {
    "code": "SEP_001",
    "type": "validation_error",
    "message": "Invalid skill_id format",
    "details": {
      "field": "skill_id",
      "received": "invalid@id",
      "expected": "^[a-z0-9-]+$"
    },
    "suggestion": "Use lowercase letters, numbers, and hyphens only"
  }
}
```

### 6.2 错误码表

| 错误码 | 类型 | 说明 |
|--------|------|------|
| SEP_001 | validation_error | 参数验证失败 |
| SEP_002 | authentication_error | 认证失败 |
| SEP_003 | authorization_error | 权限不足 |
| SEP_004 | not_found | 资源不存在 |
| SEP_005 | rate_limit | 请求频率限制 |
| SEP_006 | skill_error | 技能执行错误 |
| SEP_007 | sync_error | 同步失败 |
| SEP_008 | version_mismatch | 版本不兼容 |
| SEP_009 | internal_error | 内部错误 |
| SEP_010 | platform_error | 平台适配错误 |

### 6.3 HTTP状态码映射

| HTTP状态 | SEP错误码 | 场景 |
|----------|-----------|------|
| 200 | - | 成功 |
| 400 | SEP_001 | 请求参数错误 |
| 401 | SEP_002 | 认证失败 |
| 403 | SEP_003 | 权限不足 |
| 404 | SEP_004 | 资源不存在 |
| 429 | SEP_005 | 频率限制 |
| 500 | SEP_009 | 服务器错误 |

---

## 7. 版本兼容性

### 7.1 版本策略

SEP遵循语义化版本 (SemVer)：
- **Major**: 破坏性变更
- **Minor**: 向后兼容的功能添加
- **Patch**: 向后兼容的问题修复

### 7.2 兼容性规则

| 客户端版本 | 服务端版本 | 兼容性 |
|------------|------------|--------|
| 2.0.x | 2.0.x | ✅ 完全兼容 |
| 2.0.x | 2.1.x | ✅ 向后兼容 |
| 2.1.x | 2.0.x | ⚠️ 部分兼容 |
| 1.x.x | 2.x.x | ❌ 不兼容 |

### 7.3 弃用策略

- 功能弃用提前 **3个Minor版本** 通知
- 提供迁移指南和兼容性层
- 弃用功能保留 **6个月** 后移除

---

## 8. 实现指南

### 8.1 服务端实现

Python示例：
```python
from ssee.core import EvolutionKernel, KernelConfig

# 初始化引擎
config = KernelConfig(data_dir="/data/sse")
kernel = EvolutionKernel(config)
kernel.initialize()

# 处理SEP消息
def handle_sep_message(message):
    msg_type = message["type"]
    payload = message["payload"]
    
    if msg_type == "track":
        return kernel.track(payload["skill_id"], payload["metrics"])
    elif msg_type == "analyze":
        return kernel.analyze(payload["skill_id"])
    # ... 其他类型
```

### 8.2 客户端SDK

Python SDK示例：
```python
from sse_sdk import SSEClient

client = SSEClient(
    endpoint="https://api.sse.example.com",
    api_key="your_api_key"
)

# 追踪使用
client.track("my-skill", {
    "duration_ms": 1500,
    "success": True
})

# 分析性能
analysis = client.analyze("my-skill")
```

---

## 9. 附录

### 9.1 完整JSON Schema

[见 schema/sep-v2.0-schema.json]

### 9.2 变更日志

#### v2.0.0 (2026-03-21)
- ✅ 初始版本发布
- ✅ 定义6个核心API端点
- ✅ 建立认证和错误处理规范
- ✅ 支持多平台适配

### 9.3 参考实现

- Python: `ssee/core/` 
- JavaScript: `sdk/js/`
- Go: `sdk/go/`

---

## 10. 社区与贡献

### 10.1 规范维护

- **规范维护者**: OpenClaw Team
- **讨论区**: https://github.com/openclaw/sep/discussions
- **Issue追踪**: https://github.com/openclaw/sep/issues

### 10.2 贡献指南

1. Fork 规范仓库
2. 创建特性分支
3. 提交变更建议
4. 发起 Pull Request
5. 等待审核合并

---

**SEP v2.0 - 让全球AI技能协同进化** 🌍
