"""
benchmark.py - Agent Memory System 性能基准测试
测量核心操作的延迟和吞吐量
"""

import os
import sys
import time
import json
import tempfile
import statistics

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

# ── 工具函数 ────────────────────────────────────────────

def timer(fn, *args, **kwargs):
    """计时执行，返回 (结果, 耗时ms)"""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = (time.perf_counter() - start) * 1000
    return result, elapsed

def bench(fn, iterations, label, *args, **kwargs):
    """多次执行取统计值"""
    times = []
    result = None
    for _ in range(iterations):
        result, elapsed = timer(fn, *args, **kwargs)
        times.append(elapsed)

    return {
        "label": label,
        "iterations": iterations,
        "avg_ms": round(statistics.mean(times), 2),
        "median_ms": round(statistics.median(times), 2),
        "p95_ms": round(sorted(times)[int(iterations * 0.95)] if iterations > 1 else times[0], 2),
        "p99_ms": round(sorted(times)[int(iterations * 0.99)] if iterations > 1 else times[0], 2),
        "min_ms": round(min(times), 2),
        "max_ms": round(max(times), 2),
        "ops_per_sec": round(1000 / statistics.mean(times), 1) if statistics.mean(times) > 0 else 0,
    }

def print_result(r):
    print(f"  {r['label']:40s} | avg={r['avg_ms']:8.2f}ms | p95={r['p95_ms']:8.2f}ms | {r['ops_per_sec']:8.1f} ops/s")

def bar_chart(items, title, key="avg_ms", max_width=40):
    """ASCII 柱状图"""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")
    max_val = max(i[key] for i in items) if items else 1
    for item in items:
        val = item[key]
        bar_len = int((val / max_val) * max_width) if max_val > 0 else 0
        bar = "█" * bar_len
        label = item["label"][:35]
        print(f"  {label:35s} {bar} {val:.1f}ms")


