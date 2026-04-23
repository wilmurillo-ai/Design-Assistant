---
name: four-layer-memory
description: 四层记忆架构。身份层、工作记忆层、短期日志层、长期存储层分层管理，让记忆既可持续累积，又不会把上下文一次性塞满。
---

# Four-Layer Memory

## 分层定义

1. Identity Layer: 人格锚点、核心身份、长期不变偏好
2. Working Memory Layer: 当前任务、近期关注、热记忆
3. Short-Term Log Layer: 每日记录、近期会话、完整回溯
4. Long-Term Storage Layer: 经确认的偏好、知识、关系和经验

## 使用原则

- 稳定信息进 `identity/` 或 `long-term-memory/`
- 临时任务进 `working-memory/`
- 每日会话进 `short-term-logs/`
- 过期日志转 `archive/`

## 推荐命令

```bash
python3 scripts/personal_ai_memory.py status
python3 scripts/personal_ai_memory.py bootstrap
python3 scripts/personal_ai_memory.py archive --keep-days 14
```
