# 配置指南

## 快速配置流程

### 1. 安装 mcporter

```bash
npm install -g mcporter
mcporter --version
```

### 2. 申请 JY_API_KEY

**申请邮箱：** datamap@gildata.com

**邮件标题：** 数据地图 KEY 申请-XX 公司 - 申请人姓名

**邮件正文模板：**
```
姓名：张三
手机号：13800138000
公司/单位全称：XX 科技有限公司
所属部门：技术部
岗位：工程师
MCP_KEY 申请用途：OpenClaw Skill 政策解读
Skill 申请列表：jy-policy-interpretation
是否需要 Skill 安装包：否，自行下载
```

### 3. 配置 MCP 服务

收到 JY_API_KEY 后，执行：

```bash
# 配置 jy-financedata-tool 服务
mcporter config add jy-financedata-tool --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=你的 JY_API_KEY"

# 配置 jy-financedata-api 服务
mcporter config add jy-financedata-api --url "https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=你的 JY_API_KEY"
```

### 4. 验证配置

```bash
# 查看已配置的服务
mcporter list

# 测试调用
mcporter call jy-financedata-tool.PolicyResearch query="行业=AI&beginDate=2026-03-01&endDate=2026-03-30"
```

### 5. 配置 OpenClaw（如未自动识别）

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "skills": {
    "entries": {
      "mcporter": {
        "enabled": true,
        "env": {
          "MCPORTER_CONFIG": "/root/config/mcporter.json"
        }
      }
    }
  }
}
```

重启 OpenClaw：

```bash
openclaw gateway restart
```

## 常见问题

### Q1: mcporter 安装失败

**解决方案：**
1. 确保已安装 Node.js（v16+）
2. 使用 sudo 权限安装：`sudo npm install -g mcporter`
3. 检查 npm 源：`npm config get registry`，可切换为淘宝源

### Q2: mcporter list 显示为空

**解决方案：**
1. 确认已完成步骤 3 的 MCP 服务配置
2. 检查 JY_API_KEY 是否有效
3. 检查网络连接是否正常

### Q3: 调用工具返回错误

**可能原因：**
1. JY_API_KEY 无效或过期 → 重新申请
2. 查询参数格式错误 → 检查 query 参数
3. 网络问题 → 检查网络连接
4. 服务端问题 → 联系聚源技术支持

### Q4: 查询结果为空

**解决方案：**
1. 放宽日期范围（如从"近一周"改为"近一月"）
2. 调整政策关键词（使用更通用的名称）
3. 确认政策类型和地域范围是否正确

### Q5: 政策解读维度不完整

**说明：**
- 政策解读维度由聚源数据 MCP 服务提供
- 不同政策的分析维度可能有所不同
- 所有返回的维度都会保留并输出

## 配置文件位置

| 系统 | mcporter 配置 | OpenClaw 配置 |
|------|-------------|-------------|
| Linux | `/root/config/mcporter.json` 或 `~/.config/mcporter.json` | `~/.openclaw/openclaw.json` |
| macOS | `~/.config/mcporter.json` | `~/.openclaw/openclaw.json` |
| Windows | `C:\Users\用户名\config\mcporter.json` | `C:\Users\用户名\.openclaw\openclaw.json` |

## 环境变量

如使用非默认配置文件路径，需设置环境变量：

```bash
export MCPORTER_CONFIG=/path/to/your/mcporter.json
```

或在 OpenClaw 配置中指定：

```json
{
  "skills": {
    "entries": {
      "mcporter": {
        "enabled": true,
        "env": {
          "MCPORTER_CONFIG": "/path/to/your/mcporter.json"
        }
      }
    }
  }
}
```

## 测试查询

配置完成后，可使用以下命令测试：

```bash
# 查询近一月 AI 行业政策
mcporter call jy-financedata-tool.PolicyResearch query="行业=AI&beginDate=2026-03-01&endDate=2026-03-30"

# 查询最新货币政策
mcporter call jy-financedata-tool.PolicyResearch query="关键词=货币政策&beginDate=2026-02-01&endDate=2026-03-30"

# 查询新能源行业政策
mcporter call jy-financedata-tool.PolicyResearch query="行业=新能源&beginDate=2026-03-01&endDate=2026-03-30"
```

## 联系支持

如遇问题，可通过以下方式联系支持：

- **聚源数据技术支持**：datamap@gildata.com
- **OpenClaw 社区**：https://discord.com/invite/clawd
- **Skill 文档**：https://clawhub.ai/
