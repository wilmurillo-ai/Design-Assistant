# 天机·玄机子持久性与权限文档

## 文档概述
本文档详细说明天机·玄机子技能的持久性设置、权限范围、执行边界和安全控制，响应ClawHub审查反馈的持久性与权限问题。

## 审查反馈摘要
**审查反馈原文**:
> "技能未设置 always:true（默认允许自主调用），没有请求修改其他技能或系统设置，但 SKILL.md 和代码允许生成并（通过建议/示例）执行临时脚本和 spawn OpenClaw sessions。生成/执行临时脚本是其功能的一部分，但把 exec/read/write/edit 列为 allowed-tools 意味着技能在有权限时可以创建/修改文件并运行命令——这在功能上是必要，但增加了风险边界，建议限制在受控环境或人工确认后执行。"

## 持久性设置分析

### 1. 持久性配置状态

#### 1.1 当前配置分析
```yaml
persistence_configuration:
  always_enabled: false
  invocation_mode: "user_invoked_only"
  auto_start: false
  background_service: false
  scheduled_execution: false
```

#### 1.2 安全含义
- ✅ **非持久化运行**：技能不会在后台持续运行
- ✅ **用户触发执行**：仅当用户明确调用时执行
- ✅ **无自动启动**：系统重启后不会自动启动
- ✅ **无计划任务**：不会创建定时执行任务

#### 1.3 用户影响
- **安全优势**：减少攻击面，防止未经授权执行
- **使用影响**：用户需要主动调用技能
- **资源影响**：不占用持续的系统资源
- **监控影响**：执行行为明确，易于审计

### 2. 权限范围分析

#### 2.1 系统修改权限
```yaml
system_modification_permissions:
  system_settings: "none"
  system_files: "none"
  system_services: "none"
  network_configuration: "none"
  user_accounts: "none"
```

#### 2.2 技能修改权限
```yaml
skill_modification_permissions:
  other_skills: "none"
  skill_configurations: "none"
  skill_files: "read_only_own"
  skill_registry: "none"
```

#### 2.3 文件系统权限
```yaml
filesystem_permissions:
  read_access:
    - "user_provided_image_paths"
    - "openclaw_configuration"
    - "own_skill_files"
  write_access:
    - "/tmp/tianji_*.sh"
    - "/tmp/tianji_subagent_*.json"
  delete_access:
    - "own_temporary_files"
  execute_access:
    - "generated_scripts_with_confirmation"
```

## 工具权限风险分析

### 1. 工具权限详细分析

#### 1.1 exec 工具权限
```yaml
exec_tool_permissions:
  necessity: "required"
  risk_level: "high"
  usage_scenarios:
    - "openclaw sessions spawn"
    - "shell_command_execution"
    - "subprocess_creation"
  risk_controls:
    - "user_confirmation_required"
    - "command_validation"
    - "execution_auditing"
    - "environment_restriction"
```

#### 1.2 read 工具权限
```yaml
read_tool_permissions:
  necessity: "required"
  risk_level: "medium"
  usage_scenarios:
    - "image_file_reading"
    - "configuration_reading"
    - "script_file_reading"
  risk_controls:
    - "path_validation"
    - "content_sanitization"
    - "access_logging"
    - "size_limitation"
```

#### 1.3 write 工具权限
```yaml
write_tool_permissions:
  necessity: "required"
  risk_level: "medium"
  usage_scenarios:
    - "temporary_script_generation"
    - "configuration_file_generation"
    - "log_file_writing"
  risk_controls:
    - "location_restriction:/tmp/"
    - "filename_pattern:tianji_*"
    - "content_validation"
    - "user_review_requirement"
```

#### 1.4 edit 工具权限
```yaml
edit_tool_permissions:
  necessity: "optional"
  risk_level: "low"
  usage_scenarios:
    - "temporary_file_modification"
    - "configuration_adjustment"
  risk_controls:
    - "own_files_only"
    - "backup_creation"
    - "change_logging"
    - "rollback_capability"
```

### 2. 风险边界扩展分析

#### 2.1 审查反馈关键点分析
> "生成/执行临时脚本是其功能的一部分，但把 exec/read/write/edit 列为 allowed-tools 意味着技能在有权限时可以创建/修改文件并运行命令——这在功能上是必要，但增加了风险边界"

