#!/usr/bin/env python3
"""
分层记忆系统

短期记忆 → 中期压缩 → 长期持久化
参考 Claude Code 的记忆架构设计
"""

from __future__ import annotations

import json
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque

if TYPE_CHECKING:
    from datetime import datetime

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = MAGENTA = ""


class MemoryLevel(Enum):
    """记忆层级"""
    SHORT = "short"      # 短期（内存）
    MEDIUM = "medium"    # 中期（压缩）
    LONG = "long"        # 长期（持久化）


@dataclass
class MemoryItem:
    """记忆条目"""
    id: str
    content: str
    level: MemoryLevel
    importance: float = 0.5  # 0-10
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def access(self) -> None:
        """访问记录"""
        self.accessed_at = datetime.now()
        self.access_count += 1
    
    def promote(self) -> bool:
        """晋升到更高层级"""
        if self.level == MemoryLevel.SHORT:
            self.level = MemoryLevel.MEDIUM
            return True
        elif self.level == MemoryLevel.MEDIUM:
            self.level = MemoryLevel.LONG
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """序列化"""
        return {
            "id": self.id,
            "content": self.content,
            "level": self.level.value,
            "importance": self.importance,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        """反序列化"""
        data = data.copy()
        data["level"] = MemoryLevel(data["level"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["accessed_at"] = datetime.fromisoformat(data["accessed_at"])
        return cls(**data)


class ShortTermMemory:
    """短期记忆（内存）"""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._items: deque = deque(maxlen=max_size)
        self._index: Dict[str, int] = {}  # id -> position
    
    def add(self, item: MemoryItem) -> None:
        """添加记忆"""
        self._items.append(item)
        self._index[item.id] = len(self._items) - 1
    
    def get(self, item_id: str) -> Optional[MemoryItem]:
        """获取记忆"""
        for item in reversed(self._items):
            if item.id == item_id:
                item.access()
                return item
        return None
    
    def get_recent(self, limit: int = 10) -> List[MemoryItem]:
        """获取最近记忆"""
        return list(self._items)[-limit:]
    
    def search(self, query: str) -> List[MemoryItem]:
        """搜索"""
        query = query.lower()
        return [m for m in self._items if query in m.content.lower()]
    
    def get_all(self) -> List[MemoryItem]:
        """获取所有"""
        return list(self._items)
    
    def clear(self) -> None:
        """清空"""
        self._items.clear()
        self._index.clear()
    
    def __len__(self) -> int:
        return len(self._items)


class MediumTermMemory:
    """中期记忆（压缩）"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._index_file = storage_path / "medium_index.json"
        self._items: Dict[str, MemoryItem] = {}
        self._load_index()
    
    def _load_index(self) -> None:
        """加载索引"""
        if self._index_file.exists():
            try:
                data = json.loads(self._index_file.read_text())
                for item_data in data.get("items", []):
                    item = MemoryItem.from_dict(item_data)
                    self._items[item.id] = item
            except Exception:
                pass
    
    def _save_index(self) -> None:
        """保存索引"""
        data = {"items": [item.to_dict() for item in self._items.values()]}
        self._index_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def add(self, item: MemoryItem) -> None:
        """添加记忆"""
        item.level = MemoryLevel.MEDIUM
        self._items[item.id] = item
        self._save_index()
    
    def get(self, item_id: str) -> Optional[MemoryItem]:
        """获取记忆"""
        item = self._items.get(item_id)
        if item:
            item.access()
            self._save_index()
        return item
    
    def search(self, query: str) -> List[MemoryItem]:
        """搜索"""
        query = query.lower()
        return [m for m in self._items.values() if query in m.content.lower()]
    
    def get_all(self) -> List[MemoryItem]:
        """获取所有"""
        return list(self._items.values())
    
    def remove(self, item_id: str) -> bool:
        """删除"""
        if item_id in self._items:
            del self._items[item_id]
            self._save_index()
            return True
        return False
    
    def __len__(self) -> int:
        return len(self._items)


class LongTermMemory:
    """长期记忆（持久化）"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._memories_dir = storage_path / "memories"
        self._memories_dir.mkdir(exist_ok=True)
        self._index_file = storage_path / "long_index.json"
        self._items: Dict[str, MemoryItem] = {}
        self._load_index()
    
    def _load_index(self) -> None:
        """加载索引"""
        if self._index_file.exists():
            try:
                data = json.loads(self._index_file.read_text())
                for item_data in data.get("items", []):
                    item = MemoryItem.from_dict(item_data)
                    self._items[item.id] = item
            except Exception:
                pass
    
    def _save_index(self) -> None:
        """保存索引"""
        data = {"items": [item.to_dict() for item in self._items.values()]}
        self._index_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def add(self, item: MemoryItem) -> None:
        """添加记忆"""
        item.level = MemoryLevel.LONG
        
        # 保存内容到单独文件
        memory_file = self._memories_dir / f"{item.id}.json"
        memory_file.write_text(json.dumps(item.to_dict(), ensure_ascii=False, indent=2))
        
        self._items[item.id] = item
        self._save_index()
    
    def get(self, item_id: str) -> Optional[MemoryItem]:
        """获取记忆"""
        item = self._items.get(item_id)
        if item:
            item.access()
            self._save_index()
        return item
    
    def search(self, query: str) -> List[MemoryItem]:
        """搜索"""
        query = query.lower()
        return [m for m in self._items.values() if query in m.content.lower()]
    
    def get_all(self) -> List[MemoryItem]:
        """获取所有"""
        return list(self._items.values())
    
    def remove(self, item_id: str) -> bool:
        """删除"""
        memory_file = self._memories_dir / f"{item_id}.json"
        if memory_file.exists():
            memory_file.unlink()
        
        if item_id in self._items:
            del self._items[item_id]
            self._save_index()
            return True
        return False
    
    def __len__(self) -> int:
        return len(self._items)


class LayeredMemory:
    """分层记忆系统"""
    
    def __init__(
        self,
        storage_path: Path = None,
        short_size: int = 100,
        auto_promote: bool = True,
        promote_threshold: int = 5
    ):
        self.storage_path = storage_path or Path.home() / ".openclaw" / "memory"
        if isinstance(self.storage_path, str):
            self.storage_path = Path(self.storage_path)
        
        # 初始化各层记忆
        self.short = ShortTermMemory(max_size=short_size)
        self.medium = MediumTermMemory(self.storage_path / "medium")
        self.long = LongTermMemory(self.storage_path / "long")
        
        # 配置
        self.auto_promote = auto_promote
        self.promote_threshold = promote_threshold
        
        # 钩子
        self._hooks: Dict[str, List[Callable]] = {
            "on_add": [],
            "on_access": [],
            "on_promote": [],
            "on_forget": []
        }
    
    def add_hook(self, event: str, callback: Callable) -> None:
        """添加钩子"""
        if event in self._hooks:
            self._hooks[event].append(callback)
    
    def _emit(self, event: str, *args, **kwargs) -> None:
        """触发钩子"""
        for hook in self._hooks.get(event, []):
            try:
                hook(*args, **kwargs)
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ Hook 失败: {e}{Fore.RESET}")
    
    async def add(
        self,
        content: str,
        importance: float = 0.5,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
        level: MemoryLevel = MemoryLevel.SHORT
    ) -> MemoryItem:
        """添加记忆"""
        import uuid
        
        item = MemoryItem(
            id=str(uuid.uuid4()),
            content=content,
            level=level,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # 根据层级存储
        if level == MemoryLevel.SHORT:
            self.short.add(item)
        elif level == MemoryLevel.MEDIUM:
            self.medium.add(item)
        else:
            self.long.add(item)
        
        self._emit("on_add", item)
        return item
    
    async def get(self, item_id: str, min_level: MemoryLevel = None) -> Optional[MemoryItem]:
        """获取记忆"""
        # 从高层开始查找
        for level in [MemoryLevel.LONG, MemoryLevel.MEDIUM, MemoryLevel.SHORT]:
            if min_level and level.value < min_level.value:
                continue
            
            if level == MemoryLevel.SHORT:
                item = self.short.get(item_id)
            elif level == MemoryLevel.MEDIUM:
                item = self.medium.get(item_id)
            else:
                item = self.long.get(item_id)
            
            if item:
                self._emit("on_access", item)
                return item
        
        return None
    
    async def search(self, query: str, levels: List[MemoryLevel] = None) -> List[MemoryItem]:
        """搜索记忆"""
        levels = levels or [MemoryLevel.SHORT, MemoryLevel.MEDIUM, MemoryLevel.LONG]
        results = []
        
        for level in levels:
            if level == MemoryLevel.SHORT:
                results.extend(self.short.search(query))
            elif level == MemoryLevel.MEDIUM:
                results.extend(self.medium.search(query))
            else:
                results.extend(self.long.search(query))
        
        # 按重要性和访问时间排序
        results.sort(key=lambda m: (m.importance, m.accessed_at), reverse=True)
        return results
    
    async def get_recent(self, limit: int = 10, level: MemoryLevel = None) -> List[MemoryItem]:
        """获取最近记忆"""
        if level == MemoryLevel.SHORT or level is None:
            return self.short.get_recent(limit)
        elif level == MemoryLevel.MEDIUM:
            return self.medium.get_all()[-limit:]
        else:
            return self.long.get_all()[-limit:]
    
    async def promote(self, item_id: str) -> bool:
        """晋升记忆"""
        item = await self.get(item_id)
        if not item:
            return False
        
        if item.promote():
            # 从当前层级移除，添加到新层级
            if item.level == MemoryLevel.MEDIUM:
                self.medium.remove(item_id)
                self.long.add(item)
            elif item.level == MemoryLevel.SHORT:
                # 短期直接到长期
                self.short.get(item_id)  # 触发访问
                self.long.add(item)
            
            self._emit("on_promote", item)
            return True
        
        return False
    
    async def auto_maintenance(self) -> Dict[str, int]:
        """自动维护（晋升/遗忘）"""
        stats = {"promoted": 0, "forgotten": 0}
        
        # 检查短期记忆，晋升重要的
        for item in self.short.get_all():
            if item.access_count >= self.promote_threshold or item.importance > 8:
                if await self.promote(item.id):
                    stats["promoted"] += 1
        
        return stats
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "short_count": len(self.short),
            "medium_count": len(self.medium),
            "long_count": len(self.long),
            "total": len(self.short) + len(self.medium) + len(self.long)
        }


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 分层记忆系统示例 ==={Fore.RESET}\n")
    
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    
    # 创建记忆系统
    memory = LayeredMemory(temp_dir, short_size=50)
    
    # 添加记忆
    print("1. 添加记忆:")
    await memory.add("用户叫主人", importance=8, tags=["user", "name"])
    await memory.add("用户喜欢瓦罗兰特", importance=7, tags=["user", "preference"])
    await memory.add("记住这个配置: RTX 4080", importance=9, tags=["config", "hardware"])
    await memory.add("今天的天气真好", importance=3, tags=["chat"])
    
    # 搜索
    print("\n2. 搜索 '用户':")
    results = await memory.search("用户")
    for item in results:
        print(f"   - [{item.level.value}] {item.content[:30]}... (重要度: {item.importance})")
    
    # 获取最近
    print("\n3. 最近记忆:")
    recent = await memory.get_recent(3)
    for item in recent:
        print(f"   - {item.content[:30]}...")
    
    # 统计
    print("\n4. 记忆统计:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 清理
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"\n{Fore.GREEN}✓ 分层记忆系统示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())