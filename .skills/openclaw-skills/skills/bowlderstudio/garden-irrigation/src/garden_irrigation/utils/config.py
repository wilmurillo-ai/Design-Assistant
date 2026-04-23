from __future__ import annotations

from pathlib import Path
import json


class Config:
    def __init__(self, root: Path):
        self.root = root
        self.config_dir = root / 'config'
        self.system = self._load_json('system.json')
        self.zones = self._load_json('zones.json').get('zones', [])

    def _load_json(self, name: str):
        with open(self.config_dir / name, 'r', encoding='utf-8') as f:
            return json.load(f)
