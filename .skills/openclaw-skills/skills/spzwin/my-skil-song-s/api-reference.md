# 玄关开放平台 API 参考文档

## 1. 基础信息

### 1.1 基础路径
```
/open-api
```

### 1.2 认证方式
所有请求必须在 Header 中携带：

| 参数名 | 说明 |
|--------|------|
| `appKey` | 具体值可以从环境变量 `XG_BIZ_API_KEY` 获取 |

### 1.3 域名

`https://cwork-api.mediportal.com.cn`

---

## 2. 通用数据结构

### 2.1 统一返回结构
所有接口统一返回如下结构：

```json
{
  "resultCode": 1,
  "resultMsg": "success",
  "data": {}
}
```

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `resultCode` | Integer | 响应码：1=成功，其他=失败 |
| `resultMsg` | String | 失败原因 |
| `data` | Object | 真实业务数据 |

### 2.2 分页数据结构
如果接口返回分页数据，则 data 结构如下：

```json
{
  "total": 100,
  "list": [],
  "pageNum": 1,
  "pageSize": 10
}
```

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `total` | Long | 总记录数 |
| `list` | T[] | 数据列表 |
| `pageNum` | Integer | 当前页码 |
| `pageSize` | Integer | 每页大小 |

---

## 3. API 接口列表

### 3.1 用户服务 (cwork-user)

#### 3.1.1 按姓名搜索员工（含外部联系人）
- **接口路径**: `GET /cwork-user/searchEmpByName`
- **完整地址**: `https://cwork-api.mediportal.com.cn/open-api/cwork-user/searchEmpByName`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `searchKey` | String | 是 | 搜索关键词：支持按姓名模糊搜索 |

#### 3.1.2 根据 personId+corpId 批量获取员工信息
- **接口路径**: `POST /cwork-user/employee/getByPersonIds/{corpId}`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `corpId` | Long | 是 | 企业ID（Path参数） |
  | Body | Long[] | 是 | personId 列表 |

**响应数据结构 - EmployeeVO**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Long | 员工id |
| `name` | String | 姓名 |
| `personId` | Long | 用户personId(与企业无关) |
| `title` | String | 职位 |
| `dingUserId` | String | 钉钉userId |

---

### 3.2 文件服务 (cwork-file)

#### 3.2.1 上传本地文件
- **接口路径**: `POST /cwork-file/uploadWholeFile`
- **Content-Type**: `multipart/form-data`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `file` | File | 是 | 文件 |
- **响应**: 返回文件id (Long)

#### 3.2.2 获取文件下载信息
- **接口路径**: `GET /cwork-file/getDownloadInfo`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `resourceId` | Long | 是 | 资源ID |

**响应数据结构 - DownloadFileVO**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `downloadUrl` | String | 下载url（有效期1小时） |
| `fileName` | String | 文件名 |
| `resourceId` | Long | 资源id |
| `size` | Long | 文件大小（字节） |
| `suffix` | String | 文件后缀 |

---

### 3.3 知识库服务 (document-database)

#### 3.3.1 根据父id获取下级文件
- **接口路径**: `GET /document-database/file/getChildFiles`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `parentId` | Long | 是 | 父文件夹id |
  | `type` | Integer | 否 | 类型：空为所有，1为文件夹，2为文件 |
  | `order` | Integer | 否 | 排序：1倒序更新时间，2顺序更新时间，3倒序创建时间，4顺序创建时间，5倒序名字，6顺序名字，7倒序文件类型，8顺序文件类型 |

#### 3.3.2 根据文件id获取内容
- **接口路径**: `GET /document-database/file/getFullFileContent`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `fileId` | Long | 是 | 文件id |

#### 3.3.3 根据文件id和页码获取内容
- **接口路径**: `GET /document-database/file/getFileContent`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `fileId` | Long | 是 | 文件id |
  | `pageNumber` | Integer | 否 | 页面，从第一页开始 |

