---
name: openclaw-config-optimizer
slug: skylv-openclaw-config-optimizer
version: 1.0.2
description: "OpenClaw Configuration Optimizer. Analyze and optimize OpenClaw config files for better performance and security. Triggers: optimize config, OpenClaw settings, config review, performance tuning, security hardening."
author: SKY-lv
license: MIT
tags: [openclaw, config, optimization, security, performance]
keywords: openclaw, skill, automation, ai-agent
triggers: openclaw config optimizer
---

# OpenClaw Config Optimizer — OpenClaw 配置优化助手

## 功能说明

帮助用户分析和优化 OpenClaw 配置文件，提升性能、安全性和稳定性。提供配置审查、优化建议、一键优化等功能。

## 使用场景

1. **配置审查** - 检查当前配置的问题和风险
2. **性能优化** - 优化配置提升运行速度
3. **安全加固** - 修复安全漏洞和配置风险
4. **最佳实践** - 应用官方推荐配置
5. **故障排查** - 诊断配置相关的问题

## 使用方法

### 1. 配置审查

```
用户：帮我检查一下 OpenClaw 配置有没有问题
```

输出：
- 配置文件位置和内容分析
- 发现的问题列表（严重/警告/建议）
- 修复建议

### 2. 性能优化

```
用户：OpenClaw 运行有点慢，怎么优化？
```

输出：
- 当前性能瓶颈分析
- 优化建议（模型选择、并发设置、缓存配置）
- 一键优化脚本

### 3. 安全加固

```
用户：如何加固 OpenClaw 的安全性？
```

输出：
- 安全检查清单
- 风险配置项
- 加固步骤

### 4. 最佳实践配置

```
用户：OpenClaw 的最佳实践配置是什么？
```

输出：
- 推荐的配置文件模板
- 关键配置项说明
- 应用场景适配建议

## 配置优化项

### 性能优化

| 配置项 | 优化建议 | 影响 |
|--------|----------|------|
| model | 使用本地模型或缓存 | 减少 API 调用延迟 |
| concurrency | 根据 CPU 核心数调整 | 提升并行处理能力 |
| cache.enabled | 启用缓存 | 减少重复计算 |
| cache.ttl | 设置合理的缓存过期时间 | 平衡内存和命中率 |

### 安全加固

| 配置项 | 安全设置 | 说明 |
|--------|----------|------|
| apiKeys | 使用环境变量存储 | 避免硬编码在配置文件中 |
| allowedTools | 限制可用工具范围 | 减少潜在风险 |
| sandbox | 启用沙箱模式 | 隔离危险操作 |
| logging | 关闭敏感信息日志 | 防止信息泄露 |

### 稳定性提升

| 配置项 | 建议值 | 说明 |
|--------|--------|------|
| retry.maxAttempts | 3-5 | 自动重试失败请求 |
| retry.backoffMs | 1000-3000 | 指数退避避免雪崩 |
| timeout.seconds | 60-120 | 避免长时间等待 |
| heartbeat.interval | 30-60 | 保持连接活跃 |

## 配置文件位置

### Windows
```
C:\Users\{user}\.qclaw\openclaw.json
C:\Users\{user}\.qclaw\config\skills\
```

### macOS/Linux
```
~/.qclaw/openclaw.json
~/.qclaw/config/skills/
```

## 优化检查清单

### 基础检查

- [ ] 配置文件语法正确（JSON 格式）
- [ ] 必需的字段完整
- [ ] API Keys 有效且未过期
- [ ] 路径配置正确

### 性能检查

- [ ] 启用了缓存
- [ ] 并发设置合理
- [ ] 模型选择适合场景
- [ ] 超时设置不过长

### 安全检查

- [ ] API Keys 未硬编码
- [ ] 敏感工具已限制
- [ ] 沙箱模式已启用
- [ ] 日志不包含敏感信息

### 稳定性检查

- [ ] 重试机制已配置
- [ ] 超时设置合理
- [ ] 心跳间隔适当
- [ ] 错误处理完善

## 一键优化脚本

```bash
# 备份当前配置
cp openclaw.json openclaw.json.bak

# 应用优化配置
node optimize-config.js

# 验证配置
openclaw config.validate

# 重启 OpenClaw
openclaw gateway restart
```

## 常见问题

### Q: 配置优化后 OpenClaw 不工作了？
A: 恢复备份的配置文件 `cp openclaw.json.bak openclaw.json`，然后逐步应用优化项。

### Q: 如何知道哪些配置项最重要？
A: 优先优化：API Keys、模型选择、缓存设置、安全限制。

### Q: 配置优化能提升多少性能？
A: 通常可提升 30-50% 的响应速度，具体取决于当前配置和使用场景。

## 相关文件

- OpenClaw 配置文档：https://docs.openclaw.ai/config
- 安全最佳实践：https://docs.openclaw.ai/security
- 性能调优指南：https://docs.openclaw.ai/performance

## 触发词

- 自动：检测配置、优化、性能、安全相关关键词
- 手动：/config-optimize, /openclaw-config, /optimize
- 短语：优化配置、配置审查、性能调优、安全加固

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
