# AssetClaw - API 端点速查手册

> 基于实时后端接口文档 `GET /api/api-documentation` 汇总
> 系统共 60+ 模块，688 个接口

---

## 核心模块速查

### 资产 `/assets`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/assets` | 资产列表（支持 search/pageSize/department_id/status） | — |
| POST | `/assets` | 创建资产 | asset_code, asset_name, category_id |
| GET | `/assets/{id}` | 资产详情 | id |
| PUT | `/assets/{id}` | 更新资产 | id |
| DELETE | `/assets/{id}` | 删除资产 | id |
| GET | `/assets/{id}/change-logs` | 变更日志 | id |
| GET | `/assets/{id}/transitions` | 可执行状态迁移 | id |
| GET | `/assets/export` | 导出 Excel | — |
| POST | `/assets/import` | 导入资产 | file |
| GET | `/assets/duplicate-check` | 编码重复检查 | asset_code |
| GET | `/assets/departments/list` | 部门列表（资产筛选用） | — |

### 维修 `/maintenance`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/maintenance/requests` | 维修申请列表 | — |
| POST | `/maintenance/ai/submit-request` | 创建维修申请（AI/skill 安全入口） | asset_code, fault_description |
| GET | `/maintenance/requests/{id}` | 申请详情 | id |
| PUT | `/maintenance/requests/{id}` | 更新申请 | id |
| POST | `/maintenance/requests/{id}/approve` | 审批 | approved, opinion |
| POST | `/maintenance/requests/{id}/start` | 开始执行 | repair_person |
| POST | `/maintenance/requests/{id}/complete` | 完成维修 | — |
| POST | `/maintenance/requests/{id}/cancel` | 取消申请 | — |
| GET | `/maintenance/workorders` | 维修工单列表 | — |
| POST | `/maintenance/workorders` | 创建工单 | title, asset_code |
| GET | `/maintenance/workorders/{id}` | 工单详情 | id |
| PUT | `/maintenance/workorders/{id}` | 更新工单 | id |
| POST | `/maintenance/workorders/{id}/assign` | 分配工单 | assigned_to |
| POST | `/maintenance/workorders/{id}/start` | 开始工单 | — |
| POST | `/maintenance/workorders/{id}/complete` | 完成工单 | — |
| POST | `/maintenance/workorders/{id}/cancel` | 取消工单 | — |
| POST | `/maintenance/workorders/{id}/close` | 关闭工单 | — |
| POST | `/maintenance/workorders/{id}/materials` | 追加材料 | — |
| GET | `/maintenance/logs` | 维修日志列表 | — |
| POST | `/maintenance/logs` | 创建维修日志 | asset_code, maintenance_type, maintenance_date, maintenance_person, maintenance_content |
| GET | `/maintenance/plans` | 预防性维护计划列表 | — |
| POST | `/maintenance/plans` | 创建维护计划 | — |
| PUT | `/maintenance/plans/{id}` | 更新维护计划 | id |
| POST | `/maintenance/plans/{id}/complete` | 完成维护计划 | — |
| GET | `/maintenance/plans/{id}/history` | 维护历史 | id |
| GET | `/maintenance/statistics` | 维修统计 | — |
| GET | `/maintenance/efficiency/overview` | 维修效率概览 | — |
| GET | `/maintenance/costs/analysis` | 维修费用分析 | — |
| GET | `/maintenance/ai/pending` | AI 待处理请求 | — |
| POST | `/maintenance/ai/init` | AI 对话初始化 | — |
| POST | `/maintenance/ai/message` | AI 发送消息 | conversation_id, message |
| GET | `/maintenance/reminders` | 维护提醒列表 | — |
| POST | `/maintenance/reminders/config` | 配置提醒 | plan_id, reminder_days, reminder_types |
| POST | `/maintenance/reminders/send` | 发送提醒 | plan_id, reminder_type |
| GET | `/maintenance/reminders/check` | 检查到期提醒 | — |
| GET | `/maintenance/templates` | 维修模板列表 | — |
| POST | `/maintenance/templates` | 创建维修模板 | — |

