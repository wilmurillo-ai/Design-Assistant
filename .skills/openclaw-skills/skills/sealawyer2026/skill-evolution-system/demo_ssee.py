#!/usr/bin/env python3
"""
技能自进化引擎 (SSEE) 演示脚本

演示 SSE Core v2.0 的核心功能
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/skill-evolution-system')

from ssee.core import EvolutionKernel, KernelConfig
from ssee.adapters import OpenClawAdapter, AdapterRegistry


def demo_kernel():
    """演示进化内核"""
    print("=" * 60)
    print("🚀 SSE Core v2.0 演示")
    print("=" * 60)
    
    # 1. 初始化内核
    print("\n📦 1. 初始化进化内核...")
    from pathlib import Path
    config = KernelConfig(
        data_dir=Path("/tmp/ssee_demo"),
        auto_evolve=False,
        sync_enabled=True,
    )
    kernel = EvolutionKernel(config)
    
    if kernel.initialize():
        print("   ✅ 内核初始化成功")
    else:
        print("   ❌ 内核初始化失败")
        return
    
    # 显示内核状态
    status = kernel.get_status()
    print(f"   📊 版本: {status['version']}")
    print(f"   📊 注册技能: {status['registered_skills']}")
    print(f"   📊 插件: {status['plugins']}")
    
    # 2. 注册技能
    print("\n📝 2. 注册测试技能...")
    skills = [
        "zhang-contract-review",
        "zhang-litigation-strategy",
        "zhang-criminal-defense",
    ]
    
    for skill_id in skills:
        kernel.register_skill(skill_id, {
            "name": skill_id,
            "version": "1.0.0",
            "category": "legal",
        })
    print(f"   ✅ 已注册 {len(skills)} 个技能")
    
    # 3. 模拟技能使用
    print("\n📊 3. 模拟技能使用追踪...")
    
    # 模拟多次调用
    for i in range(5):
        kernel.track("zhang-contract-review", {
            "duration": 1.2 + i * 0.1,
            "success": True,
            "tokens_used": 1500 + i * 100,
        })
    
    # 模拟一些失败
    kernel.track("zhang-contract-review", {
        "duration": 3.5,
        "success": False,
        "error": "timeout",
    })
    
    print("   ✅ 已记录 6 次调用")
    
    # 4. 性能分析
    print("\n🔍 4. 性能分析...")
    analysis = kernel.analyze("zhang-contract-review")
    
    if analysis.get("status") == "analyzed":
        summary = analysis.get("summary", {})
        print(f"   📈 总调用: {summary.get('total_calls')}")
        print(f"   📈 成功率: {summary.get('success_rate')}%")
        print(f"   📈 平均耗时: {summary.get('avg_duration')}s")
        print(f"   📈 健康度: {summary.get('health_score')}")
        
        bottlenecks = analysis.get("bottlenecks", [])
        if bottlenecks:
            print(f"   ⚠️  发现 {len(bottlenecks)} 个瓶颈")
    
    # 5. 生成进化计划
    print("\n📝 5. 生成进化计划...")
    plan = kernel.plan("zhang-contract-review", analysis)
    
    print(f"   📋 优先级: {plan.get('priority')}")
    print(f"   📋 当前健康度: {plan.get('health_score_current')}")
    print(f"   📋 目标健康度: {plan.get('health_score_target')}")
    print(f"   📋 优化任务: {len(plan.get('tasks', []))} 个")
    
    for task in plan.get("tasks", [])[:2]:
        print(f"      - [{task['priority']}] {task['description']}")
    
    # 6. 技能同步（飞轮核心）
    print("\n🔄 6. 技能间同步进化...")
    sync_result = kernel.sync_skills(skills)
    
    print(f"   🔄 同步技能: {len(sync_result.get('skills_synced', []))} 个")
    print(f"   🔄 发现模式: {sync_result.get('patterns_discovered')} 个")
    print(f"   🔄 应用模式: {sync_result.get('patterns_applied')} 个")
    
    # 7. 执行进化
    print("\n⚡ 7. 执行技能进化...")
    # 注意：实际执行需要确认
    print("   ⏸️ 进化执行已暂停（需用户确认）")
    print("   💡 运行 kernel.evolve(skill_id, plan) 执行进化")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)


def demo_adapter():
    """演示适配器"""
    print("\n\n🔌 适配器演示")
    print("=" * 60)
    
    # 创建 OpenClaw 适配器
    adapter = OpenClawAdapter({
        "skills_dir": "~/.openclaw/workspace/skills"
    })
    
    if adapter.connect():
        print("✅ 已连接到 OpenClaw")
        
        skills = adapter.get_skill_list()
        print(f"📋 发现 {len(skills)} 个技能")
        
        # 显示前3个技能
        for skill in skills[:3]:
            print(f"   - {skill['name']} (v{skill['version']})")
    else:
        print("❌ 无法连接到 OpenClaw")


if __name__ == "__main__":
    demo_kernel()
    demo_adapter()
