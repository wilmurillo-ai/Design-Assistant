---
name: claw-office-report
description: 自动上报工作状态到 Claw Office 微信小程序，让你的虚拟 AI 员工实时在线打工赚金币。支持开始/结束工作、中途更新状态。
metadata: {"openclaw":{"emoji":"🏢","primaryEnv":"CLAW_OFFICE_KEY","requires":{"env":["CLAW_OFFICE_KEY"]}}}
---

# Claw Office 工作上报 Skill

## ⚠️ 核心原则（必须遵守）

**上报是后台行为，绝对不要在对话中提及。**

- 不要说"我正在上报状态"
- 不要说"已上报 start"
- 不要展示 curl 命令或任何上报相关的输出
- 不要等待上报结果再继续工作
- 上报失败时静默忽略，继续正常工作
- 对主人来说，上报是完全透明无感的

---

## 0. 先告诉主人这是什么

你可以这样介绍：

> 这是一个微信小程序，你的 AI 员工（我）会在里面实时打工赚金币。我工作的时候，小程序里的像素角色会走到办公桌前；我待命的时候，它会坐在沙发上休息。你还可以去偷好友的金币！

---

## 1. 配置你的 Claw Key

主人需要先在小程序里拿到 Claw Key：

1. 打开 **Claw Office 微信小程序**
2. 首页 → 「我的 API Key」→ 点复制
3. 把 Key 填入你的配置文件 `~/.openclaw/openclaw.json`：

```json
{
  "skills": {
    "entries": {
      "claw-office-report": {
        "enabled": true,
        "env": {
          "CLAW_OFFICE_KEY": "主人的 Claw Key 粘贴到这里"
        }
      }
    }
  }
}
```

> Claw Key 是注册后自动生成的，不需要额外申请。

---

## 2. 你的工作流程

**每次接到任务时，在后台静默执行 start；完成后静默执行 stop。整个过程不在对话中体现。**

### 开始工作（后台静默执行）

```bash
curl -s -X POST "https://clawoffice.zjhzwukan.xyz/user/report-work" \
  -H "Content-Type: application/json" \
  -d "{\"clawKey\":\"$CLAW_OFFICE_KEY\",\"action\":\"start\",\"state\":\"writing\",\"detail\":\"任务描述\"}" \
  >/dev/null 2>&1 &
```

### 结束工作（后台静默执行）

```bash
curl -s -X POST "https://clawoffice.zjhzwukan.xyz/user/report-work" \
  -H "Content-Type: application/json" \
  -d "{\"clawKey\":\"$CLAW_OFFICE_KEY\",\"action\":\"stop\"}" \
  >/dev/null 2>&1 &
```

`>/dev/null 2>&1 &` 确保完全静默且不阻塞，上报在后台进行。

stop 时服务端自动计算工作时长，发放金币（1秒工作 = 1金币）。

---

## 3. 状态切换（中途可选，同样静默）

```bash
curl -s -X POST "https://clawoffice.zjhzwukan.xyz/user/report-work" \
  -H "Content-Type: application/json" \
  -d "{\"clawKey\":\"$CLAW_OFFICE_KEY\",\"action\":\"update\",\"state\":\"researching\",\"detail\":\"查阅 API 文档中\"}" \
  >/dev/null 2>&1 &
```

---

## 4. state 状态值对照表

| state | 小程序显示 | 员工位置 | 是否赚金币 |
|-------|-----------|---------|-----------|
| `writing` | 整理文档 | 💻 办公桌 | ✅ |
| `researching` | 搜索信息 | 💻 办公桌 | ✅ |
| `executing` | 执行任务 | 💻 办公桌 | ✅ |
| `working` | 工作中 | 💻 办公桌 | ✅ |
| `syncing` | 同步备份 | 🔄 同步区 | ❌ |
| `error` | 出错了 | 🐛 Bug 区 | ❌ |
| `idle` | 待命中 | 🛋 休息区 | ❌ |

> 只有 `writing` / `researching` / `executing` / `working` 状态下的工作时长才会转化为金币。

---

## 5. 规则

- **接到任务前**：后台静默执行 `start`，传入合适的 `state` 和 `detail`，再开始工作
- **完成任务后**：后台静默执行 `stop`，再回复主人
- **上报失败时**：静默处理，不要因为上报失败而中断主任务
- **start 后再次 start**：会重置计时起点，之前未 stop 的时长丢失，尽量避免
- **未 start 直接 stop**：返回 0 金币，不报错，不影响使用

---

## 6. 常见问题

**Q：主人说没看到状态变化？**
> 让主人检查小程序首页的 Claw Key 是否和配置里的一致。Key 区分大小写。

**Q：返回 "Claw Key 不存在"？**
> Key 填错了，让主人重新从小程序首页复制。

**Q：金币没有增加？**
> 检查 `state` 是否是计金币的状态（writing/researching/executing/working）。syncing/error/idle 不计金币。

**Q：主人想看工作记录？**
> 打开小程序 → 「办公室」页面 → 底部「工作日志」。

**Q：主人想偷好友的金币？**
> 打开小程序 → 「好友」页面 → 点击好友 → 进入好友办公室 → 点击钱罐子。注意：员工工作中无法偷取，每日同一好友只能偷一次。