> 报修创建请优先使用 `/maintenance/ai/submit-request`。该入口不需要二次风险确认，但提交成功后仍进入待审批；审批、开始执行、完成维修仍使用 `/maintenance/requests/{id}/...`。

### 盘点 `/inventory-plans` `/inventory-tasks` `/inventory-discrepancies`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/inventory-plans` | 盘点计划列表 | — |
| POST | `/inventory-plans` | 创建盘点计划 | plan_name, plan_no |
| PUT | `/inventory-plans/{id}/activate` | 激活计划 | id |
| PUT | `/inventory-plans/{id}/cancel` | 取消计划 | id |
| PUT | `/inventory-plans/{id}/complete` | 完成计划 | id |
| GET | `/inventory-tasks` | 盘点任务列表 | — |
| POST | `/inventory-tasks` | 创建盘点任务 | inventory_plan_id, task_name, assignee, assignee_name |
| PUT | `/inventory-tasks/{id}/start` | 开始盘点 | id |
| PUT | `/inventory-tasks/{id}/complete` | 完成盘点 | id, actual_count |
| PUT | `/inventory-tasks/{id}/cancel` | 取消任务 | id |
| PUT | `/inventory-tasks/{id}/assign` | 分配任务 | id |
| GET | `/inventory-discrepancies` | 盘点差异列表 | — |
| PUT | `/inventory-discrepancies/{id}/handle` | 处理差异 | id, handling_status, handling_method |
| POST | `/inventory-discrepancies/batch-handle` | 批量处理差异 | ids, handling_status, handling_method |
| POST | `/inventory-discrepancies/generate-from-details` | 从明细生成差异 | — |
| GET | `/inventory-discrepancies/{id}/statistics` | 差异统计 | inventory_id |

### 调配 `/transfer`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/transfer` | 调配申请列表 | — |
| POST | `/transfer` | 发起调配申请 | asset_code, reason, to_department |
| GET | `/transfer/{id}` | 调配详情 | id |
| PUT | `/transfer/{id}/approve` | 审批调配 | approved, opinion |
| PUT | `/transfer/{id}/complete` | 执行完成 | id |
| DELETE | `/transfer/{id}` | 删除调配 | id |
| GET | `/transfer/statistics` | 调配统计 | — |

### 闲置 `/idle`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/idle` | 闲置资产列表 | — |
| POST | `/idle` | 发布闲置 | asset_code/publish_person |
| GET | `/idle/{id}` | 闲置详情 | id |
| PUT | `/idle/{id}/allocate` | 调配闲置 | id, target_department |
| PUT | `/idle/{id}/cancel` | 取消闲置 | id |
| DELETE | `/idle/{id}` | 删除闲置记录 | id |
| GET | `/idle/statistics` | 闲置统计 | — |

### 报废 `/scrapping`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/scrapping` | 报废申请列表 | — |
| POST | `/scrapping` | 创建报废申请 | asset_code, asset_name, applicant, scrapping_reason |
| POST | `/scrapping/{id}/approve` | 审批报废 | approved, opinion |
| POST | `/scrapping/{id}/complete` | 完成报废 | — |
| POST | `/scrapping/{id}/dispose` | 处置 | — |
| POST | `/scrapping/{id}/appraise` | 资产估价 | — |
| GET | `/scrapping/statistics/summary` | 报废统计 | — |

### 采购 `/procurement`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/procurement/requests` | 采购申请列表 | — |
| POST | `/procurement/requests` | 创建采购申请 | title |
| PUT | `/procurement/requests/{id}/approve` | 审批采购 | approved, opinion |
| PUT | `/procurement/requests/{id}/execute` | 执行采购 | completed, result |
| PUT | `/procurement/requests/{id}/acceptance` | 验收 | — |
| GET | `/procurement/stats` | 采购统计 | — |

