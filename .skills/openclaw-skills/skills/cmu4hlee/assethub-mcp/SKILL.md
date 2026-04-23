---
name: "assethub-mcp"
description: "🏥 AssetHub 资产管理系统 AI 助手 via MCP 协议。支持资产查询、维修管理、调配审批、统计分析等 35+ 功能"
version: "2.2.0"
tags: ["资产管理", "医疗设备", "MCP", "维修管理", "库存管理", "科室调配", "固定资产"]
metadata: { 
  "openclaw": { 
    "emoji": "🏥", 
    "requires": { 
      "bins": ["mcporter"] 
    },
    "install": [
      {
        "id": "node",
        "kind": "node",
        "package": "mcporter",
        "bins": ["mcporter"],
        "label": "Install mcporter (Node.js required)"
      }
    ]
  }
}
---

# 🏥 AssetHub MCP Server

> 资产管理系统 MCP 服务器，通过 mcporter 提供 35+ 资产管理工具，支持资产全生命周期管理。

## ✨ 功能特点

- 📦 **资产全生命周期** - 采购入库 → 使用管理 → 维修保养 → 调配共享 → 报废处置
- 🔧 **维修管理** - 工单创建、进度跟踪、验收评价
- 🔄 **科室调配** - 闲置资产发布、申请审批、执行调拨
- 📊 **统计分析** - 资产统计、部门统计、价值统计、维修效率
- 🏢 **多租户支持** - 支持配置租户 ID，分离数据
- 🤖 **AI 集成** - AI 对话、AI 分析、智能维修建议

## 🔧 MCP 配置

### 配置文件（推荐）

创建 `~/.openclaw/workspace/config/mcporter.json`:

```json
{
  "mcpServers": {
    "assethub": {
      "command": "/path/to/mcp-assethub",
      "env": {
        "ASSETHUB_API_URL": "http://localhost:5183/api",
        "ASSETHUB_USERNAME": "zhangsan",
        "ASSETHUB_PASSWORD": "Abcd1234",
        "ASSETHUB_TENANT_ID": "3",
        "ASSETHUB_TOOL_PREFIX": "assethub"
      }
    }
  }
}
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `ASSETHUB_API_URL` | API 服务器地址 | http://localhost:5183/api |
| `ASSETHUB_USERNAME` | 登录用户名 | zhangsan |
| `ASSETHUB_PASSWORD` | 登录密码 | Abcd1234 |
| `ASSETHUB_TENANT_ID` | 租户 ID | 3 |
| `ASSETHUB_TOOL_PREFIX` | 工具名前缀 | assethub |

### 手动安装 mcporter

```bash
npm install -g mcporter
```

## 📋 工具清单（35+）

### 资产查询 🔍

| 工具 | 说明 | 参数 |
|------|------|------|
| `assethub_list_assets` | 查询资产列表（分页） | keyword, department, status, limit, page |
| `assethub_list_all_assets` | 全量查询资产（不分页） | category_id, department, location, search |
| `assethub_get_asset` | 获取单个资产详情 | asset_code 或 id |
| `assethub_get_asset_statistics` | 获取资产统计概览 | - |
| `assethub_get_asset_change_logs` | 获取资产变更日志 | id |

### 资产管理 ✏️

| 工具 | 说明 | 参数 |
|------|------|------|
| `assethub_create_asset` | 创建新资产 | asset_name, category_id, asset_code, department_new... |
| `assethub_update_asset` | 更新资产信息 | id, asset_name, status, location, remark... |
| `assethub_delete_asset` | 删除资产 | id |

### 维修管理 🔧

| 工具 | 说明 | 参数 |
|------|------|------|
| `assethub_list_maintenance_workorders` | 维修工单列表 | assigned_to, priority, status, limit, page |
| `assethub_create_maintenance_log` | 创建维修日志 | asset_code, maintenance_type, maintenance_content... |
| `assethub_list_maintenance_logs` | 维修日志列表 | asset_code, start_date, end_date, status |
| `assethub_update_workorder_status` | 更新工单状态 | id, status, notes |
| `assethub_get_maintenance_templates` | 维修模板列表 | - |
| `assethub_get_maintenance_efficiency` | 维修效率统计 | - |

### 资产调配 🔄

| 工具 | 说明 | 参数 |
|------|------|------|
| `assethub_list_transfers` | 调配记录列表 | asset_code, status, limit, page |
| `assethub_transfer_asset` | 申请资产调配 | asset_code, target_department, reason, transfer_date |
| `assethub_approve_transfer` | 审批调配申请 | action(approve/reject), id, comment |
| `assethub_execute_transfer` | 执行调配 | id |

### 闲置资产 📦

| 工具 | 说明 | 参数 |
|------|------|------|
| `assethub_list_idle_assets` | 闲置资产列表 | category_id, keyword, limit, page |
| `assethub_publish_idle_asset` | 发布闲置资产 | asset_code, publish_date, publish_person, remark |
| `assethub_cancel_idle_asset` | 取消发布 | id |
| `assethub_allocate_idle_asset` | 调配闲置资产 | id, target_department, allocate_date, comment |

### 基础数据 📁

| 工具 | 说明 | 参数 |
|------|------|------|
| `assethub_list_departments` | 部门列表 | tree, include_children, parent_id |
| `assethub_list_users` | 用户列表 | department_code, keyword, role, status |
| `assethub_get_asset_categories` | 资产分类列表 | parent_id, tree |
| `assethub_get_department_statistics` | 部门资产统计 | - |
| `assethub_get_value_statistics` | 资产价值统计 | - |

### 工作流与 AI 🤖

| 工具 | 说明 | 参数 |
|------|------|------|
| `assethub_get_todo_tasks` | 待处理任务 | - |
| `assethub_complete_task` | 完成工作流任务 | id, variables |
| `assethub_init_ai_conversation` | 初始化 AI 对话 | - |
| `assethub_send_ai_message` | 发送 AI 消息 | conversation_id, message, history |
| `assethub_get_ai_pending` | AI 待处理请求 | - |
| `assethub_get_ai_analysis` | AI 维修分析 | department, start_date, end_date, type |

## 💡 使用示例

### 基础查询

```bash
# 列出资产（分页搜索）
mcporter call assethub.assethub_list_assets keyword:=CT limit:=20 page:=1

