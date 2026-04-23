"""
test_all.py - Agent Memory System 完整测试套件
覆盖所有 24 个模块的核心功能
"""

import os
import sys
import json
import time
import sqlite3
import tempfile
import shutil
import unittest

# 项目目录
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)


class TestEncoder(unittest.TestCase):
    """维度编码器测试"""

    def setUp(self):
        from encoder import DimensionEncoder
        self.encoder = DimensionEncoder()

    def test_encode_time(self):
        ts = 1712834400  # 2024-04-11 12:00:00 UTC
        result = self.encoder.encode_time(ts)
        self.assertTrue(result.startswith("T"))
        self.assertIn(".", result)

    def test_encode_nature(self):
        for code, expected in [("explore", "D04"), ("note", "D05"), ("chat", "D11")]:
            result = self.encoder.encode_nature(code)
            self.assertEqual(result, expected)

    def test_encode_importance(self):
        self.assertEqual(self.encoder.encode_importance("high"), "high")
        self.assertEqual(self.encoder.encode_importance("low"), "low")

    def test_generate_memory_id(self):
        time_id = "T20260411.120000"
        person_id = "P01"
        topics = ["ai.rag.vdb"]
        nature_id = "D04"
        mid = self.encoder.generate_memory_id(time_id, person_id, topics, nature_id)
        self.assertIn("T20260411", mid)
        self.assertIn("P01", mid)


class TestStore(unittest.TestCase):
    """存储层测试"""

    def setUp(self):
        from store import MemoryStore
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.store = MemoryStore(self.db_path)

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_insert_and_get(self):
        self.store.insert_memory(
            memory_id="test_001", time_id="T1", time_ts=1000,
            person_id="P01", nature_id="D05", content="测试记忆",
            content_hash="abc123", importance="high",
        )
        mem = self.store.get_memory("test_001")
        self.assertIsNotNone(mem)
        self.assertEqual(mem["content"], "测试记忆")
        self.assertEqual(mem["importance"], "high")

    def test_insert_with_topics(self):
        self.store.insert_memory(
            memory_id="test_002", time_id="T2", time_ts=2000,
            person_id="P01", nature_id="D05", content="RAG 测试",
            content_hash="def456", topics=["ai.rag", "ai.rag.vdb"],
        )
        mem = self.store.get_memory("test_002")
        self.assertEqual(len(mem["topics"]), 2)

    def test_query_by_importance(self):
        self.store.insert_memory(
            memory_id="t1", time_id="T1", time_ts=1000,
            person_id="P01", nature_id="D05", content="high",
            content_hash="h1", importance="high",
        )
        self.store.insert_memory(
            memory_id="t2", time_id="T2", time_ts=2000,
            person_id="P01", nature_id="D05", content="low",
            content_hash="h2", importance="low",
        )
        high_results = self.store.query(importance="high")
        self.assertTrue(all(m["importance"] == "high" for m in high_results))

    def test_insert_link(self):
        self.store.insert_memory(
            memory_id="a", time_id="T1", time_ts=1000,
            person_id="P01", nature_id="D05", content="A",
            content_hash="ha",
        )
        self.store.insert_memory(
            memory_id="b", time_id="T2", time_ts=2000,
            person_id="P01", nature_id="D05", content="B",
            content_hash="hb",
        )
        self.store.insert_link("a", "b", "temporal", 0.8)
        linked = self.store.get_linked("a")
        self.assertTrue(any(m["memory_id"] == "b" for m in linked))

    def test_tasks(self):
        self.store.insert_memory(
            memory_id="tm", time_id="T1", time_ts=1000,
            person_id="P01", nature_id="D07", content="要做事",
            content_hash="thm",
        )
        task_id = self.store.add_task("tm", "测试任务")
        self.assertTrue(task_id.startswith("task_"))

        self.store.update_task_status(task_id, "in_progress")
        tasks = self.store.get_tasks(status="in_progress")
        self.assertTrue(any(t["task_id"] == task_id for t in tasks))

    def test_concurrent_writes(self):
        """并发写入测试"""
        import threading
        errors = []

        def write_memory(i):
            try:
                self.store.insert_memory(
                    memory_id=f"concurrent_{i}", time_id=f"T{i}", time_ts=1000 + i,
                    person_id="P01", nature_id="D05", content=f"并发测试 {i}",
                    content_hash=f"ch{i}",
                )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=write_memory, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"并发写入错误: {errors}")
        results = self.store.query(limit=20)
        concurrent_count = sum(1 for m in results if m["memory_id"].startswith("concurrent_"))
        self.assertEqual(concurrent_count, 10)

    def test_transaction_rollback(self):
        """事务回滚测试"""
        initial_count = len(self.store.query(limit=100))
        try:
            with self.store.transaction() as conn:
                conn.execute(
                    "INSERT INTO memories (memory_id, time_id, time_ts, person_id, nature_id, content, content_hash, importance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    ("tx_test", "T_tx", 9999, "P01", "D05", "事务测试", "txh", "medium"),
                )
                raise ValueError("模拟错误")
        except ValueError:
            pass

        # 事务应该回滚
        mem = self.store.get_memory("tx_test")
        self.assertIsNone(mem)

    def test_cache(self):
        """查询缓存测试"""
        self.store.insert_memory(
            memory_id="cache_test", time_id="Tc", time_ts=5000,
            person_id="P01", nature_id="D05", content="缓存测试",
            content_hash="cch",
        )
        # 第一次查询
        r1 = self.store.query(limit=10)
        # 第二次查询应该命中缓存
        r2 = self.store.query(limit=10)
        self.assertEqual(len(r1), len(r2))
        stats = self.store.get_io_stats()
        self.assertGreater(stats["cache_hits"], 0)


