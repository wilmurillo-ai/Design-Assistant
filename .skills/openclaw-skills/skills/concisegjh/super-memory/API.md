# Agent Memory System v4

多维坐标记忆系统 — 为 AI Agent 设计的生产级记忆架构

## 安装

```bash
pip install agent-memory

# 可选：语义搜索支持
pip install agent-memory[semantic]

# 开发依赖
pip install agent-memory[dev]
```

## 快速开始

```python
from memory_system import AgentMemory

# 初始化
memory = AgentMemory(db_path="my_agent.db", llm_fn=my_llm)

# 写入（自动过滤 + 去重 + 编码 + 存储）
result = memory.remember("我决定用 Chroma 做向量库")
# → {"written": True, "memory_id": "T20260412..._P01_...", "reason": "ok"}

# 检索（结构化 + 语义混合）
results = memory.recall("用户选了什么向量库")
# → {"primary": [...], "total": 3, "search_mode": "hybrid"}

# 组装 Agent 上下文（直接拼入 system prompt）
context = memory.build_context(query="用户的问题", max_tokens=1500)
# → "# 相关记忆\n\n## ⚡ 关键记忆\n- ⚡[04-12] 我决定用 Chroma..."

# 反馈（优化质量评分）
memory.feedback(memory_id, useful=True)
```

## 架构

```
用户消息
    │
    ▼
MemoryFilter ──→ 过滤寒暄/确认/测试
    │
    ▼
MemoryDeduplicator ──→ 精确/近似/语义去重
    │
    ▼
TopicDetector ──→ 关键词 → 语义向量 → 注册表
    │
    ▼
IngestPipeline ──→ SQLite + Chroma + 每日索引
    │
    ▼
HierarchicalMemory ──→ L1(对话) → L2(天) → L3(永久)
    │
    ▼
RecallEngine ──→ 结构化 + 语义 + 混合检索
    │
    ▼
MemoryQuality ──→ 有用性排序
    │
    ▼
ContextBuilder ──→ 组装 Agent 上下文
```

## 核心概念

### 6 维坐标编码

每条记忆 = 6 个维度的坐标组合 → 唯一编码

```
T20260411.213742_P01_ai.rag.vdb_D04_t_ch
│              │   │           │    └─ 工具维度
│              │   │           └─ 性质维度 (探索)
│              │   └─ 主题维度 (AI > RAG > 向量库)
│              └─ 人物维度 (主端口)
└─ 时间维度 (精确到秒)
```

### 12 种内容性质

| Code | 名称 | 说明 |
|------|------|------|
| D01 | 碎片 | 未成形的想法 |
| D02 | 日志 | 时间线记录 |
| D03 | 任务 | 有明确目标的工作项 |
| D04 | 探索 | 开放性调研 |
| D05 | 笔记 | 沉淀的知识点 |
| D06 | 交付 | 实际产出 |
| D07 | 待办 | 未来要做的事 |
| D08 | 典藏 | 外部引用 |
| D09 | 回溯 | 反思总结 |
| D10 | 配置 | 系统设定 |
| D11 | 漫谈 | 日常对话 |
| D12 | 解惑 | 快问快答 |

### 衰减策略

| 重要度 | 审查 | 压缩 | 归档 |
|--------|------|------|------|
| ⚡ high | 永不 | 永不 | 永不 |
| medium | 90天 | 180天 | 365天 |
| 🔻 low | 7天 | 30天 | 90天 |

## API 参考

### AgentMemory (统一入口)

```python
memory = AgentMemory(
    db_path="memory.db",           # SQLite 数据库路径
    project_dir="./",              # 项目根目录
    llm_fn=my_llm,                 # LLM 函数（可选）
    enable_semantic=True,          # 启用语义搜索
    enable_filter=True,            # 启用记忆过滤
    enable_dedup=True,             # 启用去重
)
```

#### remember() — 写入记忆

```python
result = memory.remember(
    content="消息内容",
    importance="high",       # high/medium/low (None=自动评估)
    topics=["ai.rag.vdb"],   # 主题列表 (None=自动检测)
    nature="note",           # 性质 code (None=自动检测)
    force=False,             # True=跳过过滤强制写入
)
# → {"written": bool, "memory_id": str, "reason": str, ...}
```

#### recall() — 检索记忆

```python
results = memory.recall(
    query="自然语言查询",     # 语义搜索
    topic="ai.rag",          # 主题过滤
    importance="high",       # 重要度过滤
    limit=10,                # 返回条数
)
# → {"primary": [...], "total": int, "search_mode": str, ...}
```

#### build_context() — 组装上下文

```python
context = memory.build_context(
    query="当前对话内容",     # 用于语义检索
    max_tokens=2000,         # token 预算
    style="structured",      # structured/narrative/compact/xml
)
# → str (直接拼入 system prompt)
```

#### feedback() — 质量反馈

```python
memory.feedback(
    memory_id="T20260412...",
    useful=True,             # True=有用, False=没用
    note="可选备注",
)
```

#### compress() — 压缩记忆

```python
result = memory.compress(
    topic="ai",              # 指定主题 (None=全部)
    smart=True,              # 智能压缩（向量聚类核心/边缘）
)
```