### 质检 `/quality-control`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/quality-control/metrology` | 计量记录列表 | — |
| POST | `/quality-control/metrology` | 创建计量记录 | asset_code, metrology_type, metrology_date |
| GET | `/quality-control/quality-control` | 质检记录列表 | — |
| POST | `/quality-control/quality-control` | 创建质检记录 | asset_code, qc_type, qc_date, result |
| GET | `/quality-control/statistics` | 质检统计 | — |
| GET | `/quality-control/asset/{assetCode}/history` | 资产质检历史 | assetCode |
| GET | `/quality-control/expiring` | 即将到期质检 | — |

### 文档 `/technical-documents`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/technical-documents` | 文档列表 | — |
| POST | `/technical-documents` | 上传文档 | file, title |
| POST | `/technical-documents/{id}/review` | 审核文档 | status, comment |
| POST | `/technical-documents/{id}/share` | 创建分享 | expires_days |
| GET | `/technical-documents/enhanced/categories` | 文档分类 | — |
| GET | `/technical-documents/enhanced/tags` | 文档标签 | — |
| POST | `/technical-documents/enhanced/documents/{id}/favorite` | 收藏 | id |
| GET | `/technical-documents/enhanced/my/favorites` | 我的收藏 | — |
| POST | `/technical-documents/ai/ask` | AI 问答 | question |
| POST | `/technical-documents/ai/search` | AI 搜索 | query |
| POST | `/technical-documents/ai/summary` | AI 摘要 | — |

### 折旧 `/depreciation`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/depreciation` | 折旧列表 |
| GET | `/depreciation/summary/by-department` | 按部门折旧汇总 |
| GET | `/depreciation/summary/by-month` | 按月折旧趋势 |
| GET | `/depreciation/summary/by-type` | 按类型折旧汇总 |
| GET | `/depreciation/methods` | 折旧方法列表 |
| POST | `/depreciation/calculate` | 计算折旧 |
| GET | `/depreciation/export` | 导出折旧报表 |

### 部门 `/departments`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/departments/tree` | 部门树 | — |
| GET | `/departments` | 部门列表 | — |
| POST | `/departments` | 创建部门 | department_name |
| GET | `/departments/{id}` | 部门详情 | id |
| PUT | `/departments/{id}` | 更新部门 | id |
| DELETE | `/departments/{id}` | 删除部门 | id |

### 用户 `/users`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/users` | 用户列表 | — |
| POST | `/users` | 创建用户 | username, real_name, password, role |
| GET | `/users/me` | 当前用户 | — |
| GET | `/users/profile` | 用户资料 | — |
| GET | `/users/roles` | 角色列表 | — |
| POST | `/users/register` | 注册用户 | — |

### 角色权限 `/roles-permissions`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/roles-permissions/roles` | 角色列表 |
| GET | `/roles-permissions/roles/{role}/permissions` | 角色权限 |
| PUT | `/roles-permissions/roles/{role}/permissions` | 更新角色权限 |
| GET | `/roles-permissions/roles/{role}/menus` | 角色菜单 |
| PUT | `/roles-permissions/roles/{role}/menus` | 更新角色菜单 |
| GET | `/roles-permissions/user/menus` | 当前用户菜单 |
| GET | `/roles-permissions/user/permissions` | 当前用户权限 |
| GET | `/roles-permissions/permissions/definitions` | 权限定义列表 |

### 模块配置 `/module-configs` `/modules`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/modules` | 模块清单 | — |
| GET | `/module-configs/list` | 租户模块配置列表 | — |
| POST | `/module-configs/enable` | 启用模块 | module_id |
| POST | `/module-configs/disable` | 停用模块 | module_id |
| GET | `/module-configs/{moduleId}` | 单模块配置 | moduleId |
| PUT | `/module-configs/{moduleId}` | 更新模块配置 | moduleId |
| GET | `/module-configs/{moduleId}/menus` | 模块菜单 | moduleId |
| PUT | `/module-configs/{moduleId}/menus` | 更新模块菜单 | moduleId, menus |
| GET | `/module-configs/{moduleId}/versions` | 版本历史 | moduleId |
| POST | `/module-configs/{moduleId}/versions` | 创建版本备份 | moduleId, change_log |
| POST | `/module-configs/{moduleId}/rollback` | 回滚版本 | version_id |
| GET | `/module-configs/{moduleId}/validate` | 验证配置 | moduleId |
| GET | `/module-configs/{moduleId}/backup` | 备份配置 | moduleId |

