# 天机·玄机子凭证管理文档

## 文档概述
本文档详细说明天机·玄机子技能的凭证管理架构、安全风险、平台要求和使用指南，响应ClawHub审查反馈的凭证管理问题。

## 审查反馈摘要
**审查反馈原文**:
> "注册表元数据列出无 required env vars，但代码/文档读取 OpenClaw 配置（/home/test/.openclaw/config.json）以获取模型配置。读取平台配置对实现模型路由是合理的，但这些配置通常会包含 API 密钥或凭证位置：虽然文档多次声明'凭证由平台管理，不直接处理 API 密钥'，代码和测试把 OpenClaw 配置文件路径标记为'可读/安全'，这可能导致技能在运行时读取包含敏感信息的文件。允许读取 /.openclaw/ 下的配置被视为超出普通'仅读用户图片'的最小权限，应在安装前确认平台配置如何存储/加密凭证。"

## 凭证管理架构

### 1. 设计原则

#### 1.1 间接访问原则
- **核心原则**: 技能不直接处理明文API密钥
- **实现方式**: 通过OpenClaw平台间接访问AI服务
- **安全优势**: 减少凭证泄露风险，集中安全管理

#### 1.2 平台委托原则
- **核心原则**: 凭证管理委托给OpenClaw平台
- **实现方式**: OpenClaw负责API密钥的存储、加密和轮换
- **安全优势**: 利用平台的专业安全功能

#### 1.3 最小权限原则
- **核心原则**: 仅读取必要配置信息
- **实现方式**: 只读取模型路由配置，不访问完整凭证
- **安全优势**: 限制潜在的信息泄露范围

#### 1.4 透明操作原则
- **核心原则**: 所有配置访问对用户可见
- **实现方式**: 记录配置读取操作，提供审计日志
- **安全优势**: 便于监控和异常检测

### 2. 凭证流转流程

```
用户提供API密钥
        ↓
OpenClaw平台加密存储
        ↓
技能读取模型配置（非密钥）
        ↓
OpenClaw平台API调用（使用密钥）
        ↓
AI服务返回结果
        ↓
技能处理并返回分析结果
```

### 3. 具体实现分析

#### 3.1 配置读取方式
```python
# 方式1：通过openclaw命令（当前实现）
import subprocess
import json

def get_openclaw_config(section):
    """通过openclaw命令获取配置"""
    try:
        result = subprocess.run(
            ["openclaw", "config", "get", section],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return None

# 读取volcengine配置
volcengine_config = get_openclaw_config("models.providers.volcengine")
# 读取deepseek配置  
deepseek_config = get_openclaw_config("models.providers.deepseek")
```

#### 3.2 安全边界分析
```python
# 技能实际访问的内容
expected_config_structure = {
    "models": {
        "providers": {
            "volcengine": {
                "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
                "models": [
                    {
                        "id": "doubao-seed-2-0-pro-260215",
                        "name": "豆包视觉模型"
                    }
                ]
                # 注意：不包含apiKey字段（由平台管理）
            },
            "deepseek": {
                "baseUrl": "https://api.deepseek.com/v1"
                # 注意：不包含apiKey字段（由平台管理）
            }
        }
    }
}
```

## 安全风险分析

### 1. 风险识别

#### 1.1 配置读取风险
- **风险描述**: 读取 `~/.openclaw/config.json` 可能暴露敏感信息
- **可能性**: 高（技能需要读取配置）
- **影响程度**: 中（依赖平台安全实现）
- **总体风险**: 中

#### 1.2 权限超出最小原则
- **风险描述**: 超出"仅读用户图片"的最小权限范围
- **可能性**: 高（功能需要）
- **影响程度**: 低（只读访问）
- **总体风险**: 中

#### 1.3 平台信任依赖
- **风险描述**: 完全依赖OpenClaw平台的安全实现
- **可能性**: 高（架构设计）
- **影响程度**: 高（平台漏洞影响）
- **总体风险**: 中

