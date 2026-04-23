# 生产接入建议（中文）

## 目标

这份说明用于把 `telegram-group-moderation` 从 demo / skeleton 接入层，推进到更稳的生产接入版本。

## 推荐生产架构

建议至少分成两个部分：

### 1. Webhook 接入层

职责：
- 接收 Telegram update
- 做 secret 校验
- 做 chat allowlist 校验
- 做基础消息标准化
- 快速返回 200
- 尽量不在请求线程里做重操作

### 2. 审核与动作执行层

职责：
- 读取标准化后的待处理事件
- 调用审核核心
- 根据规则执行 delete / warn / mute / ban / review
- 写违规次数与审计日志

如果群消息量较大，不建议所有处理都在 webhook 同步线程中完成。

## offense count 存储建议

当前 skill 的 PHP 版本内置：
- 本地 JSON 文件 demo
- Redis 最小可用实现
- DB 驱动结构预留

生产建议：
- 单实例低并发：可先用数据库
- 多实例部署：优先 Redis 或数据库
- 不建议长期依赖本地 JSON 文件

原因：
- 多实例下不同机器之间不会共享违规计数
- JSON 文件不适合高并发写入
- 进程异常中断时更容易出现覆盖或竞争问题

## 阶梯处罚建议

建议保留默认三段式，但要支持按群配置：

- 第 1 次：删除 + 警告
- 第 2 次：删除 + 禁言
- 第 3 次：删除 + 封禁

同时建议额外补：
- 管理员豁免
- 服务机器人豁免
- 特定群白名单策略
- 高风险关键词直接跳过前两级处罚

## Review 机制建议

生产环境下不要只返回 review 状态而不落地。

建议至少做一个：
- 发送到管理员审核群
- 写入 review 队列表
- 写入审计表，供后台查看

如果只做 review 但没有人接收，等于没做。

## Telegram Bot 权限建议

机器人至少需要：
- 删除消息权限
- 限制成员权限
- 封禁成员权限

如果需要更完整治理，还可能需要：
- 读取群消息权限
- 在管理员审核群发送消息权限

## 日志建议

生产建议至少记录：
- chat_id
- message_id
- user_id
- username
- normalized content 摘要
- audit_status
- risk_level
- action
- offense_count
- reason
- created_at

## 超时与失败策略

建议所有外部调用都设置：
- connect timeout
- request timeout

并区分两类失败：

### 1. 审核核心失败

建议：
- 高风险群：偏保守处理
- 普通群：review 或写待人工复核队列

### 2. Telegram API 动作失败

建议：
- 单独记录错误日志
- 允许有限次重试
- 不要把动作失败误写成审核通过

## 媒体处理建议

如果你的群里广告主要出现在图片和视频：

需要额外补：
- 图片 OCR
- 二维码识别
- 视频抽帧
- 字幕 OCR
- ASR 语音转文本

否则 Telegram 接入层只能稳定拦文本和 caption，不能宣称完整多模态审核。

## 上线顺序建议

### 阶段 1：测试群
- 开启 dry-run 或 review
- 不开 ban
- 观察误判率

### 阶段 2：小流量正式群
- 开 delete + warn
- 暂时只对高风险开 mute

### 阶段 3：稳定后再加 ban
- 对重复违规或高风险诈骗再启用 ban

## 0.1.1 建议目标

如果要把这个 skill 定义为更完整的 0.1.1，建议至少满足：
- 文档上明确 demo 与生产边界
- 配置上明确 offense store / review / action policy 的扩展方向
- 示例代码上包含 webhook secret、warn、mute、review、阶梯处罚
- 发布文案明确“可生产接入，不等于完整风控成品”
