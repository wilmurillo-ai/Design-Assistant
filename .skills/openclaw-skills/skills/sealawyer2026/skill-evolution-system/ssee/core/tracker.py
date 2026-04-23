#!/usr/bin/env python3
"""
技能追踪器 - 记录技能使用数据
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class SkillTracker:
    """技能使用数据追踪器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.data_file = self.data_dir / "tracking_data.json"
        self._data: Dict[str, List[Dict]] = {}
    
    def initialize(self):
        """初始化追踪器"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_data()
    
    def track(self, skill_id: str, metrics: Dict[str, Any]) -> Dict:
        """记录技能使用"""
        if skill_id not in self._data:
            self._data[skill_id] = []
        
        record = {
            "id": f"{skill_id}_{int(datetime.now().timestamp() * 1000)}",
            "skill": skill_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }
        
        self._data[skill_id].append(record)
        self._save_data()
        
        return {"status": "success", "record_id": record["id"]}
    
    def get_data(self, skill_id: str) -> List[Dict]:
        """获取技能追踪数据"""
        return self._data.get(skill_id, [])
    
    def _load_data(self):
        """加载数据"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self._data = json.load(f)
    
    def _save_data(self):
        """保存数据"""
        with open(self.data_file, 'w') as f:
            json.dump(self._data, f, indent=2)