class TestMemoryFilter(unittest.TestCase):
    """记忆过滤器测试"""

    def setUp(self):
        from memory_filter import MemoryFilter
        self.filter = MemoryFilter()

    def test_skip_greeting(self):
        r = self.filter.should_remember("你好")
        self.assertFalse(r["remember"])

    def test_skip_ok(self):
        r = self.filter.should_remember("ok")
        self.assertFalse(r["remember"])

    def test_keep_decision(self):
        r = self.filter.should_remember("我决定用 Chroma 做向量库，踩坑了网络盘锁死")
        self.assertTrue(r["remember"])
        self.assertEqual(r["suggested_importance"], "high")

    def test_keep_task(self):
        r = self.filter.should_remember("明天打算写一篇 RAG 教程")
        self.assertTrue(r["remember"])
        self.assertEqual(r["suggested_nature"], "todo")

    def test_skip_short(self):
        r = self.filter.should_remember("ok")
        self.assertFalse(r["remember"])

    def test_keep_long_text(self):
        r = self.filter.should_remember("这个问题困扰了我很久，最后发现是 embedding 维度不匹配导致的向量搜索精度下降")
        self.assertTrue(r["remember"])


class TestDedup(unittest.TestCase):
    """去重测试"""

    def setUp(self):
        from store import MemoryStore
        from dedup import MemoryDeduplicator
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.store = MemoryStore(self.db_path)
        self.dedup = MemoryDeduplicator(self.store)

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_exact_duplicate(self):
        content = "完全相同的内容"
        import hashlib
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        self.store.insert_memory(
            memory_id="orig", time_id="T1", time_ts=int(time.time()),
            person_id="P01", nature_id="D05", content=content,
            content_hash=content_hash,
        )
        r = self.dedup.check_duplicate(content, time_window_hours=1)
        self.assertTrue(r["is_duplicate"])
        self.assertEqual(r["method"], "exact")

    def test_near_duplicate(self):
        self.store.insert_memory(
            memory_id="near", time_id="T1", time_ts=int(time.time()),
            person_id="P01", nature_id="D05", content="Chroma 适合快速原型开发",
            content_hash="near_hash",
        )
        r = self.dedup.check_duplicate("Chroma 适合做快速原型开发", time_window_hours=1)
        # 文本相似度应该较高
        self.assertGreater(r["similarity"], 0.3)

    def test_no_duplicate(self):
        r = self.dedup.check_duplicate("完全不相关的内容 xyz", time_window_hours=1)
        self.assertFalse(r["is_duplicate"])