# ── 基准测试 ────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  ⚡ Agent Memory System 性能基准测试")
    print("=" * 60)

    # 初始化
    from encoder import DimensionEncoder
    from store import MemoryStore
    from pipeline import IngestPipeline
    from recall import RecallEngine
    from memory_filter import MemoryFilter
    from dedup import MemoryDeduplicator
    from context_builder import ContextBuilder
    from hierarchical import HierarchicalMemory

    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    encoder = DimensionEncoder()
    store = MemoryStore(db_path)
    pipeline = IngestPipeline(store, encoder)
    recall = RecallEngine(store, encoder)
    mem_filter = MemoryFilter()
    dedup = MemoryDeduplicator(store)
    ctx_builder = ContextBuilder(recall)
    hierarchy = HierarchicalMemory(store)

    results = []

    # ── 1. 编码器 ──────────────────────────────────────

    print("\n📝 1. 编码器性能")
    print("─" * 60)

    r = bench(encoder.encode_time, 1000, "encode_time()")
    results.append(r); print_result(r)

    r = bench(encoder.encode_nature, 1000, "encode_nature('note')", "note")
    results.append(r); print_result(r)

    r = bench(encoder.generate_memory_id, 500, "generate_memory_id()",
              "T20260412.120000", "P01", ["ai.rag.vdb"], "D05")
    results.append(r); print_result(r)

    # ── 2. 写入性能 ────────────────────────────────────

    print("\n📝 2. 写入性能 (单条)")
    print("─" * 60)

    def write_single(i):
        pipeline.ingest(
            content=f"基准测试消息 {i}: RAG 架构用 Chroma 向量库比较好",
            person_code="main",
            importance="medium",
        )

    # 预热
    write_single(0)

    times = []
    for i in range(1, 201):
        _, elapsed = timer(write_single, i)
        times.append(elapsed)

    write_result = {
        "label": "ingest() 单条写入",
        "iterations": 200,
        "avg_ms": round(statistics.mean(times), 2),
        "median_ms": round(statistics.median(times), 2),
        "p95_ms": round(sorted(times)[int(200 * 0.95)], 2),
        "p99_ms": round(sorted(times)[int(200 * 0.99)], 2),
        "min_ms": round(min(times), 2),
        "max_ms": round(max(times), 2),
        "ops_per_sec": round(1000 / statistics.mean(times), 1),
    }
    results.append(write_result); print_result(write_result)

    # ── 3. 批量写入 ────────────────────────────────────

    print("\n📝 3. 批量写入性能")
    print("─" * 60)

    for batch_size in [10, 50, 100]:
        def batch_write():
            for i in range(batch_size):
                pipeline.ingest(
                    content=f"批量测试 {batch_size} 第{i}条: 测试内容",
                    person_code="main",
                )
        r = bench(batch_write, 1, f"批量写入 {batch_size} 条")
        # 换算成单条
        r["label"] = f"批量写入 {batch_size} 条 ({r['avg_ms']/batch_size:.2f}ms/条)"
        r["ops_per_sec"] = round(batch_size * 1000 / r["avg_ms"], 1)
        results.append(r); print_result(r)

    # ── 4. 查询性能 ────────────────────────────────────

    print("\n📝 4. 查询性能")
    print("─" * 60)

    r = bench(store.query, 500, "query() 全表 (limit=50)")
    results.append(r); print_result(r)

    r = bench(store.query, 500, "query() 按 importance", importance="medium")
    results.append(r); print_result(r)

    r = bench(store.query, 500, "query() 按 topic", topic_code="ai.rag")
    results.append(r); print_result(r)

    r = bench(store.query, 200, "query() 关键词搜索", keyword="Chroma")
    results.append(r); print_result(r)

    # 获取一个实际的 memory_id 用于测试
    existing_ids = [m["memory_id"] for m in store.query(limit=5)]
    test_mid = existing_ids[0] if existing_ids else "test_001"

    r = bench(store.get_memory, 500, "get_memory() 单条", test_mid)
    results.append(r); print_result(r)

    # ── 5. 缓存效果 ────────────────────────────────────

    print("\n📝 5. 缓存命中效果")
    print("─" * 60)

    # 冷查询
    store._invalidate_cache()
    _, cold = timer(store.query, limit=50)
    # 热查询
    _, hot = timer(store.query, limit=50)
    cache_speedup = cold / hot if hot > 0 else 0
    print(f"  冷查询: {cold:.2f}ms → 热查询: {hot:.2f}ms → 加速 {cache_speedup:.1f}x")

    stats = store.get_io_stats()
    print(f"  缓存命中率: {stats['cache_hit_rate']:.0%}")
    print(f"  FTS 可用: {'✅' if stats['has_fts'] else '❌'}")

    # ── 6. 检索性能 ────────────────────────────────────

    print("\n📝 6. 检索性能 (RecallEngine)")
    print("─" * 60)

    def recall_topic():
        recall.recall(topic_path="ai.rag")
    r = bench(recall_topic, 200, "recall() 结构化检索")
    results.append(r); print_result(r)

    def recall_keyword():
        recall.recall(keyword="Chroma")
    r = bench(recall_keyword, 200, "recall() 关键词检索")
    results.append(r); print_result(r)

    # ── 7. 过滤器性能 ──────────────────────────────────

    print("\n📝 7. MemoryFilter 性能")
    print("─" * 60)

    def filter_pass():
        mem_filter.should_remember("我决定用 Chroma 做向量库，踩坑了网络盘锁死的问题")
    r = bench(filter_pass, 1000, "should_remember() 通过")
    results.append(r); print_result(r)

    def filter_block():
        mem_filter.should_remember("ok")
    r = bench(filter_block, 1000, "should_remember() 拦截")
    results.append(r); print_result(r)

    # ── 8. 去重性能 ────────────────────────────────────

    print("\n📝 8. 去重性能")
    print("─" * 60)

    def dedup_bench():
        dedup.check_duplicate("Chroma 适合做快速原型开发")
    r = bench(dedup_bench, 100, "check_duplicate() (100条候选)")
    results.append(r); print_result(r)

    # ── 9. 上下文组装 ──────────────────────────────────

    print("\n📝 9. ContextBuilder 性能")
    print("─" * 60)

    def build_structured():
        ctx_builder.build(max_tokens=1000, style="structured")
    r = bench(build_structured, 200, "build() structured")
    results.append(r); print_result(r)

    def build_compact():
        ctx_builder.build(max_tokens=500, style="compact")
    r = bench(build_compact, 200, "build() compact")
    results.append(r); print_result(r)

    # ── 10. 层级记忆 ───────────────────────────────────

    print("\n📝 10. 层级记忆性能")
    print("─" * 60)

    def l1_add_bench():
        hierarchy.l1_add("测试消息", "user")
    r = bench(l1_add_bench, 1000, "l1_add()")
    results.append(r); print_result(r)

    # 填充一些数据给 l1_context
    for i in range(20):
        hierarchy.l1_add(f"上下文消息 {i}", "user" if i % 2 == 0 else "assistant")

    def l1_ctx_bench():
        hierarchy.l1_context()
    r = bench(l1_ctx_bench, 500, "l1_context()")
    results.append(r); print_result(r)

    # ── 汇总报告 ──────────────────────────────────────

    print("\n" + "=" * 60)
    print("  📊 汇总")
    print("=" * 60)

    # 按类别分组柱状图
    write_items = [r for r in results if "写入" in r["label"] or "ingest" in r["label"]]
    query_items = [r for r in results if "query" in r["label"].lower() or "recall" in r["label"].lower() or "get_memory" in r["label"]]
    other_items = [r for r in results if r not in write_items and r not in query_items]

    if write_items:
        bar_chart(write_items, "写入延迟 (avg ms)")
    if query_items:
        bar_chart(query_items, "查询延迟 (avg ms)")
    if other_items:
        bar_chart(other_items, "其他操作延迟 (avg ms)")

    # 关键指标
    print(f"\n{'─' * 60}")
    print(f"  🎯 关键指标")
    print(f"{'─' * 60}")

    write_ops = [r for r in results if "ops_per_sec" in r and "写入" in r["label"]]
    query_ops = [r for r in results if "ops_per_sec" in r and ("query" in r["label"].lower() or "get_memory" in r["label"])]

    if write_ops:
        max_write = max(r["ops_per_sec"] for r in write_ops)
        print(f"  写入吞吐:  {max_write:.0f} ops/s (单条)")
    if query_ops:
        max_query = max(r["ops_per_sec"] for r in query_ops)
        print(f"  查询吞吐:  {max_query:.0f} ops/s")

    total_memories = len(store.query(limit=10000))
    print(f"  测试数据量: {total_memories} 条记忆")
    print(f"  数据库大小: {os.path.getsize(db_path) / 1024:.1f} KB")

    # JSON 报告
    report_path = os.path.join(PROJECT_DIR, "benchmark_report.json")
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_memories": total_memories,
        "db_size_kb": round(os.path.getsize(db_path) / 1024, 1),
        "results": results,
    }
    with open(report_path, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\n💾 详细报告: {report_path}")

    # 清理
    store.close()
    os.close(db_fd)
    os.unlink(db_path)


if __name__ == "__main__":
    main()