#### 2.2 风险扩展维度
```yaml
risk_boundary_expansion:
  file_operations:
    from: "read_user_files"
    to: "create_executable_scripts"
    risk_increase: "medium"
    
  process_operations:
    from: "none"
    to: "spawn_subprocesses"
    risk_increase: "high"
    
  system_interaction:
    from: "minimal"
    to: "platform_api_calls"
    risk_increase: "medium"
    
  persistence:
    from: "none"
    to: "temporary_file_creation"
    risk_increase: "low"
```

#### 2.3 风险控制策略
```yaml
risk_control_strategy:
  layered_defense:
    - "prevention: input_validation"
    - "detection: behavior_monitoring"
    - "response: incident_handling"
    - "recovery: system_restoration"
    
  principle_implementation:
    - "least_privilege: minimal_required_permissions"
    - "defense_in_depth: multiple_control_layers"
    - "separation_of_duties: user_confirmation_required"
    - "fail_safe: default_deny_unless_explicitly_allowed"
```

## 受控环境实施指南

### 1. 环境分类与配置

#### 1.1 环境分类标准
```yaml
environment_classification:
  development:
    purpose: "代码开发和功能测试"
    security_level: "low"
    isolation: "minimal"
    monitoring: "basic"
    recommended_for: "developers_only"
    
  testing:
    purpose: "功能测试和安全验证"
    security_level: "medium"
    isolation: "sandbox"
    monitoring: "standard"
    recommended_for: "qa_teams"
    
  staging:
    purpose: "集成测试和性能验证"
    security_level: "high"
    isolation: "container"
    monitoring: "enhanced"
    recommended_for: "devops_teams"
    
  production:
    purpose: "最终用户使用"
    security_level: "maximum"
    isolation: "full"
    monitoring: "comprehensive"
    recommended_for: "end_users_with_caution"
```

#### 1.2 环境选择决策流程
```
开始环境选择
    ↓
评估使用场景
    ├─ 开发新功能 → 选择development环境
    ├─ 测试现有功能 → 选择testing环境
    ├─ 验证集成 → 选择staging环境
    └─ 生产部署 → 选择production环境
          ↓
    实施对应安全控制
          ↓
    定期安全评估
```

### 2. 沙盒环境配置

#### 2.1 基础沙盒配置
```bash
#!/bin/bash
# setup_sandbox_environment.sh

echo "设置沙盒环境..."

# 1. 创建专用用户
SANDBOX_USER="tianji-sandbox"
sudo useradd -r -s /bin/false "$SANDBOX_USER"
echo "创建用户: $SANDBOX_USER"

# 2. 创建沙盒目录
SANDBOX_DIR="/var/sandbox/tianji"
sudo mkdir -p "$SANDBOX_DIR"
sudo chown "$SANDBOX_USER:$SANDBOX_USER" "$SANDBOX_DIR"
sudo chmod 750 "$SANDBOX_DIR"
echo "创建沙盒目录: $SANDBOX_DIR"

# 3. 设置资源限制
cat > /etc/systemd/system/tianji-sandbox.service << EOF
[Service]
User=$SANDBOX_USER
Group=$SANDBOX_USER
WorkingDirectory=$SANDBOX_DIR
ExecStart=/usr/bin/python3 /path/to/tianji_core.py
MemoryLimit=512M
CPUQuota=50%
IOWeight=100
BlockIOWeight=100
PrivateTmp=yes
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictNamespaces=yes
RestrictRealtime=yes
SystemCallFilter=@system-service
SystemCallArchitectures=native
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
EOF

# 4. 启用服务
sudo systemctl daemon-reload
echo "沙盒环境设置完成"
```

#### 2.2 容器化部署
```dockerfile
# Dockerfile for Tianji Fengshui
FROM python:3.9-slim AS builder

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -r -s /bin/false tianji

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置权限
RUN chown -R tianji:tianji /app

# 运行时阶段
FROM python:3.9-slim

# 创建运行时用户
RUN useradd -r -s /bin/false tianji

# 从构建阶段复制已安装的包
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app /app

WORKDIR /app

# 设置权限
RUN chown -R tianji:tianji /app
USER tianji

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import sys; sys.exit(0)"

# 运行命令
CMD ["python3", "tianji_core.py"]
```

#### 2.3 容器运行配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  tianji-fengshui:
    build: .
    container_name: tianji-fengshui
    user: "1000:1000"  # 非root用户
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=100M
    volumes:
      - ./config:/config:ro
      - ./logs:/logs:rw
    environment:
      - OPENCLAW_CONFIG_PATH=/config/openclaw.json
      - LOG_LEVEL=INFO
    networks:
      - tianji-network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.1'
          memory: 128M
    security_opt:
      - no-new-privileges:true
      - seccomp:unconfined
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