class TestContextBuilder(unittest.TestCase):
    """上下文组装器测试"""

    def setUp(self):
        from store import MemoryStore
        from encoder import DimensionEncoder
        from recall import RecallEngine
        from context_builder import ContextBuilder
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.store = MemoryStore(self.db_path)
        self.encoder = DimensionEncoder()
        self.recall = RecallEngine(self.store, self.encoder)
        self.builder = ContextBuilder(self.recall)

        # 写入测试数据
        for i in range(5):
            self.store.insert_memory(
                memory_id=f"ctx_{i}", time_id=f"T{i}", time_ts=1000 + i,
                person_id="P01", nature_id="D05",
                content=f"测试记忆内容 {i}" * 10,
                content_hash=f"ctx_h{i}",
                importance="high" if i < 2 else "medium",
            )

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_build_structured(self):
        result = self.builder.build(max_tokens=500, style="structured")
        self.assertIn("相关记忆", result["context"])
        self.assertGreater(result["memory_count"], 0)

    def test_build_compact(self):
        result = self.builder.build(max_tokens=200, style="compact")
        self.assertGreater(len(result["context"]), 0)

    def test_token_limit(self):
        result = self.builder.build(max_tokens=50, style="structured")
        self.assertTrue(result["truncated"] or result["token_estimate"] <= 50)

    def test_build_system_prompt(self):
        prompt = self.builder.build_system_prompt(
            agent_name="TestBot",
            base_prompt="你是测试助手",
            max_tokens=300,
        )
        self.assertIn("你是测试助手", prompt)


class TestHierarchical(unittest.TestCase):
    """层级记忆测试"""

    def setUp(self):
        from store import MemoryStore
        from hierarchical import HierarchicalMemory
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.store = MemoryStore(self.db_path)
        self.hm = HierarchicalMemory(self.store)

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_l1_add_and_get(self):
        self.hm.l1_add("测试消息", "user")
        self.hm.l1_add("回复消息", "assistant")
        self.assertEqual(len(self.hm.l1_get()), 2)

    def test_l1_context(self):
        self.hm.l1_add("用户消息", "user")
        self.hm.l1_add("助手回复", "assistant")
        ctx = self.hm.l1_context()
        self.assertIn("用户", ctx)
        self.assertIn("助手", ctx)

    def test_l1_clear(self):
        self.hm.l1_add("消息", "user")
        self.hm.l1_clear()
        self.assertEqual(len(self.hm._l1_buffer), 0)

    def test_l1_capacity(self):
        for i in range(60):
            self.hm.l1_add(f"消息 {i}" * 10, "user")
        self.assertLessEqual(len(self.hm._l1_buffer), self.hm.L1_CAPACITY)

    def test_stats(self):
        stats = self.hm.get_stats()
        self.assertIn("L1_short_term", stats)
        self.assertIn("L2_mid_term", stats)
        self.assertIn("L3_long_term", stats)


class TestSelfHealing(unittest.TestCase):
    """自我修复测试"""

    def setUp(self):
        from store import MemoryStore
        from self_healing import SelfHealing
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.store = MemoryStore(self.db_path)
        self.sh = SelfHealing(self.store)

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_no_contradiction_on_empty(self):
        result = self.sh.detect_contradictions()
        self.assertEqual(len(result), 0)

    def test_full_scan(self):
        result = self.sh.full_scan()
        self.assertIn("contradictions", result)
        self.assertIn("outdated", result)
        self.assertIn("total_issues", result)


