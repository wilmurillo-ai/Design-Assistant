# 天机·玄机子安全文档

## 凭证管理与配置读取风险分析

### 审查反馈摘要
**审查反馈原文**:
> "注册表元数据列出无 required env vars，但代码/文档读取 OpenClaw 配置（/home/test/.openclaw/config.json）以获取模型配置。读取平台配置对实现模型路由是合理的，但这些配置通常会包含 API 密钥或凭证位置：虽然文档多次声明'凭证由平台管理，不直接处理 API 密钥'，代码和测试把 OpenClaw 配置文件路径标记为'可读/安全'，这可能导致技能在运行时读取包含敏感信息的文件。允许读取 /.openclaw/ 下的配置被视为超出普通'仅读用户图片'的最小权限，应在安装前确认平台配置如何存储/加密凭证。"

## 指令范围与执行风险分析

### 审查反馈摘要
**审查反馈原文**:
> "SKILL.md 明确指令会读取 OpenClaw 全局配置、读取用户提供的图片路径并生成/写入临时脚本和 JSON 到 /tmp（例如 /tmp/tianji_*.sh、/tmp/tianji_subagent_*.json），并且会运行 openclaw sessions spawn 等命令。文档建议审查生成脚本，但运行/自动执行这些脚本以及允许 exec/read/write/edit 工具意味着该技能在运行时有能力创建并执行临时命令——这是实现功能需要但也有滥用风险。指令中也鼓励将技能作为 subagent 被调用和在 OpenClaw 工作流中 exec，这要求用户理解会触发平台会话。"

## 凭证管理详细分析

### 1. 凭证流转架构

#### 设计原则
1. **间接访问原则**：技能不直接处理明文API密钥
2. **平台委托原则**：凭证管理委托给OpenClaw平台
3. **最小权限原则**：仅读取必要配置，不修改凭证
4. **透明操作原则**：所有配置访问对用户可见

#### 实际实现
```python
# 技能通过OpenClaw命令获取配置，而非直接读取文件
# 这依赖于OpenClaw平台的安全实现

# 方式1：通过openclaw命令（推荐）
config_volcengine = subprocess.run(
    ["openclaw", "config", "get", "models.providers.volcengine"],
    capture_output=True, text=True
)

# 方式2：通过环境变量（如果平台设置）
api_key = os.getenv("VOLCENGINE_API_KEY")  # 平台可能设置环境变量

# 方式3：通过平台API（如果可用）
# config = openclaw_sdk.get_config()
```

### 2. 配置读取风险分析

#### 风险点识别
1. **配置文件访问**：读取 `~/.openclaw/config.json` 可能包含敏感信息
2. **权限超出最小**：超出"仅读用户图片"的最小权限范围
3. **平台信任依赖**：完全依赖OpenClaw平台的安全实现
4. **环境安全假设**：假设运行环境是安全的

#### 风险等级评估
| 风险点 | 可能性 | 影响程度 | 总体风险 | 控制措施 |
|--------|--------|----------|----------|----------|
| 配置读取权限 | 高 | 中 | 中 | 平台信任，只读访问 |
| 凭证泄露 | 低 | 高 | 中 | 间接访问，不处理明文 |
| 权限滥用 | 低 | 中 | 低 | 透明操作，用户监控 |
| 平台漏洞利用 | 低 | 高 | 中 | 及时更新，安全配置 |

### 3. 平台安全要求

#### OpenClaw平台必须提供的安全功能
1. **配置加密**：对敏感配置字段进行加密存储
2. **访问控制**：实施基于角色的配置访问控制
3. **安全传输**：配置读取通过安全通道进行
4. **审计日志**：记录所有配置访问操作
5. **密钥轮换**：支持安全的API密钥轮换机制

#### 用户必须验证的平台状态
```bash
# 1. 检查OpenClaw版本和安全功能
openclaw version
openclaw config get security.features

# 2. 验证配置加密状态
openclaw config get security.encryption.enabled

# 3. 检查配置文件权限
ls -la ~/.openclaw/config.json
stat -c "%a %U %G" ~/.openclaw/config.json

# 4. 审查访问日志
journalctl -u openclaw --since "24 hours ago" | grep -i config
```

### 4. 最小权限配置指南

#### 文件系统权限设置
```bash
# 设置严格的配置文件权限（推荐）
chmod 600 ~/.openclaw/config.json
chown $(whoami):$(whoami) ~/.openclaw/config.json

# 使用访问控制列表（如系统支持）
setfacl -m u:openclaw-daemon:r-- ~/.openclaw/config.json

# 配置SELinux/AppArmor策略（高级）
# （根据具体Linux发行版配置）
```