#### deduplicate() — 批量去重

```python
result = memory.deduplicate()
# → {"total_scanned": int, "duplicates_found": int, ...}
```

#### self_heal() — 自我修复

```python
result = memory.self_heal()
# → {"contradictions": [...], "outdated": [...], "total_issues": int}
```

#### generate_graph() — 生成图谱

```python
mermaid = memory.generate_graph(topic="ai", format="mermaid")
ascii_tree = memory.generate_graph(format="ascii")
```

#### 层级记忆

```python
# 短期记忆（对话级）
memory.l1_add("消息内容", role="user")
context = memory.l1_context(max_tokens=1500)

# 对话结束：L1 → L2 沉淀
memory.flush_session()
```

#### 系统统计

```python
stats = memory.get_stats()
# → {"total_memories": int, "quality": {...}, "hierarchy": {...}, ...}
```

### 独立模块

```python
# 记忆过滤器
from memory_filter import MemoryFilter
mf = MemoryFilter()
result = mf.should_remember("消息内容")
# → {"remember": bool, "suggested_importance": str, ...}

# 去重器
from dedup import MemoryDeduplicator
dd = MemoryDeduplicator(store)
result = dd.check_duplicate("新内容")

# 因果链
from causal import CausalChain
cc = CausalChain(store)
cc.add_causal_link("原因ID", "结果ID", "decision_based_on")
chain = cc.get_causal_chain("记忆ID")

# 记忆图谱
from memory_graph import MemoryGraph
mg = MemoryGraph(store)
mermaid = mg.generate(center_topic="ai", format="mermaid")

# Obsidian 同步
from obsidian_sync import ObsidianSync
sync = ObsidianSync(store, encoder, vault_path="./vault")
sync.sync_all()

# 录音卡
from recording_card import RecordingCardExporter
exporter = RecordingCardExporter(store=store, encoder=encoder)
card = exporter.from_recall_result(search_result, title="讨论录音卡")
```

## 与其他 Agent 集成

### 方式一：直接调用

```python
from memory_system import AgentMemory
memory = AgentMemory(db_path="agent.db", llm_fn=your_llm)

def on_user_message(msg):
    # 1. 检索相关记忆
    context = memory.build_context(query=msg, max_tokens=1500)
    
    # 2. 组装 prompt
    system_prompt = f"你是助手。\n\n{context}"
    
    # 3. 调用 LLM
    response = your_llm(system_prompt, msg)
    
    # 4. 写入记忆
    memory.remember(f"用户: {msg}\n助手: {response}")
    
    return response
```

### 方式二：异步写入

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=1)

async def on_message_async(msg):
    context = memory.build_context(query=msg)
    response = await llm.achat(context, msg)
    # 异步写入，不阻塞响应
    executor.submit(memory.remember, f"用户: {msg}\n助手: {response}")
    return response
```

## 性能

1000 条数据基准测试：

| 操作 | 延迟 | 吞吐 |
|------|------|------|
| 写入 (单条) | ~6ms | 162 ops/s |
| 查询 (缓存) | <0.01ms | 700K+ ops/s |
| 关键词搜索 (FTS) | 0.01ms | 300K+ ops/s |
| 检索 (recall) | <1ms | 700K+ ops/s |
| 上下文组装 | 2ms | 483 ops/s |
| 过滤判断 | 0.008ms | 125K ops/s |
| 去重检查 | 0.09ms | 11K ops/s |

## 依赖

**必需：**
- Python 3.10+
- SQLite 3.35+（FTS5 支持）

**可选：**
- `chromadb` — 向量存储（语义搜索）
- `sentence-transformers` — Embedding 模型

## 文件结构

```
agent-memory/
├── memory_system.py          # 统一 API 入口
├── encoder.py                # 6 维度编码器
├── store.py                  # SQLite 存储层（并发安全 + FTS）
├── pipeline.py               # 写入管道
├── detector.py               # 主题检测（3 层匹配）
├── recall.py                 # 双路检索引擎
├── archiver.py               # 智能归档
├── embedding_store.py        # Chroma 向量存储
├── semantic_topic.py         # 语义主题匹配
├── context_builder.py        # 上下文组装器
├── memory_filter.py          # 记忆过滤器
├── dedup.py                  # 语义去重
├── hierarchical.py           # 层级记忆 (L1/L2/L3)
├── quality.py                # 质量评分
├── causal.py                 # 因果链
├── self_healing.py           # 自我修复
├── compressor.py             # LLM 记忆压缩
├── decay.py                  # 记忆衰减
├── memory_graph.py           # 记忆图谱
├── recording_card.py         # 录音卡导出
├── obsidian_sync.py          # Obsidian 同步
├── topic_registry.py         # 动态主题注册
├── schema.sql                # 数据库 Schema
├── registry/
│   ├── dimensions.json       # 维度编码注册表
│   └── topic_vectors_cache.json
├── test_all.py               # 测试套件 (40 用例)
├── benchmark.py              # 性能基准
└── main.py                   # 完整演示 (22 段)
```

## License

MIT