networks:
  tianji-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 3. 权限最小化配置

#### 3.1 Linux权限配置
```bash
#!/bin/bash
# setup_minimal_permissions.sh

echo "设置最小权限..."

# 1. 技能文件权限
SKILL_DIR="/home/test/.openclaw/workspace/skills/tianji-fengshui"
sudo chmod -R 555 "$SKILL_DIR"  # 只读执行
sudo chown -R root:root "$SKILL_DIR"  # root所有

# 2. 临时目录权限
sudo chmod 1777 /tmp  # sticky bit，防止删除他人文件

# 3. 日志目录权限
LOG_DIR="/var/log/tianji"
sudo mkdir -p "$LOG_DIR"
sudo chmod 733 "$LOG_DIR"  # 所有者读写执行，组和其他写执行
sudo chown tianji-sandbox:tianji-sandbox "$LOG_DIR"

# 4. 配置文件权限
CONFIG_FILE="$HOME/.openclaw/config.json"
chmod 400 "$CONFIG_FILE"  # 只读

# 5. 设置Linux能力
sudo setcap -r /usr/bin/python3  # 移除所有特权
sudo setcap cap_net_bind_service=ep /usr/bin/python3  # 仅允许绑定端口

echo "最小权限设置完成"
```

#### 3.2 SELinux/AppArmor配置
```bash
#!/bin/bash
# setup_mac_security.sh

echo "设置强制访问控制..."

# 1. 检查SELinux状态
if command -v sestatus >/dev/null 2>&1; then
    echo "配置SELinux策略..."
    # 创建SELinux策略模块
    cat > tianji.te << EOF
module tianji 1.0;

require {
    type unconfined_t;
    type tmp_t;
    type var_log_t;
    class file { read write create open unlink };
    class dir { search add_name write remove_name };
}

# 允许访问临时文件
allow unconfined_t tmp_t:file { read write create open unlink };
allow unconfined_t tmp_t:dir { search add_name write remove_name };

# 允许访问日志
allow unconfined_t var_log_t:file { read write create open };
allow unconfined_t var_log_t:dir { search add_name write };
EOF
    
    checkmodule -M -m -o tianji.mod tianji.te
    semodule_package -o tianji.pp -m tianji.mod
    sudo semodule -i tianji.pp
fi

# 2. 检查AppArmor状态
if command -v aa-status >/dev/null 2>&1; then
    echo "配置AppArmor策略..."
    # 创建AppArmor配置文件
    sudo cat > /etc/apparmor.d/usr.bin.tianji << EOF
#include <tunables/global>

/usr/bin/python3 {
  #include <abstractions/base>
  #include <abstractions/python>
  
  # 技能文件访问
  /home/test/.openclaw/workspace/skills/tianji-fengshui/** r,
  
  # 临时文件访问
  /tmp/tianji_* rw,
  /tmp/ rw,
  
  # 日志文件访问
  /var/log/tianji/* rw,
  
  # 网络访问
  network inet tcp,
  network inet6 tcp,
  
  # 拒绝其他访问
  deny /etc/** r,
  deny /var/** r,
  deny /usr/** r,
  deny /bin/** r,
  deny /sbin/** r,
}
EOF
    
    sudo apparmor_parser -r /etc/apparmor.d/usr.bin.tianji
fi

echo "强制访问控制设置完成"
```

#### 3.3 网络权限控制
```bash
#!/bin/bash
# setup_network_restrictions.sh

echo "设置网络权限控制..."

# 1. 创建专用网络命名空间
sudo ip netns add tianji-ns
sudo ip link add veth-tianji type veth peer name veth-host
sudo ip link set veth-tianji netns tianji-ns
sudo ip netns exec tianji-ns ip addr add 10.0.0.2/24 dev veth-tianji
sudo ip netns exec tianji-ns ip link set veth-tianji up
sudo ip netns exec tianji-ns ip link set lo up
sudo ip addr add 10.0.0.1/24 dev veth-host
sudo ip link set veth-host up

# 2. 配置网络策略
sudo iptables -A FORWARD -i veth-host -o eth0 -j ACCEPT
sudo iptables -A FORWARD -i eth0 -o veth-host -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -t nat -A POSTROUTING -s 10.0.0.0/24 -o eth0 -j MASQUERADE

# 3. 限制出站连接
sudo iptables -A OUTPUT -m owner --uid-owner tianji-sandbox -p tcp -d api.deepseek.com --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -m owner --uid-owner tianji-sandbox -p tcp -d ark.cn-beijing.volces.com --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -m owner --uid-owner tianji-sandbox -p tcp -j REJECT --reject-with tcp-reset

# 4. 配置DNS限制
echo "nameserver 8.8.8.8" | sudo tee /etc/netns/tianji-ns/resolv.conf
sudo ip netns exec tianji-ns echo "options timeout:1 attempts:1" >> /etc/netns/tianji-ns/resolv.conf

echo "网络权限控制设置完成"
```