### IoT `/iot`

| 方法 | 路径 | 说明 | 必填参数 |
|------|------|------|---------|
| GET | `/iot/devices` | IoT 设备列表 | — |
| POST | `/iot/devices` | 注册设备 | device_name, device_type |
| GET | `/iot/devices/{id}` | 设备详情 | id |
| PUT | `/iot/devices/{id}` | 更新设备 | id |
| DELETE | `/iot/devices/{id}` | 删除设备 | id |
| POST | `/iot/devices/assets/{assetCode}/link` | 资产绑定设备 | assetCode |
| POST | `/iot/devices/assets/{assetCode}/unlink` | 解除绑定 | assetCode |
| GET | `/iot/devices/types` | 设备类型列表 | — |
| POST | `/iot/location/assets/{assetCode}/location` | 上报位置 | assetCode |
| GET | `/iot/location/assets/{assetCode}/location` | 查询位置 | assetCode |
| GET | `/iot/location/assets/{assetCode}/location/history` | 位置历史 | assetCode |
| POST | `/iot/zone-location/ingest` | 单条区域定位上报 | — |
| POST | `/iot/zone-location/ingest/batch` | 批量区域定位上报 | — |
| GET | `/iot/zone-location/assets/{assetCode}/latest` | 最新区域位置 | assetCode |
| GET | `/iot/zone-location/assets/{assetCode}/series` | 区域位置时序 | assetCode |
| GET | `/iot/zone-location/pipeline/health` | 区域定位管道健康 | — |
| POST | `/iot/location/beacon-location` | Beacon 位置上报 | — |
| GET | `/iot/environment-monitoring/assets/{assetCode}/latest` | 环境监测最新 | assetCode |
| GET | `/iot/environment-monitoring/assets/{assetCode}/series` | 环境监测时序 | assetCode |
| GET | `/iot/environment-monitoring/pipeline/health` | 环境监测管道健康 | — |

### 告警

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/intelligent-alerts` | 智能告警列表 |
| GET | `/intelligent-alerts/overview` | 告警概览 |
| GET | `/intelligent-alerts/maintenance` | 维修类告警 |
| GET | `/intelligent-alerts/safety` | 安全类告警 |
| GET | `/intelligent-alerts/qualifications` | 资质类告警 |
| POST | `/intelligent-alerts/{id}/handle` | 处理告警 |
| POST | `/intelligent-alerts/{id}/read` | 标记已读 |
| POST | `/intelligent-alerts/read-all` | 全部已读 |
| GET | `/location-alerts` | 位置告警列表 |
| PUT | `/location-alerts/{id}/handle` | 处理位置告警 |
| POST | `/location-alerts/batch/handle` | 批量处理位置告警 |
| GET | `/location-alerts/stats` | 位置告警统计 |

### 审计 `/audit-logs`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/audit-logs` | 审计日志列表 |
| GET | `/audit-logs/{id}` | 日志详情 |
| GET | `/audit-logs/stats` | 审计统计 |

### 仪表盘 `/dashboard`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dashboard` | 仪表盘数据 |
| GET | `/dashboard/realtime` | 实时数据 |
| GET | `/analysis/value-distribution` | 价值分布 |
| GET | `/analysis/depreciation` | 折旧分析 |
| GET | `/risk/dashboard` | 风险仪表盘 |
| GET | `/risk/status` | 风险状态 |
| GET | `/compliance/status` | 合规状态 |
| GET | `/compliance/dashboard-stats` | 合规统计 |

