#!/usr/bin/env python3
"""
IDE 集成模块

VSCode、Cursor、JetBrains 等 IDE 集成
参考 Claude Code 的 IDE 集成方案
"""

import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


@dataclass
class IDEProject:
    """IDE 项目"""
    name: str
    path: Path
    ide_type: str  # vscode, cursor, jetbrains
    config: Dict[str, Any] = field(default_factory=dict)
    last_opened: datetime = None


@dataclass
class CodeLocation:
    """代码位置"""
    file: str
    line: int
    column: int = 0
    end_line: Optional[int] = None


@dataclass
class Symbol:
    """代码符号（函数、类等）"""
    name: str
    kind: str  # function, class, method, variable
    location: CodeLocation
    signature: Optional[str] = None
    documentation: Optional[str] = None


class IDEIntegration:
    """IDE 集成基类"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
    
    async def open_file(self, file_path: str, line: int = None):
        """打开文件"""
        raise NotImplementedError
    
    async def go_to_definition(self, file_path: str, line: int, column: int):
        """跳转到定义"""
        raise NotImplementedError
    
    async def find_references(self, file_path: str, line: int, column: int):
        """查找引用"""
        raise NotImplementedError
    
    async def get_symbols(self, file_path: str) -> List[Symbol]:
        """获取文件中的符号"""
        raise NotImplementedError
    
    async def run_command(self, command: str, args: List[str] = None):
        """运行 IDE 命令"""
        raise NotImplementedError


class VSCodeIntegration(IDEIntegration):
    """VSCode 集成"""
    
    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.ide_type = "vscode"
    
    async def open_file(self, file_path: str, line: int = None):
        """打开文件"""
        cmd = ["code", file_path]
        if line:
            cmd.extend(["-g", f"{file_path}:{line}"])
        
        await asyncio.create_subprocess_exec(*cmd)
    
    async def go_to_definition(self, file_path: str, line: int, column: int = 0):
        """跳转到定义"""
        # 使用 VSCode 的 go to definition
        cmd = ["code", "--goto", f"{file_path}:{line}:{column}"]
        await asyncio.create_subprocess_exec(*cmd)
    
    async def find_references(self, file_path: str, line: int, column: int):
        """查找引用"""
        # 使用扩展命令
        cmd = ["code", "--extension", "references", file_path, str(line), str(column)]
        await asyncio.create_subprocess_exec(*cmd)
    
    async def get_symbols(self, file_path: str) -> List[Symbol]:
        """获取符号（使用 ctags 或 IDE API）"""
        # 简化：使用 ctags
        symbols = []
        
        try:
            proc = await asyncio.create_subprocess_exec(
                "ctags", "-x", "--c-kinds=f", file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, _ = await proc.communicate()
            
            for line in stdout.decode().splitlines():
                parts = line.split()
                if len(parts) >= 4:
                    symbols.append(Symbol(
                        name=parts[0],
                        kind="function",
                        location=CodeLocation(
                            file=file_path,
                            line=int(parts[2])
                        )
                    ))
        except FileNotFoundError:
            pass
        
        return symbols
    
    async def run_command(self, command: str, args: List[str] = None):
        """运行 VSCode 命令"""
        cmd = ["code", "--command", command]
        if args:
            cmd.extend(args)
        
        await asyncio.create_subprocess_exec(*cmd)


class CursorIntegration(VSCodeIntegration):
    """Cursor IDE 集成（继承 VSCode）"""
    
    def __init__(self, project_path: Path):
        super().__init__(project_path)
        self.ide_type = "cursor"
    
    async def open_file(self, file_path: str, line: int = None):
        """打开文件"""
        cmd = ["cursor", file_path]
        if line:
            cmd.extend(["-g", f"{file_path}:{line}"])
        
        await asyncio.create_subprocess_exec(*cmd)


class JetBrainsIntegration(IDEIntegration):
    """JetBrains 系列 IDE 集成"""
    
    def __init__(self, project_path: Path, ide_name: str = "idea"):
        super().__init__(project_path)
        self.ide_type = ide_name
        self.ide_binary = ide_name  # idea, pycharm, webstorm 等
    
    async def open_file(self, file_path: str, line: int = None):
        """打开文件"""
        # 使用 IDE 打开文件
        cmd = [self.ide_binary, f"{file_path}"]
        if line:
            cmd.extend(["--line", str(line)])
        
        # 后台运行
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        # 不等待完成
    
    async def go_to_definition(self, file_path: str, line: int, column: int = 0):
        """跳转到定义"""
        # 使用 IDE 的 action
        await self.run_command("GotoDeclaration", [file_path, str(line)])
    
    async def find_references(self, file_path: str, line: int, column: int):
        """查找引用"""
        await self.run_command("FindUsages", [file_path, str(line)])
    
    async def get_symbols(self, file_path: str) -> List[Symbol]:
        """获取符号（需要 IDE 插件）"""
        # 简化实现
        return []
    
    async def run_command(self, command: str, args: List[str] = None):
        """运行 IDE 命令"""
        # 使用命令行工具（如果配置了）
        pass


class IDEManager:
    """IDE 管理器"""
    
    def __init__(self):
        self.integrations: Dict[str, IDEIntegration] = {}
        self.current_project: Optional[IDEProject] = None
        
        # 检测可用的 IDE
        self._detect_ides()
    
    def _detect_ides(self):
        """检测可用的 IDE"""
        # 检查命令行工具
        for ide in ["code", "cursor", "idea", "pycharm", "webstorm", "goland"]:
            try:
                proc = subprocess.run(
                    ["which", ide],
                    capture_output=True,
                    text=True
                )
                if proc.returncode == 0:
                    print(f"{Fore.GREEN}✓ 检测到 IDE: {ide}{Fore.RESET}")
            except Exception:
                pass
    
    def register_integration(self, name: str, integration: IDEIntegration):
        """注册集成"""
        self.integrations[name] = integration
    
    async def open_in_ide(
        self,
        ide: str,
        project_path: Path,
        file_path: str = None,
        line: int = None
    ):
        """在指定 IDE 中打开"""
        integration = self.integrations.get(ide)
        
        if not integration:
            # 尝试创建
            if ide == "vscode":
                integration = VSCodeIntegration(project_path)
            elif ide == "cursor":
                integration = CursorIntegration(project_path)
            elif ide in ["idea", "pycharm", "webstorm"]:
                integration = JetBrainsIntegration(project_path, ide)
            else:
                raise ValueError(f"不支持的 IDE: {ide}")
            
            self.integrations[ide] = integration
        
        await integration.open_file(file_path or str(project_path), line)
    
    def get_available_ides(self) -> List[str]:
        """获取可用的 IDE 列表"""
        return list(self.integrations.keys())
    
    async def create_project_config(
        self,
        project_path: Path,
        ide: str = "vscode"
    ) -> Path:
        """创建项目配置文件"""
        
        if ide == "vscode":
            # 创建 .vscode 目录和设置
            vscode_dir = project_path / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            # settings.json
            settings = {
                "editor.formatOnSave": True,
                "editor.tabSize": 4,
                "python.linting.enabled": True,
                "files.exclude": {
                    "**/__pycache__": True,
                    "**/*.pyc": True
                }
            }
            
            (vscode_dir / "settings.json").write_text(
                json.dumps(settings, indent=2)
            )
            
            # tasks.json (常用任务)
            tasks = {
                "version": "2.0.0",
                "tasks": [
                    {
                        "label": "Run",
                        "type": "shell",
                        "command": "python main.py",
                        "problemMatcher": []
                    },
                    {
                        "label": "Test",
                        "type": "shell", 
                        "command": "pytest",
                        "problemMatcher": []
                    }
                ]
            }
            
            (vscode_dir / "tasks.json").write_text(
                json.dumps(tasks, indent=2)
            )
            
            return vscode_dir
        
        return None


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== IDE 集成示例 ==={Fore.RESET}\n")
    
    # 创建管理器
    manager = IDEManager()
    
    # 可用的 IDE
    print("1. 可用 IDE:")
    for ide in manager.get_available_ides():
        print(f"   - {ide}")
    
    if not manager.get_available_ides():
        print(f"   {Fore.YELLOW}未检测到 IDE（需要安装并配置命令行工具）{Fore.RESET}")
    
    # 创建配置
    print("\n2. 创建项目配置:")
    import tempfile
    temp_dir = Path(tempfile.mkdtemp())
    
    config_path = await manager.create_project_config(temp_dir, "vscode")
    print(f"   已创建: {config_path}")
    
    # 符号解析
    print("\n3. 符号解析:")
    test_file = temp_dir / "test.py"
    test_file.write_text("""
def hello():
    pass

class MyClass:
    def method(self):
        pass
""")
    
    # 创建 VSCode 集成并获取符号
    integration = VSCodeIntegration(temp_dir)
    symbols = await integration.get_symbols(str(test_file))
    
    for sym in symbols:
        print(f"   - {sym.name} ({sym.kind}) at line {sym.location.line}")
    
    print(f"\n{Fore.GREEN}✓ IDE 集成示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())