## 人工确认与执行控制

### 1. 人工确认流程设计

#### 1.1 确认级别定义
```yaml
confirmation_levels:
  none:
    description: "无需确认，自动执行"
    risk_level: "high"
    usage: "不推荐"
    
  basic:
    description: "简单确认（是/否）"
    risk_level: "medium"
    usage: "低风险操作"
    
  detailed:
    description: "详细确认（显示命令详情）"
    risk_level: "low"
    usage: "中风险操作"
    
  expert:
    description: "专家确认（显示完整上下文）"
    risk_level: "very_low"
    usage: "高风险操作"
```

#### 1.2 确认流程实现
```python
# confirmation_system.py
import datetime
import hashlib
import json
from typing import Dict, Any

class ConfirmationSystem:
    """人工确认系统"""
    
    def __init__(self, log_file: str = "/var/log/tianji/confirmations.log"):
        self.log_file = log_file
        self.confirmation_history = []
        
    def require_confirmation(self, 
                           operation: str, 
                           command: str, 
                           context: Dict[str, Any],
                           level: str = "detailed") -> bool:
        """要求人工确认"""
        
        # 生成操作ID
        operation_id = hashlib.sha256(
            f"{operation}{command}{datetime.datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        
        # 显示确认信息
        self._display_confirmation(operation, command, context, level, operation_id)
        
        # 获取用户输入
        response = self._get_user_response(level)
        
        # 记录确认结果
        self._log_confirmation(
            operation_id, operation, command, context, level, response
        )
        
        return response == "yes"
    
    def _display_confirmation(self, operation, command, context, level, operation_id):
        """显示确认信息"""
        print(f"\n{'='*60}")
        print(f"⚠️  需要人工确认 (ID: {operation_id})")
        print(f"{'='*60}")
        print(f"操作: {operation}")
        print(f"时间: {datetime.datetime.now()}")
        
        if level in ["detailed", "expert"]:
            print(f"\n命令详情:")
            print(f"  {command}")
            
        if level == "expert":
            print(f"\n完整上下文:")
            for key, value in context.items():
                print(f"  {key}: {value}")
        
        print(f"\n确认级别: {level}")
        print(f"{'='*60}")
    
    def _get_user_response(self, level):
        """获取用户响应"""
        if level == "none":
            return "yes"
        
        prompt = "确认执行? "
        if level == "expert":
            prompt = "请仔细审查上述信息，确认执行? "
        
        while True:
            response = input(f"{prompt}(yes/no/details): ").strip().lower()
            if response in ["yes", "no"]:
                return response
            elif response == "details" and level != "expert":
                # 显示更多详情
                print("显示更多详情...")
                # 实现详情显示逻辑
            else:
                print("请输入 'yes' 或 'no'")
    
    def _log_confirmation(self, operation_id, operation, command, context, level, response):
        """记录确认结果"""
        log_entry = {
            "id": operation_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "operation": operation,
            "command": command[:500],  # 限制长度
            "context_keys": list(context.keys()),
            "level": level,
            "response": response,
            "user": os.getenv("USER", "unknown")
        }
        
        # 保存到文件
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # 保存到内存历史
        self.confirmation_history.append(log_entry)
        
        # 如果确认，可以触发执行
        if response == "yes":
            print(f"✅ 已确认，操作ID: {operation_id}")
        else:
            print(f"❌ 已取消，操作ID: {operation_id}")

# 使用示例
confirmation = ConfirmationSystem()

# 在执行危险操作前调用
if confirmation.require_confirmation(
    operation="OpenClaw会话创建",
    command="openclaw sessions spawn --config /tmp/tianji_subagent_12345.json",
    context={
        "image_path": "/tmp/palm.jpg",
        "analysis_type": "palm",
        "model": "doubao-seed-2-0-pro-260215",
        "estimated_cost": "0.05 USD"
    },
    level="detailed"
):
    # 执行命令
    execute_command("openclaw sessions spawn --config /tmp/tianji_subagent_12345.json")
```

