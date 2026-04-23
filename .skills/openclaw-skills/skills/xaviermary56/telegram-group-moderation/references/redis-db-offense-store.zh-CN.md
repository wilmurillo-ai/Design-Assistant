# Redis / DB offense store 设计说明（中文）

## 目标

把当前本地 JSON 文件版违规次数统计，升级为更适合生产环境的 Redis / DB 方案。

## 为什么要升级

本地 JSON 文件仅适合：
- 单机 demo
- 本地联调
- 小范围测试

不适合生产的原因：
- 多实例之间无法共享违规次数
- 高并发写入容易冲突
- 不利于审计和排查
- 不方便做跨群或跨时间维度分析

## Redis 方案建议

### 适用场景

适合：
- 高频实时判断
- 多实例部署
- 违规窗口统计以“最近 N 小时/天”为主

### 推荐 key 设计

```text
telegram:moderation:v1:offense:<chat_id>:<user_id>
```

### 推荐 value 结构

可选方案 1：有序集合（推荐）
- score：违规时间戳
- member：时间戳或 trace_id

优点：
- 方便按时间窗口清理
- 方便统计最近一段时间内的违规次数

### 推荐逻辑

1. reject 时写入当前时间戳
2. 清理窗口外数据
3. 统计当前窗口内数量
4. 返回 offense_count

### TTL 建议

TTL 可以略大于 `offense_window_seconds`，例如：
- 窗口 24h
- TTL 30h 或 48h

## DB 方案建议

### 适用场景

适合：
- 需要长期审计
- 需要后台查看处罚历史
- 需要复杂统计报表

### 建议表结构

表名示例：

```text
telegram_moderation_offense_log
```

字段建议：
- `id`
- `chat_id`
- `user_id`
- `message_id`
- `audit_status`
- `risk_level`
- `action`
- `reason`
- `created_at`

### 统计方式

实时判断时可按：
- `chat_id`
- `user_id`
- `created_at >= now - offense_window_seconds`

统计最近窗口内的 reject 次数。

## 推荐实践

如果你要：
- **高性能实时处罚** -> Redis 优先
- **长期审计和报表** -> DB 必备
- **两者都要** -> Redis 负责实时判断，DB 负责审计落库

## Skill 当前建议

当前 skill 更推荐这种落地方式：
- offense_count 判断用 Redis
- 处罚日志和 review 日志落 DB

这样既快，也方便回查。

## 当前 skill 已实现到什么程度

当前 PHP 版已经补上 Redis offense store 的最小可用实现：
- 使用 Redis zset 记录违规时间戳
- reject 时写入当前时间
- 自动清理窗口外数据
- 返回当前窗口内 offense_count
- 使用 key 前缀 + `chat_id:user_id` 作为统计维度

当前 DB 版也已经补上了最小可用实现：
- 使用 PDO 写入 offense log
- 按 `chat_id + user_id + created_at` 统计时间窗口内的违规次数
- 默认表名为 `telegram_moderation_offense_log`

如果你不想直接使用默认表结构，可以按自己的项目表结构修改 SQL。
