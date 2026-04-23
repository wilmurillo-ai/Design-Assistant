# 错误处理指南

本文档说明 didi-taxi skill 使用过程中可能遇到的错误及解决方案。

> `<skill-dir>` 代表 didi-taxi 技能的安装根目录（即 SKILL.md 所在目录），可通过 `openclaw skills info didi-taxi` 获取。

## 目录

- [错误处理指南](#错误处理指南)
  - [目录](#目录)
  - [统一错误码表](#统一错误码表)
  - [watch 订单与 Cron 错误](#watch-订单与-cron-错误)
  - [常见问题 (FAQ)](#常见问题-faq)
  - [获取帮助](#获取帮助)

***

## 统一错误码表

所有 MCP 工具返回的统一错误码对照：

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `-32001` | 命中限流 | 请等待一段时间后重试（配额限制按时间窗口重置） |
| `-32002` | 鉴权失败（`auth failed`） | Key 存在但无效或已过期，执行 `## API Key 与配置` 的引导流程（含发送二维码） |
| `-32010` | 参数验证失败 | 检查参数格式，确保所有值为字符串 |
| `-32011` | 订单不存在 | 确认订单ID正确 |
| `-32021` | 预估结果过期 | 重新调用价格预估获取新的 traceId |
| `-32030` | 不支持订单类型 | 该类型订单不支持此操作 |
| `-32031` | 订单未支付 | 订单未进入支付状态 |
| `-32040` | 订单已经取消过了 | 订单已被取消，无需重复操作 |
| `-32041` | 订单无法被取消 | 司机已接单或订单已完成，无法通过 API 取消 |
| `-32050` | 内部错误 | 稍后重试，如持续失败请联系客服 |
| `-32060` | 支付失败 | 检查支付账户状态或更换支付方式 |

***

## watch 订单与 Cron 错误

### 单次探测脚本无法启动

**症状：**

```
node: cannot find module '<skill-dir>/scripts/didi_poll_order.js'
```

**解决方案：**

```bash
# 确认脚本路径
ls -la <skill-dir>/scripts/didi_poll_order.js

# 使用单次探测模式启动
node <skill-dir>/scripts/didi_poll_order.js --order-id "ORDER_ID"
```

### Cron 任务未按预期推送消息

**症状：**
watch 订单后，当前对话没有每 30 秒收到新消息

**解决方案：**

```bash
# 查看 Cron 任务
openclaw cron list

# 手动触发一次任务，确认当前配置是否可运行
openclaw cron run JOB_ID

# 查看单次探测日志
cat <skill-dir>/tmp/didi_orders/{ORDER_ID}.txt
```

如果任务绑定会话配置失败，检查 `--session isolated` 参数是否正确，并通过 `openclaw cron list` 确认任务状态。

### 终态后任务未自动清理

**症状：**

订单已到达或已终态，但 cron 任务仍存在

**解决方案：**

```bash
# 立即手动删除任务
openclaw cron remove JOB_ID
```

### 重复创建 watch 任务

**症状：**

同一订单在短时间内被创建了多个 cron 任务

**解决方案：**

```bash
# 查找相关任务并清理
openclaw cron list
openclaw cron remove JOB_ID_1
openclaw cron remove JOB_ID_2
```

***

## 常见问题 (FAQ)

**Q: 为什么说"我要上班"没反应？**
A: 需要先配置 `assets/PREFERENCE.md` 中的家和公司地址，以及上班场景的车型偏好。

**Q: 预估价格和实际价格不一致？**
A: 预估价格为参考值，实际费用以行程完成后为准。

**Q: 如何查看历史订单？**
A: 当前 API 仅支持查询 MCP 渠道未完成订单，历史订单请在滴滴 App 中查看。

**Q: watch 订单会在什么时候自动结束？**
A: `status=2` 或 `status in [3..12]` 时结束，并自动删除对应 cron 任务。

**Q: 支持哪些城市？**
A: 支持滴滴服务覆盖的所有中国大陆城市。

***

## 获取帮助

如果以上方案无法解决问题，请：

1. 检查 [workflow.md](./workflow.md) 确认操作流程
2. 查看日志文件 `<skill-dir>/tmp/didi_orders/{ORDER_ID}.txt`
3. 访问 <https://mcp.didichuxing.com> 获取最新文档
