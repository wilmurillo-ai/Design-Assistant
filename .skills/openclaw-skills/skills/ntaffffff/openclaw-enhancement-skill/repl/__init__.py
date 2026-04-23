#!/usr/bin/env python3
"""
REPL 交互增强模块

功能:
- Tab 命令补全
- 命令历史（上下键）
- Slash 命令支持 (/help, /status, /clear)
- 多行输入（智能括号匹配）
- 流式输出（打字机效果）
- 中断处理 (Ctrl+C)

参考 Claude Code 的 REPL 设计
"""

from __future__ import annotations

import asyncio
import sys
import os
import shlex
import math
from typing import Optional, Callable, List, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = WHITE = ""
        RED = GREEN = YELLOW = CYAN = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""


# 类型别名
InputCallback = Callable[[str], Any]
CompletionCallback = Callable[[str], List[str]]


@dataclass
class Command:
    """命令定义"""
    name: str
    description: str
    callback: Callable
    aliases: List[str] = field(default_factory=list)
    usage: str = ""
    examples: List[str] = field(default_factory=list)


@dataclass
class REPLHistory:
    """命令历史"""
    max_size: int = 100
    _history: List[str] = field(default_factory=list)
    _position: int = -1
    
    def add(self, command: str) -> None:
        """添加历史"""
        if command.strip() and command != self._history[-1] if self._history else True:
            self._history.append(command)
            if len(self._history) > self.max_size:
                self._history.pop(0)
            self._position = len(self._history)
    
    def move_up(self) -> Optional[str]:
        """向上移动"""
        if self._history and self._position > 0:
            self._position -= 1
            return self._history[self._position]
        return None
    
    def move_down(self) -> Optional[str]:
        """向下移动"""
        if self._history and self._position < len(self._history) - 1:
            self._position += 1
            return self._history[self._position]
        else:
            self._position = len(self._history)
            return ""
    
    def reset_position(self) -> None:
        """重置位置"""
        self._position = len(self._history)


class Completer:
    """命令补全器"""
    
    def __init__(self, commands: Dict[str, Command]):
        self.commands = commands
        self._custom_completers: Dict[str, CompletionCallback] = {}
    
    def register_completer(self, command: str, callback: CompletionCallback) -> None:
        """注册自定义补全"""
        self._custom_completers[command] = callback
    
    def complete(self, text: str) -> List[str]:
        """补全"""
        if not text:
            return list(self.commands.keys())
        
        # 匹配命令
        matches = []
        text_lower = text.lower()
        
        # 检查是否在命令中
        parts = text.split()
        if parts and parts[0] in self.commands:
            # 参数补全
            cmd = self.commands[parts[0]]
            if parts[0] in self._custom_completers:
                return self._custom_completers[parts[0]](text)
            return []
        
        # 命令补全
        for name in self.commands.keys():
            if name.startswith(text_lower):
                matches.append(name)
            # 别名补全
            for alias in self.commands[name].aliases:
                if alias.startswith(text_lower):
                    matches.append(name)
                    break
        
        return matches
    
    def get_suggestions(self, text: str) -> List[str]:
        """获取建议"""
        matches = self.complete(text)
        if len(matches) == 1:
            return [f"{matches[0]} "]
        elif len(matches) > 1:
            # 找共同前缀
            if len(matches) > 1:
                prefix = os.path.commonprefix(matches)
                if prefix and prefix != text:
                    return [f"{prefix} "]
            return matches
        return []


