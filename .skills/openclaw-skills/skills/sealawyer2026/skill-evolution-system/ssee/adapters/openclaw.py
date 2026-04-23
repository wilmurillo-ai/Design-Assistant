#!/usr/bin/env python3
"""
OpenClaw 平台适配器
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List
from .base import SkillAdapter, AdapterRegistry


class OpenClawAdapter(SkillAdapter):
    """OpenClaw 平台适配器"""
    
    def __init__(self, config: Dict = None):
        super().__init__("openclaw", config)
        self.skills_dir = Path(config.get("skills_dir", "~/.openclaw/workspace/skills")).expanduser()
    
    def connect(self) -> bool:
        """连接到 OpenClaw"""
        try:
            # 检查 openclaw 命令是否可用
            result = subprocess.run(["which", "openclaw"], capture_output=True, text=True)
            if result.returncode == 0:
                self._connected = True
                return True
            return False
        except Exception:
            return False
    
    def get_skill_list(self) -> List[Dict]:
        """获取技能列表"""
        skills = []
        if self.skills_dir.exists():
            for skill_dir in self.skills_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    metadata = self._parse_skill_md(skill_dir / "SKILL.md")
                    skills.append({
                        "id": skill_dir.name,
                        "name": metadata.get("name", skill_dir.name),
                        "version": metadata.get("version", "1.0.0"),
                        "path": str(skill_dir),
                    })
        return skills
    
    def get_skill_metadata(self, skill_id: str) -> Dict:
        """获取技能元数据"""
        skill_path = self.skills_dir / skill_id
        if not skill_path.exists():
            return {"error": "Skill not found"}
        
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            return {"error": "SKILL.md not found"}
        
        return self._parse_skill_md(skill_md)
    
    def track_skill_usage(self, skill_id: str, metrics: Dict) -> Dict:
        """追踪技能使用"""
        # 记录到本地追踪系统
        return {
            "status": "tracked",
            "skill": skill_id,
            "platform": self.platform_name,
            "metrics": metrics,
        }
    
    def update_skill(self, skill_id: str, updates: Dict) -> bool:
        """更新技能"""
        skill_path = self.skills_dir / skill_id
        if not skill_path.exists():
            return False
        
        try:
            # 更新 SKILL.md
            skill_md = skill_path / "SKILL.md"
            if skill_md.exists() and "content" in updates:
                with open(skill_md, 'w') as f:
                    f.write(updates["content"])
            
            # 更新版本号
            if "version" in updates:
                # 这里可以添加版本更新逻辑
                pass
            
            return True
        except Exception as e:
            print(f"更新失败: {e}")
            return False
    
    def _parse_skill_md(self, skill_md: Path) -> Dict:
        """解析 SKILL.md 文件"""
        metadata = {}
        with open(skill_md, 'r') as f:
            content = f.read()
            
        # 解析 frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"').strip("'")
        
        return metadata


# 注册适配器
AdapterRegistry.register("openclaw", OpenClawAdapter)
