#!/usr/bin/env python3
"""
OpenClaw 增强模块调用脚本

通过命令行调用各个增强模块
用法: python3 enhancer.py <模块> <参数>
"""

import sys
import json
import asyncio
import os

# 获取技能目录
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SKILL_DIR)

def run_cli(args: str = "") -> str:
    """CLI彩色输出"""
    from cli.color_output import info, success, warning, error, table
    
    output = []
    output.append("ℹ 系统消息")
    output.append("✓ 成功")
    output.append("⚠ 警告")
    output.append("✗ 错误")
    output.append("")
    output.append("+------+----+")
    output.append("| 功能 | 状态 |")
    output.append("+------+----+")
    output.append("| A    | ✓   |")
    output.append("| B    | ✓   |")
    output.append("+------+----+")
    return "\n".join(output)

def run_memory(args: str = "") -> str:
    """分层记忆"""
    import tempfile, shutil
    from memory.layered_memory import LayeredMemory
    
    temp = tempfile.mkdtemp()
    mem = LayeredMemory(temp)
    
    async def main():
        await mem.add("用户叫主人", importance=8, tags=["user"])
        await mem.add("用户喜欢瓦罗兰特", importance=7, tags=["game"])
        results = await mem.search("用户")
        stats = mem.get_stats()
        return len(results), stats
    
    count, stats = asyncio.run(main())
    shutil.rmtree(temp)
    
    return f"记忆搜索: 找到 {count} 条\n统计: 短期{stats['short_count']}条, 长期{stats['long_count']}条"

def run_multi_agent(args: str = "") -> str:
    """多Agent协作"""
    from multi_agent.system import AgentTeam, PlannerAgent, ExecutorAgent
    
    team = AgentTeam("项目团队")
    team.add_agent(PlannerAgent("planner"))
    team.add_agent(ExecutorAgent("executor"))
    
    async def main():
        results = await team.run_workflow(args or "写一个Hello World程序")
        return results
    
    results = asyncio.run(main())
    
    output = [f"完成 {len(results)} 个任务:"]
    for task_id, task in results.items():
        desc = task.description[:30] + "..." if len(task.description) > 30 else task.description
        status = "✓" if task.status.value == "completed" else "✗"
        output.append(f"  {status} {desc}")
    
    return "\n".join(output)

def run_sandbox(args: str = "") -> str:
    """沙箱隔离"""
    from sandbox import ProcessSandbox, SandboxConfig
    
    config = SandboxConfig(security_level="basic")
    sandbox = ProcessSandbox(config)
    
    async def main():
        result = await sandbox.execute_command(args or "echo hello")
        return result
    
    result = asyncio.run(main())
    
    return f"执行结果: {'成功' if result.success else '失败'}\n输出: {result.output.strip()}"

def run_error_recovery(args: str = "") -> str:
    """错误恢复"""
    from error_recovery import retry_on_error, RetryConfig
    
    @retry_on_error(RetryConfig(max_retries=3, initial_delay=0.01))
    def test():
        return "成功!"
    
    result = test()
    return f"重试结果: {result}"

def run_compression(args: str = "") -> str:
    """智能压缩"""
    from compression import ImportanceScorer, Message
    
    scorer = ImportanceScorer()
    msg = Message(role="user", content=args or "重要信息", importance=0.8)
    score = scorer.score(msg)
    
    return f"内容: {msg.content}\n重要性评分: {score:.2f}"

def run_tools(args: str = "") -> str:
    """工具系统"""
    from tools.schema import ToolRegistry, ToolDefinition, ToolCapability
    
    registry = ToolRegistry()
    registry.register(ToolDefinition(
        name="hello",
        description="打招呼",
        capabilities=[ToolCapability.EXECUTE]
    ))
    
    tools = list(registry._tools.keys())
    return f"已注册工具: {', '.join(tools)}"

def run_repl(args: str = "") -> str:
    """REPL交互"""
    from repl import SlashCommandHandler
    
    handler = SlashCommandHandler()
    result = handler.execute(args or "/help")
    
    return result[:200] + "..." if len(result) > 200 else result

# 模块映射
MODULES = {
    "cli": run_cli,
    "memory": run_memory,
    "multi_agent": run_multi_agent,
    "multiagent": run_multi_agent,
    "sandbox": run_sandbox,
    "error_recovery": run_error_recovery,
    "error": run_error_recovery,
    "compression": run_compression,
    "tools": run_tools,
    "repl": run_repl,
}

def main():
    if len(sys.argv) < 2:
        print("OpenClaw 增强模块")
        print("用法: python3 enhancer.py <模块> [参数]")
        print(f"可用模块: {', '.join(MODULES.keys())}")
        sys.exit(1)
    
    module = sys.argv[1].lower()
    args = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
    
    if module not in MODULES:
        print(f"错误: 未知模块 '{module}'")
        print(f"可用模块: {', '.join(MODULES.keys())}")
        sys.exit(1)
    
    try:
        result = MODULES[module](args)
        print(result)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()