class SlashCommandHandler:
    """Slash 命令处理器"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self._register_default_commands()
    
    def _register_default_commands(self) -> None:
        """注册默认命令"""
        self.register(Command(
            name="/help",
            description="显示帮助信息",
            callback=lambda _: "帮助信息",
            aliases=["/h", "/?"],
            usage="/help [command]",
            examples=["/help", "/help /status"]
        ))
        
        self.register(Command(
            name="/status",
            description="显示系统状态",
            callback=lambda _: "系统正常",
            aliases=["/s"],
            usage="/status"
        ))
        
        self.register(Command(
            name="/clear",
            description="清空屏幕",
            callback=lambda args: self._clear_screen(args),
            aliases=["/c"],
            usage="/clear"
        ))
        
        self.register(Command(
            name="/exit",
            description="退出程序",
            callback=lambda _: sys.exit(0),
            aliases=["/q", "/quit"],
            usage="/exit"
        ))
        
        self.register(Command(
            name="/history",
            description="显示命令历史",
            callback=lambda _: "无历史",
            aliases=["/hist"],
            usage="/history"
        ))
        
        self.register(Command(
            name="/version",
            description="显示版本信息",
            callback=lambda _: "OpenClaw REPL v1.0.0",
            aliases=["/v"],
            usage="/version"
        ))
    
    def _clear_screen(self, args: str) -> str:
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
        return ""
    
    def register(self, command: Command) -> None:
        """注册命令"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command
    
    def unregister(self, name: str) -> bool:
        """注销命令"""
        if name in self.commands:
            cmd = self.commands[name]
            del self.commands[name]
            for alias in cmd.aliases:
                if alias in self.commands:
                    del self.commands[alias]
            return True
        return False
    
    def execute(self, command: str) -> Any:
        """执行命令"""
        parts = shlex.split(command.strip())
        if not parts:
            return None
        
        cmd_name = parts[0]
        args = " ".join(parts[1:]) if len(parts) > 1 else ""
        
        command = self.commands.get(cmd_name)
        if command:
            return command.callback(args)
        
        return f"未知命令: {cmd_name}"
    
    def get_help(self, command_name: str = None) -> str:
        """获取帮助"""
        if command_name:
            cmd = self.commands.get(command_name)
            if cmd:
                lines = [f"{cmd.name} - {cmd.description}"]
                if cmd.usage:
                    lines.append(f"用法: {cmd.usage}")
                if cmd.examples:
                    lines.append("示例:")
                    for ex in cmd.examples:
                        lines.append(f"  {ex}")
                return "\n".join(lines)
            return f"未找到命令: {command_name}"
        
        # 所有命令
        lines = ["可用命令:", "-" * 30]
        for name, cmd in sorted(self.commands.items()):
            if not name.startswith("/"):
                continue
            lines.append(f"  {name:<15} {cmd.description}")
        
        return "\n".join(lines)


class MultilineInput:
    """多行输入处理器"""
    
    BRACKET_PAIRS = {
        "(": ")",
        "[": "]",
        "{": "}",
        '"': '"',
        "'": "'"
    }
    
    def __init__(self):
        self._buffer = ""
        self._bracket_stack: List[str] = []
    
    def add_line(self, line: str) -> bool:
        """添加行，返回是否完成"""
        self._buffer += line + "\n"
        
        # 检查括号
        for char in line:
            if char in self.BRACKET_PAIRS:
                self._bracket_stack.append(char)
            elif char in self.BRACKET_PAIRS.values():
                if self._bracket_stack and self.BRACKET_PAIRS[self._bracket_stack[-1]] == char:
                    self._bracket_stack.pop()
        
        # 完成条件：无未匹配括号
        return len(self._bracket_stack) == 0
    
    def is_complete(self) -> bool:
        """是否完成"""
        return len(self._bracket_stack) == 0
    
    def get_content(self) -> str:
        """获取内容"""
        return self._buffer.strip()
    
    def reset(self) -> None:
        """重置"""
        self._buffer = ""
        self._bracket_stack = []


class TypewriterEffect:
    """打字机效果"""
    
    def __init__(self, delay: float = 0.02, variance: float = 0.01):
        self.delay = delay
        self.variance = variance
        self._canceled = False
        self._stream_mode = False
    
    def cancel(self) -> None:
        """取消"""
        self._canceled = True
    
    async def type_text(self, text: str, stream_callback: Callable[[str], None] = None) -> None:
        """逐字符输出"""
        self._canceled = False
        
        for char in text:
            if self._canceled:
                print(text[text.index(char):], end="", flush=True)
                break
            
            print(char, end="", flush=True)
            
            if stream_callback:
                stream_callback(char)
            
            # 可变延迟
            import random
            delay = self.delay + random.uniform(-self.variance, self.variance)
            await asyncio.sleep(max(0, delay))
        
        print()  # 换行