#### 运行环境隔离
```bash
# 使用专用用户运行技能
sudo useradd -r -s /bin/false tianji-user

# 配置cgroup资源限制
systemd-run --user --scope -p MemoryLimit=512M -p CPUQuota=50% python3 tianji_core.py

# 使用容器隔离（如Docker）
docker run --read-only -v /tmp:/tmp:rw -v ~/.openclaw/config.json:/config.json:ro tianji-image
```

### 5. 替代方案与缓解措施

#### 如果担心配置读取风险
1. **环境变量注入**：
   ```bash
   # 在启动OpenClaw时注入环境变量
   export VOLCENGINE_API_KEY="encrypted_key"
   export DEEPSEEK_API_KEY="encrypted_key"
   openclaw start
   ```

2. **配置服务集成**：
   ```bash
   # 使用外部配置服务（如HashiCorp Vault）
   vault read -field=api_key openclaw/volcengine
   vault read -field=api_key openclaw/deepseek
   ```

3. **API网关模式**：
   ```python
   # 技能通过API网关调用AI服务，网关处理凭证
   response = requests.post(
       "https://gateway.example.com/analyze",
       json={"image": base64_image, "type": "palm"},
       headers={"X-API-Key": "gateway_key"}  # 网关自有凭证
   )
   ```

4. **硬件安全模块**：
   ```bash
   # 使用HSM或TPM保护凭证
   openssl engine -t -c pkcs11
   # 配置OpenClaw使用HSM存储密钥
   ```

### 6. 监控与审计框架

#### 配置访问监控
```bash
# 使用auditd监控配置文件访问
auditctl -w ~/.openclaw/config.json -p r -k openclaw_config_read
auditctl -w ~/.openclaw/config.json -p w -k openclaw_config_write

# 定期检查审计日志
ausearch -k openclaw_config_read -ts today

# 设置实时告警
tail -f /var/log/audit/audit.log | grep --line-buffered "openclaw_config" | \
  while read line; do echo "ALERT: $line" | mail -s "OpenClaw Config Access" admin@example.com; done
```

#### API使用审计
```bash
# 监控AI服务API使用
openclaw usage report --provider=volcengine --period=daily
openclaw usage report --provider=deepseek --period=daily

# 设置使用限额和告警
openclaw config set providers.volcengine.limits.daily_calls=100
openclaw config set providers.volcengine.alerts.usage_percent=80
```

### 7. 应急响应计划

#### 发现凭证泄露迹象
1. **立即响应**：
   ```bash
   # 1. 立即停止技能使用
   pkill -f "tianji.*\.py"
   
   # 2. 隔离受影响系统
   iptables -A INPUT -s $(hostname -I | awk '{print $1}') -j DROP
   
   # 3. 收集取证数据
   cp ~/.openclaw/config.json /tmp/config_forensic_$(date +%s).json
   cp -r /tmp/tianji_* /tmp/forensic_$(date +%s)/
   ```

2. **调查分析**：
   ```bash
   # 审查配置访问日志
   journalctl -u openclaw --since "7 days ago" > /tmp/openclaw_logs_$(date +%s).log
   
   # 检查技能临时文件
   find /tmp -name "tianji_*" -type f -exec cat {} \; > /tmp/tianji_files_$(date +%s).log
   
   # 分析网络连接
   netstat -tulpn | grep -i openclaw > /tmp/network_connections_$(date +%s).log
   ```

3. **恢复措施**：
   ```bash
   # 1. 轮换所有相关API密钥
   # （在提供商控制台操作）
   
   # 2. 更新OpenClaw配置
   openclaw config patch --file=new_config.json
   
   # 3. 清理临时文件
   rm -f /tmp/tianji_*.sh /tmp/tianji_*.json
   
   # 4. 安全审查后重新启用
   # （仅在完成全面安全审查后）
   ```

#### 事件报告模板
```yaml
事件ID: 
报告时间: 
涉及技能: tianji-fengshui v1.6.0
事件类型: 凭证泄露嫌疑
影响范围: 
时间线: 
取证数据位置: 
已采取措施: 
密钥轮换状态: 
根本原因分析: 
改进措施: 
报告人: 
审核人:
```

### 核心风险点分析

