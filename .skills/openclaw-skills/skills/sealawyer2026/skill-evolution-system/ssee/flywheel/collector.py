#!/usr/bin/env python3
"""
数据收集器 - 数据飞轮第一层

收集全球技能使用数据
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class DataCollector:
    """
    技能数据收集器
    
    负责从各平台收集技能使用数据
    """
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.raw_data_file = self.data_dir / "raw_data.json"
        self._data: List[Dict] = []
    
    def initialize(self):
        """初始化收集器"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_data()
    
    def collect(self, source: str, data: Dict) -> bool:
        """
        收集数据
        
        Args:
            source: 数据来源（平台名称）
            data: 数据内容
            
        Returns:
            bool: 收集是否成功
        """
        record = {
            "id": f"record_{int(datetime.now().timestamp() * 1000)}",
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        
        self._data.append(record)
        self._save_data()
        return True
    
    def get_data(self, source: str = None, limit: int = 100) -> List[Dict]:
        """获取收集的数据"""
        if source:
            return [d for d in self._data if d["source"] == source][:limit]
        return self._data[-limit:]
    
    def _load_data(self):
        """加载数据"""
        if self.raw_data_file.exists():
            with open(self.raw_data_file, 'r') as f:
                self._data = json.load(f)
    
    def _save_data(self):
        """保存数据"""
        with open(self.raw_data_file, 'w') as f:
            json.dump(self._data, f, indent=2)