# 全量查询资产
mcporter call assethub.assethub_list_all_assets department:="手术室"

# 获取单个资产详情
mcporter call assethub.assethub_get_asset asset_code:=ASSET001

# 获取资产统计
mcporter call assethub.assethub_get_asset_statistics
```

### 资产管理

```bash
# 创建新资产
mcporter call assethub.assethub_create_asset asset_code:="ASSET002" asset_name:="心电监护仪" category_id:=1 department_new:="心内科"

# 更新资产信息
mcporter call assethub.assethub_update_asset id:=1 status:="维修" remark:="设备故障"
```

### 维修管理

```bash
# 创建维修日志
mcporter call assethub.assethub_create_maintenance_log asset_code:="ASSET001" maintenance_content:="例行保养" maintenance_date:="2026-03-28" maintenance_person:="张三" maintenance_type:="定期保养"

# 获取维修工单
mcporter call assethub.assethub_list_maintenance_workorders status:=in_progress limit:=10

# 更新工单状态
mcporter call assethub.assethub_update_workorder_status id:=1 status:=completed notes:="维修完成"
```

### 资产调配

```bash
# 申请资产调配
mcporter call assethub.assethub_transfer_asset asset_code:="ASSET001" reason:="科室共用" target_department:="ICU" transfer_date:="2026-03-28"

# 审批调配申请
mcporter call assethub.assethub_approve_transfer action:=approve comment:="同意" id:=1

# 执行调配
mcporter call assethub.assethub_execute_transfer id:=1
```

### 闲置资产

```bash
# 获取闲置资产列表
mcporter call assethub.assethub_list_idle_assets keyword:="监护仪"

# 发布闲置资产
mcporter call assethub.assethub_publish_idle_asset asset_code:="ASSET003" publish_person:="李四"

# 调配闲置资产
mcporter call assethub.assethub_allocate_idle_asset id:=1 target_department:="手术室" allocate_date:="2026-03-28"
```

### 基础数据

```bash
# 获取部门列表（树形）
mcporter call assethub.assethub_list_departments tree:=true

# 获取资产分类
mcporter call assethub.assethub_get_asset_categories tree:=true

# 获取用户列表
mcporter call assethub.assethub_list_users role:=technician
```

## 📊 返回数据示例

### 资产统计

```json
{
  "total_count": 28291,
  "total_value": "¥125,000,000",
  "by_status": [
    {"status": "在用", "count": 28286},
    {"status": "维修", "count": 3},
    {"status": "闲置", "count": 1},
    {"status": "报废", "count": 1}
  ],
  "by_category": [
    {"category": "医疗设备", "count": 1680},
    {"category": "办公家具", "count": 7144},
    {"category": "普通设备", "count": 18455}
  ]
}
```

### 资产列表

```json
{
  "data": [
    {
      "id": 1,
      "asset_code": "ASSET001",
      "asset_name": "CT 机",
      "category": "医疗设备",
      "status": "在用",
      "department": "放射科",
      "location": "1号楼 2层",
      "purchase_date": "2024-01-15",
      "purchase_price": 2500000
    }
  ],
  "total": 100,
  "page": 1,
  "pageSize": 20
}
```

## 🏥 适用场景

- 🏥 **医院资产管理系统** - 医疗设备全生命周期管理
- 🔧 **设备维修管理** - 工单派发、维修记录、效率统计
- 🔄 **科室资产调配** - 闲置资产共享、审批流程
- 📊 **资产统计分析** - 部门统计、价值分析、使用率统计
- 📦 **库存物料管理** - 维修配件库存管理

## ⚠️ 注意事项

1. **API 地址** - 确保 AssetHub 服务已启动并可达
2. **租户 ID** - 多租户环境下正确配置 `ASSETHUB_TENANT_ID`
3. **权限控制** - 生产环境建议使用环境变量而非配置文件
4. **数据安全** - 敏感凭据请妥善保管

## 📝 版本历史

- **2.2.0** - 完善文档，增加完整工具说明和使用示例
- **2.1.0** - 新增 MCP 配置说明，工具分类整理
- **1.0.3** - 初始版本

---

**版本**: 2.2.0  
**标签**: 🏥 资产管理 | 🔧 维修管理 | 🔄 科室调配 | 📊 统计分析