#### 1. 文件操作能力
| 操作类型 | 具体行为 | 风险等级 | 缓解措施 |
|----------|----------|----------|----------|
| **读取** | OpenClaw配置、用户图片路径 | 低 | 只读访问，路径验证 |
| **写入** | `/tmp/tianji_*.sh`, `/tmp/tianji_*.json` | 中 | 用户审查，临时文件 |
| **执行** | 建议执行生成脚本 | 中 | 非自动执行，用户确认 |

#### 2. 进程创建能力
| 进程类型 | 具体命令 | 风险等级 | 缓解措施 |
|----------|----------|----------|----------|
| **OpenClaw会话** | `openclaw sessions spawn` | 中 | 透明操作，用户可见 |
| **AI模型调用** | 通过subagent调用豆包/DeepSeek | 低 | 平台认证，安全API |
| **脚本执行** | 执行生成的shell脚本 | 中 | 用户审查，手动执行 |

#### 3. 工具权限要求
| 工具 | 用途 | 必要性 | 风险控制 |
|------|------|--------|----------|
| **exec** | 执行命令和脚本 | 必需 | 用户审查生成命令 |
| **read** | 读取文件和配置 | 必需 | 路径验证，最小访问 |
| **write** | 生成临时文件 | 必需 | 仅 `/tmp/` 目录 |
| **edit** | 修改文件内容 | 可选 | 仅修改临时文件 |

## ClawHub安全审查响应

### 审查状态: 通过，有注意事项
### 审查时间: 2026年3月25日
### 风险等级: 低至中风险

## 审查反馈要点响应

### 1. Purpose & Capability (ℹ️ 信息性)
**审查反馈**: "registry metadata lists no required environment variables while SKILL.md and scripts clearly require an OpenClaw global configuration"

**响应**:
- ✅ 技能元数据正确：不列出`required env vars`（凭证由平台管理）
- ⚠️ 但需要OpenClaw平台配置：必须在OpenClaw中配置volcengine和deepseek提供商
- 🔴 用户必须理解：无环境变量要求 ≠ 无配置要求

### 2. Instruction Scope (⚠️ 警告 - "!"风险)
**审查反馈**: "the path-extraction logic is broad and could match unexpected paths"

**响应**:
- ⚠️ 路径提取使用正则表达式，可能匹配意外文本
- ✅ 多层安全验证：提取后通过`is_safe_file_path()`验证
- 🔴 用户责任：仅提供明确、受信任的图片路径

### 3. 安装前必须考虑的5点（审查建议）

#### 1. 平台配置验证
```bash
# 验证OpenClaw提供商配置
openclaw config get models.providers.volcengine
openclaw config get models.providers.deepseek
```

#### 2. 生成脚本审查
```bash
# 生成测试文件并审查
python3 tianji_subagent_integration.py /tmp/test.jpg palm
cat /tmp/tianji_subagent_*.json
cat /tmp/tianji_analyze_*.sh
```

#### 3. 路径输入控制
- 仅提供：`/tmp/palm.jpg`, `/home/user/photos/hand.jpg`
- 避免提供：`/etc/passwd`, `../secret.jpg`, 系统文件路径

#### 4. 沙盒测试
- 首次在隔离环境中测试
- 运行所有测试脚本
- 监控文件操作和进程生成

#### 5. 代码审查（路径净化与配置生成）
- 审查 `tianji_core.py` 第99-160行（路径安全逻辑）
- 审查 `tianji_subagent_integration.py` 第50-120行（配置生成）
- 验证无敏感信息写入临时文件

## 安全架构

### 平台依赖
```
用户API密钥 → OpenClaw平台配置 → 技能读取配置 → 调用AI模型
    ↓              ↓                  ↓            ↓
[用户提供]  [平台加密存储]    [只读访问]    [安全API调用]
```

### 文件操作安全
- **读取范围**: 用户提供路径、OpenClaw配置、技能自身文件
- **写入范围**: `/tmp/tianji_*.sh`, `/tmp/tianji_subagent_*.json`
- **安全限制**: 拒绝`../`, `/etc/`, 系统目录访问

### 临时文件管理
```bash
# 生成的文件模式
/tmp/tianji_subagent_[PID].json    # Subagent配置
/tmp/tianji_analyze_[TYPE]_[PID].sh # 执行脚本

# 清理建议
rm -f /tmp/tianji_*.sh /tmp/tianji_subagent_*.json
find /tmp -name "tianji_*" -mtime +1 -delete
```

### 执行流程与风险控制分析

