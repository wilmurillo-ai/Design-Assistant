# RoundTable Skill - 多 Agent 深度讨论系统

## 技能说明

RoundTable 是一个多专家 Agent 讨论系统，模拟真实的圆桌会议场景。每个 Agent 从不同专业角度（技术、安全、体验等）提供独立观点，经过 5 轮深度讨论后形成更完善的方案。用户无须提前创建子Agent，它利用Sessions_Spawn根据项目需求自动创建临时的子Agent，每个Agent都会扮演不同的角色，得到不同的Prompt，配置不同的模型，进行圆桌讨论，以期实现多维度专业角度的审视和合规，消除单一agent的技能盲区。适用于复杂项目前期的头脑风暴或项目后期的优化和合规审查。该技能会消耗成倍Token和时间，应根据需求选择。用户还可以参与补充意见以增强讨论。
配置有多模型的用户会获得更好的效果。该Skill打包了Agency-Agent的146个垂直领域专家的Prompt，使得每个子agent都具备专业领域的思维方式。

## 版本

0.9.0

## 触发词

- RoundTable
- 圆桌会议
- 圆桌讨论
- 多 Agent 讨论
- 多专家讨论

## 确认机制

自动确认：RoundTable 启动后自动开始讨论，无需手动确认

## 运行时行为

- 子 Agent 调用：使用 openclaw.tools.sessions_spawn 创建临时子 Agent
- 讨论历史：每轮讨论会传递完整历史给子 Agent（用于上下文引用）
- 模型选择：优先使用 OpenClaw 官方 API，降级到标准配置或环境变量

## 作者

Krislu <krislu666@foxmail.com>

## 许可

MIT
