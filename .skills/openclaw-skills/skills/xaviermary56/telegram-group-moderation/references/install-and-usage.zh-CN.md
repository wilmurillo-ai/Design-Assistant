# 安装与使用说明（中文）

## 适用场景

这个 skill 适合以下场景：

- 你已经有一套内容审核规则，想接入 Telegram 群组
- 你希望机器人在群里自动拦截广告、联系方式、引流内容
- 你希望把审核结果映射成删除消息、警告、禁言、封禁或人工复核动作
- 你当前项目是 PHP 7.3 / Yaf，想先做一个可逐步增强的接入层

这个 skill 更像是 **Telegram 接入层**，不是替代审核规则本身。  
建议配合现有 `post-content-moderation` 一起使用。

## 推荐架构

建议拆成两层：

### 第一层：审核策略核心

使用：`post-content-moderation`

负责：
- 判断是否广告
- 判断是否联系方式 / 引流
- 处理白名单 / 自定义规则
- 输出 `pass / reject / review`

### 第二层：Telegram 接入层

使用：`telegram-group-moderation`

负责：
- 接收 Telegram webhook
- 提取群消息文本、caption、图片/视频存在信息
- 组装审核请求
- 调用审核核心
- 根据结果执行 delete / warn / mute / ban / review

## 当前版本能做什么

当前版本已经提供：

- Telegram update 标准化骨架
- webhook 示例入口
- 删除消息示例
- 封禁用户示例
- 限时禁言示例
- review 通知管理员群示例
- 群组 allowlist
- 管理员豁免
- dry-run 配置
- 审核核心外部 endpoint 调用骨架
- PHP / Python / Go / Java 多语言接入示例

## 当前版本还没有完全补齐的部分

上线前请注意，当前示例脚本还需要你按业务补充：

- offense count 违规次数累计
- 图片 OCR / 二维码识别 / 视频抽帧 / ASR
- 与你现有审核服务的真实字段对接

当前这版已经补上基础能力：
- webhook secret 校验
- warn 提示消息发送
- mute 限时禁言动作
- review 转管理员群通知
- offense count 时间窗口统计
- 按第 1 / 2 / 3 次违规切换阶梯处罚

## 配置说明

主要配置位于：

- `scripts/config.php`

### 1. Telegram 配置

#### `telegram.bot_token`

Telegram Bot Token。

来源：
- 通过 BotFather 创建机器人后获得

建议：
- 只通过环境变量注入
- 不要写死在代码里

#### `telegram.api_base`

Telegram Bot API 地址。

默认：

```text
https://api.telegram.org
```

#### `telegram.webhook_secret`

Webhook 鉴权密钥。

建议：
- 生产环境必须启用
- 在 webhook 入口校验 header 或路径中的 secret

#### `telegram.allowed_hosts`

Telegram API 出站白名单。

默认：

```php
['api.telegram.org']
```

#### `telegram.allowed_chat_ids`

允许处理的群组 ID 白名单。

建议：
- 一开始只放测试群
- 验证稳定后再扩展到正式群

#### `telegram.admin_review_chat_id`

管理员审核群 / 告警群 ID。

建议用途：
- 把 review 结果推送给管理组
- 记录高风险命中摘要

### 2. 审核核心配置

#### `moderation_core.mode`

审核核心模式。

当前默认：

```text
external
```

含义：
- 当前 Telegram skill 默认把内容投递到一个外部审核接口
- 这个接口可以是你现有的审核服务
- 也可以是你后面包装好的 `post-content-moderation` HTTP 服务

#### `moderation_core.endpoint`

审核核心接口地址。

建议：
- 使用 HTTPS
- 放入 allowlist
- 只允许可信内网或固定业务域名

#### `moderation_core.token`

审核核心接口鉴权 token。

建议：
- 使用 Bearer Token
- 仅通过环境变量注入

#### `moderation_core.allowed_hosts`

审核核心接口地址白名单。

建议：
- 不要留空直接上线
- 只允许你的正式审核服务域名

#### `moderation_core.dry_run`

是否 dry-run。

开启后：
- 不会真的走正式审核链路
- 当前示例会直接返回 `review`
- 适合联调 Telegram 接入和动作逻辑

### 3. 动作策略配置

#### `policy.delete_on_reject`

命中拒绝时是否删消息。

#### `policy.warn_on_reject`

命中拒绝时是否警告。

当前示例里已经支持发送 warn 消息。

