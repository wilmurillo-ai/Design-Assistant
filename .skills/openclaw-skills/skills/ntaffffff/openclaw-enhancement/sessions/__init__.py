#!/usr/bin/env python3
"""
多会话管理模块

同时管理多个项目/会话的上下文
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import copy

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


@dataclass
class Session:
    """会话"""
    id: str
    name: str
    project_path: Path
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """添加消息"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        self.last_active = datetime.now()
    
    def get_messages(self, limit: int = None) -> List[Dict]:
        """获取消息"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def clear_messages(self):
        """清空消息"""
        self.messages = []


class SessionManager:
    """会话管理器"""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path.home() / ".openclaw" / "sessions"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, Session] = {}
        self.active_session_id: Optional[str] = None
        self._load_sessions()
    
    def _load_sessions(self):
        """加载会话"""
        # 从文件加载（简化实现）
        index_file = self.storage_path / "index.json"
        if index_file.exists():
            try:
                data = json.loads(index_file.read_text())
                for sess_data in data.get("sessions", []):
                    session = Session(
                        id=sess_data["id"],
                        name=sess_data["name"],
                        project_path=Path(sess_data["project_path"]),
                        created_at=datetime.fromisoformat(sess_data["created_at"]),
                        last_active=datetime.fromisoformat(sess_data["last_active"]),
                        is_active=sess_data.get("is_active", True)
                    )
                    self.sessions[session.id] = session
            except Exception as e:
                print(f"{Fore.YELLOW}加载会话失败: {e}{Fore.RESET}")
    
    def _save_index(self):
        """保存索引"""
        data = {
            "sessions": [
                {
                    "id": s.id,
                    "name": s.name,
                    "project_path": str(s.project_path),
                    "created_at": s.created_at.isoformat(),
                    "last_active": s.last_active.isoformat(),
                    "is_active": s.is_active
                }
                for s in self.sessions.values()
            ]
        }
        index_file = self.storage_path / "index.json"
        index_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def create_session(self, name: str, project_path: Path = None) -> Session:
        """创建会话"""
        session = Session(
            id=str(uuid.uuid4()),
            name=name,
            project_path=project_path or Path.cwd()
        )
        self.sessions[session.id] = session
        self.active_session_id = session.id
        self._save_index()
        
        print(f"{Fore.GREEN}✓ 创建会话: {name} (ID: {session.id[:8]}...){Fore.RESET}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)
    
    def get_active_session(self) -> Optional[Session]:
        """获取当前活跃会话"""
        if self.active_session_id:
            return self.sessions.get(self.active_session_id)
        
        # 返回最近活跃的
        if self.sessions:
            recent = max(self.sessions.values(), key=lambda s: s.last_active)
            return recent
        
        return None
    
    def set_active_session(self, session_id: str) -> bool:
        """设置活跃会话"""
        if session_id in self.sessions:
            self.active_session_id = session_id
            self.sessions[session_id].last_active = datetime.now()
            self._save_index()
            return True
        return False
    
    def list_sessions(self, active_only: bool = False) -> List[Session]:
        """列出会话"""
        sessions = list(self.sessions.values())
        
        if active_only:
            sessions = [s for s in sessions if s.is_active]
        
        # 按最后活跃时间排序
        sessions.sort(key=lambda s: s.last_active, reverse=True)
        return sessions
    
    def switch_session(self, session_id: str) -> bool:
        """切换会话"""
        return self.set_active_session(session_id)
    
    def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            self._save_index()
            
            if self.active_session_id == session_id:
                # 切换到其他活跃会话
                active = self.list_sessions(active_only=True)
                if active:
                    self.active_session_id = active[0].id
                else:
                    self.active_session_id = None
            
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            if self.active_session_id == session_id:
                self.active_session_id = None
            
            self._save_index()
            return True
        return False
    
    def save_session(self, session_id: str):
        """保存会话到文件"""
        session = self.sessions.get(session_id)
        if not session:
            return
        
        # 保存消息
        session_file = self.storage_path / f"{session_id}.json"
        data = {
            "id": session.id,
            "name": session.name,
            "project_path": str(session.project_path),
            "created_at": session.created_at.isoformat(),
            "last_active": session.last_active.isoformat(),
            "messages": session.messages,
            "context": session.context,
            "metadata": session.metadata
        }
        session_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def load_session(self, session_id: str) -> bool:
        """从文件加载会话"""
        session_file = self.storage_path / f"{session_id}.json"
        if not session_file.exists():
            return False
        
        try:
            data = json.loads(session_file.read_text())
            session = Session(
                id=data["id"],
                name=data["name"],
                project_path=Path(data["project_path"]),
                created_at=datetime.fromisoformat(data["created_at"]),
                last_active=datetime.fromisoformat(data["last_active"]),
                messages=data.get("messages", []),
                context=data.get("context", {}),
                metadata=data.get("metadata", {})
            )
            self.sessions[session.id] = session
            return True
        except Exception as e:
            print(f"{Fore.RED}✗ 加载会话失败: {e}{Fore.RESET}")
            return False
    
    def cleanup_old_sessions(self, days: int = 30):
        """清理旧会话"""
        cutoff = datetime.now() - timedelta(days=days)
        to_delete = []
        
        for session in self.sessions.values():
            if session.last_active < cutoff:
                to_delete.append(session.id)
        
        for session_id in to_delete:
            self.delete_session(session_id)
        
        if to_delete:
            print(f"{Fore.CYAN}清理了 {len(to_delete)} 个旧会话{Fore.RESET}")
        
        return len(to_delete)


# ============ 使用示例 ============

def example():
    """示例"""
    print(f"{Fore.CYAN}=== 多会话管理示例 ==={Fore.RESET}\n")
    
    # 创建管理器
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    manager = SessionManager(temp_dir)
    
    # 1. 创建会话
    print("1. 创建会话:")
    session1 = manager.create_session("Python项目", Path("/home/user/project1"))
    session2 = manager.create_session("JavaScript项目", Path("/home/user/project2"))
    
    # 2. 列出会话
    print("\n2. 列出所有会话:")
    for s in manager.list_sessions():
        active_marker = " ✓" if s.id == manager.active_session_id else ""
        print(f"   - {s.name} (ID: {s.id[:8]}...){active_marker}")
    
    # 3. 添加消息
    print("\n3. 添加消息:")
    session = manager.get_active_session()
    session.add_message("user", "你好")
    session.add_message("assistant", "你好！有什么可以帮你的？")
    print(f"   当前会话消息数: {len(session.messages)}")
    
    # 4. 切换会话
    print("\n4. 切换会话:")
    manager.switch_session(session1.id)
    print(f"   切换到: {manager.get_active_session().name}")
    
    # 5. 列出消息
    print("\n5. 获取最近消息:")
    for msg in session.get_messages(2):
        print(f"   {msg['role']}: {msg['content'][:30]}...")
    
    # 6. 清理
    print("\n6. 清理测试:")
    manager.cleanup_old_sessions(0)
    
    # 清理临时目录
    import shutil
    shutil.rmtree(temp_dir)
    
    print(f"\n{Fore.GREEN}✓ 多会话管理示例完成!{Fore.RESET}")


if __name__ == "__main__":
    example()