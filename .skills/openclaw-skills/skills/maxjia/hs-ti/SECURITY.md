# Security Policy / 安全策略

## Security Best Practices / 安全最佳实践

### API Key Management / API密钥管理

#### Recommended Methods / 推荐方法

1. **Environment Variables / 环境变量（推荐）**
   ```bash
   export HILLSTONE_API_KEY="your-actual-api-key-here"
   ```
   - Most secure method / 最安全的方法
   - No file storage required / 无需文件存储
   - Easy to rotate keys / 易于密钥轮换

2. **Secure File Storage / 安全文件存储**
   ```bash
   chmod 600 config.json
   ```
   - Restrict file permissions / 限制文件权限
   - Only owner can read/write / 仅所有者可读写
   - Prevents unauthorized access / 防止未授权访问

#### Configuration Options / 配置选项

The hs-ti skill supports multiple configuration methods for API key management:
hs-ti技能支持多种API密钥管理方式：

**Priority Order / 优先级顺序：**
1. Environment variable `HILLSTONE_API_KEY` (highest priority / 最高优先级)
2. Config file `config.json` (fallback / 备选)

**Example Configuration / 配置示例：**

```json
{
  "api_key": "your-api-key-here",
  "api_url": "https://ti.hillstonenet.com.cn"
}
```

**Or use environment variable / 或使用环境变量：**
```bash
export HILLSTONE_API_KEY="your-api-key-here"
```

### Logging Security / 日志安全

The hs-ti skill implements automatic sensitive data masking in logs:
hs-ti技能在日志中实现了自动敏感数据遮蔽：

**Masking Rules / 遮蔽规则：**
- IOC values are partially masked in logs / IOC值在日志中部分遮蔽
- Example: `example.com` → `ex******m.com`
- Example: `192.168.1.1` → `19********.1`
- API keys are never logged / API密钥从不记录

**Log Location / 日志位置：**
- Path: `~/.openclaw/logs/hs_ti.log`
- Contains: Query results, performance metrics, errors / 包含：查询结果、性能指标、错误
- Does NOT contain: API keys, full IOC values / 不包含：API密钥、完整IOC值

### Network Security / 网络安全

#### HTTPS Enforcement / HTTPS强制
- All API calls use HTTPS by default / 所有API调用默认使用HTTPS
- Configurable `api_url` parameter / 可配置`api_url`参数
- Ensure URL starts with `https://` / 确保URL以`https://`开头

#### Connection Pool / 连接池
- Implements connection pooling for efficiency / 实现连接池以提高效率
- Maximum connections configurable (default: 10) / 最大连接数可配置（默认：10）
- Automatic connection cleanup / 自动连接清理

### File System Security / 文件系统安全

#### Permissions / 权限
```bash
# Restrict config file access / 限制配置文件访问
chmod 600 ~/.openclaw/skills/hs-ti/config.json

# Restrict log file access / 限制日志文件访问
chmod 600 ~/.openclaw/logs/hs_ti.log
```

#### Export Files / 导出文件
- Export files are written to `examples/exports/` / 导出文件写入`examples/exports/`
- Review export permissions / 检查导出权限
- Clean up sensitive exports regularly / 定期清理敏感导出文件

### Operational Security / 运行安全

#### Verification / 验证
Before using the skill, verify:
使用技能前，请验证：

1. **Source Verification / 来源验证**
   - Confirm skill is from trusted source / 确认技能来自可信来源
   - Check publisher: `maxjia` / 检查发布者：`maxjia`
   - Verify homepage: `https://clawhub.ai/maxjia/hs-ti` / 验证主页：`https://clawhub.ai/maxjia/hs-ti`

2. **API Key Source / API密钥来源**
   - Obtain API key from official Hillstone channels / 从官方云瞻渠道获取API密钥
   - Never share API keys / 从不共享API密钥
   - Rotate keys regularly / 定期轮换密钥

3. **Environment Isolation / 环境隔离**
   - Run in sandbox or VM when testing / 测试时在沙箱或虚拟机中运行
   - Monitor network traffic / 监控网络流量
   - Review log files regularly / 定期检查日志文件

#### Audit Recommendations / 审计建议

**Regular Security Audits / 定期安全审计：**
- Review `~/.openclaw/logs/hs_ti.log` for unusual activity / 检查异常活动
- Verify config file permissions / 验证配置文件权限
- Check for unexpected network connections / 检查意外的网络连接
- Monitor API key usage / 监控API密钥使用情况

**Incident Response / 事件响应：**
If you suspect security compromise:
如果您怀疑安全被破坏：