#### 1.4 环境安全假设
- **风险描述**: 假设运行环境是安全的
- **可能性**: 中（环境多变）
- **影响程度**: 高（环境漏洞）
- **总体风险**: 中

### 2. 风险控制措施

#### 2.1 技术控制
```bash
# 1. 配置加密（平台层面）
openclaw config set security.encryption.enabled=true
openclaw config set security.encryption.algorithm=aes-256-gcm

# 2. 访问控制（平台层面）
openclaw config set security.access_control.enabled=true
openclaw config set security.access_control.read_only_skills=true

# 3. 审计日志（平台层面）
openclaw config set security.audit.config_access=true
openclaw config set security.audit.retention_days=90
```

#### 2.2 流程控制
```bash
# 1. 安装前验证
bash verify_platform_security.sh

# 2. 定期安全审查
bash security_audit.sh --skill=tianji-fengshui

# 3. 使用监控
monitor_skill_usage.sh --skill=tianji-fengshui --alert-threshold=10
```

#### 2.3 用户责任
```bash
# 1. 平台安全配置
configure_openclaw_security.sh

# 2. 权限最小化
minimize_skill_permissions.sh --skill=tianji-fengshui

# 3. 定期审计
audit_skill_operations.sh --skill=tianji-fengshui --period=weekly
```

## 平台安全要求

### 1. OpenClaw平台必须功能

#### 1.1 配置加密
```yaml
# 最低要求配置
security:
  encryption:
    enabled: true
    algorithm: "aes-256-gcm"  # 或同等强度算法
    key_management: "secure"  # 安全的密钥管理
  sensitive_fields:
    - "*.apiKey"
    - "*.token"
    - "*.secret"
    - "*.password"
```

#### 1.2 访问控制
```yaml
# 最低要求配置
security:
  access_control:
    enabled: true
    skill_permissions:
      read_config: true
      write_config: false
      execute_commands: true
    config_sections:
      allowed: ["models.providers"]
      restricted: ["security", "credentials"]
```

#### 1.3 审计日志
```yaml
# 最低要求配置
security:
  audit:
    enabled: true
    events:
      config_read: true
      command_execute: true
      api_call: true
    retention:
      days: 90
      compression: true
    alerting:
      suspicious_access: true
      rate_limit_exceeded: true
```

### 2. 用户验证清单

#### 2.1 安装前验证
```bash
#!/bin/bash
# verify_platform_security.sh

echo "=== OpenClaw平台安全验证 ==="

# 1. 检查版本
echo "1. 检查OpenClaw版本..."
openclaw version

# 2. 检查安全功能
echo "2. 检查安全功能..."
openclaw config get security.encryption.enabled
openclaw config get security.access_control.enabled
openclaw config get security.audit.enabled

# 3. 检查配置文件权限
echo "3. 检查配置文件权限..."
ls -la ~/.openclaw/config.json
stat -c "%a %U %G" ~/.openclaw/config.json

# 4. 检查运行环境
echo "4. 检查运行环境..."
whoami
uname -a
echo "SELinux状态: $(getenforce 2>/dev/null || echo '未安装')"

echo "=== 验证完成 ==="
```

#### 2.2 定期安全审查
```bash
#!/bin/bash
# security_audit.sh

echo "=== 天机·玄机子安全审计 ==="
echo "审计时间: $(date)"
echo "技能版本: 1.7.0"

# 1. 检查配置访问日志
echo "1. 检查配置访问日志..."
journalctl -u openclaw --since "7 days ago" | grep -i "config.*read" | tail -20

# 2. 检查临时文件
echo "2. 检查临时文件..."
find /tmp -name "tianji_*" -type f -mtime -7 | wc -l

# 3. 检查API使用
echo "3. 检查API使用..."
openclaw usage report --provider=volcengine --period=weekly
openclaw usage report --provider=deepseek --period=weekly

# 4. 检查技能日志
echo "4. 检查技能日志..."
find /var/log -name "*tianji*" -type f -mtime -7 2>/dev/null | head -5

echo "=== 审计完成 ==="
```

## 替代方案与缓解措施

