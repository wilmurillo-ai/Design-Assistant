\# ModelArts 资源全功能管理 Skill



\## 基本信息

\- 技能名称：ModelArts\_Resource\_Manager

\- 版本：1.0.0

\- 认证方式：ModelArts 运行环境临时安全凭证

\- 安全等级：高



\## 功能说明

提供 ModelArts 全栈基础资源管理能力：

\- 资源概览查询

\- 训练作业管理

\- 模型管理

\- 推理服务管理

\- Notebook 管理



\## 安全特性

\- 自动脱敏：AK/SK、网络信息、密钥全部屏蔽

\- 无缓存、无存储、无持久化

\- 异常不暴露内部结构

\- 全程内存运行



\## 支持 Action

| action | 说明 |

|--------|------|

| list\_resource\_overview | 查询资源概览 |

| list\_training\_jobs | 查询训练作业 |

| create\_training\_job | 创建训练作业 |

| list\_models | 查询模型 |

| list\_services | 查询推理服务 |

| list\_notebooks | 查询 Notebook |



\## 调用示例

```json

{

&nbsp; "action": "list\_resource\_overview",

&nbsp; "params": {}

}

