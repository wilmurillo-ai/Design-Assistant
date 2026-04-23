#!/usr/bin/env python3
"""
数据共享器 - 数据飞轮第三层

实现技能数据的安全共享
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class DataSharer:
    """
    技能数据共享器
    
    安全地共享技能进化经验
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.shared_dir = self.data_dir / "shared"
        self._shared_patterns: Dict[str, Any] = {}
    
    def initialize(self):
        """初始化共享器"""
        self.shared_dir.mkdir(parents=True, exist_ok=True)
    
    def share_pattern(self, pattern: Dict, target_skills: List[str]) -> Dict:
        """
        共享进化模式
        
        Args:
            pattern: 进化模式
            target_skills: 目标技能列表
            
        Returns:
            Dict: 共享结果
        """
        pattern_id = f"pattern_{int(datetime.now().timestamp())}"
        
        shared = {
            "id": pattern_id,
            "pattern": pattern,
            "shared_with": target_skills,
            "timestamp": datetime.now().isoformat(),
        }
        
        self._shared_patterns[pattern_id] = shared
        return shared
    
    def get_shared_patterns(self, skill_id: str = None) -> List[Dict]:
        """获取共享的模式"""
        patterns = list(self._shared_patterns.values())
        if skill_id:
            patterns = [p for p in patterns if skill_id in p.get("shared_with", [])]
        return patterns