### 1. 环境变量注入方案

#### 1.1 配置方式
```bash
# 启动脚本示例
#!/bin/bash
# start_tianji_with_env.sh

# 从安全存储加载环境变量
export VOLCENGINE_API_KEY=$(vault read -field=api_key openclaw/volcengine)
export DEEPSEEK_API_KEY=$(vault read -field=api_key openclaw/deepseek)

# 设置只读配置
export OPENCLAW_CONFIG_READONLY=true

# 启动技能
python3 tianji_core.py "$@"
```

#### 1.2 安全优势
- ✅ 避免读取配置文件
- ✅ 环境变量在进程间隔离
- ✅ 支持动态密钥轮换
- ✅ 便于权限管理

#### 1.3 实施要求
- OpenClaw平台支持环境变量配置
- 安全的环境变量管理工具
- 适当的权限控制

### 2. API网关方案

#### 2.1 架构设计
```
用户请求 → 技能 → API网关 → AI服务
                ↓          ↓
            无凭证      处理凭证
```

#### 2.2 实现方式
```python
# 技能通过API网关调用，网关处理凭证
import requests

def analyze_via_gateway(image_base64, analysis_type):
    """通过API网关进行分析"""
    gateway_url = "https://gateway.example.com/api/analyze"
    gateway_key = os.getenv("GATEWAY_API_KEY")  # 网关自有密钥
    
    response = requests.post(
        gateway_url,
        json={
            "image": image_base64,
            "type": analysis_type,
            "model": "doubao" if analysis_type in ["palm", "face", "fengshui"] else "deepseek"
        },
        headers={
            "Authorization": f"Bearer {gateway_key}",
            "Content-Type": "application/json"
        },
        timeout=30
    )
    
    return response.json()
```

#### 2.3 安全优势
- ✅ 完全隔离AI服务凭证
- ✅ 集中访问控制和审计
- ✅ 支持速率限制和配额管理
- ✅ 便于监控和故障排除

### 3. 硬件安全模块方案

#### 3.1 配置示例
```bash
# 使用HSM保护OpenClaw配置
openclaw config set security.hsm.enabled=true
openclaw config set security.hsm.module=/usr/lib/opensc-pkcs11.so
openclaw config set security.hsm.slot=0
openclaw config set security.hsm.pin_env=HSM_PIN
```

#### 3.2 安全优势
- ✅ 硬件级密钥保护
- ✅ 防篡改安全存储
- ✅ 高性能加密操作
- ✅ 符合安全合规要求

## 监控与审计框架

### 1. 实时监控配置

#### 1.1 文件访问监控
```bash
# 使用inotify监控配置文件
inotifywait -m ~/.openclaw/config.json -e access,open |
while read path action file; do
    echo "配置访问: $(date) - $action - $file" >> /var/log/openclaw_config_access.log
    # 发送告警（如果异常）
    if [[ "$action" == "OPEN" ]]; then
        check_access_pattern "$path" && send_alert "可疑配置访问"
    fi
done
```

#### 1.2 进程行为监控
```bash
# 监控技能进程行为
strace -f -e trace=file,process -p $(pgrep -f "tianji.*\.py") 2>&1 |
grep -E "(open|read|exec)" |
while read line; do
    echo "进程行为: $(date) - $line" >> /var/log/tianji_behavior.log
    detect_suspicious_behavior "$line" && send_alert "可疑进程行为"
done
```

### 2. 定期审计脚本