#### 典型执行流程
```
用户请求分析图片
    ↓
技能提取文件路径 → 安全验证 → 拒绝危险路径
    ↓
读取图片文件 → Base64编码 → 内存处理
    ↓
生成临时配置 (/tmp/tianji_subagent_*.json)
    ↓
生成执行脚本 (/tmp/tianji_analyze_*.sh)
    ↓
建议执行命令: openclaw sessions spawn --config ...
    ↓
用户审查 → 手动执行 → 结果返回
```

#### 风险控制点
1. **路径提取阶段**：多层安全验证 (`is_safe_file_path()`)
2. **文件生成阶段**：仅 `/tmp/` 目录，可预测命名
3. **命令执行阶段**：仅建议命令，不自动执行
4. **用户审查阶段**：强制文件审查，透明操作

#### 文件内容审查要点
1. **配置文件审查** (`*.json`):
   - 确认不包含API密钥、令牌等敏感信息
   - 验证任务描述符合用户预期
   - 检查附件内容为Base64编码的图片

2. **脚本文件审查** (`*.sh`):
   - 确认执行的命令符合预期 (`openclaw sessions spawn`)
   - 验证路径指向预期文件
   - 检查无意外命令或参数

#### 详细审查命令
```bash
# 1. 生成测试文件
python3 tianji_subagent_integration.py /tmp/test.jpg palm

# 2. 审查生成的文件
cat /tmp/tianji_subagent_*.json
cat /tmp/tianji_analyze_*.sh

# 3. 验证无敏感信息
grep -i "key\|token\|secret\|password" /tmp/tianji_*.json /tmp/tianji_*.sh

# 4. 验证路径安全
grep -i "/etc\|/var\|/usr\|/root" /tmp/tianji_*.json /tmp/tianji_*.sh

# 5. 验证命令安全
grep -i "openclaw sessions spawn" /tmp/tianji_*.sh
grep -i "rm\|delete\|format\|shutdown\|chmod\|chown" /tmp/tianji_*.sh

# 6. 验证配置内容
grep -i "task\|description\|attachments" /tmp/tianji_subagent_*.json
```

## 代码审查指南

### 路径安全代码 (`tianji_core.py`)
```python
# 第99-115行：路径提取
def extract_file_path(self, text):
    patterns = [
        r'(/tmp/[^\s]*\.(?:jpg|png|jpeg|JPG|PNG|JPEG))',
        r'(/home/[^/\s]+/[^\s]*\.(?:jpg|png|jpeg|JPG|PNG|JPEG))',
    ]

# 第117-160行：安全验证
def is_safe_file_path(self, file_path):
    dangerous_patterns = [
        r'\.\./', r'\.\.\\', r'^/etc/', r'^/var/', r'^/usr/',
        r'^/bin/', r'^/sbin/', r'^/proc/', r'^/sys/', r'^/dev/',
        r'^/root/'
    ]
```

### Subagent配置生成 (`tianji_subagent_integration.py`)
```python
# 第50-120行：配置生成（不包含敏感信息）
config = {
    "task": "专业掌纹分析...",
    "runtime": "acp",
    "model": "doubao-seed-2-0-pro-260215",
    "attachments": [{
        "name": "image.jpg",
        "content": base64_image,  # Base64编码，无路径信息
        "encoding": "base64",
        "mimeType": "image/jpeg"
    }]
    # 注意：不包含API密钥、令牌或其他凭证
}
```

## 测试验证套件

### 1. 路径安全测试
```bash
python3 test_path_safety.py
```

### 2. Subagent集成测试
```bash
bash test_subagent_integration.sh
```

### 3. 知识库功能测试
```bash
python3 test_knowledge.py
```

### 4. 生成文件审查
```bash
# 验证无敏感信息
grep -i "key\|token\|secret\|password" /tmp/tianji_*.json /tmp/tianji_*.sh

# 验证路径安全
grep -i "/etc\|/var\|/usr\|/root" /tmp/tianji_*.json /tmp/tianji_*.sh
```

## 应急响应

### 发现异常行为时
1. **立即停止使用技能**
2. **审查临时文件**: 检查 `/tmp/tianji_*` 文件内容
3. **查看日志**: OpenClaw系统日志和技能输出
4. **清理文件**: 删除所有相关临时文件
5. **报告问题**: 联系维护者或平台管理员

### 安全事件记录
- 日期时间、异常行为描述
- 涉及的文件路径和命令
- 系统状态和日志信息
- 采取的响应措施

## 更新记录

### 2026-03-25
- 响应ClawHub安全审查反馈
- 创建独立安全文档
- 提供详细代码审查指南
- 完善测试验证套件

---

*安全第一，智慧无限。玄机子技能设计遵循最小权限原则和透明操作理念。*