### 工作流 `/workflow`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/workflow/default` | 默认工作流 |
| GET | `/workflow/states` | 状态列表 |
| GET | `/workflow/transitions` | 迁移规则列表 |
| POST | `/workflow/transition/{assetId}` | 执行状态迁移 |

### AI 分析 `/asset-ai-analysis`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/asset-ai-analysis/analysis-history` | 分析历史 |
| POST | `/asset-ai-analysis/analyze-asset/{assetCode}` | 分析单个资产 |
| POST | `/asset-ai-analysis/analyze-assets` | 批量分析 |
| POST | `/asset-ai-analysis/custom-analysis` | 自定义分析 |
| GET | `/asset-ai-analysis/reports/{id}` | 分析报告 |
| GET | `/asset-ai-analysis/datasources` | 数据源列表 |
| GET | `/asset-ai-analysis/dimensions` | 分析维度 |

### Agent Mesh

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/agent-mesh/intelligence/predictive-maintenance` | 预测性维护 |
| POST | `/agent-mesh/intelligence/risk-score` | 风险评分 |
| POST | `/agent-mesh/intelligence/health-index` | 健康指数 |
| GET | `/agent-mesh/intelligence/health-trend` | 健康趋势 |
| GET | `/agent-mesh/intelligence/risk-trend` | 风险趋势 |

### 标签打印 `/asset-labels`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/asset-labels/templates` | 标签模板列表 |
| POST | `/asset-labels/templates` | 创建模板 |
| GET | `/asset-labels/templates/{id}` | 模板详情 |
| PUT | `/asset-labels/templates/{id}` | 更新模板 |
| DELETE | `/asset-labels/templates/{id}` | 删除模板 |
| POST | `/asset-labels/print` | 打印标签 |
| POST | `/asset-labels/print/batch` | 批量打印 |
| POST | `/asset-labels/generate-zpl-batch` | 生成 ZPL |
| POST | `/asset-labels/printer/test-connection` | 测试打印机 |

### 位置编码 `/location-codes`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/location-codes` | 位置编码列表 |
| POST | `/location-codes` | 创建位置编码 |
| GET | `/location-codes/{id}` | 位置编码详情 |
| PUT | `/location-codes/{id}` | 更新位置编码 |
| DELETE | `/location-codes/{id}` | 删除位置编码 |

### 验收 `/acceptance`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/acceptance/records` | 验收记录列表 |
| POST | `/acceptance/records` | 创建验收记录 |
| GET | `/acceptance/records/{id}` | 验收详情 |
| PUT | `/acceptance/records/{id}` | 更新验收 |
| PUT | `/acceptance/records/{id}/status` | 更新状态 |
| GET | `/acceptance/statistics` | 验收统计 |

### 备份 `/backup`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/backup` | 备份列表 |
| POST | `/backup` | 创建备份 |
| GET | `/backup/{id}/download` | 下载备份 |
| POST | `/backup/{id}/restore` | 恢复备份 |
| DELETE | `/backup/{id}` | 删除备份 |

### 系统配置 `/system-config`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/system-config/database` | 数据库配置 |
| PUT | `/system-config/database` | 更新数据库配置 |
| POST | `/system-config/database/test` | 测试数据库连接 |
| GET | `/system-config/iot-tokens` | IoT Token 列表 |
| POST | `/system-config/iot-tokens/generate` | 生成 Token |
| POST | `/system-config/iot-tokens/{id}/revoke` | 吊销 Token |
| GET | `/system-config/iot-tokens/usage-guide` | Token 使用指南 |

### 接口发现

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api-documentation` | API 文档概览 |
| GET | `/api-documentation/modules` | 模块列表 |
| GET | `/api-documentation/module/{path}` | 指定模块文档 |
| GET | `/api-documentation/endpoints` | 全部端点 |
| GET | `/health` | 健康检查 |
| GET | `/health/detailed` | 详细健康状态 |