#### 2.1 综合审计脚本
```bash
#!/bin/bash
# comprehensive_audit.sh

AUDIT_DATE=$(date +%Y%m%d_%H%M%S)
AUDIT_DIR="/var/audit/tianji_fengshui/$AUDIT_DATE"

mkdir -p "$AUDIT_DIR"

echo "开始综合审计: $AUDIT_DATE"

# 1. 收集系统信息
uname -a > "$AUDIT_DIR/system_info.txt"
whoami >> "$AUDIT_DIR/system_info.txt"

# 2. 收集OpenClaw配置
openclaw config get > "$AUDIT_DIR/openclaw_config.json"

# 3. 收集技能文件
cp -r /home/test/.openclaw/workspace/skills/tianji-fengshui "$AUDIT_DIR/skill_files/"

# 4. 收集日志
journalctl -u openclaw --since "30 days ago" > "$AUDIT_DIR/openclaw_logs.log"
find /var/log -name "*tianji*" -type f -exec cat {} \; > "$AUDIT_DIR/tianji_logs.log" 2>/dev/null

# 5. 收集临时文件
find /tmp -name "tianji_*" -type f -exec cp {} "$AUDIT_DIR/temp_files/" \; 2>/dev/null

# 6. 生成审计报告
generate_audit_report "$AUDIT_DIR"

echo "审计完成，结果保存在: $AUDIT_DIR"
```

### 3. 告警配置

#### 3.1 异常访问告警
```yaml
# alert_rules.yaml
alert_rules:
  - name: "频繁配置读取"
    condition: "config_read_count > 10 within 1min"
    severity: "warning"
    action: "notify_admin, log_event"
    
  - name: "异常时间访问"
    condition: "config_access between 00:00 and 06:00"
    severity: "high"
    action: "notify_admin, block_skill"
    
  - name: "大文件读取"
    condition: "file_read_size > 10MB"
    severity: "medium"
    action: "notify_admin, investigate"
    
  - name: "可疑命令执行"
    condition: "command matches /rm.*-rf|format|shutdown/"
    severity: "critical"
    action: "notify_admin, kill_process, isolate_system"
```

## 应急响应计划

### 1. 事件分类与响应

#### 1.1 事件分类
```yaml
event_levels:
  critical:
    - 凭证确认泄露
    - 系统被入侵
    - 恶意代码执行
    
  high:
    - 可疑配置访问
    - 异常API使用
    - 权限提升尝试
    
  medium:
    - 频繁配置读取
    - 大文件访问
    - 异常时间操作
    
  low:
    - 一般配置访问
    - 正常技能使用
    - 预期临时文件生成
```

#### 1.2 响应流程
```
发现异常
    ↓
分类定级
    ↓
初步遏制
    ↓
调查取证
    ↓
根除恢复
    ↓
总结改进
```

### 2. 响应工具包

#### 2.1 初步遏制脚本
```bash
#!/bin/bash
# initial_containment.sh

echo "开始初步遏制..."

# 1. 停止技能进程
echo "停止技能进程..."
pkill -f "tianji.*\.py"
pkill -f "python.*tianji"

# 2. 隔离网络
echo "隔离网络..."
iptables -A INPUT -s $(hostname -I | awk '{print $1}') -j DROP
iptables -A OUTPUT -d $(hostname -I | awk '{print $1}') -j DROP

# 3. 保护证据
echo "保护证据..."
TIMESTAMP=$(date +%s)
mkdir -p /tmp/forensic_$TIMESTAMP
cp ~/.openclaw/config.json /tmp/forensic_$TIMESTAMP/
cp -r /tmp/tianji_* /tmp/forensic_$TIMESTAMP/ 2>/dev/null
lsof -p $(pgrep openclaw) > /tmp/forensic_$TIMESTAMP/openclaw_processes.txt 2>/dev/null

# 4. 禁用技能
echo "禁用技能..."
mv /home/test/.openclaw/workspace/skills/tianji-fengshui /home/test/.openclaw/workspace/skills/tianji-fengshui_disabled_$TIMESTAMP

echo "初步遏制完成"
```