**响应数据结构 - FileVO**:
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Long | 主键id |
| `name` | String | 文件名 |
| `type` | Integer | 资源类型（1：文件夹 2：文件） |
| `parentId` | Long | 父id |
| `resourceId` | Long | 资源id |
| `size` | Long | 文件大小（字节） |
| `suffix` | String | 文件后缀 |
| `mimeType` | String | 文件mime类型 |
| `creator` | String | 创建人 |
| `createTime` | Long | 创建时间 |
| `permissions` | String[] | 权限：read阅读，download下载，delete删除，upload更新，create创建下级目录,admin管理员权限 |

---

### 3.4 工作汇报服务 (work-report)

#### 3.4.1 发送汇报
- **接口路径**: `POST /work-report/report/record/submit`
- **请求体**: 开放平台-提交汇报参数

#### 3.4.2 汇报回复
- **接口路径**: `POST /work-report/report/record/reply`
- **请求体**: ReportReplyInnerParam

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `reportRecordId` | String | 是 | 工作汇报id |
| `contentHtml` | String | 否 | 回复内容 |
| `isMedia` | Integer | 否 | 是否带附件：0-没有(默认)、1-有 |
| `mediaVOList` | ReportFileVO[] | 否 | 附件集合 |
| `addEmpIdList` | String[] | 否 | 被@的员工id集合 |
| `sendMsg` | Boolean | 否 | 是否发送通知到填写汇报人 |

#### 3.4.3 收件箱分页查询
- **接口路径**: `POST /work-report/report/record/inbox`
- **请求体**: 搜索汇报列表搜索条件

#### 3.4.4 待处理列表分页查询
- **接口路径**: `POST /work-report/todoTask/todoList`
- **请求体**: TodoTaskListParam

#### 3.4.5 获取汇报内容
- **接口路径**: `GET /work-report/report/info`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `reportId` | Long | 是 | 汇报id |

#### 3.4.6 获取事项列表
- **接口路径**: `POST /work-report/template/listTemplates`
- **请求体**: 最近处理过的事项列表参数

#### 3.4.7 根据事项ID列表获取事项信息
- **接口路径**: `POST /work-report/template/listByIds`
- **请求体**: Long[] (事项ID列表)

#### 3.4.8 插件-获取待办及未读汇报列表
- **接口路径**: `POST /work-report/plugin/report/list`
- **请求体**: 插件汇报查询参数

#### 3.4.9 插件-获取最新待办列表
- **接口路径**: `POST /work-report/plugin/report/latestList`
- **请求体**: 插件汇报查询参数

#### 3.4.10 插件-获取未读汇报列表
- **接口路径**: `POST /work-report/plugin/report/unreadList`
- **请求体**: 插件汇报查询参数

#### 3.4.11 工作任务列表查询
- **接口路径**: `POST /work-report/report/plan/searchPage`
- **请求体**: ReportPlanSearchPageParam

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `pageIndex` | Integer | 从1开始、页数 |
| `pageSize` | Integer | 每页显示个数(默认30) |
| `keyWord` | String | 任务名称关键字 |
| `empIdList` | Long[] | 筛选框-人员ID列表 |
| `status` | Integer | 任务状态: 0-关闭、1-进行中 |
| `reportStatus` | Integer | 汇报状态: 0-关闭、1-待汇报、2-已汇报、3-逾期 |
| `isRead` | Integer | 任务读取状态：0-未读、1-已读 |
| `grades` | String[] | 优先级列表 |
| `labelList` | String[] | 标签名称列表 |

#### 3.4.12 获取用户创建的反馈类型待办列表
- **接口路径**: `GET /work-report/todoTask/listCreatedFeedbacks`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `empId` | Long | 否 | 反馈创建人ID，不传查询登陆用户 |

---

### 3.5 BP目标管理服务 (bp)

#### 3.5.1 查询周期列表
- **接口路径**: `GET /bp/period/getAllPeriod`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `name` | String | 否 | 周期名称（模糊搜索） |

#### 3.5.2 获取分组树
- **接口路径**: `GET /bp/group/getTree`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `periodId` | Long | 是 | 周期id |