### 2. 执行控制策略

#### 2.1 基于风险的执行控制
```python
# execution_controller.py
import re
from typing import List, Tuple

class ExecutionController:
    """执行控制器"""
    
    def __init__(self):
        self.allowed_patterns = [
            r"^openclaw sessions spawn --config /tmp/tianji_subagent_\d+\.json$",
            r"^python3 tianji_core.py .*$",
            r"^python3 tianji_subagent_integration.py .*$",
        ]
        
        self.blocked_patterns = [
            r".*rm.*-rf.*",
            r".*format.*",
            r".*shutdown.*",
            r".*chmod.*777.*",
            r".*chown.*root.*",
            r".*wget.*http://.*",
            r".*curl.*http://.*",
            r".*nc.*-l.*-p.*",
            r".*python.*-c.*import.*os.*system.*",
        ]
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """验证命令是否允许执行"""
        
        # 检查是否匹配允许模式
        for pattern in self.allowed_patterns:
            if re.match(pattern, command):
                return True, "命令匹配允许模式"
        
        # 检查是否匹配阻止模式
        for pattern in self.blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False, f"命令匹配阻止模式: {pattern}"
        
        # 默认阻止
        return False, "命令不在允许列表中，需要额外确认"
    
    def execute_with_control(self, command: str, context: dict) -> bool:
        """受控执行命令"""
        
        # 验证命令
        is_valid, reason = self.validate_command(command)
        
        if not is_valid:
            print(f"❌ 命令验证失败: {reason}")
            
            # 即使验证失败，也可以请求人工确认
            confirmation = input("命令验证失败，是否强制执行? (yes/no): ").strip().lower()
            if confirmation != "yes":
                return False
        
        # 记录执行
        self._log_execution(command, context, is_valid, reason)
        
        # 执行命令
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # 记录结果
            self._log_result(command, result)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("⏰ 命令执行超时")
            return False
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")
            return False
    
    def _log_execution(self, command, context, is_valid, reason):
        """记录执行信息"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "command": command,
            "context": context,
            "validated": is_valid,
            "validation_reason": reason,
            "user": os.getenv("USER", "unknown")
        }
        
        with open("/var/log/tianji/executions.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def _log_result(self, command, result):
        """记录执行结果"""
        result_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "command": command,
            "returncode": result.returncode,
            "stdout_length": len(result.stdout),
            "stderr_length": len(result.stderr),
            "success": result.returncode == 0
        }
        
        with open("/var/log/tianji/results.log", "a") as f:
            f.write(json.dumps(result_entry) + "\n")

# 使用示例
controller = ExecutionController()

# 受控执行命令
success = controller.execute_with_control(
    command="openclaw sessions spawn --config /tmp/tianji_subagent_12345.json",
    context={
        "purpose": "掌纹分析",
        "image": "/tmp/palm.jpg",
        "requested_by": "user123"
    }
)

if success:
    print("✅ 命令执行成功")
else:
    print("❌ 命令执行失败")
```

## 监控与审计配置

### 1. 综合监控系统

#### 1.1 监控配置
```yaml
monitoring_configuration:
  file_operations:
    enabled: true
    paths:
      - "/tmp/tianji_*"
      - "~/.openclaw/config.json"
    events: ["create", "modify", "delete"]
    
  process_operations:
    enabled: true
    commands:
      - "openclaw"
      - "python3.*tianji"
    events: ["start", "exit"]
    
  network_operations:
    enabled: true
    destinations:
      - "api.deepseek.com"
      - "ark.cn-beijing.volces.com"
    protocols: ["tcp"]
    
  resource_usage:
    enabled: true
    metrics:
      - "cpu_percent"
      - "memory_rss"
      - "file_descriptors"
    thresholds:
      cpu: 80
      memory: 512
      fd: 100
```

#### 1.2 审计配置
```yaml
audit_configuration:
  log_retention:
    days: 90
    compression: true
    encryption: true
    
  alerting:
    enabled: true
    channels:
      - "email"
      - "slack"
      - "webhook"
    
  compliance:
    standards:
      - "nist_800_53"
      - "iso_27001"
      - "gdpr"
    reporting:
      frequency: "monthly"
      format: "pdf"
```

### 2. 应急响应计划

#### 2.1 事件响应流程
```
发现安全事件
    ↓
初步分类定级
    ↓
启动应急响应
    ↓
遏制影响扩散
    ↓
调查取证分析
    ↓
根除威胁来源
    ↓
恢复系统正常
    ↓
总结改进措施
```

