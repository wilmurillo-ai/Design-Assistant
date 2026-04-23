#!/usr/bin/env python3
"""
技能自动更新器
基于进化计划自动执行技能更新
"""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class SkillAutoUpdater:
    """自动更新技能内容"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/skills/.evolution-data")
        self.data_dir = Path(data_dir)
        self.plan_file = self.data_dir / "evolution_plans.json"
        self.skills_dir = Path(os.path.expanduser("~/.openclaw/workspace/skills"))
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def update_skill(self, skill_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """执行技能更新"""
        skill_path = self.skills_dir / skill_name
        if not skill_path.exists():
            return {"error": f"技能 '{skill_name}' 不存在"}
        
        plan = self._load_plan(skill_name)
        if "error" in plan:
            return plan
        
        result = {
            "skill_name": skill_name,
            "dry_run": dry_run,
            "started_at": datetime.now().isoformat(),
            "actions": [],
            "warnings": [],
            "completed_at": None
        }
        
        # 创建备份
        if not dry_run:
            backup_path = self._create_backup(skill_name)
            result["actions"].append(f"创建备份: {backup_path}")
        
        # 执行各阶段更新
        for phase in plan.get("phases", []):
            phase_result = self._execute_phase(skill_path, phase, dry_run)
            result["actions"].extend(phase_result.get("actions", []))
            result["warnings"].extend(phase_result.get("warnings", []))
        
        # 更新版本号
        if not dry_run:
            self._update_version(skill_path, plan.get("version", "1.0.1"))
            result["actions"].append(f"更新版本号至 {plan.get('version', '1.0.1')}")
        
        result["completed_at"] = datetime.now().isoformat()
        
        return result
    
    def batch_update(self, skill_names: List[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """批量更新技能"""
        if skill_names is None:
            plans = self._load_json(self.plan_file)
            skill_names = list(plans.keys())
        
        results = {
            "dry_run": dry_run,
            "started_at": datetime.now().isoformat(),
            "skills_processed": [],
            "successful": [],
            "failed": [],
            "details": {}
        }
        
        for skill_name in skill_names:
            result = self.update_skill(skill_name, dry_run)
            results["skills_processed"].append(skill_name)
            results["details"][skill_name] = result
            
            if "error" in result:
                results["failed"].append(skill_name)
            else:
                results["successful"].append(skill_name)
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    def _execute_phase(self, skill_path: Path, phase: Dict, dry_run: bool) -> Dict[str, Any]:
        """执行单个进化阶段"""
        result = {
            "phase": phase.get("name"),
            "actions": [],
            "warnings": []
        }
        
        for task in phase.get("tasks", []):
            task_result = self._execute_task(skill_path, task, dry_run)
            result["actions"].extend(task_result.get("actions", []))
            result["warnings"].extend(task_result.get("warnings", []))
        
        return result
    
    def _execute_task(self, skill_path: Path, task: Dict, dry_run: bool) -> Dict[str, Any]:
        """执行单个任务"""
        result = {
            "actions": [],
            "warnings": []
        }
        
        description = task.get("description", "")
        category = task.get("category", "")
        
        # 根据任务类型执行相应操作
        if "修复" in description or category == "bugfix":
            if not dry_run:
                # 记录需要修复的问题
                self._log_improvement(skill_path, "bugfix", description)
            result["actions"].append(f"[Bugfix] {description}")
        
        elif "优化" in description or category == "性能":
            if not dry_run:
                self._add_optimization_note(skill_path, description)
            result["actions"].append(f"[优化] {description}")
        
        elif "文档" in description or "SKILL.md" in description:
            if not dry_run:
                self._update_documentation(skill_path)
            result["actions"].append(f"[文档] 更新文档")
        
        elif "功能" in description or category == "功能增强":
            if not dry_run:
                self._log_improvement(skill_path, "feature", description)
            result["actions"].append(f"[功能] {description}")
        
        else:
            result["actions"].append(f"[其他] {description}")
        
        return result
    
    def _create_backup(self, skill_name: str) -> Path:
        """创建技能备份"""
        skill_path = self.skills_dir / skill_name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{skill_name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copytree(skill_path, backup_path)
        return backup_path
    
    def _update_version(self, skill_path: Path, new_version: str):
        """更新技能版本号"""
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text(encoding='utf-8')
        
        # 尝试更新版本号
        if "version:" in content:
            content = re.sub(
                r'version:\s*[\d.]+',
                f'version: {new_version}',
                content
            )
        else:
            # 在frontmatter后添加版本
            content = content.replace(
                "---\n\n#",
                f"---\nversion: {new_version}\n\n#"
            )
        
        skill_md.write_text(content, encoding='utf-8')
    
    def _log_improvement(self, skill_path: Path, improvement_type: str, description: str):
        """记录改进日志"""
        log_file = skill_path / "IMPROVEMENTS.md"
        
        entry = f"\n## {datetime.now().strftime('%Y-%m-%d')}\n"
        entry += f"- **类型**: {improvement_type}\n"
        entry += f"- **描述**: {description}\n"
        
        if log_file.exists():
            content = log_file.read_text(encoding='utf-8')
            content += entry
        else:
            content = f"# 改进日志\n{entry}"
        
        log_file.write_text(content, encoding='utf-8')
    
    def _add_optimization_note(self, skill_path: Path, note: str):
        """添加优化备注"""
        # 可以添加到某个专门的优化记录文件
        pass
    
    def _update_documentation(self, skill_path: Path):
        """更新文档"""
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return
        
        content = skill_md.read_text(encoding='utf-8')
        
        # 添加最后更新时间
        update_line = f"\n<!-- 最后更新: {datetime.now().strftime('%Y-%m-%d')} -->\n"
        
        if "<!-- 最后更新:" not in content:
            content += update_line
        else:
            content = re.sub(
                r'<!-- 最后更新: [\d-]+ -->',
                update_line.strip(),
                content
            )
        
        skill_md.write_text(content, encoding='utf-8')
    
    def rollback(self, skill_name: str, backup_timestamp: str = None) -> Dict[str, Any]:
        """回滚到之前的版本"""
        skill_path = self.skills_dir / skill_name
        
        if backup_timestamp:
            backup_name = f"{skill_name}_{backup_timestamp}"
        else:
            # 找到最新的备份
            backups = [d for d in self.backup_dir.iterdir() if d.name.startswith(skill_name)]
            if not backups:
                return {"error": f"未找到 '{skill_name}' 的备份"}
            backup_name = sorted(backups)[-1].name
        
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            return {"error": f"备份不存在: {backup_path}"}
        
        # 删除当前版本并恢复备份
        if skill_path.exists():
            shutil.rmtree(skill_path)
        
        shutil.copytree(backup_path, skill_path)
        
        return {
            "success": True,
            "restored_from": str(backup_path),
            "skill_name": skill_name
        }
    
    def _load_plan(self, skill_name: str) -> Dict:
        """加载进化计划"""
        plans = self._load_json(self.plan_file)
        return plans.get(skill_name, {"error": "未找到进化计划"})
    
    def _load_json(self, file_path: Path) -> Dict:
        """加载JSON文件"""
        if not file_path.exists():
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


if __name__ == "__main__":
    import sys
    
    updater = SkillAutoUpdater()
    
    if len(sys.argv) < 2:
        print("用法: python auto_update_skill.py <command> [args]")
        print("命令: update <skill> [--dry-run], batch [--dry-run], rollback <skill> [timestamp]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    dry_run = "--dry-run" in sys.argv
    
    if cmd == "update" and len(sys.argv) >= 3:
        skill = sys.argv[2]
        result = updater.update_skill(skill, dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "batch":
        skills = None
        if len(sys.argv) > 2 and not sys.argv[2].startswith("--"):
            skills = [s for s in sys.argv[2:] if not s.startswith("--")]
        result = updater.batch_update(skills, dry_run)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "rollback" and len(sys.argv) >= 3:
        skill = sys.argv[2]
        timestamp = sys.argv[3] if len(sys.argv) > 3 else None
        result = updater.rollback(skill, timestamp)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"未知命令: {cmd}")
