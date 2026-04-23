---
name: xgjk-cwork
description: CWork 协同办公原子化技能包 (XGJK v1.05)
---

# xgjk-cwork — 索引

本技能包基于 XGJK v1.05 协议构建，将 CWork 核心协同能力原子化，通过"一接口一脚本"的模式提供高可靠的自动化办公支持。

**当前版本**: v1.0.0
**接口版本**: 所有业务接口统一使用 `/openapi/*` 前缀，自带 `access-token` 鉴权。

## 能力概览
- **user-search**: 按姓名模糊搜索内部员工
- **inbox**: 获取收件箱汇报列表
- **outbox**: 获取发件箱汇报列表
- **report-detail**: 获取单篇汇报的结构化详情
- **tasks**: 工作任务与计划索引
- **todos**: 待办事项管理（列表、完成状态切换）
- **templates**: 汇报模板清单获取
- **ai-qa**: CWork AI 知识库 SSE 问答
- **plan-create**: 快捷创建个人计划

统一规范：
- 认证与鉴权：`./common/auth.md`
- 通用约束：`./common/conventions.md`
- 应用标识：`./openapi/common/appkey.md`

## 脚本使用规则
1. **Python 强制性**: 所有脚本必须使用 Python 编写。
2. **独立执行**: 脚本可通过环境变量 `XG_USER_TOKEN` 独立于 Agent 运行。
3. **1:1 映射**: 每个接口文档 (`openapi/`) 必须对应一个 Python 脚本 (`scripts/`)。

## 能力树

```
xgjk-cwork/
├── SKILL.md
├── common/
│   ├── auth.md          # 认证与鉴权
│   └── conventions.md  # 通用约束
├── openapi/
│   ├── common/
│   │   └── appkey.md   # 应用标识配置
│   ├── user-search/
│   │   ├── api-index.md
│   │   └── search-emp.md
│   ├── inbox/
│   │   ├── api-index.md
│   │   └── get-list.md
│   ├── outbox/
│   │   ├── api-index.md
│   │   └── get-list.md
│   ├── report-detail/
│   │   ├── api-index.md
│   │   └── get-info.md
│   ├── tasks/
│   │   ├── api-index.md
│   │   └── get-page.md
│   ├── todos/
│   │   ├── api-index.md
│   │   ├── get-list.md
│   │   └── complete.md
│   ├── templates/
│   │   ├── api-index.md
│   │   └── get-list.md
│   ├── ai-qa/
│   │   ├── api-index.md
│   │   └── ask-sse.md
│   └── plan-create/
│       ├── api-index.md
│       └── create-simple.md
├── examples/
│   ├── user-search/README.md    # 含 3S1R 管理闭环
│   ├── inbox/README.md          # 含 3S1R 管理闭环
│   ├── outbox/README.md         # 含 3S1R 管理闭环
│   ├── report-detail/README.md  # 含 3S1R 管理闭环
│   ├── tasks/README.md          # 含 3S1R 管理闭环
│   ├── todos/README.md          # 含 3S1R 管理闭环（含写操作确认）
│   ├── templates/README.md      # 含 3S1R 管理闭环
│   ├── ai-qa/README.md          # 含 3S1R 管理闭环（含 SSE 说明）
│   └── plan-create/README.md    # 含 3S1R 管理闭环（含写操作确认）
└── scripts/
    ├── user-search/
    │   ├── search-emp.py
    │   └── README.md
    ├── inbox/
    │   └── get-list.py
    ├── outbox/
    │   └── get-list.py
    ├── report-detail/
    │   └── get-info.py
    ├── tasks/
    │   └── get-page.py
    ├── todos/
    │   ├── get-list.py
    │   └── complete.py
    ├── templates/
    │   └── get-list.py
    ├── ai-qa/
    │   └── ask-sse.py
    └── plan-create/
        └── create-simple.py
```

## 模块数量统计

| 分类 | 数量 | 说明 |
|------|------|------|
| 业务模块 | 9 | user-search / inbox / outbox / report-detail / tasks / todos / templates / ai-qa / plan-create |
| API 接口文档 | 11 | 含 todos/complete.md 和 todos/get-list.md 两个接口 |
| Python 脚本 | 10 | 与接口 1:1 映射（todos 有两条独立脚本） |
| 示例指引文档 | 9 | examples/<module>/README.md，含 3S1R 标准化流程 |
| 公共配置 | 3 | auth.md / conventions.md / appkey.md |