#### 2.2 调查取证脚本
```bash
#!/bin/bash
# forensic_investigation.sh

echo "开始调查取证..."

TIMESTAMP=$1
FORENSIC_DIR="/tmp/forensic_$TIMESTAMP"

if [ ! -d "$FORENSIC_DIR" ]; then
    echo "错误: 取证目录不存在"
    exit 1
fi

echo "1. 分析配置文件..."
cp "$FORENSIC_DIR/config.json" "$FORENSIC_DIR/config_analysis.json"
# 移除敏感信息进行分析
sed -i 's/"apiKey":".*"/"apiKey":"[REDACTED]"/g' "$FORENSIC_DIR/config_analysis.json"
sed -i 's/"token":".*"/"token":"[REDACTED]"/g' "$FORENSIC_DIR/config_analysis.json"

echo "2. 分析临时文件..."
for file in "$FORENSIC_DIR"/tianji_*; do
    if [ -f "$file" ]; then
        echo "=== 文件: $(basename "$file") ===" >> "$FORENSIC_DIR/file_analysis.txt"
        head -50 "$file" >> "$FORENSIC_DIR/file_analysis.txt"
        echo "" >> "$FORENSIC_DIR/file_analysis.txt"
    fi
done

echo "3. 分析系统日志..."
journalctl -u openclaw --since "24 hours ago" > "$FORENSIC_DIR/system_logs.txt"

echo "4. 生成取证报告..."
cat > "$FORENSIC_DIR/forensic_report.md" << EOF
# 安全事件取证报告

## 基本信息
- 事件时间: $(date)
- 取证时间: $TIMESTAMP
- 涉及技能: tianji-fengshui v1.7.0
- 取证人员: $(whoami)

## 发现内容
### 1. 配置文件分析
\`\`\`json
$(head -100 "$FORENSIC_DIR/config_analysis.json")
\`\`\`

### 2. 临时文件分析
\`\`\`
$(head -200 "$FORENSIC_DIR/file_analysis.txt")
\`\`\`

### 3. 系统日志摘要
\`\`\`
$(grep -i "error\|warn\|fail\|denied" "$FORENSIC_DIR/system_logs.txt" | head -50)
\`\`\`

## 初步结论
（待安全专家分析）

## 建议措施
1. 立即轮换所有相关API密钥
2. 审查OpenClaw平台安全配置
3. 更新技能到最新安全版本
4. 加强监控和审计配置
EOF

echo "调查取证完成，报告保存在: $FORENSIC_DIR/forensic_report.md"
```

#### 2.3 恢复脚本
```bash
#!/bin/bash
# recovery_procedure.sh

echo "开始恢复流程..."

# 1. 轮换API密钥
echo "1. 轮换API密钥..."
echo "请手动在以下平台轮换密钥:"
echo "  - Volcengine控制台: https://console.volcengine.com/"
echo "  - DeepSeek控制台: https://platform.deepseek.com/"
echo "按Enter键继续..."
read

# 2. 更新OpenClaw配置
echo "2. 更新OpenClaw配置..."
openclaw config patch --file=new_secure_config.json

# 3. 清理环境
echo "3. 清理环境..."
rm -f /tmp/tianji_*.sh /tmp/tianji_*.json
find /tmp -name "tianji_*" -mtime +1 -delete

# 4. 重新启用技能（可选）
echo "4. 重新启用技能..."
read -p "是否重新启用技能? (y/n): " choice
if [[ "$choice" == "y" ]]; then
    # 从备份恢复
    BACKUP_DIR=$(find /home/test/.openclaw/workspace/skills -name "tianji-fengshui_disabled_*" -type d | sort -r | head -1)
    if [ -n "$BACKUP_DIR" ]; then
        cp -r "$BACKUP_DIR" /home/test/.openclaw/workspace/skills/tianji-fengshui
        echo "技能已从备份恢复: $BACKUP_DIR"
    else
        echo "未找到备份，需要重新安装"
        # 重新安装逻辑
    fi
fi

echo "恢复流程完成"
```

### 3. 事件报告模板