#### `policy.ban_on_high_risk`

高风险拒绝时是否直接封禁。

建议：
- 初期先关闭
- 观察误判情况后再打开

#### `policy.mute_seconds`

禁言时长。

当前示例里已经接入 `restrictChatMember`，可作为基础限时禁言实现。

#### `policy.offense_window_seconds`

违规统计时间窗口。

含义：
- 只统计这个时间窗口内的违规次数
- 超过窗口的历史违规会自动失效

例如：
- 配置 `86400` 表示只统计最近 24 小时内的违规记录

#### `policy.first_offense_action`
- `policy.second_offense_action`
- `policy.third_offense_action`

用于定义阶梯处罚动作。

推荐初始配置：
- 第 1 次：`delete_and_warn`
- 第 2 次：`delete_and_mute`
- 第 3 次：`delete_and_ban`

#### `policy.offense_store_driver`

违规次数存储驱动。

当前支持的结构是：
- `file`：本地 JSON demo
- `redis`：已提供最小可用实现
- `db`：生产 stub，等你接真实数据库

#### `policy.offense_store_path`

违规次数存储路径。

当前示例默认使用本地文件 JSON 存储，仅适合单机 demo 或联调环境。
生产环境更建议替换为 Redis 或数据库。

#### `policy.offense_store_table`

数据库驱动下建议使用的 offense log 表名。

默认：
- `telegram_moderation_offense_log`

#### `policy.re_audit_edited_messages`

是否重审编辑后的消息。

建议：
- 默认开启
- 否则用户可能先发正常内容，再编辑成广告

#### `policy.admin_user_ids`

管理员豁免 ID 列表。

建议：
- 仅放可信管理员
- 不要把普通机器人或普通用户放进去

#### `policy.trusted_bot_user_ids`

可信服务机器人 ID 列表。

建议：
- 用于放行你自己接入的系统机器人
- 避免被误删

### 4. Redis / DB 配置

#### `redis.host` / `redis.port` / `redis.password` / `redis.database`

Redis offense store 的连接配置。

#### `redis.key_prefix`

Redis key 前缀。

默认：

```text
telegram:moderation:v1:offense:
```

最终 key 示例：

```text
telegram:moderation:v1:offense:-1001234567890:777
```

#### `db.dsn` / `db.username` / `db.password`

数据库 offense store 配置。

当前代码里 DB 驱动已经提供最小可用 PDO 实现。
默认建议表结构见：
- `references/db-schema-example.sql`

## 推荐上线步骤

### 第一步：先测试群联调

建议只配置一个测试群：

- `allowed_chat_ids` 先只放测试群
- 打开 dry-run
- 暂时不启用 ban

### 第二步：验证消息链路

重点验证：

- 普通文本消息
- 带 caption 的图片
- 带 caption 的视频
- 编辑消息
- 转发消息
- 管理员消息
- 机器人消息

### 第三步：验证动作链路

重点验证：

- reject 是否真的删消息
- 高风险是否按预期 ban
- 管理员是否正确豁免
- 日志是否能定位 chat_id / user_id / message_id

### 第四步：再逐步上线正式群

建议按群逐步放量，不要一次性全开。

## 风险边界

这版 skill 目前属于：
- 可作为 Telegram 审核接入层 skeleton 使用
- 适合继续二次开发

这版 skill 暂时不应直接宣称为：
- 完整的 Telegram 反垃圾即插即用成品
- 完整的图片二维码审核系统
- 完整的视频字幕/语音审核系统

## 建议的下一步增强

建议后续优先补：

1. offense count 存储从本地文件 demo 升级到 Redis / DB
2. 多级阶梯处罚增加可配置豁免与更细分动作
3. mute / unmute 做更完整的恢复策略
4. review 转管理员群增加更丰富证据摘要
5. 图片 OCR / 二维码识别
6. 视频字幕 / 抽帧 / ASR
7. 与现有 `post-content-moderation` 做真实 HTTP 契约统一

如果你准备生产接入，继续阅读：
- `references/production-rollout.zh-CN.md`
- `references/http-contract-example.json`
- `references/http-contract-production.zh-CN.md`
- `references/http-contract-production-v2.zh-CN.md`
- `references/redis-db-offense-store.zh-CN.md`
- `references/audit-log-rollout.zh-CN.md`
- `references/audit-log-schema-example.sql`
- `references/config-template.env.example`
