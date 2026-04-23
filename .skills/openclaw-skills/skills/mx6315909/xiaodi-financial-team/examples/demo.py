"""
金融团队使用示例

演示个股分析、持仓复盘、风险预警等场景
"""

import sys
sys.path.insert(0, "../scripts")
from agents import FinanceTeam


def demo_list_agents():
    """示例 0: 列出所有 Agent"""
    print("=" * 60)
    print("👥 金融团队成员")
    print("=" * 60)

    team = FinanceTeam()
    agents = team.list_agents()

    print("\n共 7 个专业 Agent:")
    for i, name in enumerate(agents, 1):
        agent = team.get_agent(name)
        print(f"  {i}. {agent.emoji} {name} - {agent.role}")


def demo_stock_analysis():
    """示例 1: 个股分析"""
    print("\n" + "=" * 60)
    print("📊 示例 1: 个股分析流程")
    print("=" * 60)

    team = FinanceTeam()
    result = team.analyze_stock(code="600821", name="金开新能")

    print(f"\n股票: {result['code']} {result['name']}")
    print(f"工作流: {result['workflow']}")
    print(f"状态: {result['status']}")

    for agent_name, output in result["results"].items():
        emoji = output.get("emoji", "")
        print(f"\n{emoji} [{agent_name}]")
        if "result" in output:
            for key, value in output["result"].items():
                if isinstance(value, list):
                    print(f"  - {key}:")
                    for item in value:
                        print(f"      • {item}")
                elif isinstance(value, dict):
                    print(f"  - {key}:")
                    for k, v in value.items():
                        print(f"      • {k}: {v}")
                else:
                    print(f"  - {key}: {value}")


def demo_portfolio_review():
    """示例 2: 持仓复盘"""
    print("\n" + "=" * 60)
    print("📈 示例 2: 持仓复盘")
    print("=" * 60)

    team = FinanceTeam()
    holdings = [
        {"code": "600821", "name": "金开新能", "shares": 1000},
        {"code": "000988", "name": "华工科技", "shares": 500},
    ]

    result = team.review_portfolio(holdings=holdings)

    print(f"\n工作流: {result['workflow']}")
    print(f"持仓: {[h['code'] for h in result['holdings']]}")

    # 只显示投顾专家的综合分析
    advisor_result = result["results"]["投顾专家"]
    emoji = advisor_result.get("emoji", "")
    print(f"\n{emoji} [投顾专家综合分析]")
    if "result" in advisor_result:
        for key, value in advisor_result["result"].items():
            print(f"  - {key}: {value}")


def demo_single_agent():
    """示例 3: 单个 Agent 执行"""
    print("\n" + "=" * 60)
    print("🎯 示例 3: 商机助理技术分析")
    print("=" * 60)

    team = FinanceTeam()
    result = team.execute(
        agent_name="商机助理",
        task="分析 600821 金开新能技术面"
    )

    emoji = result.get("emoji", "")
    print(f"\n{emoji} [{result['agent']}]")
    if "result" in result:
        print("\n技术分析结果:")
        for key, value in result["result"].items():
            if isinstance(value, dict):
                print(f"  - {key}:")
                for k, v in value.items():
                    print(f"      • {k}: {v}")
            elif isinstance(value, list):
                print(f"  - {key}: {', '.join(map(str, value))}")
            else:
                print(f"  - {key}: {value}")


def demo_risk_check():
    """示例 4: 风险预警"""
    print("\n" + "=" * 60)
    print("🚨 示例 4: 风险预警")
    print("=" * 60)

    team = FinanceTeam()
    holdings = [
        {"code": "600821", "name": "金开新能"},
        {"code": "000988", "name": "华工科技"},
    ]

    result = team.check_risks(holdings=holdings)

    emoji = result.get("emoji", "")
    print(f"\n{emoji} [{result['agent']}]")
    if "result" in result:
        print("\n风险状态:")
        for key, value in result["result"].items():
            if isinstance(value, list):
                print(f"  - {key}:")
                for item in value:
                    print(f"      • {item}")
            else:
                print(f"  - {key}: {value}")


if __name__ == "__main__":
    # 运行所有示例
    demo_list_agents()
    demo_stock_analysis()
    demo_portfolio_review()
    demo_single_agent()
    demo_risk_check()

    print("\n" + "=" * 60)
    print("🎉 所有示例运行完成！")
    print("=" * 60)