#### 2.2 响应工具包
```bash
#!/bin/bash
# emergency_response_toolkit.sh

# 应急响应工具包
# 用法: ./emergency_response_toolkit.sh <action> [options]

ACTION=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FORENSIC_DIR="/tmp/forensic_$TIMESTAMP"

case $ACTION in
    "contain")
        echo "执行初步遏制..."
        # 停止技能进程
        pkill -f "tianji.*\.py"
        pkill -f "python.*tianji"
        
        # 隔离网络
        iptables -A INPUT -s $(hostname -I | awk '{print $1}') -j DROP
        
        # 保护证据
        mkdir -p "$FORENSIC_DIR"
        cp ~/.openclaw/config.json "$FORENSIC_DIR/"
        cp -r /tmp/tianji_* "$FORENSIC_DIR/" 2>/dev/null
        
        echo "初步遏制完成，取证数据保存在: $FORENSIC_DIR"
        ;;
        
    "investigate")
        echo "开始调查取证..."
        # 收集系统信息
        uname -a > "$FORENSIC_DIR/system_info.txt"
        whoami >> "$FORENSIC_DIR/system_info.txt"
        
        # 收集进程信息
        ps aux | grep -i tianji > "$FORENSIC_DIR/processes.txt"
        
        # 收集网络连接
        netstat -tulpn | grep -i python > "$FORENSIC_DIR/network.txt"
        
        # 收集日志
        journalctl -u openclaw --since "7 days ago" > "$FORENSIC_DIR/logs.txt"
        
        echo "调查取证完成"
        ;;
        
    "recover")
        echo "开始恢复流程..."
        # 清理临时文件
        rm -f /tmp/tianji_*.sh /tmp/tianji_*.json
        
        # 禁用技能
        mv /home/test/.openclaw/workspace/skills/tianji-fengshui \
           /home/test/.openclaw/workspace/skills/tianji-fengshui_disabled_$TIMESTAMP
        
        echo "恢复流程完成，技能已禁用"
        ;;
        
    "report")
        echo "生成事件报告..."
        # 生成报告模板
        cat > "$FORENSIC_DIR/incident_report.md" << EOF
# 安全事件报告

## 事件摘要
- 事件ID: $TIMESTAMP
- 报告时间: $(date)
- 涉及技能: tianji-fengshui v1.8.0
- 响应人员: $(whoami)

## 响应措施
### 遏制措施
- 停止技能进程: $(date)
- 隔离网络: $(date)
- 保护证据: $(date)

### 调查发现
（待填写）

### 恢复措施
- 清理临时文件: $(date)
- 禁用技能: $(date)

## 改进建议
1. 
2. 
3. 
EOF
        
        echo "事件报告生成完成: $FORENSIC_DIR/incident_report.md"
        ;;
        
    *)
        echo "用法: $0 <contain|investigate|recover|report>"
        exit 1
        ;;
esac
```

## 总结与建议

### 1. 部署建议总结

#### 1.1 环境选择建议
- **开发测试**：使用沙盒环境，基础监控
- **功能验证**：使用容器环境，标准监控
- **生产部署**：使用完全隔离环境，全面监控

#### 1.2 安全控制建议
1. **始终实施最小权限原则**
2. **强制人工确认高风险操作**
3. **实施多层防御策略**
4. **建立完整的监控审计体系**
5. **准备应急响应能力**

#### 1.3 用户教育建议
1. **提供详细的安全使用指南**
2. **定期进行安全培训**
3. **建立安全反馈机制**
4. **分享最佳实践案例**

### 2. 持续改进路线图

#### 2.1 短期改进（1-3个月）
1. 完善自动化安全测试
2. 增强实时监控能力
3. 优化人工确认流程
4. 提供更多部署模板

#### 2.2 中期改进（3-6个月）
1. 集成更多安全工具
2. 实现自动化合规检查
3. 建立安全评分系统
4. 提供安全态势仪表板

#### 2.3 长期愿景（6-12个月）
1. 实现零信任安全架构
2. 建立威胁情报集成
3. 提供AI驱动的安全分析
4. 形成安全开发生命周期

---

**文档版本**: v1.0  
**最后更新**: 2026年3月25日  
**对应技能版本**: tianji-fengshui v1.8.0  
**文档状态**: ✅ 完成  

**使用建议**: 本文档应与技能的其他安全文档结合使用，形成完整的安全控制体系。建议根据实际部署环境选择适当的安全控制措施。