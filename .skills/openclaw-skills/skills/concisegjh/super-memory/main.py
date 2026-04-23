#!/usr/bin/env python3
"""
main.py - Agent Memory System 演示
双路检索（结构化 + 语义）+ 多主题智能拆分
"""

import os
import json
import time
from encoder import DimensionEncoder
from store import MemoryStore
from pipeline import IngestPipeline
from recall import RecallEngine
from archiver import Archiver
from topic_registry import TopicRegistry
from recording_card import RecordingCardExporter
from decay import MemoryDecay
from obsidian_sync import ObsidianSync


def mock_llm(prompt: str) -> str:
    """模拟 LLM 拆分响应（演示用）"""
    # 根据 prompt 内容返回预设的拆分结果
    if "RAG" in prompt and "评审会" in prompt:
        return json.dumps([
            {"content": "RAG 用 Chroma 挺好的，轻量又好上手", "topic": "ai.rag.vdb", "nature": "note", "tools": ["chroma"], "knowledge": ["pref"]},
            {"content": "明天下午3点开项目评审会", "topic": "dev", "nature": "todo", "tools": [], "knowledge": []},
        ], ensure_ascii=False)
    elif "Agent" in prompt and "Docker" in prompt:
        return json.dumps([
            {"content": "Agent 的记忆系统可以用多维坐标的方式", "topic": "ai.agent.mem", "nature": "explore", "tools": [], "knowledge": ["skill"]},
            {"content": "部署方面用 Docker 容器化比较好", "topic": "dev.ops", "nature": "note", "tools": ["docker"], "knowledge": ["pref"]},
        ], ensure_ascii=False)
    # 默认：单片段
    return json.dumps([
        {"content": "", "topic": "", "nature": "", "tools": [], "knowledge": []}
    ], ensure_ascii=False)


