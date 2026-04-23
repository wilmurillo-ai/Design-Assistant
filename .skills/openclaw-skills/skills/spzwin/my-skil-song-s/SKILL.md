---
name: cwork-openapi
description: 玄关（工作协同）开放平台 API 使用指南。当开发人员询问玄关开放平台提供了哪些 API、如何调用、接口参数说明、代码示例时使用此 Skill。涵盖用户服务、文件服务、工作汇报服务、BP目标管理服务、知识库服务等模块。
---

# 玄关开放平台 API Skill

## 概述

本 Skill 提供玄关（工作协同）开放平台 OpenAPI 的完整使用指南，帮助开发人员快速接入和使用平台提供的各种服务。

## 服务模块

平台提供以下服务模块：

| 模块 | 路径前缀 | 功能说明 |
|------|----------|----------|
| **用户服务** | `/cwork-user` | 员工信息查询、搜索 |
| **文件服务** | `/cwork-file` | 文件上传、下载 |
| **工作汇报服务** | `/work-report` | 汇报发送、回复、待办查询 |
| **BP目标管理服务** | `/bp` | 目标周期、分组、任务管理 |
| **知识库服务** | `/document-database` | 文档库文件管理 |

## 快速开始

### 1. 基础信息

- **基础路径**: `/open-api`
- **认证方式**: Header 中携带 `appKey`，具体值可以从环境变量 `XG_BIZ_API_KEY` 获取
- **请求域名**: `https://cwork-api.mediportal.com.cn`

### 2. 通用请求头

```python
headers = {
    "Content-Type": "application/json",
    "appKey": "your_app_key_here",  # 从环境变量 `XG_BIZ_API_KEY` 获取
    "Accept": "application/json"
}
```

### 3. 统一返回结构

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": {}
}
```

- `resultCode`: 1=成功，其他=失败
- `resultMsg`: 失败原因
- `data`: 业务数据

## 核心功能速查

### 用户相关

| 功能 | 接口 | 方法 |
|------|------|------|
| 搜索员工 | `/cwork-user/searchEmpByName` | GET |
| 批量获取员工 | `/cwork-user/employee/getByPersonIds/{corpId}` | POST |

### 文件相关

| 功能 | 接口 | 方法 |
|------|------|------|
| 上传文件 | `/cwork-file/uploadWholeFile` | POST (multipart) |
| 获取下载信息 | `/cwork-file/getDownloadInfo` | GET |

### 工作汇报相关

| 功能 | 接口 | 方法 |
|------|------|------|
| 发送汇报 | `/work-report/report/record/submit` | POST |
| 回复汇报 | `/work-report/report/record/reply` | POST |
| 获取待办 | `/work-report/todoTask/todoList` | POST |
| 获取汇报内容 | `/work-report/report/info` | GET |
| 查询工作任务 | `/work-report/report/plan/searchPage` | POST |

### BP目标管理相关

| 功能 | 接口 | 方法 |
|------|------|------|
| 查询周期列表 | `/bp/period/getAllPeriod` | GET |
| 获取分组树 | `/bp/group/getTree` | GET |
| 查询任务树 | `/bp/task/v2/getSimpleTree` | GET |
| 获取目标详情 | `/bp/task/v2/getGoalAndKeyResult` | GET |

### 知识库相关

| 功能 | 接口 | 方法 |
|------|------|------|
| 获取下级文件 | `/document-database/file/getChildFiles` | GET |
| 获取文件内容 | `/document-database/file/getFullFileContent` | GET |

## 详细参考文档

- **完整 API 文档**: 参见 [references/api-reference.md](references/api-reference.md)
  - 所有接口的详细参数说明
  - 请求/响应数据结构
  - 字段类型和说明

- **代码示例**: 参见 [references/code-examples.md](references/code-examples.md)
  - Python 调用示例
  - 完整的请求代码
  - 错误处理最佳实践

## 使用场景指南

### 场景 1: 查询员工信息

当需要获取员工信息时：

1. **模糊搜索**: 使用 `searchEmpByName` 接口，按姓名模糊搜索
2. **精确查询**: 使用 `getByPersonIds` 接口，传入 personId 列表批量获取

### 场景 2: 文件操作

1. **上传**: 调用 `uploadWholeFile`，返回文件 ID
2. **下载**: 
   - 先调用 `getDownloadInfo` 获取下载 URL（有效期1小时）
   - 使用 URL 下载文件内容

### 场景 3: 发送工作汇报

1. **获取事项列表**: 调用 `listTemplates` 获取可用的事项
2. **构建层级参数**: 定义汇报的流转层级（建议、决策、传阅）
3. **发送汇报**: 调用 `submit` 接口提交

### 场景 4: 处理待办

1. **查询待办**: 调用 `todoList` 获取待处理列表
2. **获取详情**: 调用 `getReportInfo` 查看汇报内容
3. **回复处理**: 调用 `reply` 进行回复或审批

### 场景 5: BP目标管理

1. **获取周期**: 调用 `getAllPeriod` 获取可用的目标周期
2. **获取分组**: 调用 `getGroupTree` 获取周期下的分组树
3. **查询任务**: 调用 `getSimpleTree` 获取分组下的任务树
4. **查看详情**: 调用 `getGoalAndKeyResult` 查看目标详情

## 注意事项

1. **认证**: 所有请求必须在 Header 中携带有效的 `appKey`
2. **文件上传**: 使用 `multipart/form-data`，不要设置 `Content-Type` 头
3. **下载链接**: 通过 `getDownloadInfo` 获取的 URL 有效期为1小时
4. **分页**: 分页接口的 `pageNum` 从 1 开始
5. **ID 类型**: 大多数 ID 字段为 Long 类型（64位整数）

## 常见问题

**Q: 如何获取 appKey？**
A: 从环境变量 `XG_BIZ_API_KEY` 获取。

**Q: 文件上传大小有限制吗？**
A: 请参考工作协同系统的具体配置，通常有单文件大小限制。

**Q: 汇报的 levelParams 如何构建？**
A: level 从 1 开始递增，type 可选值：read（传阅）、suggest（建议）、decide（决策）。每个层级需要指定 nodeCode、nodeName 和 levelUserList。