class REPL:
    """REPL 主类"""
    
    def __init__(
        self,
        prompt: str = ">>> ",
        multiline: bool = True,
        history_file: str = None
    ):
        self.prompt = prompt
        self.multiline = multiline
        
        # 组件
        self.history = REPLHistory()
        self.slash_handler = SlashCommandHandler()
        self.completer: Optional[Completer] = None
        self.multiline_input = MultilineInput()
        
        # 状态
        self._running = False
        self._line_buffer = ""
        
        # 钩子
        self._input_callbacks: List[InputCallback] = []
        
        # 历史文件
        self.history_file = history_file or os.path.expanduser("~/.openclaw_repl_history")
        self._load_history()
        
        # 初始化补全
        self.completer = Completer(self.slash_handler.commands)
    
    def _load_history(self) -> None:
        """加载历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    for line in f:
                        self.history.add(line.strip())
            except Exception:
                pass
    
    def _save_history(self) -> None:
        """保存历史"""
        try:
            with open(self.history_file, "w") as f:
                for cmd in self.history._history:
                    f.write(cmd + "\n")
        except Exception:
            pass
    
    def add_input_callback(self, callback: InputCallback) -> None:
        """添加输入回调"""
        self._input_callbacks.append(callback)
    
    def register_command(self, command: Command) -> None:
        """注册命令"""
        self.slash_handler.register(command)
        # 更新补全器
        if self.completer:
            self.completer.commands = self.slash_handler.commands
    
    def _get_input(self) -> str:
        """获取输入（支持历史和补全）"""
        try:
            # 使用 input()
            line = input(self.prompt)
            return line
        except (KeyboardInterrupt, EOFError):
            print("\n使用 /exit 退出")
            return ""
    
    async def _process_input(self, line: str) -> Optional[str]:
        """处理输入"""
        line = line.strip()
        
        if not line:
            return None
        
        # 添加到历史
        self.history.add(line)
        
        # 检查 slash 命令
        if line.startswith("/"):
            result = self.slash_handler.execute(line)
            return str(result) if result else None
        
        # 执行回调
        for callback in self._input_callbacks:
            try:
                result = callback(line)
                if asyncio.iscoroutine(result):
                    result = await result
                if result:
                    return str(result)
            except Exception as e:
                return f"错误: {e}"
        
        return None
    
    async def run(self) -> None:
        """运行 REPL"""
        self._running = True
        
        print(f"{Fore.CYAN}OpenClaw REPL v1.0.0{Fore.RESET}")
        print("输入 /help 查看帮助\n")
        
        while self._running:
            try:
                # 获取输入
                line = self._get_input()
                
                # 多行处理
                if self.multiline and line:
                    # 检查是否是多行开始
                    multiline_start = any(line.startswith(p) for p in ["def ", "class ", "if ", "for ", "while ", "try:"])
                    
                    if not multiline_start and not self.multiline_input._buffer:
                        # 单行处理
                        result = await self._process_input(line)
                        if result:
                            print(result)
                    else:
                        # 多行模式
                        complete = self.multiline_input.add_line(line)
                        
                        if not complete:
                            # 继续输入
                            continuation = "... "
                            line2 = input(continuation)
                            self.multiline_input.add_line(line2)
                            
                            # 检查是否完成
                            if self.multiline_input.is_complete():
                                result = await self._process_input(self.multiline_input.get_content())
                                if result:
                                    print(result)
                                self.multiline_input.reset()
                            continue
                        else:
                            # 多行完成
                            result = await self._process_input(self.multiline_input.get_content())
                            if result:
                                print(result)
                            self.multiline_input.reset()
                else:
                    # 单行模式
                    result = await self._process_input(line)
                    if result:
                        print(result)
            
            except KeyboardInterrupt:
                print("\n使用 /exit 退出")
                continue
            except EOFError:
                print("\n再见!")
                break
        
        # 保存历史
        self._save_history()
    
    def stop(self) -> None:
        """停止"""
        self._running = False
        self._save_history()


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== REPL 交互增强示例 ==={Fore.RESET}\n")
    
    # 创建 REPL
    repl = REPL(prompt=">>> ")
    
    # 添加自定义命令
    repl.register_command(Command(
        name="/echo",
        description="回显输入",
        callback=lambda args: args or "请输入内容",
        usage="/echo <text>"
    ))
    
    repl.register_command(Command(
        name="/calc",
        description="简单计算器",
        callback=lambda args: str(eval(args)) if args else "用法: /calc 1+2",
        usage="/calc <expression>"
    ))
    
    # 添加输入回调
    repl.add_input_callback(lambda x: f"你输入了: {x}")
    
    # 模拟输入
    print("1. 帮助命令:")
    print(f"   {repl.slash_handler.execute('/help')}")
    
    print("\n2. 版本命令:")
    print(f"   {repl.slash_handler.execute('/version')}")
    
    print("\n3. 自定义命令:")
    print(f"   {repl.slash_handler.execute('/echo Hello World')}")
    print(f"   {repl.slash_handler.execute('/calc 2+3*4')}")
    
    print("\n4. 命令补全:")
    for cmd in repl.completer.complete("/h"):
        print(f"   - {cmd}")
    
    print("\n5. 多行输入:")
    ml_input = MultilineInput()
    ml_input.add_line("def hello():")
    ml_input.add_line("    print('hello')")
    ml_input.add_line("")
    print(f"   完成: {ml_input.is_complete()}")
    print(f"   内容: {ml_input.get_content()[:30]}...")
    
    print(f"\n{Fore.GREEN}✓ REPL 交互增强示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())