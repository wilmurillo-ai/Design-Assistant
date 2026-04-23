#!/usr/bin/env python3
"""
项目级记忆模块

每个项目可以有专属的配置/记忆文件 CLAUDE.md
参考 Claude Code 的项目级配置
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""

# 默认的 CLAUDE.md 文件名
CLAUDE_FILENAME = "CLAUDE.md"
CLAUDE_CONFIG_FILENAME = ".claude.json"


@dataclass
class ProjectContext:
    """项目上下文"""
    project_path: Path
    name: str
    description: str = ""
    working_directory: str = "."
    commands: Dict[str, str] = field(default_factory=dict)  # 自定义命令
    rules: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)  # 可用工具
    preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClaudeFile:
    """CLAUDE.md 文件内容"""
    path: Path
    instructions: str = ""
    context: str = ""
    commands: Dict[str, str] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    last_modified: datetime = field(default_factory=datetime.now)
    content_hash: str = ""


class ProjectMemory:
    """项目级记忆管理"""
    
    def __init__(self, workspace_root: Path = None):
        self.workspace_root = workspace_root or Path.cwd()
        self.projects: Dict[Path, ProjectContext] = {}
        self.current_project: Optional[ProjectContext] = None
        self._cache: Dict[Path, ClaudeFile] = {}
    
    def detect_project(self, path: Path = None) -> Optional[ProjectContext]:
        """检测项目根目录"""
        path = path or Path.cwd()
        
        # 向上查找 CLAUDE.md 文件
        current = path.resolve()
        while current != current.parent:
            claude_file = current / CLAUDE_FILENAME
            if claude_file.exists():
                return self.load_project(current)
            current = current.parent
        
        return None
    
    def load_project(self, project_path: Path) -> ProjectContext:
        """加载项目配置"""
        project_path = project_path.resolve()
        
        # 读取 CLAUDE.md
        claude_file = project_path / CLAUDE_FILENAME
        instructions = ""
        context = ""
        commands = {}
        tools = []
        rules = []
        
        if claude_file.exists():
            content = claude_file.read_text(encoding="utf-8")
            
            # 解析文件内容
            sections = content.split("\n## ")
            for section in sections:
                if section.startswith("Instructions"):
                    instructions = section.split("\n", 1)[1].strip()
                elif section.startswith("Context"):
                    context = section.split("\n", 1)[1].strip()
                elif section.startswith("Commands"):
                    # 解析命令
                    lines = section.split("\n")[1:]
                    for line in lines:
                        if ":" in line:
                            cmd, desc = line.split(":", 1)
                            commands[cmd.strip()] = desc.strip()
                elif section.startswith("Tools"):
                    lines = section.split("\n")[1:]
                    tools = [line.strip().lstrip("- ") for line in lines if line.strip()]
                elif section.startswith("Rules"):
                    lines = section.split("\n")[1:]
                    rules = [line.strip().lstrip("- ") for line in lines if line.strip()]
        
        # 读取 .claude.json 配置
        config_file = project_path / CLAUDE_CONFIG_FILENAME
        preferences = {}
        if config_file.exists():
            try:
                preferences = json.loads(config_file.read_text(encoding="utf-8"))
            except:
                pass
        
        project = ProjectContext(
            project_path=project_path,
            name=project_path.name,
            description=context[:100] if context else "",
            working_directory=str(project_path),
            commands=commands,
            tools=tools,
            rules=rules,
            preferences=preferences
        )
        
        self.projects[project_path] = project
        self.current_project = project
        
        return project
    
    def get_or_create_project(self, path: Path = None) -> ProjectContext:
        """获取或创建项目"""
        path = path or Path.cwd()
        
        # 先尝试检测
        project = self.detect_project(path)
        if project:
            return project
        
        # 没有找到，创建新项目
        project_path = path.resolve()
        if project_path.name == "CLAUDE.md":
            project_path = project_path.parent
        
        # 创建默认 CLAUDE.md
        claude_file = project_path / CLAUDE_FILENAME
        if not claude_file.exists():
            default_content = """# CLAUDE.md - 项目配置

## Instructions
你是一个有帮助的 AI 助手。请根据项目需求提供帮助。

## Context
这是一个新创建的项目。

## Commands
- test: 运行测试
- build: 构建项目
- lint: 代码检查

## Tools
- read: 读取文件
- write: 写入文件
- edit: 编辑文件