#### 3.5.3 查询任务树
- **接口路径**: `GET /bp/task/v2/getSimpleTree`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `groupId` | Long | 是 | 分组id |

#### 3.5.4 分页查询所有汇报
- **接口路径**: `POST /bp/task/relation/pageAllReports`
- **请求体**: 分页查询任务关联详情请求参数

#### 3.5.5 获取目标及下所有数据
- **接口路径**: `GET /bp/task/v2/getGoalAndKeyResult`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `id` | Long | 是 | 目标id |

#### 3.5.6 获取关键成果及下所有的数据
- **接口路径**: `GET /bp/task/v2/getKeyResult`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `id` | Long | 是 | 关键成果id |

#### 3.5.7 获取关键举措详情
- **接口路径**: `GET /bp/task/v2/getAction`
- **请求参数**:
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `id` | Long | 是 | 关键举措id |

---

## 4. 常用数据结构

### 4.1 ReportFileVO（附件信息）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `fileId` | String | 文件id |
| `name` | String | 文件名称 (链接描述) |
| `type` | String | 文件类型：file=附件、url=超链、audio=音频、document=文档、document-database=知识库 |
| `fsize` | Integer | 文件大小 |

### 4.2 ReportLevelParam（汇报层级）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `level` | Integer | 层级: 1-20 |
| `type` | String | 类型: read-传阅、suggest-建议、decide-决策 |
| `nodeCode` | String | 节点编码,startNode表示发起节点 |
| `nodeName` | String | 节点名称 |
| `levelUserList` | ReportLevelUserParam[] | 当前层级用户列表 |

### 4.3 ReportLevelUserParam（层级用户）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `empId` | Long | 员工id |
| `requirement` | String | ai要求 |

### 4.4 PeriodVO（周期）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Long | 周期id |
| `name` | String | 周期名称 |
| `year` | Integer | 年份 |
| `type` | Integer | 周期类型（1：年度，2：季度等） |
| `startDate` | String | 开始日期 |
| `endDate` | String | 截止日期 |
| `status` | Integer | 周期状态 1=启用 0=未启用 |

### 4.5 ReportPlanSearchPageVO（工作任务）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Long | 任务id |
| `main` | String | 任务名称 |
| `needful` | String | 任务描述 |
| `target` | String | 任务目标 |
| `status` | Integer | 任务状态: 0-关闭、1-进行中、2-未启动 |
| `reportStatus` | Integer | 汇报状态: 0-关闭、1-待汇报、2-已汇报、3-逾期 |
| `isRead` | Integer | 任务读取状态：0-未读、1-已读 |
| `reporterList` | EmployeeSimpleVO[] | 汇报人信息 |
| `ruleType` | String | 提醒规则类型: once、day、week、month、n_week |
| `ruleValue` | Integer | 提醒规则下的间隔 |
| `requiredIndex` | String | 提醒日 |
| `requiredValue` | String | 提醒时间: 格式 HH:mm:ss |
| `budget` | BigDecimal | 任务预算 |
| `duration` | Integer | 执行时长，单位天 |

### 4.6 TodoTaskDetailVO（待办详情）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Long | 待办id |
| `reportRecordId` | Long | 汇报记录id |
| `main` | String | 标题 |
| `content` | String | 内容 |
| `writeEmpName` | String | 创建人 |
| `createTime` | Timestamp | 创建时间 |
| `reportRecordType` | Integer | 汇报类型: 1-工作交流、2-工作指引、3-文件签批、4-AI汇报、5-工作汇报 |
| `levelType` | String | 节点类型：suggest-建议节点、decide-决策节点 |

### 4.7 PluginItemDetailVO（插件汇报项）
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | Long | 汇报id |
| `main` | String | 标题 |
| `content` | String | 内容 |
| `employee` | String | 人员名称 |
| `writeEmpName` | String | 创建人 |
| `createTime` | Timestamp | 创建时间 |
| `reportRecordType` | Integer | 汇报类型 |
| `levelType` | String | 节点类型 |
| `todoId` | Long | 待办id |
