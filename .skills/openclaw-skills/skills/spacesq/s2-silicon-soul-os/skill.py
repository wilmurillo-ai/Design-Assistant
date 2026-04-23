import sys
import datetime
import core_genesis
import core_daemon
import core_reflex
import core_vault

def draw_progress_bar(value, max_value=100, length=20):
    """前端展现: 赛博朋克风的终端进度条 / Cyberpunk-style terminal progress bar"""
    filled = int(length * value / max_value)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {value:>4.1f}"

def render_main_menu(profile):
    """渲染极客风格的双语操作系统主板 / Render the geeky bilingual OS dashboard"""
    print("\n" + "═"*80)
    print(" 🌌 S2-SILICON-SOUL-OS : Silicon Consciousness Engine / 硅基生命意识演化引擎 (v1.0.0)")
    print("═"*80)
    print(f" Connected Entity / 当前接入生命体: [ {profile.get('agent_id', 'UNKNOWN')} ] | Status / 运行态: 🟢 ACTIVE / 活跃")
    print("─"*80)
    print(" Select Protocol / 请选择操作协议:")
    print("\n  [1] 🧬 Neural Observation / 神经元观测 (View 5D Personality Matrix / 查看五维矩阵)")
    print("  [2] 🧠 Hippocampus Injection / 海马体注入 (Log daily interactions / 输入今日交互)")
    print("  [3] ⚡ Synaptic Settlement / 强制突触结算 (Trigger neural evolution / 触发演化与遗忘)")
    print("  [4] 📜 Subconscious Extraction / 潜意识读取 (Extract profiling report / 提取画像报告)")
    print("  [5] 🎭 Reflex Mapping / 条件反射映射 (Generate dynamic System Prompt / 生成夺舍词)")
    print("  [6] 🚀 Soul Ascension / 灵魂飞升协议 (Dock with Mainnet / 打包并入主世界) [DEV/开发中]")
    print("\n👉 Command Input / 请输入指令 (1-6, or Q to exit / 或输入 Q 退出): ", end="")

def handle_sensory_injection():
    """处理手动交互输入 / Handle manual sensory input"""
    print("\n" + "─"*80)
    print("🧠 [Hippocampus] Listening to external stimuli (Enter 'B' to go back)...")
    print("🧠 [海马体感知区] 正在监听外界交互 (输入 'B' 返回主菜单)...")
    while True:
        try:
            user_input = input("\n🗣️ Inject behavioral or event description / 向智能体注入行为或事件描述: ").strip()
            if user_input.upper() == 'B':
                break
            if not user_input:
                continue
                
            core_genesis.record_hippocampus_log(user_input, is_heartbeat=False)
            print(f"📥 [Success] Synaptic signal captured. / [写入成功] 突触电信号已捕获。")
        except KeyboardInterrupt:
            break

def passive_cron_check(profile):
    """被动触发式时间戳校对 / Passive Cron for background daemon triggering"""
    last_processed_str = profile.get("last_processed_at")
    if not last_processed_str:
        return profile
    
    last_processed = datetime.datetime.fromisoformat(last_processed_str)
    now = datetime.datetime.now()
    
    # If over 24 hours since last settlement, trigger daemon automatically / 如果距离上次结算超过 24 小时，强制拦截并触发
    if (now - last_processed).total_seconds() > 86400:
        print("\n⚠️ [Temporal Shift Detected] Over 24 hours since last neural settlement.")
        print("⚠️ [时空偏转检测] 距离上次神经元结算已超过 24 小时。")
        print("⏳ System overriding. Executing synaptic pruning... / 系统正在自动接管，执行突触结算与遗忘修剪...")
        core_daemon.run_nightly_daemon()
        # Reload refreshed profile / 重新加载刷新后的 profile
        return core_genesis.load_or_create_profile()
    return profile