## Rules
1. 遵循项目规范
2. 保持代码整洁
3. 及时更新文档
"""
            claude_file.write_text(default_content, encoding="utf-8")
            print(f"{Fore.GREEN}✓ 已创建 CLAUDE.md: {claude_file}{Fore.RESET}")
        
        return self.load_project(project_path)
    
    def update_instructions(self, instructions: str, project_path: Path = None):
        """更新指令"""
        project = self._get_project(project_path)
        if not project:
            return
        
        claude_file = project.project_path / CLAUDE_FILENAME
        content = claude_file.read_text(encoding="utf-8") if claude_file.exists() else ""
        
        # 更新 Instructions 部分
        lines = content.split("\n")
        new_lines = []
        in_instructions = False
        
        for line in lines:
            if line.startswith("## Instructions"):
                in_instructions = True
                new_lines.append(line)
            elif in_instructions and line.startswith("## "):
                in_instructions = False
                new_lines.append(f"{instructions}\n")
                new_lines.append(line)
            elif not in_instructions:
                new_lines.append(line)
        
        claude_file.write_text("\n".join(new_lines), encoding="utf-8")
        self._cache.pop(project.project_path, None)
    
    def add_command(self, name: str, description: str, project_path: Path = None):
        """添加自定义命令"""
        project = self._get_project(project_path)
        if not project:
            return
        
        project.commands[name] = description
        
        # 更新文件
        claude_file = project.project_path / CLAUDE_FILENAME
        if claude_file.exists():
            content = claude_file.read_text(encoding="utf-8")
            
            # 检查是否有 Commands 部分
            if "## Commands" not in content:
                content += f"\n\n## Commands\n- {name}: {description}\n"
            else:
                # 添加到 Commands 部分
                lines = content.split("\n")
                new_lines = []
                in_commands = False
                
                for line in lines:
                    if line.startswith("## Commands"):
                        in_commands = True
                    elif in_commands and line.startswith("## "):
                        new_lines.append(f"- {name}: {description}\n")
                        in_commands = False
                    
                    if in_commands and not line.strip().startswith("-") and line.strip():
                        new_lines.append(f"- {name}: {description}\n")
                        in_commands = False
                    
                    new_lines.append(line)
                
                content = "\n".join(new_lines)
            
            claude_file.write_text(content, encoding="utf-8")
    
    def add_rule(self, rule: str, project_path: Path = None):
        """添加规则"""
        project = self._get_project(project_path)
        if not project:
            return
        
        if rule not in project.rules:
            project.rules.append(rule)
    
    def get_context_prompt(self, project_path: Path = None) -> str:
        """获取项目上下文提示"""
        project = self._get_project(project_path)
        if not project:
            return ""
        
        parts = []
        
        if project.description:
            parts.append(f"项目: {project.description}")
        
        if project.commands:
            cmds = ", ".join(f"`{k}`" for k in project.commands.keys())
            parts.append(f"可用命令: {cmds}")
        
        if project.tools:
            tools = ", ".join(f"`{t}`" for t in project.tools[:5])
            parts.append(f"可用工具: {tools}")
        
        if project.rules:
            parts.append(f"规则: {'; '.join(project.rules[:3])}")
        
        return "\n".join(parts) if parts else ""
    
    def watch_project(self, project_path: Path, callback):
        """监听项目文件变化"""
        # 简化实现
        pass
    
    def _get_project(self, project_path: Path = None) -> Optional[ProjectContext]:
        """获取项目"""
        if project_path:
            return self.projects.get(project_path.resolve())
        return self.current_project
    
    def list_projects(self) -> List[ProjectContext]:
        """列出所有加载的项目"""
        return list(self.projects.values())


# ============ 默认项目模板 ============

DEFAULT_TEMPLATES = {
    "python": """# CLAUDE.md - Python 项目

## Instructions
你是一个 Python 开发助手。请遵循 PEP 8 规范，使用类型注解。

## Context
这是一个 Python 项目。

## Commands
- test: 运行 pytest 测试
- lint: 运行 ruff 检查
- format: 运行 black 格式化

## Tools
- read: 读取 Python 文件
- write: 写入 Python 文件
- edit: 编辑 Python 文件
- grep: 搜索代码

## Rules
1. 使用类型注解
2. 遵循 PEP 8
3. 编写 docstring
4. 测试覆盖率 > 80%
""",
    
    "javascript": """# CLAUDE.md - JavaScript 项目

## Instructions
你是一个 JavaScript/TypeScript 开发助手。

## Context
这是一个 JS/TS 项目。

## Commands
- test: 运行 Vitest 测试
- lint: 运行 ESLint 检查
- build: 运行 Vite 构建

## Tools
- read: 读取 JS/TS 文件
- write: 写入 JS/TS 文件

## Rules
1. 使用 TypeScript
2. 遵循 ESLint 规则
3. 组件使用 functional 风格
""",
    
    "general": """# CLAUDE.md

## Instructions
你是一个有帮助的 AI 助手。

## Context
通用项目配置。

## Commands
- help: 显示帮助

## Rules
1. 保持代码简洁
2. 及时更新文档
"""
}


def create_project_template(project_path: Path, template: str = "general"):
    """创建项目模板"""
    claude_file = project_path / CLAUDE_FILENAME
    
    if claude_file.exists():
        print(f"{Fore.YELLOW}⚠ CLAUDE.md 已存在{Fore.RESET}")
        return False
    
    template_content = DEFAULT_TEMPLATES.get(template, DEFAULT_TEMPLATES["general"])
    claude_file.write_text(template_content, encoding="utf-8")
    
    print(f"{Fore.GREEN}✓ 已创建 {template} 项目模板: {claude_file}{Fore.RESET}")
    return True


# ============ 使用示例 ============

def example():
    """示例"""
    print(f"{Fore.CYAN}=== 项目级记忆示例 ==={Fore.RESET}\n")
    
    # 创建记忆管理器
    memory = ProjectMemory()
    
    # 检测或创建项目
    print("1. 检测项目...")
    project = memory.get_or_create_project()
    
    print(f"   项目名称: {project.name}")
    print(f"   项目路径: {project.project_path}")
    
    # 获取上下文提示
    print("\n2. 获取上下文提示...")
    context = memory.get_context_prompt()
    if context:
        print(f"   {context}")
    else:
        print("   (无特殊配置)")
    
    # 列出命令
    print("\n3. 可用命令:")
    for name, desc in project.commands.items():
        print(f"   /{name}: {desc}")
    
    # 列出规则
    print("\n4. 规则:")
    for rule in project.rules:
        print(f"   - {rule}")
    
    print(f"\n{Fore.GREEN}✓ 项目级记忆示例完成!{Fore.RESET}")


if __name__ == "__main__":
    example()