1. Immediately rotate API key / 立即轮换API密钥
2. Review logs for suspicious activity / 检查日志中的可疑活动
3. Update skill to latest version / 更新技能到最新版本
4. Report security issues to: `maxjia` / 向`maxjia`报告安全问题

### Data Privacy / 数据隐私

#### What Data is Collected / 收集哪些数据

**Collected / 收集的数据：**
- API queries (IOC values, types) / API查询（IOC值、类型）
- Query timestamps / 查询时间戳
- Response times / 响应时间
- Error messages (sanitized) / 错误消息（已清理）

**NOT Collected / 不收集的数据：**
- Personal information / 个人信息
- System credentials / 系统凭据
- Other skills' data / 其他技能的数据
- Full API keys (only stored locally) / 完整API密钥（仅本地存储）

#### Data Retention / 数据保留

- **Logs**: Retained indefinitely until manually deleted / 日志：无限期保留直到手动删除
- **Cache**: Cleared on restart or when TTL expires / 缓存：重启时清除或TTL过期时清除
- **Exports**: Retained until manually deleted / 导出：保留直到手动删除

**Cleanup Commands / 清理命令：**
```bash
# Clear logs / 清除日志
rm ~/.openclaw/logs/hs_ti.log

# Clear cache (automatic on restart) / 清除缓存（重启时自动）
# Cache is automatically managed by the skill / 缓存由技能自动管理

# Clear exports / 清除导出
rm -rf ~/.openclaw/skills/hs-ti/examples/exports/*
```

### Vulnerability Reporting / 漏洞报告

**How to Report / 如何报告：**

If you discover a security vulnerability:
如果您发现安全漏洞：

1. **Do NOT create public issue** / **不要创建公开issue**
2. Email: Contact through ClawHub / 邮件：通过ClawHub联系
3. Include: / 包含：
   - Vulnerability description / 漏洞描述
   - Steps to reproduce / 复现步骤
   - Impact assessment / 影响评估
   - Proposed fix (if any) / 建议的修复（如有）

**Response Time / 响应时间：**
- Acknowledgment within 48 hours / 48小时内确认
- Fix timeline depends on severity / 修复时间线取决于严重程度

### Supported Python Version / 支持的Python版本

- Minimum: Python 3.8 / 最低：Python 3.8
- Recommended: Python 3.10+ / 推荐：Python 3.10+
- Tested on: Python 3.8, 3.9, 3.10, 3.11, 3.12 / 测试于：Python 3.8, 3.9, 3.10, 3.11, 3.12

### Dependencies / 依赖项

**No External Dependencies Required / 无需外部依赖：**
- Uses only Python standard library / 仅使用Python标准库
- `urllib` - HTTP requests / HTTP请求
- `json` - JSON parsing / JSON解析
- `logging` - Logging / 日志记录
- `threading` - Thread safety / 线程安全
- `pathlib` - File operations / 文件操作

**Security Benefits / 安全优势：**
- No supply chain attacks from third-party packages / 无第三方包的供应链攻击
- Minimal attack surface / 最小攻击面
- Regular Python security updates / 定期Python安全更新

### Compliance / 合规性

This skill is designed with security best practices in mind:
本技能设计时考虑了安全最佳实践：

- **Data Minimization** / 数据最小化：Only collects necessary data / 仅收集必要数据
- **Secure by Default** / 默认安全：HTTPS, sensitive data masking / HTTPS、敏感数据遮蔽
- **Transparency** / 透明度：Open source, documented behavior / 开源、文档化的行为
- **User Control** / 用户控制：Configurable logging, caching / 可配置的日志、缓存

---

## Quick Security Checklist / 快速安全检查清单

Before deploying to production:
部署到生产环境前：

- [ ] API key stored securely (environment variable or restricted file) / API密钥安全存储（环境变量或受限文件）
- [ ] Config file permissions set to 600 / 配置文件权限设置为600
- [ ] HTTPS URL configured / HTTPS URL已配置
- [ ] Latest version installed / 已安装最新版本
- [ ] Logs reviewed for sensitive data / 已检查日志中的敏感数据
- [ ] Network traffic monitored / 已监控网络流量
- [ ] Backup and recovery plan in place / 已有备份和恢复计划

---

## Contact / 联系方式

**Security Questions / 安全问题：**
- Publisher: `maxjia` / 发布者：`maxjia`
- Homepage: `https://clawhub.ai/maxjia/hs-ti` / 主页：`https://clawhub.ai/maxjia/hs-ti`
- License: MIT / 许可证：MIT

**Last Updated / 最后更新：** 2026-04-01
**Version / 版本：** 2.2.0
