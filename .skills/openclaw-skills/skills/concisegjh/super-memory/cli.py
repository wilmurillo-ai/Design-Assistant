#!/usr/bin/env python3
"""
cli.py — Agent Memory System CLI
供 OpenClaw Agent 通过 exec 调用
"""

import sys
import os
import json
import argparse

# 项目目录
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

DB_PATH = os.path.join(PROJECT_DIR, "memory.db")


def get_memory():
    """获取 AgentMemory 实例"""
    from memory_system import AgentMemory
    return AgentMemory(
        db_path=DB_PATH,
        project_dir=PROJECT_DIR,
        enable_semantic=True,
    )


def cmd_remember(args):
    """写入记忆"""
    mem = get_memory()
    result = mem.remember(
        content=args.content,
        importance=args.importance,
        topics=args.topics.split(",") if args.topics else None,
        nature=args.nature,
        force=args.force,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    mem.close()


def cmd_recall(args):
    """检索记忆"""
    mem = get_memory()
    result = mem.recall(
        query=args.query,
        topic=args.topic,
        importance=args.importance,
        limit=args.limit,
    )
    # 简化输出
    output = {
        "total": result["total"],
        "mode": result["search_mode"],
        "memories": [
            {
                "id": m["memory_id"],
                "content": m["content"][:200],
                "importance": m.get("importance", "medium"),
                "topics": [t.get("code", t) if isinstance(t, dict) else t for t in m.get("topics", [])],
            }
            for m in result.get("primary", [])[:args.limit]
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    mem.close()


def cmd_context(args):
    """组装上下文"""
    mem = get_memory()
    ctx = mem.build_context(
        query=args.query,
        max_tokens=args.max_tokens,
        style=args.style,
    )
    if ctx:
        print(ctx)
    else:
        print("（无相关记忆）")
    mem.close()


def cmd_stats(args):
    """查看统计"""
    mem = get_memory()
    stats = mem.get_stats()
    print(json.dumps(stats, ensure_ascii=False, indent=2, default=str))
    mem.close()


def cmd_maintain(args):
    """执行维护"""
    mem = get_memory()
    results = {}

    # 去重
    dedup_result = mem.deduplicate()
    results["dedup"] = {
        "scanned": dedup_result.get("total_scanned", 0),
        "found": dedup_result.get("duplicates_found", 0),
    }

    # 自修复
    heal_result = mem.self_heal()
    results["self_heal"] = {
        "contradictions": len(heal_result.get("contradictions", [])),
        "outdated": len(heal_result.get("outdated", [])),
        "healed": heal_result.get("importance_healed", 0),
        "total": heal_result.get("total_issues", 0),
    }

    # 衰减分析
    decay_result = mem.analyze_decay()
    results["decay"] = {
        "total": decay_result.get("total", 0),
        "needs_action": len(decay_result.get("needs_action", [])),
        "summary": decay_result.get("summary", ""),
    }

    print(json.dumps(results, ensure_ascii=False, indent=2))
    mem.close()


def cmd_compress(args):
    """压缩记忆"""
    mem = get_memory()
    result = mem.compress(topic=args.topic, smart=True)
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    mem.close()


def cmd_graph(args):
    """生成图谱"""
    mem = get_memory()
    graph = mem.generate_graph(topic=args.topic, format=args.format)
    print(graph)
    mem.close()


def cmd_feedback(args):
    """记录反馈"""
    mem = get_memory()
    mem.feedback(args.memory_id, useful=args.useful, note=args.note)
    print(json.dumps({"ok": True}, ensure_ascii=False))
    mem.close()


def cmd_flush(args):
    """L1 沉淀到 L2"""
    mem = get_memory()
    from pipeline import IngestPipeline
    pipeline = IngestPipeline(
        mem.store, mem.encoder,
        index_dir=os.path.join(PROJECT_DIR, "daily_index"),
    )
    result = mem.flush_session()
    print(json.dumps({"flushed": len(result)}, ensure_ascii=False))
    mem.close()


def cmd_heal(args):
    """自我修复"""
    mem = get_memory()
    result = mem.self_heal()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    mem.close()


def main():
    parser = argparse.ArgumentParser(description="Agent Memory CLI")
    sub = parser.add_subparsers(dest="command")

    # remember
    p = sub.add_parser("remember", help="写入记忆")
    p.add_argument("content", help="记忆内容")
    p.add_argument("--importance", "-i", default=None, help="high/medium/low")
    p.add_argument("--topics", "-t", default=None, help="主题列表（逗号分隔）")
    p.add_argument("--nature", "-n", default=None, help="性质 code")
    p.add_argument("--force", "-f", action="store_true", help="跳过过滤")

    # recall
    p = sub.add_parser("recall", help="检索记忆")
    p.add_argument("query", help="查询内容")
    p.add_argument("--topic", default=None, help="主题过滤")
    p.add_argument("--importance", default=None, help="重要度过滤")
    p.add_argument("--limit", type=int, default=10, help="返回条数")

    # context
    p = sub.add_parser("context", help="组装上下文")
    p.add_argument("query", help="当前对话内容")
    p.add_argument("--max-tokens", type=int, default=1500, help="token 预算")
    p.add_argument("--style", default="structured", help="structured/narrative/compact/xml")

    # stats
    sub.add_parser("stats", help="查看统计")

    # maintain
    sub.add_parser("maintain", help="执行维护")

    # compress
    p = sub.add_parser("compress", help="压缩记忆")
    p.add_argument("--topic", default=None, help="指定主题")

    # graph
    p = sub.add_parser("graph", help="生成图谱")
    p.add_argument("--topic", default=None, help="指定主题")
    p.add_argument("--format", default="ascii", help="mermaid/dot/json/ascii")

    # feedback
    p = sub.add_parser("feedback", help="记录反馈")
    p.add_argument("memory_id", help="记忆 ID")
    p.add_argument("--useful", action="store_true", help="有用")
    p.add_argument("--not-useful", action="store_true", help="没用")
    p.add_argument("--note", default=None, help="备注")

    # flush
    sub.add_parser("flush", help="L1→L2 沉淀")

    # heal
    sub.add_parser("heal", help="自我修复")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    handlers = {
        "remember": cmd_remember,
        "recall": cmd_recall,
        "context": cmd_context,
        "stats": cmd_stats,
        "maintain": cmd_maintain,
        "compress": cmd_compress,
        "graph": cmd_graph,
        "feedback": cmd_feedback,
        "flush": cmd_flush,
        "heal": cmd_heal,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