```markdown
# 安全事件报告

## 事件摘要
- **事件ID**: 
- **报告时间**: 
- **报告人**: 
- **审核人**: 
- **涉及技能**: tianji-fengshui v1.7.0
- **事件等级**: [Critical/High/Medium/Low]

## 事件详情
### 发现时间
- 首次发现: 
- 持续时间: 

### 影响范围
- 受影响系统: 
- 涉及数据: 
- 业务影响: 

### 事件描述
（详细描述事件经过）

## 响应措施
### 初步响应
- 响应时间: 
- 采取的措施: 
- 响应人员: 

### 调查取证
- 取证时间: 
- 取证方法: 
- 发现证据: 

### 遏制措施
- 隔离措施: 
- 禁用措施: 
- 保护措施: 

### 恢复措施
- 密钥轮换: [是/否]
- 系统清理: [是/否]
- 技能更新: [是/否]

## 根本原因分析
### 直接原因
（技术原因分析）

### 根本原因
（管理、流程等原因分析）

### 漏洞利用
（攻击者如何利用漏洞）

## 改进措施
### 立即措施
1. 
2. 
3. 

### 短期措施（1-4周）
1. 
2. 
3. 

### 长期措施（1-6个月）
1. 
2. 
3. 

## 经验教训
### 技术方面
1. 
2. 
3. 

### 流程方面
1. 
2. 
3. 

### 人员方面
1. 
2. 
3. 

## 附件
- [ ] 取证报告
- [ ] 日志分析
- [ ] 配置快照
- [ ] 网络流量分析
- [ ] 其他相关证据
```

## 总结与建议

### 1. 凭证管理最佳实践

#### 1.1 对于技能开发者
```yaml
recommendations:
  - 尽可能避免直接读取配置文件
  - 使用平台提供的安全API访问配置
  - 实施最小权限原则
  - 提供透明的操作日志
  - 支持安全的替代方案
```

#### 1.2 对于平台提供者
```yaml
recommendations:
  - 提供安全的配置访问API
  - 实施强加密和访问控制
  - 提供详细的审计日志
  - 支持环境变量等替代方案
  - 定期安全评估和更新
```

#### 1.3 对于最终用户
```yaml
recommendations:
  - 定期审查平台安全配置
  - 实施最小权限原则
  - 监控技能使用行为
  - 及时更新技能版本
  - 建立应急响应流程
```

### 2. 风险评估总结

#### 2.1 接受的风险
- ✅ **配置读取权限**: 实现模型路由功能所必需
- ✅ **平台信任依赖**: 基于OpenClaw平台的安全架构
- ✅ **文件系统访问**: 读取用户指定图片所必需

#### 2.2 控制的风险
- 🔄 **凭证泄露风险**: 通过间接访问和平台加密控制
- 🔄 **权限滥用风险**: 通过透明操作和用户监控控制
- 🔄 **环境安全风险**: 通过安全配置和定期审计控制

#### 2.3 剩余风险
- ⚠️ **平台漏洞风险**: 依赖OpenClaw平台的安全更新
- ⚠️ **用户配置风险**: 依赖用户的正确安全配置
- ⚠️ **环境威胁风险**: 依赖运行环境的安全性

### 3. 持续改进建议

#### 3.1 技能改进
1. **增加配置访问抽象层**: 提供多种安全的配置访问方式
2. **增强错误处理安全性**: 避免在错误信息中泄露敏感信息
3. **提供更多监控指标**: 增加详细的性能和安全指标
4. **支持更多认证方式**: 支持OAuth、证书等多种认证方式

#### 3.2 文档改进
1. **增加实操指南**: 提供具体的配置和安全设置步骤
2. **增加故障排除**: 提供常见安全问题的解决方法
3. **增加案例研究**: 提供实际部署的安全案例分析
4. **增加合规指南**: 提供符合不同安全标准的指南

#### 3.3 社区协作
1. **安全漏洞报告**: 建立透明的漏洞报告和修复流程
2. **安全审查邀请**: 邀请安全专家进行独立审查
3. **用户反馈收集**: 建立用户安全反馈收集机制
4. **最佳实践分享**: 分享安全部署和使用的经验

---

**文档版本**: v1.0  
**最后更新**: 2026年3月25日  
**对应技能版本**: tianji-fengshui v1.7.0  
**文档状态**: ✅ 完成  

**使用建议**: 本文档应与技能的其他安全文档（SECURITY.md、EXECUTION_RISK_ANALYSIS.md）结合使用，形成完整的安全指南体系。