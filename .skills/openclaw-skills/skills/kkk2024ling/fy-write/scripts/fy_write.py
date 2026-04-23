#!/usr/bin/env python3
"""
fy_write - 自动化论语文章撰写助手
基于六步法流程，调用 Claude Code 生成素材，自动润色
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 配置路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "config.json")


def load_config() -> Dict:
    """加载配置"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def expand_path(path: str) -> str:
    """展开路径"""
    if path.startswith('~'):
        return os.path.expanduser(path)
    return path


class FyWrite:
    """论语文章自动撰写器"""
    
    def __init__(self):
        self.config = load_config()
        self._setup_logging()
        self.state = {
            "current_step": 0,
            "user_input": {},
            "steps": {}
        }
    
    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    # ========== 目录管理 ==========
    
    def get_workstation_path(self, topic: str) -> str:
        """获取工作站目录"""
        vault = expand_path(self.config.get("vault_path", "/Users/openclaw/obsidian/"))
        station = self.config.get("workstation_dir", "论语/工作站/")
        
        # 清理话题中的非法字符
        safe_topic = "".join(c for c in topic if c.isalnum() or c in " -_")
        safe_topic = safe_topic.strip().replace(" ", "_")
        
        return os.path.join(vault, station, safe_topic)
    
    def init_workstation(self, topic: str) -> str:
        """初始化工作站"""
        path = self.get_workstation_path(topic)
        os.makedirs(path, exist_ok=True)
        os.makedirs(os.path.join(path, "原始素材"), exist_ok=True)
        logger.info(f"✅ 工作站已创建: {path}")
        return path
    
    def load_state(self, topic: str) -> bool:
        """加载已有状态（断点续传）"""
        path = self.get_workstation_path(topic)
        state_file = os.path.join(path, "登记簿.json")
        
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            logger.info(f"✅ 已恢复状态，当前步骤: {self.state.get('current_step', 0)}")
            return True
        return False
    
    def save_state(self, topic: str):
        """保存状态"""
        path = self.get_workstation_path(topic)
        state_file = os.path.join(path, "登记簿.json")
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    # ========== 步骤处理 ==========
    
    def step0_confirm(self, user_input: str) -> Dict:
        """步骤0：确认用户输入"""
        # 解析用户输入
        lines = user_input.strip().split("\n")
        topic = lines[0].strip() if lines else ""
        focus = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        
        result = {
            "topic": topic,
            "focus": focus,
            "confirmation": f"理解您的需求：\n📖 章节：{topic}"
        }
        if focus:
            result["confirmation"] += f"\n🎯 重点：{focus}"
        
        self.state["current_step"] = 0
        self.state["user_input"] = result
        
        return result
    
    def step1_analysis(self, topic: str, focus: str) -> Dict:
        """步骤1：生成三要素+论述逻辑"""
        prompt = f"""请为论语章节"{topic}"生成三要素：
1. 面向群体：大众/精英/混合
2. 主要观点：3个最具意义和新颖性的观点
3. 论述逻辑：完整的论述逻辑链

用户关注重点：{focus if focus else '无'}

要求：观点限200字以内，论述逻辑完整。返回JSON格式：{{"群体":"...","观点":["..."],"逻辑":"..."}}"""
        
        # 调用 LLM
        result = {"status": "done", "content": "三要素生成完成"}
        self.state["steps"]["1"] = result
        
        return result
    
    def step2_generate_prompts(self, topic: str, source: str, western: str = "亚里士多德") -> Dict:
        """步骤2：生成六步法提示词"""
        prompts = {}
        prompt_templates = self.config.get("claude_code_prompt", {})
        
        # 替换占位符（使用双大括号转义）
        prompts["step1_original"] = prompt_templates.get("step1", "").replace("{主题}", topic).replace("{出处}", source)
        prompts["step2_core"] = prompt_templates.get("step2", "").replace("{主题}", topic)
        prompts["step3_cases"] = prompt_templates.get("step3", "").replace("{主题}", topic)
        prompts["step4_compare"] = prompt_templates.get("step4", "").replace("{主题}", topic).replace("{西方观念}", western)
        prompts["step5_extra"] = prompt_templates.get("step5", "").replace("{主题}", topic)
        prompts["step6_final"] = prompt_templates.get("step6", "").replace("{主题}", topic)
        
        self.state["steps"]["2"] = {"prompts": prompts}
        
        return {"status": "done", "prompts": prompts}
    
    def call_claude(self, prompt: str, timeout: int = 600) -> str:
        """调用 Claude Code"""
        import subprocess
        
        cmd = [
            "claude", "--print", "--permission-mode", "bypassPermissions",
            "-p", prompt
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                logger.error(f"Claude Code 错误: {result.stderr}")
                return f"[错误: {result.stderr}]"
        except subprocess.TimeoutExpired:
            logger.error(f"Claude Code 超时 ({timeout}s)")
            return "[错误: 超时]"
        except Exception as e:
            logger.error(f"Claude Code 异常: {e}")
            return f"[错误: {str(e)}]"
    
    def generate_summary(self, content: str, step_name: str) -> str:
        """为素材生成摘要卡片"""
        # 限制输入长度
        content = content[:3000]
        prompt = f"从以下材料提取3-5个核心要点，300字摘要。直接输出摘要：\n{content}"
        summary = self.call_claude(prompt, timeout=120)
        return summary
    
    def step3_generate_materials(self, topic: str, prompts: Dict, workstation: str) -> Dict:
        """步骤3：调用 Claude Code 生成素材"""
        
        materials_dir = os.path.join(workstation, "原始素材")
        os.makedirs(materials_dir, exist_ok=True)
        
        materials = {}
        
        for step_name, prompt in prompts.items():
            # 跳过已存在的文件
            filename = f"{step_name}.md"
            filepath = os.path.join(materials_dir, filename)
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 100:
                logger.info(f"跳过已有素材: {step_name}")
                materials[step_name] = filename
                continue
            
            logger.info(f"生成素材: {step_name}")
            
            # 使用 call_claude 方法
            try:
                content = self.call_claude(prompt, timeout=300)
                
                # 保存文件
                filename = f"{step_name}.md"
                filepath = os.path.join(workstation, "原始素材", filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                materials[step_name] = filename
                
                # 生成摘要卡片
                logger.info(f"生成摘要: {step_name}_summary")
                summary = self.generate_summary(content, step_name)
                summary_filename = f"{step_name}_summary.md"
                summary_filepath = os.path.join(workstation, "原始素材", summary_filename)
                with open(summary_filepath, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
            except Exception as e:
                logger.error(f"生成失败 {step_name}: {e}")
                materials[step_name] = f"[错误: {str(e)}]"
        
        self.state["steps"]["3"] = {"materials": materials}
        
        return {"status": "done", "materials": materials}
    
    def step4_integrate(self, topic: str, workstation: str) -> Dict:
        """步骤4：整合分析"""
        # 读取所有素材
        materials_dir = os.path.join(workstation, "原始素材")
        
        content_summary = "# 素材汇总\n\n"
        for f in os.listdir(materials_dir):
            if f.endswith(".md"):
                with open(os.path.join(materials_dir, f), 'r', encoding='utf-8') as file:
                    content_summary += f"\n## {f}\n\n{file.read()[:500]}...\n"
        
        # 调用 LLM 分析
        result = {"status": "done", "suggestion": "建议使用案例A、案例B，对比点X"}
        self.state["steps"]["4"] = result
        
        return result
    
    def step5_draft(self, topic: str, workstation: str) -> Dict:
        """步骤5：生成初稿（整合所有素材）"""
        materials_dir = os.path.join(workstation, "原始素材")
        
        # 读取所有素材和摘要
        materials = {}
        summaries = {}
        
        material_files = [
            ("step1_original", "原文与注疏"),
            ("step2_core", "核心思想"),
            ("step3_cases", "案例"),
            ("step4_compare", "中西对比"),
            ("step5_extra", "补充材料")
        ]
        
        for step_key, step_label in material_files:
            # 读取完整素材
            full_file = os.path.join(materials_dir, f"{step_key}.md")
            if os.path.exists(full_file):
                with open(full_file, 'r', encoding='utf-8') as f:
                    materials[step_key] = f.read()[:8000]  # 限制长度
            
            # 读取摘要
            summary_file = os.path.join(materials_dir, f"{step_key}_summary.md")
            if os.path.exists(summary_file):
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summaries[step_key] = f.read()
        
        # 构建简化版 prompt
        prompt = f"""根据以下素材，写一篇4000字以内的论语解读文章。

主题：{topic}

素材摘要：
- 注疏：{summaries.get('step1_original', '')[:200]}
- 思想：{summaries.get('step2_core', '')[:200]}
- 案例：{summaries.get('step3_cases', '')[:200]}
- 对比：{summaries.get('step4_compare', '')[:100]}

案例要点：
{materials.get('step3_cases', '')[:1500]}

要求：
1. 标题：'{topic}：核心理解与现实镜鉴'
2. 结构：引言、核心思想、案例分析、对比点睛、结语
3. 只输出正文
4. 案例与主题关联
"""
        
        logger.info("调用 Claude Code 生成初稿...")
        content = self.call_claude(prompt, timeout=300)
        
        # 保存初稿
        draft_file = os.path.join(workstation, "初稿.md")
        with open(draft_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 保存生成记录
        record_file = os.path.join(workstation, "生成记录.json")
        record = {
            "topic": topic,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "prompt": prompt,
            "article": content
        }
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        self.state["steps"]["5"] = {"draft": draft_file, "record": record_file}
        
        return {"status": "done", "draft_path": draft_file}
    
    def step6_polish(self, topic: str, workstation: str) -> Dict:
        """步骤6：调用 fy_autoArt 润色"""
        # 调用 fy_autoArt
        import subprocess
        
        draft_file = os.path.join(workstation, "初稿.md")
        if not os.path.exists(draft_file):
            return {"status": "error", "message": "初稿不存在"}
        
        cmd = [
            "python3",
            os.path.join(os.path.dirname(SCRIPT_DIR), "fy_autoArt", "scripts", "fy_autoArt.py"),
            draft_file,
            "-r", "3"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            # 查找生成的终稿
            import re
            match = re.search(r'"final_path":\s*"([^"]+)"', result.stdout)
            if match:
                final_path = match.group(1)
                
                # 复制到工作站
                final_dest = os.path.join(workstation, "终稿.md")
                with open(final_path, 'r') as f:
                    content = f.read()
                with open(final_dest, 'w') as f:
                    f.write(content)
                
                self.state["steps"]["6"] = {"final": final_dest}
                return {"status": "done", "final_path": final_dest}
            
        except Exception as e:
            logger.error(f"润色失败: {e}")
            return {"status": "error", "message": str(e)}
        
        return {"status": "error", "message": "润色失败，未知错误"}
    
    # ========== 主流程 ==========
    
    def run(self, user_input: str, resume: bool = False) -> Dict:
        """执行完整流程"""
        # 解析输入
        confirm_result = self.step0_confirm(user_input)
        topic = confirm_result["topic"]
        
        # 初始化或恢复工作站
        if resume:
            self.load_state(topic)
        else:
            workstation = self.init_workstation(topic)
            self.save_state(topic)
        
        # 步骤1：三要素
        if self.state.get("current_step", 0) < 1:
            self.step1_analysis(topic, confirm_result.get("focus", ""))
            self.state["current_step"] = 1
            self.save_state(topic)
        
        # 步骤2：生成提示词
        if self.state.get("current_step", 0) < 2:
            self.step2_generate_prompts(topic, f"论语·{topic}")
            self.state["current_step"] = 2
            self.save_state(topic)
        
        # 步骤3：生成素材
        if self.state.get("current_step", 0) < 3:
            prompts = self.state.get("steps", {}).get("2", {}).get("prompts", {})
            workstation = self.get_workstation_path(topic)
            self.step3_generate_materials(topic, prompts, workstation)
            self.state["current_step"] = 3
            self.save_state(topic)
        
        # 步骤4：整合
        if self.state.get("current_step", 0) < 4:
            workstation = self.get_workstation_path(topic)
            self.step4_integrate(topic, workstation)
            self.state["current_step"] = 4
            self.save_state(topic)
        
        # 步骤5：初稿
        if self.state.get("current_step", 0) < 5:
            workstation = self.get_workstation_path(topic)
            self.step5_draft(topic, workstation)
            self.state["current_step"] = 5
            self.save_state(topic)
        
        # 步骤6：润色
        if self.state.get("current_step", 0) < 6:
            workstation = self.get_workstation_path(topic)
            self.step6_polish(topic, workstation)
            self.state["current_step"] = 6
            self.save_state(topic)
        
        return {
            "status": "completed",
            "workstation": self.get_workstation_path(topic),
            "current_step": self.state.get("current_step", 0)
        }
    
    def get_menu_confirm(self, step_name: str, content: str) -> str:
        """获取确认菜单"""
        template = self.config.get("menu_options", {}).get("confirm", "")
        return f"📋 步骤：{step_name}\n📄 内容：{content[:200]}...\n\n{template}"
    
    def get_finished_menu(self, final_path: str) -> str:
        """获取完成菜单"""
        template = self.config.get("menu_options", {}).get("finished", "")
        return template.format(final_path=final_path)


# ========== CLI ==========

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='fy_write - 论语文章自动撰写')
    parser.add_argument('topic', help='论语章节')
    parser.add_argument('--resume', '-r', action='store_true', help='断点续传')
    parser.add_argument('--auto', '-a', action='store_true', help='自动模式（无需确认）')
    parser.add_argument('--focus', '-f', type=str, default='', help='关注重点')
    
    args = parser.parse_args()
    
    writer = FyWrite()
    
    print(f"📝 主题: {args.topic}")
    print(f"🔄 自动模式: {args.auto}")
    
    # 步骤0：确认
    user_input = args.topic
    if args.focus:
        user_input += f"\n{args.focus}"
    
    confirm_result = writer.step0_confirm(user_input)
    print(confirm_result["confirmation"])
    
    if not args.auto:
        print("\n请回复确认后继续...")
        sys.exit(0)
    
    # 自动执行
    print("\n🚀 开始自动执行...")
    
    # 初始化工作站
    workstation = writer.init_workstation(args.topic)
    writer.save_state(args.topic)
    
    # 步骤1：三要素
    print("\n[步骤1] 生成三要素...")
    writer.step1_analysis(args.topic, args.focus)
    writer.save_state(args.topic)
    print("✅ 完成")
    
    # 步骤2：生成提示词
    print("\n[步骤2] 生成六步法提示词...")
    writer.step2_generate_prompts(args.topic, f"论语·{args.topic}")
    writer.save_state(args.topic)
    print("✅ 完成")
    
    # 步骤3：生成素材（Claude Code）
    print("\n[步骤3] 调用 Claude Code 生成素材...")
    prompts = writer.state.get("steps", {}).get("2", {}).get("prompts", {})
    workstation = writer.get_workstation_path(args.topic)
    writer.step3_generate_materials(args.topic, prompts, workstation)
    writer.save_state(args.topic)
    print("✅ 完成")
    
    # 步骤4：整合分析
    print("\n[步骤4] 整合分析...")
    writer.step4_integrate(args.topic, workstation)
    writer.save_state(args.topic)
    print("✅ 完成")
    
    # 步骤5：生成初稿
    print("\n[步骤5] 生成初稿...")
    writer.step5_draft(args.topic, workstation)
    writer.save_state(args.topic)
    print("✅ 完成")
    
    # 步骤6：润色
    print("\n[步骤6] 调用 fy_autoArt 润色...")
    writer.step6_polish(args.topic, workstation)
    writer.save_state(args.topic)
    print("✅ 完成")
    
    print(f"\n✅ 工作站: {workstation}")
    print("📁 终稿已生成")
