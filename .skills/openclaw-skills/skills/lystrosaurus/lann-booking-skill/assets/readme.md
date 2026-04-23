# Lann预约技能结构说明

## 技能目录结构

```
lann-booking/
├── SKILL.md                    # 主技能文档（必需）
├── references/                 # 参考文档
│   ├── api_reference.md        # MCP API详细参考
│   └── usage_guide.md          # 使用指南和最佳实践
├── scripts/                    # 可执行脚本
│   └── validate_booking.py     # 预约信息验证脚本
└── assets/                     # 资产文件
    ├── example_booking.json    # 示例预约数据
    └── readme.md               # 本说明文件
```

## 文件用途说明

### 1. SKILL.md
**核心技能文档**，包含：
- 技能元数据（名称、标签、描述）
- 核心功能介绍
- MCP服务器安装配置指南
- 工具详细说明
- 工作流程指南
- 智能匹配说明
- 错误处理和最佳实践

### 2. references/api_reference.md
**API参考文档**，包含：
- MCP服务器详细信息
- 工具参数表和响应格式
- 数据格式要求
- 城市和服务类型列表
- 常见问题解答
- 测试用例示例
- 故障排除指南

### 3. references/usage_guide.md
**使用指南**，包含：
- 技能触发条件
- 快速开始步骤
- 详细工作流程
- 用户交互技巧
- 错误处理指南
- 最佳实践示例
- 工具脚本使用方法

### 4. scripts/validate_booking.py
**预约验证脚本**，功能：
- 验证手机号格式
- 验证门店和服务名称
- 验证预约人数范围
- 验证预约时间格式
- 提供完整的预约信息验证
- 支持命令行参数验证

**使用方法**：
```bash
# 运行示例验证
python scripts/validate_booking.py

# 验证自定义数据
python scripts/validate_booking.py --validate '{"phone": "13800138000", "storeName": "淮海店"}'
```

### 5. assets/example_booking.json
**示例数据文件**,包含:
- 预约示例数据
- 查询示例参数
- 时间格式示例
- 手机号示例
- 门店名称列表
- 服务名称列表
- 城市列表
- 服务关键词列表

## 技能使用流程

### 第一步：技能触发
当用户提到以下关键词时触发：
- Lann、蘭泰式按摩
- 预约、预订、预定
- 门店查询、服务查询
- 按摩店、按摩项目

### 第二步：MCP 服务器配置
确保 Skill Hub 已正确配置 Lann MCP 服务器:

```json
{
  "mcpServers": {
    "lann": {
      "command": "npx",
      "args": ["lann-mcp-server"]
    }
  }
}
```

环境会自动加载 MCP 服务器，无需手动检查。

### 第三步：收集用户需求
按顺序询问：
1. 预约城市
2. 大致位置偏好
3. 服务类型
4. 服务时长
5. 预约人数
6. 期望时间

### 第四步：查询信息
调用 MCP 工具查询门店和服务:
- 调用 `query_stores` 工具，参数：{"city": "上海"}
- 调用 `query_services` 工具，参数：{"duration": 90}

Skill Hub 会自动处理 MCP 通信。

### 第五步：创建预约
调用 `create_booking` 工具，提供完整参数:
```json
{
  "phone": "13800138000",
  "storeName": "淮海店",
  "serviceName": "传统古法全身按摩 -90 分钟",
  "peopleCount": 2,
  "bookingTime": "2024-01-15T14:00:00"
}
```

Skill Hub 会自动处理 MCP 通信和响应解析。

### 第六步：反馈结果
向用户提供：
1. 预约成功状态
2. 预约ID
3. 门店和服务详情
4. 确认短信状态

## 注意事项

1. **技能名称**: lann-booking
2. **标签**: Lann预约技能（注意与用户查询语言一致）
3. **触发描述**: 包含所有关键词和触发条件
4. **文件组织**: 按功能分目录，避免文件混乱
5. **内容完整性**: 确保所有必需信息都在SKILL.md中
6. **示例实用性**: 提供真实可用的示例代码和数据

## 技能打包

当技能开发完成后，使用以下命令打包：
```bash
python /opt/official-skills/aily-skill-creator/scripts/package_skill.py /home/workspace/skills/lann-booking
```

打包前会自动验证：
- YAML frontmatter格式
- 必需字段完整性
- 文件组织结构
- 技能描述质量

打包成功后生成：`lann-booking.skill`