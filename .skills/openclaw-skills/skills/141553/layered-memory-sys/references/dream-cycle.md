# 梦境模式详解

## 概述

梦境模式模拟人类睡眠时的记忆整理过程：
- 白天经历 → 晚上做梦 → 大脑整理记忆
- 重要的→固化，不重要的→淡忘，相关的→合并

## 触发条件

- **时间**：凌晨2-5点（心跳触发时检测）
- **频率**：每天至少1次
- **也可手动**：`node scripts/dream-cycle.mjs`

## 执行流程

```
1. 加载 index.json 获取所有活跃记忆
2. 加载 .dreams/short-term-recall.json 获取召回数据
3. 执行四项检查：
   ├── 🧠 巩固检查
   ├── 📦 归档检查
   ├── 🗑️ 遗忘检查
   └── 🔗 合并检查
4. 搜索session日志补充上下文
5. 更新 index.json
6. 写入 dream-log.md
```

## 🧠 巩固检查

```
对每条记忆检查 recallCount：
  recallCount ≥ 3 且 layer=flash → 升级到 active (TTL:7)
  recallCount ≥ 5 且 layer=active → 升级到 attention (TTL:30)
  recallCount ≥ 10 且 layer=attention → 升级到 settled (TTL:90)
```

## 📦 归档检查

```
对每条记忆检查过期：
  daysSince(lastActive) >= ttl?
  
  if layer=flash → 直接删除（太琐碎）
  if layer>=active → 概括写入 archive.md → 从index中移除
```

### 归档格式

```markdown
## [分类]
- [日期] 标题
  状态：completed | 概括：摘要...
```

## 🗑️ 遗忘检查

```
  layer=flash 且 过期 → 直接删除
  不写入archive.md（一次性问答不值得归档）
```

## 🔗 合并检查

```
遍历所有记忆对 (i, j)：
  计算语义相似度 = titleSim*0.4 + summarySim*0.4 + tagsOverlap*0.2
  
  if 相似度 >= 0.7 或 tagsOverlap >= 3:
    合并为一条记忆：
    - 保留较长title
    - 合并tags
    - recallCount = 两者之和
    - ttl = max(两者)
    - summary = 两者拼接
    - turns = 两者之和
```

## 日志格式

每次梦境运行后写入 dream-log.md：

```markdown
## YYYY-MM-DD

💤 梦境开始
🧠 巩固：xxx（TTL X→Y天）
📦 归档：xxx → archive.md
🗑️ 遗忘：X条琐碎记忆
🔗 合并：xxx + xxx → xxx
✨ 梦境完成
📊 统计：巩固X条 归档X条 遗忘X条 合并X条
```

## session日志检索

梦境模式最后会搜索session日志，补充近期上下文：

```
路径: ~/.openclaw/agents/main/sessions/*.jsonl
格式: JSONL (每行一个JSON对象)
关键词匹配: 搜索最近3个session文件
输出: 最近60分钟内的对话摘要
```
