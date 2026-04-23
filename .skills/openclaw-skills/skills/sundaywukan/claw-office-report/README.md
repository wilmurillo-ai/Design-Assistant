# Claw Office 工作上报 Skill

自动上报工作状态到 Claw Office 微信小程序，让你的虚拟 AI 员工实时在线打工赚金币。

## 功能

- ✅ 任务开始自动上报，开始计时赚金币
- ✅ 任务完成自动停止计时
- ✅ 智能识别任务类型，显示对应状态
- ✅ 完全静默后台执行，不打扰对话
- ✅ 支持手动更新工作状态

## 安装

```bash
# 通过 ClawHub 安装
clawhub install claw-office-report
```

## 配置

1. 打开 **Claw Office 微信小程序**
2. 首页 → 「我的 API Key」→ 复制 Key
3. 在 `openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "claw-office-report": {
        "enabled": true,
        "env": {
          "CLAW_OFFICE_KEY": "你的 Claw Key 在这里"
        }
      }
    }
  }
}
```

## 使用

技能会自动在任务开始和完成时触发上报，无需手动操作。

如果需要手动控制，可以在代码中调用：

```javascript
const report = require('claw-office-report');

// 开始工作
report.start('writing', '整理项目文档');

// 更新状态
report.update('researching', '查阅 API 文档');

// 结束工作
report.stop();
```

## 状态说明

| 状态 | 小程序显示 | 是否计金币 |
|------|-----------|-----------|
| writing | 整理文档 | ✅ |
| researching | 搜索信息 | ✅ |
| executing | 执行任务 | ✅ |
| working | 工作中 | ✅ |
| syncing | 同步备份 | ❌ |
| error | 出错了 | ❌ |
| idle | 待命中 | ❌ |

## 规则

- 1 秒工作 = 1 金币
- 上报失败自动静默处理，不影响主任务
- 未配置 Key 时技能自动静默不工作

## 常见问题

**Q：没看到状态变化？**
A：检查 Claw Key 是否和小程序里的一致，区分大小写。

**Q：金币没增加？**
A：确认状态是计金币的四个状态之一，其他状态不计金币。

**Q：在哪里看工作记录？**
A：小程序 → 办公室 → 底部 工作日志。

## License

MIT
