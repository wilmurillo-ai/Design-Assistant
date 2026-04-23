# 发布说明（中文）

## 版本 0.1.3

这是 `telegram-group-moderation` 的生产接入增强版，定位仍然是 **Telegram 群组审核接入层**，而不是替代已有审核规则系统。

核心思路是：
- 复用现有审核策略技能，例如 `post-content-moderation`
- 由 Telegram 接入层负责 webhook、消息标准化、动作执行、违规计数与审核日志
- 把审核结果映射成删消息、警告、禁言、封禁或人工复核动作

## 本版已包含内容

### 1. Telegram webhook 接入骨架

支持 Telegram update 的基础接收与处理流程，适合作为后续接入业务系统的起点。

### 2. 消息标准化逻辑

可以把 Telegram 的不同消息类型整理成统一审核输入，便于后续调用审核核心。

当前重点覆盖：
- `message`
- `edited_message`
- `channel_post`
- `edited_channel_post`

### 3. 审核核心调用骨架

内置对外部审核 endpoint 的调用结构，方便你接现有审核系统。

### 4. Telegram 动作执行增强

当前已包含：
- 删除消息示例
- 封禁用户示例
- 限时禁言示例
- 发送警告消息示例
- review 转管理员群通知示例

### 5. 多语言接入示例

当前已补充以下通用语言示例：
- PHP
- Python
- Go
- Java

### 6. Webhook 基础鉴权

当前已补充 Telegram webhook secret 校验示例，可作为生产接入前的最小安全基线。

### 7. offense count 与阶梯处罚

当前已补充：
- 基于时间窗口的违规次数统计
- file / redis / db 三种 offense store 驱动
- Redis 最小可用实现
- DB 最小可用 PDO 实现
- 按第 1 / 2 / 3 次违规自动切换处罚动作

默认思路为：
- 第 1 次：删除 + 警告
- 第 2 次：删除 + 禁言
- 第 3 次：删除 + 封禁

### 8. 生产接入参考材料

当前已新增：
- 生产接入建议文档
- env 配置模板
- moderation core HTTP 契约示例
- 生产版 HTTP 契约说明
- Redis / DB offense store 设计说明
- 默认 offense log 表结构示例

### 9. 审核日志落库与 trace_id

当前已补充：
- `TelegramTraceIdBuilder`
- `TelegramAuditLogStore`
- 默认审核日志表结构示例
- trace_id 串联 webhook / moderation / action / audit log
- 动作执行结果 `action_result` 落库

### 10. 基础安全与治理配置

已加入：
- allowlist host 校验
- allowed chat ids
- admin exempt
- trusted bot exempt
- dry-run
- 超时控制
- offense store driver 配置
- audit log table 配置

## 本版更适合什么场景

这版适合：
- 已经有审核规则，想快速接入 Telegram 群治理
- 想先搭起 webhook + 审核 + 动作执行 + 审计日志 的最小闭环
- 想在 PHP 7.3 / Yaf 项目里逐步演进 Telegram 群审核能力

## 本版暂时不包含什么

这版还不是完整成品，以下能力需要后续补齐：
- review 状态流转后台化
- offense log 审计字段进一步扩充
- mute / unmute 的更完整控制
- 阶梯处罚增加更复杂的规则与豁免体系
- 图片 OCR / 二维码识别
- 视频抽帧 / 字幕识别 / ASR
- 更完整的 Telegram Bot 管理动作封装

## 风险边界

请不要把这版直接理解为：
- 开箱即用的 Telegram 全自动风控系统
- 完整的多模态反广告引擎
- 无需二次开发即可生产上线的商业化审核机器人

更准确地说，它是：
- 一个清晰、可扩展、适合落地改造的 Telegram 审核接入层 skeleton / beta

## 推荐接入方式

建议与 `post-content-moderation` 配合使用：
- `post-content-moderation` 负责审核规则与结构化结果
- `telegram-group-moderation` 负责 Telegram webhook、消息解析、动作执行、违规计数和审计日志

## 下一步建议

建议按这个顺序继续增强：
1. review 状态流转后台化
2. offense log 审计字段进一步扩充
3. mute / unmute 做更完整的恢复策略
4. 阶梯处罚增加更复杂的规则与豁免体系
5. 再补图片 / 视频审核链路
6. 最后再做多群、多策略、多环境配置
