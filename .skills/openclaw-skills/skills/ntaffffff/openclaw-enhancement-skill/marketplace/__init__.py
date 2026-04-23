#!/usr/bin/env python3
"""
插件市场模块

插件注册、发现、安装、评分
"""

import json
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import urllib.request
import urllib.parse

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


@dataclass
class Plugin:
    """插件"""
    id: str
    name: str
    description: str
    version: str
    author: str
    repository: str
    tags: List[str] = field(default_factory=list)
    stars: int = 0
    downloads: int = 0
    installed: bool = False
    installed_version: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PluginManifest:
    """插件清单"""
    name: str
    version: str
    description: str
    author: str
    entry: str
    dependencies: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)


class PluginRegistry:
    """插件注册表"""
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path.home() / ".openclaw" / "plugins"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.plugins: Dict[str, Plugin] = {}
        self.local_plugins: Dict[str, Path] = {}  # name -> path
        self._load_local_plugins()
    
    def _load_local_plugins(self):
        """加载本地插件"""
        # 从配置文件加载已安装插件
        index_file = self.storage_path / "installed.json"
        if index_file.exists():
            try:
                data = json.loads(index_file.read_text())
                for plugin_data in data.get("plugins", []):
                    plugin = Plugin(**plugin_data)
                    self.plugins[plugin.id] = plugin
            except Exception:
                pass
    
    def _save_index(self):
        """保存索引"""
        data = {
            "plugins": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "version": p.version,
                    "author": p.author,
                    "repository": p.repository,
                    "tags": p.tags,
                    "stars": p.stars,
                    "downloads": p.downloads,
                    "installed": p.installed,
                    "installed_version": p.installed_version,
                    "created_at": p.created_at.isoformat(),
                    "updated_at": p.updated_at.isoformat()
                }
                for p in self.plugins.values()
            ]
        }
        index_file = self.storage_path / "installed.json"
        index_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    
    def register_plugin(self, manifest: PluginManifest, path: Path) -> str:
        """注册本地插件"""
        plugin_id = hashlib.md5(manifest.name.encode()).hexdigest()[:12]
        
        plugin = Plugin(
            id=plugin_id,
            name=manifest.name,
            description=manifest.description,
            version=manifest.version,
            author=manifest.author,
            repository="",
            installed=True,
            installed_version=manifest.version
        )
        
        self.plugins[plugin.id] = plugin
        self.local_plugins[manifest.name] = path
        self._save_index()
        
        print(f"{Fore.GREEN}✓ 已注册插件: {manifest.name} v{manifest.version}{Fore.RESET}")
        return plugin_id
    
    def install_plugin(self, plugin_id: str) -> bool:
        """安装插件（从市场）"""
        # 简化实现：实际应该从远程下载
        print(f"{Fore.CYAN}正在安装插件: {plugin_id}{Fore.RESET}")
        return True
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            self._save_index()
            return True
        return False
    
    def list_plugins(self, installed_only: bool = False) -> List[Plugin]:
        """列出插件"""
        plugins = list(self.plugins.values())
        if installed_only:
            plugins = [p for p in plugins if p.installed]
        return sorted(plugins, key=lambda p: p.name)
    
    def search_plugins(self, query: str) -> List[Plugin]:
        """搜索插件"""
        query = query.lower()
        results = []
        
        for plugin in self.plugins.values():
            if (query in plugin.name.lower() or 
                query in plugin.description.lower() or
                any(query in tag.lower() for tag in plugin.tags)):
                results.append(plugin)
        
        return results
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """获取插件"""
        return self.plugins.get(plugin_id)
    
    def get_plugin_by_name(self, name: str) -> Optional[Plugin]:
        """通过名称获取插件"""
        for plugin in self.plugins.values():
            if plugin.name == name:
                return plugin
        return None


class PluginMarketplace:
    """插件市场（模拟）"""
    
    def __init__(self):
        self._mock_plugins = self._create_mock_plugins()
    
    def _create_mock_plugins(self) -> Dict[str, Plugin]:
        """创建模拟插件"""
        return {
            "github-integration": Plugin(
                id="gh-001",
                name="github-integration",
                description="GitHub 集成 - 提交、PR、Issue 管理",
                version="1.0.0",
                author="openclaw",
                repository="https://github.com/openclaw/github-integration",
                tags=["github", "git", "integration"],
                stars=128,
                downloads=3500
            ),
            "docker-helper": Plugin(
                id="dh-001",
                name="docker-helper",
                description="Docker 辅助工具 - 容器管理、镜像构建",
                version="1.2.0",
                author="openclaw",
                repository="https://github.com/openclaw/docker-helper",
                tags=["docker", "containers", "devops"],
                stars=89,
                downloads=2100
            ),
            "database-tools": Plugin(
                id="db-001",
                name="database-tools",
                description="数据库工具 - SQL 查询、数据可视化",
                version="2.0.0",
                author="openclaw",
                repository="https://github.com/openclaw/database-tools",
                tags=["database", "sql", "tools"],
                stars=156,
                downloads=4200
            )
        }
    
    async def search(self, query: str) -> List[Plugin]:
        """搜索市场插件"""
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        query = query.lower()
        results = []
        
        for plugin in self._mock_plugins.values():
            if (query in plugin.name.lower() or 
                query in plugin.description.lower() or
                any(query in tag.lower() for tag in plugin.tags)):
                results.append(plugin)
        
        return results
    
    async def get_plugin_details(self, plugin_id: str) -> Optional[Plugin]:
        """获取插件详情"""
        await asyncio.sleep(0.1)
        return self._mock_plugins.get(plugin_id)
    
    async def get_trending(self, days: int = 7) -> List[Plugin]:
        """获取热门插件"""
        await asyncio.sleep(0.1)
        return sorted(
            self._mock_plugins.values(),
            key=lambda p: p.downloads,
            reverse=True
        )[:5]


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 插件市场示例 ==={Fore.RESET}\n")
    
    # 创建注册表
    registry = PluginRegistry()
    
    # 搜索市场
    print("1. 搜索插件:")
    marketplace = PluginMarketplace()
    results = await marketplace.search("git")
    for p in results:
        print(f"   - {p.name}: {p.description}")
        print(f"     ⭐ {p.stars} | ↓ {p.downloads}")
    
    # 安装插件
    print("\n2. 安装插件:")
    for p in results[:1]:
        registry.install_plugin(p.id)
        print(f"   ✓ 已安装: {p.name}")
    
    # 列出已安装
    print("\n3. 已安装插件:")
    for p in registry.list_plugins(installed_only=True):
        print(f"   - {p.name} v{p.installed_version}")
    
    print(f"\n{Fore.GREEN}✓ 插件市场示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())