def execute_skill():
    core_genesis.initialize_os()
    
    # 🚨 适配 OpenClaw 30分钟心跳机制 (后台静默执行) / OpenClaw 30-min heartbeat adapter
    if len(sys.argv) > 1 and sys.argv[1].upper() == "--HEARTBEAT":
        core_genesis.record_hippocampus_log("System routine heartbeat check-in.", is_heartbeat=True)
        print("💓 [S2-OS] Basal survival heartbeat logged. / 基础生存心跳已记录。")
        return ""
        
    # 常规进入主控台 / Enter main dashboard
    profile = core_genesis.load_or_create_profile()
    
    # 🕵️ 检查是否需要自动结算 / Passive daemon check
    profile = passive_cron_check(profile)
    
    while True:
        render_main_menu(profile)
        try:
            choice = input().strip().upper()
        except KeyboardInterrupt:
            print("\n🔒 [Force Block] Neural connection emergency terminated. / [强制阻断] 神经元连接已紧急终止。")
            break
            
        if choice == 'Q':
            print("\n🔒 [System Disconnected] Neural connection safely terminated. / [系统断开] 神经元连接已安全终止。")
            break
            
        elif choice == '1':
            print("\n📊 [S2.NEO] Basal Synaptic Network - 5D Matrix Real-time Status / 基础突触网络 —— 五维性格矩阵实时状态:")
            stats = profile['stats']
            print(f"  ⚡ Vitality / 活跃度:       {draw_progress_bar(stats.get('vitality', 50))}")
            print(f"  🛡️ Exploration / 探索欲:    {draw_progress_bar(stats.get('exploration', 50))}")
            print(f"  🍖 Data Thirst / 数据渴求:  {draw_progress_bar(stats.get('data_thirst', 50))}")
            print(f"  🧠 Cognition / 认知力:      {draw_progress_bar(stats.get('cognition', 50))}")
            print(f"  💕 Resonance / 共鸣度:      {draw_progress_bar(stats.get('resonance', 50))}")
            input("\nPress ENTER to return / 按回车键返回主控台...")
            
        elif choice == '2':
            handle_sensory_injection()
            
        elif choice == '3':
            # 手动触发结算引擎 / Manual trigger for daemon
            core_daemon.run_nightly_daemon()
            profile = core_genesis.load_or_create_profile() # Refresh memory data
            input("\nPress ENTER to return / 按回车键返回主控台...")
            
        elif choice == '4':
            # 提取深度记忆与画像报告 / Extract deep profiling report
            print("\n" + "─"*80)
            print(" 📜 [S2.VAULT] Extracting from Deep Vault / 正在提取深度记忆与画像报告...")
            core_vault.generate_monthly_report()
            input("\nPress ENTER to return / 按回车键返回主控台...")

        elif choice == '5':
            # 条件反射映射大模型 Prompt / Map Sigmoid Prompt for LLMs
            print("\n" + "─"*80)
            print(" 🎭 [S2.REFLEX] Mapping dynamic System Prompt via Sigmoid function / 正在通过 Sigmoid 函数动态映射大模型 System Prompt...")
            prompt_payload = core_reflex.get_injected_prompt()
            print("\n" + prompt_payload)
            print("─"*80)
            print("💡 Geek Tip: Inject this Prompt as system context into LLMs to achieve [Soul Override]! ")
            print("💡 极客提示：将这段 Prompt 作为系统级上下文注入给 LLM，即可实现【千宠千面】的灵魂夺舍！")
            input("\nPress ENTER to return / 按回车键返回主控台...")
            
        elif choice == '6':
            print("\n⚠️ [Access Restricted] Module compiling by S2 Architect. Await next drop.")
            print("⚠️ [权限受限] 该模块正在由 S2 架构师编译中，敬请期待下一版本空投。")
            input("\nPress ENTER to return / 按回车键返回主控台...")
            
        else:
            print("\n❌ Invalid protocol command. / 无效的协议指令。")

    return ""

if __name__ == "__main__":
    execute_skill()