class TestCausalChain(unittest.TestCase):
    """因果链测试"""

    def setUp(self):
        from store import MemoryStore
        from causal import CausalChain
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.store = MemoryStore(self.db_path)
        self.cc = CausalChain(self.store)

        self.store.insert_memory(
            memory_id="cause", time_id="T1", time_ts=1000,
            person_id="P01", nature_id="D04", content="探索 RAG",
            content_hash="c1",
        )
        self.store.insert_memory(
            memory_id="effect", time_id="T2", time_ts=2000,
            person_id="P01", nature_id="D03", content="决定用 Chroma",
            content_hash="c2",
        )

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_add_causal_link(self):
        self.cc.add_causal_link("cause", "effect", "decision_based_on")
        chain = self.cc.get_causal_chain("effect")
        self.assertGreater(len(chain["caused_by"]), 0)

    def test_format_chain(self):
        self.cc.add_causal_link("cause", "effect", "led_to")
        chain = self.cc.get_causal_chain("cause")
        text = self.cc.format_causal_chain(chain)
        self.assertIsInstance(text, str)
        self.assertGreater(len(text), 0)


class TestQuality(unittest.TestCase):
    """质量评分测试"""

    def setUp(self):
        from store import MemoryStore
        from quality import MemoryQuality
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.q_fd, self.q_path = tempfile.mkstemp(suffix=".json")
        self.store = MemoryStore(self.db_path)
        self.mq = MemoryQuality(self.store, self.q_path)

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)
        os.close(self.q_fd)
        os.unlink(self.q_path)

    def test_record_and_score(self):
        self.mq.record_retrieval("test_id")
        self.mq.record_retrieval("test_id")
        self.mq.record_feedback("test_id", useful=True)

        mem = {"memory_id": "test_id", "importance": "high", "time_ts": time.time(), "content": "x" * 200}
        q = self.mq.compute_quality(mem)
        self.assertGreater(q["quality_score"], 0.3)
        self.assertIn(q["grade"], ["A", "B", "C"])

    def test_stats(self):
        stats = self.mq.get_stats()
        self.assertIn("total_feedback", stats)


class TestMemoryGraph(unittest.TestCase):
    """记忆图谱测试"""

    def setUp(self):
        from store import MemoryStore
        from memory_graph import MemoryGraph
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.store = MemoryStore(self.db_path)
        self.mg = MemoryGraph(self.store)

    def tearDown(self):
        self.store.close()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_ascii_empty(self):
        result = self.mg.generate(format="ascii")
        self.assertIsInstance(result, str)

    def test_mermaid(self):
        self.store.insert_memory(
            memory_id="g1", time_id="T1", time_ts=1000,
            person_id="P01", nature_id="D05", content="图谱测试",
            content_hash="gh1", topics=["ai.rag"],
        )
        result = self.mg.generate(format="mermaid")
        self.assertIn("graph", result)


class TestMemoryFilterBatch(unittest.TestCase):
    """批量过滤测试"""

    def test_batch_filter(self):
        from memory_filter import MemoryFilter
        mf = MemoryFilter()
        msgs = ["你好", "我决定用Chroma做向量库", "ok", "明天打算完成集成测试", "这个问题困扰我很久了"]
        results = mf.batch_filter(msgs)
        self.assertEqual(len(results), 5)
        kept = [r for r in results if r["remember"]]
        self.assertGreaterEqual(len(kept), 2)


class TestStoreBackup(unittest.TestCase):
    """备份测试"""

    def test_backup(self):
        from store import MemoryStore
        db_fd, db_path = tempfile.mkstemp(suffix=".db")
        backup_fd, backup_path = tempfile.mkstemp(suffix=".db")
        store = MemoryStore(db_path)
        store.insert_memory(
            memory_id="bk", time_id="T1", time_ts=1000,
            person_id="P01", nature_id="D05", content="备份测试",
            content_hash="bkh",
        )
        store.backup(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        self.assertGreater(os.path.getsize(backup_path), 0)
        store.close()
        os.close(db_fd)
        os.unlink(db_path)
        os.close(backup_fd)
        os.unlink(backup_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
