# 安装后参考

## 验证 distill

```bash
bash ~/.openclaw/workspace/scripts/self-improvement/distill.sh --check-only
```

正常输出 JSON，包含 `patterns` / `category_fallback` / `meta`。

## 查看 Cron 状态

```bash
openclaw cron list
```

两个 Cron 应存在：
- `self-improvement-check`（每30分钟）
- `memory-daily-distill`（每日 23:30）

## 测试 Hook

发送包含「不对」「错了」「能不能加」等关键词的消息，观察是否写入 `.learnings/` 文件。

## 调试

```bash
# 查看 distill JSON
bash ~/.openclaw/workspace/scripts/self-improvement/distill.sh --check-only | python3 -m json.tool

# 手动触发 archive dry-run
bash ~/.openclaw/workspace/scripts/self-improvement/archive.sh --dry-run

# 查看 learnings 文件
cat ~/.openclaw/workspace/.learnings/LEARNINGS.md
```