def demo():
    print("=" * 60)
    print("  Agent Memory System v2 — 双路检索 + 智能拆分")
    print("=" * 60)

    # 初始化
    encoder = DimensionEncoder()
    store = MemoryStore(":memory:")
    topic_reg = TopicRegistry()
    index_dir = os.path.join(os.path.dirname(__file__), "daily_index")
    chroma_dir = os.path.join(os.path.dirname(__file__), "chroma_db")

    try:
        from embedding_store import EmbeddingStore
        emb_store = EmbeddingStore(persist_dir=chroma_dir)
        print("  ✅ Chroma 向量库已加载")
    except Exception as e:
        emb_store = None
        print(f"  ⚠️ Chroma 不可用: {e}")

    pipeline = IngestPipeline(store, encoder, index_dir=index_dir, embedding_store=emb_store, topic_registry=topic_reg)
    pipeline.set_llm(mock_llm)  # 启用多主题拆分
    recall = RecallEngine(store, encoder, embedding_store=emb_store)
    archiver = Archiver(pipeline, store, encoder)

    # ── 1. 普通写入 ──────────────────────────────────────

    print("\n📝 第一段：普通写入（关键词检测）\n")
    base_ts = time.time()

    basic_messages = [
        ("我想研究一下 RAG 架构，用什么向量库比较好？", "main", "explore", ["ai.rag", "ai.rag.vdb"], ["chroma"], None, "medium"),
        ("Chroma 比较轻量，适合快速原型", "main", "note", ["ai.rag.vdb"], ["chroma"], ["pref"], "medium"),
        ("踩坑记录：Chroma 不能持久化到网络盘，会锁死", "main", "note", ["ai.rag.vdb"], ["chroma"], ["lesson"], "high"),
        ("BGE 和 Jina 都不错，中文场景 BGE 更好", "main", "note", ["ai.rag.emb"], [], ["pref", "fact"], "high"),
        ("混合检索：BM25 + 向量搜索结合，再加个 Reranker", "main", "note", ["ai.rag.ret"], [], ["skill"], "medium"),
    ]

    for i, (content, person, nature, topics, tools, know, imp) in enumerate(basic_messages):
        ts = base_ts + i * 60
        result = archiver.track(
            content=content, person_code=person, ts=ts,
            topics=topics, nature_code=nature, tool_codes=tools,
            knowledge_codes=know, importance=imp,
        )
        wr = result["written"]
        print(f"  [{wr['time_id']}] {wr['nature_id']} | {', '.join(wr['topics'])}")

    # ── 2. LLM 多主题拆分写入 ─────────────────────────────

    print("\n📝 第二段：LLM 多主题拆分\n")

    # "RAG 用 Chroma 挺好的，另外明天下午3点开项目评审会"
    # → 应该拆成两条：ai.rag.vdb(note) + dev(todo)
    mixed_content = "RAG 用 Chroma 挺好的，另外明天下午3点开项目评审会"
    fragments = pipeline.split_and_ingest(
        content=mixed_content,
        person_code="main",
        ts=base_ts + 100,
        importance="medium",
    )
    print(f"  原文: {mixed_content}")
    print(f"  拆分为 {len(fragments)} 个片段:")
    for f in fragments:
        print(f"    → [{f['memory_id']}] 主题={f['topics']} 性质={f['nature_id']}")

    # "Agent 的记忆系统可以用多维坐标，部署用 Docker 比较好"
    # → 应该拆成两条：ai.agent.mem(explore) + dev.ops(note)
    mixed_content2 = "Agent 的记忆系统可以用多维坐标，部署用 Docker 比较好"
    fragments2 = pipeline.split_and_ingest(
        content=mixed_content2,
        person_code="main",
        ts=base_ts + 200,
        importance="high",
    )
    print(f"\n  原文: {mixed_content2}")
    print(f"  拆分为 {len(fragments2)} 个片段:")
    for f in fragments2:
        print(f"    → [{f['memory_id']}] 主题={f['topics']} 性质={f['nature_id']}")

    # ── 3. 双路检索演示 ──────────────────────────────────

    print("\n" + "=" * 60)
    print("  🔍 双路检索演示")
    print("=" * 60)

    # 场景1：结构化精确检索
    print("\n▸ 结构化检索：向量库相关笔记")
    r1 = recall.recall(topic_path="ai.rag.vdb", nature_code="note")
    print(f"  模式: {r1['search_mode']}  找到 {r1['total']} 条")
    for m in r1["primary"][:3]:
        print(f"  - [{m['time_id']}] {m['content'][:50]}")

    # 场景2：语义搜索（如果有 Chroma）
    if emb_store:
        print("\n▸ 语义搜索：\"怎么选择合适的向量数据库\"")
        r2 = recall.recall(
            query="怎么选择合适的向量数据库",
            semantic_weight=0.7,
        )
        print(f"  模式: {r2['search_mode']}  找到 {r2['total']} 条")
        for m in r2["primary"][:3]:
            sem = m.get("_semantic_score", 0)
            print(f"  - [{m['time_id']}] ~{sem:.2f} {m['content'][:50]}")

        # 场景3：混合检索（结构化过滤 + 语义排序）
        print("\n▸ 混合检索：高重要度 + 语义\"数据持久化问题\"")
        r3 = recall.recall(
            query="数据持久化问题",
            importance="high",
            semantic_weight=0.5,
        )
        print(f"  模式: {r3['search_mode']}  找到 {r3['total']} 条")
        for m in r3["primary"][:3]:
            imp = m.get("importance", "medium")
            sem = m.get("_semantic_score", 0)
            print(f"  - ⚡{imp} ~{sem:.2f} [{m['time_id']}] {m['content'][:50]}")
    else:
        print("\n  ⚠️ Chroma 不可用，跳过语义搜索演示")

    # ── 4. 格式化上下文 ──────────────────────────────────

    print("\n" + "=" * 60)
    print("  📋 格式化上下文")
    print("=" * 60)
    r = recall.recall(topic_path="ai.rag")
    print(recall.format_context(r))

    # ── 5. 归档历史 ──────────────────────────────────────

    print("\n" + "=" * 60)
    print("  📦 归档历史")
    print("=" * 60)
    for arch in archiver.get_archive_log():
        print(f"  [{arch['reason']}] {arch['message_count']} 条  时长 {arch['duration_s']}s  主题={arch['last_topic']}")

    # ── 6. 动态主题注册演示 ──────────────────────────────

    print("\n" + "=" * 60)
    print("  🆕 动态主题注册演示")
    print("=" * 60)

    # 测试1：已有主题匹配（should match ai.rag.vdb）
    print("\n▸ 测试1：已有主题匹配")
    r1 = topic_reg.auto_register("我想研究向量数据库选型")
    print(f"  输入: '我想研究向量数据库选型'")
    print(f"  结果: path={r1['path']}  matched={r1['matched']}  sim={r1['similarity']:.2f}  is_new={r1['is_new']}")

    # 测试2：全新领域（should create new topic）
    print("\n▸ 测试2：全新领域 → 自动注册")
    r2 = topic_reg.auto_register("我想学习 SwiftUI 做 iOS 开发")
    print(f"  输入: '我想学习 SwiftUI 做 iOS 开发'")
    print(f"  结果: path={r2['path']}  matched={r2['matched']}  sim={r2['similarity']:.2f}  is_new={r2['is_new']}")

    # 测试3：手动指定路径注册
    print("\n▸ 测试3：手动注册指定路径")
    r3 = topic_reg.register_topic(
        topic_path="dev.fe.swift",
        name="Swift",
        keywords=["swift", "swiftui", "ios", "xcode"],
    )
    print(f"  注册: dev.fe.swift → {r3}")

    # 测试4：注册后的匹配
    print("\n▸ 测试4：注册后重新匹配")
    r4 = topic_reg.auto_register("SwiftUI 的状态管理怎么搞")
    print(f"  输入: 'SwiftUI 的状态管理怎么搞'")
    print(f"  结果: path={r4['path']}  matched={r4['matched']}  sim={r4['similarity']:.2f}  is_new={r4['is_new']}")

    # 统计
    print(f"\n📊 主题统计: {topic_reg.get_stats()}")

    # ── 7. 待办状态流演示 ────────────────────────────────

    print("\n" + "=" * 60)
    print("  ✅ 待办状态流演示")
    print("=" * 60)

    # 通过 todo 性质写入，自动创建任务
    print("\n▸ 自动提取待办任务")
    base_ts2 = time.time()
    todo_msgs = [
        ("明天下午3点开项目评审会", "medium"),
        ("完成 Agent 记忆系统的 Chroma 集成", "high"),
        ("写一篇 RAG 入门教程", "low"),
        ("配置自动备份脚本到 NAS", "medium"),
    ]
    task_ids = []
    for content, imp in todo_msgs:
        r = pipeline.ingest(content, person_code="main", ts=base_ts2, nature_code="todo", importance=imp)
        if r.get("task_id"):
            task_ids.append(r["task_id"])
            print(f"  ✅ 创建任务: {content[:40]}... → {r['task_id']}")

    # 状态流转
    print("\n▸ 状态流转")
    if len(task_ids) >= 3:
        store.update_task_status(task_ids[0], "in_progress")
        print(f"  {task_ids[0]}: pending → in_progress")
        store.update_task_status(task_ids[0], "done")
        print(f"  {task_ids[0]}: in_progress → done")
        store.update_task_status(task_ids[1], "in_progress")
        print(f"  {task_ids[1]}: pending → in_progress")

    # 查询
    print("\n▸ 当前任务列表")
    tasks = store.get_tasks()
    for t in tasks:
        status_icon = {"pending": "⚪", "in_progress": "🟡", "done": "🟢", "overdue": "🔴"}.get(t["status"], "❓")
        print(f"  {status_icon} [{t['status']:12s}] {t['title'][:50]}")

    # 统计
    print(f"\n📊 任务统计: {store.get_task_stats()}")

    # ── 8. 录音卡导出演示 ────────────────────────────────

    print("\n" + "=" * 60)
    print("  📋 录音卡导出演示")
    print("=" * 60)

    exporter = RecordingCardExporter(store=store, encoder=encoder)

    # 从检索结果生成录音卡
    search_result = recall.recall(topic_path="ai.rag")
    card_md = exporter.from_recall_result(
        search_result,
        title="RAG 技术讨论录音卡",
        session_id="session_20260411",
    )
    print("\n" + card_md)

    # 保存到文件
    card_path = os.path.join(os.path.dirname(__file__), "demo_recording_card.md")
    exporter.save(card_md, card_path)
    print(f"\n💾 已保存到: {card_path}")

    # ── 9. 记忆衰减分析 ──────────────────────────────────

    print("\n" + "=" * 60)
    print("  📊 记忆衰减分析")
    print("=" * 60)

    decay = MemoryDecay(store=store, encoder=encoder)

    # 分析所有记忆
    analysis = decay.analyze_all()
    print(f"\n▸ 衰减状态: {analysis['summary']}")
    print(f"  总数: {analysis['total']}")
    print(f"  按重要度: {analysis['by_importance']}")

    if analysis["needs_action"]:
        print("\n▸ 需要处理:")
        for item in analysis["needs_action"][:5]:
            print(f"  [{item['status']:8s}] {item['importance']} | {item['age_days']}天 | {item['next_action']}")

    # 单条衰减计算示例
    sample = {"memory_id": "test", "importance": "low", "time_ts": time.time() - 86400 * 35}
    d = decay.compute_decay_score(sample)
    print(f"\n▸ 衰减示例: low + 35天 → score={d['decay_score']} status={d['status']} next={d['next_action']}")

    sample2 = {"memory_id": "test2", "importance": "high", "time_ts": time.time() - 86400 * 365}
    d2 = decay.compute_decay_score(sample2)
    print(f"▸ 衰减示例: high + 365天 → score={d2['decay_score']} status={d2['status']} next={d2['next_action']}")

    # 生成报告
    report_path = os.path.join(os.path.dirname(__file__), "decay_report.md")
    decay.generate_report(report_path)
    print(f"\n💾 衰减报告已保存到: {report_path}")

    # ── 10. Obsidian 双向同步 ────────────────────────────

    print("\n" + "=" * 60)
    print("  📂 Obsidian 同步")
    print("=" * 60)

    vault_path = os.path.join(os.path.dirname(__file__), "obsidian_vault")
    sync = ObsidianSync(store=store, encoder=encoder, vault_path=vault_path)

    # 全量同步
    result = sync.sync_all(limit=50)
    print(f"\n▸ 同步完成:")
    print(f"  记忆导出: {result['memories']} 条")
    print(f"  任务导出: {result['tasks']} 条")
    print(f"  主题索引: {'✅' if result['theme_index'] else '❌'}")
    print(f"  Vault 路径: {result['vault_path']}")

    # 展示 Vault 目录结构
    print("\n▸ Vault 目录:")
    for root, dirs, files in os.walk(vault_path):
        level = root.replace(vault_path, '').count(os.sep)
        indent = '  ' * level
        dirname = os.path.basename(root) or os.path.basename(vault_path)
        print(f"  {indent}📁 {dirname}/")
        subindent = '  ' * (level + 1)
        for f in files[:5]:
            print(f"  {subindent}📄 {f}")
        if len(files) > 5:
            print(f"  {subindent}  ... +{len(files)-5} more")

    # 读回验证
    if result['memories'] > 0:
        # 找第一个 md 文件读回来
        for root, dirs, files in os.walk(vault_path):
            for f in files:
                if f.endswith('.md') and f.startswith('T'):
                    fp = os.path.join(root, f)
                    parsed = sync.read_obsidian_file(fp)
                    if parsed:
                        print(f"\n▸ 读回验证: {f}")
                        print(f"  Frontmatter keys: {list(parsed['frontmatter'].keys())}")
                        print(f"  Content: {parsed['content'][:60]}...")
                    break
            else:
                continue
            break

    # ── 11. 语义级主题发现 ───────────────────────────────

    print("\n" + "=" * 60)
    print("  🧠 语义级主题发现")
    print("=" * 60)

    try:
        from semantic_topic import SemanticTopicMatcher

        # 创建语义匹配器（复用已有的 embedding 模型）
        sem_matcher = SemanticTopicMatcher(
            embedding_store=emb_store,
            registry_path=os.path.join(os.path.dirname(__file__), "registry", "dimensions.json"),
        )
        print(f"\n  语义匹配器已加载: {sem_matcher.get_stats()}")

        # 用语义匹配器创建新的 pipeline
        sem_pipeline = IngestPipeline(
            store, encoder,
            index_dir=index_dir,
            embedding_store=emb_store,
            topic_registry=topic_reg,
            semantic_matcher=sem_matcher,
        )

        # 测试用例：没有直接关键词，但语义上属于已知主题
        test_cases = [
            "我想给我的对话机器人加上长期记忆的能力",  # → ai.agent.mem
            "用什么方法能快速搭建一个知识问答系统",       # → ai.rag
            "前端页面加载太慢了，怎么优化",              # → dev.fe
            "容器编排用哪个方案比较好",                  # → dev.ops
        ]

        print("\n▸ 语义匹配测试（无直接关键词）:")
        for text in test_cases:
            hits = sem_matcher.match(text, top_k=1)
            if hits:
                h = hits[0]
                print(f"  「{text}」")
                print(f"    → {h['topic']} (score={h['score']:.3f})")
            else:
                print(f"  「{text}」")
                print(f"    → 无匹配")

        # 通过 pipeline 写入，验证语义匹配生效
        print("\n▸ 语义匹配 + 自动写入:")
        sem_base = time.time()
        for i, text in enumerate(test_cases):
            r = sem_pipeline.ingest(text, person_code="main", ts=sem_base + i)
            print(f"  [{r['time_id']}] → {r['topics']}  (nature={r['nature_id']})")

    except Exception as e:
        print(f"\n  ⚠️ 语义主题匹配不可用: {e}")

    # ── 12. LLM 记忆压缩摘要 ────────────────────────────

    print("\n" + "=" * 60)
    print("  📦 LLM 记忆压缩摘要")
    print("=" * 60)

    try:
        from compressor import MemoryCompressor

        def mock_compress_llm(prompt: str) -> str:
            """模拟 LLM 压缩响应"""
            if "ai" in prompt.lower():
                return """## 摘要
讨论了 RAG 架构选型，确定使用 Chroma 作为向量库，BGE 作为中文 embedding 模型，
采用 BM25 + 向量混合检索方案。发现 Chroma 不能持久化到网络盘的坑。

## 关键决策
- 选用 Chroma 作为原型阶段向量库
- 中文场景用 BGE embedding
- 采用 BM25 + 向量混合检索

## 事实记录
- Chroma 不支持网络盘持久化
- BGE 中文效果优于 Jina

## 待办事项
- 完成 Chroma 集成
- 写 RAG 入门教程"""

            return """## 摘要
讨论了 Agent 记忆系统的多维坐标架构，包括 6 个维度的编码设计。
规划了容器化部署方案。

## 关键决策
- 采用 6 维度坐标编码
- 使用 Docker 容器化部署

## 事实记录
- 时间/人物/主题/性质/工具/知识类型 6 个维度

## 待办事项
- 完成部署配置"""

        compressor = MemoryCompressor(
            store=store,
            encoder=encoder,
            llm_fn=mock_compress_llm,
        )

        # 先写入一些"老"记忆（模拟已衰减的）
        print("\n▸ 写入模拟老记忆（回溯到 200 天前）...")
        old_ts = time.time() - 86400 * 200  # 200 天前
        old_messages = [
            ("讨论了 RAG 的向量库选型，Chroma 比较适合", "ai.rag.vdb", "medium"),
            ("BGE 中文 embedding 效果比 Jina 好", "ai.rag.emb", "medium"),
            ("混合检索 BM25 + 向量效果最好", "ai.rag.ret", "medium"),
            ("Agent 记忆系统的维度设计方案定了", "ai.agent.mem", "medium"),
            ("用 Docker 容器化部署比较方便", "dev.ops", "medium"),
        ]
        for i, (content, topic, imp) in enumerate(old_messages):
            pipeline.ingest(
                content, person_code="main",
                ts=old_ts + i,
                topics=[topic],
                importance=imp,
                nature_code="note",
            )
            print(f"  写入: {content[:40]}... ({topic})")

        # 分析压缩候选
        print("\n▸ 压缩分析（dry_run=True）:")
        dry_result = compressor.compress(dry_run=True)
        print(f"  候选记忆: {dry_result['total_candidates']} 条")
        for g in dry_result.get("groups", []):
            print(f"  📁 {g['topic']}: {g['count']} 条 ({g['time_range']})")

        # 执行压缩
        print("\n▸ 执行压缩:")
        compress_result = compressor.compress()
        for c in compress_result.get("compressed", []):
            print(f"  📦 {c['topic']}: {c['source_count']} 条 → 1 条摘要 (id={c['summary_id'][:30]}...)")

        # 查看压缩后的聚合记忆
        print("\n▸ 压缩后的聚合记忆:")
        compressed_mems = store.query(limit=10)
        for mem in compressed_mems:
            if mem.get("is_aggregated"):
                print(f"  📦 [{mem['memory_id'][:40]}] source_count={mem['source_count']}")
                print(f"     {mem['content'][:100]}...")

        # 统计
        print(f"\n📊 压缩统计: {compressor.get_compression_stats()}")

    except Exception as e:
        print(f"\n  ⚠️ 记忆压缩不可用: {e}")
        import traceback
        traceback.print_exc()

    # ── 最终清理 ──────────────────────────────────────────

    # ── 13. 统一 API 演示 ────────────────────────────────

    print("\n" + "=" * 60)
    print("  🎯 统一 API 演示 (AgentMemory)")
    print("=" * 60)

    try:
        from memory_system import AgentMemory

        mem = AgentMemory(
            db_path=":memory:",
            project_dir=os.path.dirname(__file__),
            llm_fn=mock_compress_llm,
        )

        # remember — 自动过滤 + 去重 + 写入
        print("\n▸ remember() 自动过滤:")
        test_msgs = [
            ("你好", False),                    # 寒暄 → 过滤
            ("ok", False),                      # 确认 → 过滤
            ("我决定用 Chroma 做向量库，因为轻量好上手", True),  # 决策 → 写入
            ("我决定用 Chroma 做向量库，因为轻量好上手", False),  # 重复 → 去重
            ("明天要完成 BGE 模型的集成测试", True),              # 任务 → 写入
            ("随便看看", False),                 # 低信号 → 过滤
        ]
        for msg, expect_write in test_msgs:
            r = mem.remember(msg)
            status = "✅" if r["written"] == expect_write else "❌"
            print(f"  {status} 「{msg[:25]}...」→ written={r['written']} reason={r['reason']}")

        # recall — 混合检索
        print("\n▸ recall() 检索:")
        r = mem.recall("用户选了什么向量库")
        print(f"  找到 {r['total']} 条")
        for m in r.get("primary", [])[:3]:
            print(f"  - {m.get('content', '')[:50]}")

        # build_context — 组装上下文
        print("\n▸ build_context() 上下文组装:")
        ctx = mem.build_context(query="向量库选型", max_tokens=500)
        print(f"  ({len(ctx)} 字)")
        print("  " + "\n  ".join(ctx.split("\n")[:8]))

    except Exception as e:
        print(f"\n  ⚠️ AgentMemory 不可用: {e}")
        import traceback
        traceback.print_exc()

    # ── 14. 记忆过滤器 ──────────────────────────────────

    print("\n" + "=" * 60)
    print("  🛡️ 记忆过滤器")
    print("=" * 60)

    from memory_filter import MemoryFilter
    mf = MemoryFilter()

    filter_tests = [
        "hi",
        "ok",
        "我决定用 Chroma，踩坑了网络盘锁死的问题",
        "明天打算写一篇 RAG 教程",
        "随便看看有什么新进展",
        "这个问题困扰了我很久，最后发现是 embedding 维度不匹配",
    ]
    print()
    for text in filter_tests:
        r = mf.should_remember(text)
        icon = "✅" if r["remember"] else "❌"
        print(f"  {icon} [{r['suggested_importance']:6s}] {r['confidence']:.0%} | 「{text[:30]}」→ {r['reason']}")

    # ── 15. 语义去重 ────────────────────────────────────

    print("\n" + "=" * 60)
    print("  🔍 语义去重")
    print("=" * 60)

    from dedup import MemoryDeduplicator
    dd = MemoryDeduplicator(store)

    # 写入测试数据
    dedup_base = time.time()
    store.insert_memory(
        memory_id="dedup_test_1", time_id="T_dedup1", time_ts=int(dedup_base),
        person_id="P01", nature_id="D05", content="Chroma 适合快速原型开发",
        content_hash="aaa", importance="medium",
    )
    store.insert_memory(
        memory_id="dedup_test_2", time_id="T_dedup2", time_ts=int(dedup_base) + 1,
        person_id="P01", nature_id="D05", content="Chroma 很适合做快速原型",
        content_hash="bbb", importance="medium",
    )

    print("\n▸ 检测重复:")
    r = dd.check_duplicate("Chroma 适合做快速原型开发", time_window_hours=1)
    print(f"  is_duplicate={r['is_duplicate']}  method={r['method']}  sim={r['similarity']:.2f}  action={r['action']}")

    # ── 16. 因果链 ──────────────────────────────────────

    print("\n" + "=" * 60)
    print("  🔗 因果链")
    print("=" * 60)

    from causal import CausalChain
    cc = CausalChain(store)

    # 手动建立因果
    print("\n▸ 建立因果关系:")
    cc.add_causal_link("dedup_test_1", "dedup_test_2", "supports", "同主题互相印证")
    print("  dedup_test_1 🤝 dedup_test_2")

    # 自动检测
    print("\n▸ 自动检测因果:")
    detected = cc.auto_detect_causality(window_hours=24)
    print(f"  检测到 {len(detected)} 条因果关系")
    for d in detected[:3]:
        print(f"  {d['source'][:20]} → {d['target'][:20]} ({d['link_type']})")

    print(f"\n📊 因果统计: {cc.get_stats()}")

    # ── 17. 记忆质量 ────────────────────────────────────

    print("\n" + "=" * 60)
    print("  📊 记忆质量评分")
    print("=" * 60)

    from quality import MemoryQuality
    mq = MemoryQuality(store)

    # 模拟检索事件
    test_mem = store.get_memory("dedup_test_1")
    if test_mem:
        for _ in range(5):
            mq.record_retrieval("dedup_test_1")
        mq.record_feedback("dedup_test_1", useful=True, note="确实帮到了")

        q = mq.compute_quality(test_mem)
        print(f"\n▸ 质量评分: dedup_test_1")
        print(f"  分数: {q['quality_score']:.2f}  等级: {q['grade']}")
        print(f"  建议: {q['recommendation']}")
        print(f"  细分: {q['breakdown']}")

    print(f"\n📊 质量统计: {mq.get_stats()}")

    # ── 18. 智能压缩 ────────────────────────────────────

    print("\n" + "=" * 60)
    print("  📦 智能压缩 (核心/边缘)")
    print("=" * 60)

    try:
        from compressor import MemoryCompressor
        comp = MemoryCompressor(store, encoder, llm_fn=mock_compress_llm)

        print(f"\n📊 压缩统计: {comp.get_compression_stats()}")

        # smart_compress 演示
        smart_result = comp.smart_compress(embedding_store=emb_store)
        if isinstance(smart_result, dict) and "error" not in smart_result:
            print(f"\n▸ 智能压缩结果:")
            print(f"  核心记忆: {len(smart_result.get('core_memories', []))} 条（保留）")
            print(f"  边缘记忆: {len(smart_result.get('edge_memories', []))} 条（已压缩）")
            print(f"  节省 token: ~{smart_result.get('saved_tokens', 0)}")
        else:
            print(f"\n  {smart_result}")
    except Exception as e:
        print(f"\n  ⚠️ 智能压缩: {e}")

    # ── 19. 层级记忆 ────────────────────────────────────

    print("\n" + "=" * 60)
    print("  🏗️ 层级记忆管理")
    print("=" * 60)

    from hierarchical import HierarchicalMemory
    hm = HierarchicalMemory(store, mq)

    # L1 短期记忆
    print("\n▸ L1 短期记忆 buffer:")
    hm.l1_add("用户问了 RAG 的向量库选型", "user")
    hm.l1_add("我推荐了 Chroma，轻量好用", "assistant")
    hm.l1_add("用户说要考虑 Milvus 的生产方案", "user")
    print(f"  Buffer: {len(hm._l1_buffer)} 条")
    print(f"  上下文:\n    {hm.l1_context(max_tokens=200).replace(chr(10), chr(10) + '    ')}")

    # L1 → L2 沉淀
    print("\n▸ L1→L2 沉淀:")
    flushed = hm.l1_flush_to_l2(pipeline)
    print(f"  沉淀了 {len(flushed)} 条到 L2")

    # L2 → L3 升级
    print("\n▸ L2→L3 升级检测:")
    promoted = hm.l2_promote_to_l3()
    print(f"  升级了 {promoted['count']} 条")
    for p in promoted["promoted"][:3]:
        print(f"  ⬆️ {p['memory_id'][:30]}... ({p['reason']})")

    print(f"\n📊 层级统计: {hm.get_stats()}")

    # ── 20. 自我修复 ────────────────────────────────────

    print("\n" + "=" * 60)
    print("  🔧 自我修复")
    print("=" * 60)

    from self_healing import SelfHealing
    sh = SelfHealing(store)

    # 写入测试矛盾数据
    heal_base = time.time()
    store.insert_memory(
        memory_id="heal_test_a", time_id="T_heal_a", time_ts=int(heal_base),
        person_id="P01", nature_id="D05", content="Chroma 比 Milvus 更好，轻量级",
        content_hash="heal_a", importance="medium",
        topics=["ai.rag.vdb"],
    )
    store.insert_memory(
        memory_id="heal_test_b", time_id="T_heal_b", time_ts=int(heal_base) + 1,
        person_id="P01", nature_id="D05", content="Milvus 比 Chroma 更好，功能更全",
        content_hash="heal_b", importance="medium",
        topics=["ai.rag.vdb"],
    )

    # 矛盾检测
    print("\n▸ 矛盾检测:")
    contradictions = sh.detect_contradictions()
    print(f"  检测到 {len(contradictions)} 组矛盾")
    for c in contradictions[:3]:
        print(f"  ⚡ {c['content_a'][:30]} vs {c['content_b'][:30]} (score={c['contradiction_score']})")

    # 过时检测
    print("\n▸ 过时检测:")
    outdated = sh.detect_outdated()
    print(f"  检测到 {len(outdated)} 条过时记忆")

    # 完整扫描
    print("\n▸ 完整自我修复扫描:")
    scan = sh.full_scan()
    print(f"  矛盾: {len(scan['contradictions'])} 组")
    print(f"  过时: {len(scan['outdated'])} 条")
    print(f"  重要度修复: {scan['importance_healed']} 条")
    print(f"  总问题: {scan['total_issues']}")

    # ── 21. 记忆图谱 ────────────────────────────────────

    print("\n" + "=" * 60)
    print("  🗺️ 记忆图谱")
    print("=" * 60)

    from memory_graph import MemoryGraph
    mg = MemoryGraph(store)

    # ASCII 图谱
    print("\n▸ ASCII 图谱 (全局):")
    ascii_graph = mg.generate(format="ascii", max_nodes=20)
    print(f"```\n{ascii_graph}\n```")

    # Mermaid 图谱
    print("\n▸ Mermaid 图谱 (ai 主题):")
    mermaid = mg.generate(center_topic="ai", format="mermaid", max_nodes=15)
    print(f"```mermaid\n{mermaid}\n```")

    # ── 22. 完整系统统计 ────────────────────────────────

    print("\n" + "=" * 60)
    print("  📊 完整系统统计")
    print("=" * 60)

    try:
        full_stats = mem.get_stats()
        print(f"\n  总记忆: {full_stats['total_memories']}")
        print(f"  层级: L1={full_stats['hierarchy']['L1_short_term']['count']} "
              f"L2={full_stats['hierarchy']['L2_mid_term']['count']} "
              f"L3={full_stats['hierarchy']['L3_long_term']['count']}")
        print(f"  质量: 反馈={full_stats['quality']['total_feedback']} "
              f"有用率={full_stats['quality']['useful_ratio']:.0%}")
        print(f"  因果: {full_stats['causal']['total_causal_links']} 条")
        print(f"  自修复: 矛盾={full_stats['self_healing']['contradiction_links']} "
              f"过时={full_stats['self_healing']['outdated_links']}")
    except Exception as e:
        print(f"\n  ⚠️ 统计: {e}")

    # ── 最终清理 ──────────────────────────────────────────

    import shutil
    for d in [index_dir, chroma_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)
    # 清理 quality stats
    qs = os.path.join(os.path.dirname(__file__), "quality_stats.json")
    if os.path.exists(qs):
        os.remove(qs)
    # 清理 vector cache
    vc = os.path.join(os.path.dirname(__file__), "registry", "topic_vectors_cache.json")
    if os.path.exists(vc):
        os.remove(vc)

    print("\n" + "=" * 60)
    print("  ✅ 全部演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
