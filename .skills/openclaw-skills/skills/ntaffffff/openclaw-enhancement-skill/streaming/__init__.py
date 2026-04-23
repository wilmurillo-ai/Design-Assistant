#!/usr/bin/env python3
"""
流式输出模块

实时流式响应（打字机效果）
参考 Claude Code 的流式输出
"""

import asyncio
import sys
import time
from typing import AsyncIterator, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


class OutputSpeed(Enum):
    """输出速度"""
    INSTANT = 0          # 即时
    FAST = 0.01          # 快速
    NORMAL = 0.02        # 正常
    SLOW = 0.05          # 慢速


@dataclass
class StreamConfig:
    """流式输出配置"""
    speed: OutputSpeed = OutputSpeed.NORMAL
    show_cursor: bool = False
    clear_after_done: bool = False
    color_enabled: bool = True


class StreamingPrinter:
    """流式打印机"""
    
    def __init__(self, config: StreamConfig = None):
        self.config = config or StreamConfig()
        self._buffer: str = ""
        self._is_streaming: bool = False
    
    async def print(self, text: str, end: str = "\n"):
        """流式打印"""
        if self.config.speed == OutputSpeed.INSTANT:
            print(text, end=end)
            return
        
        self._is_streaming = True
        
        # 隐藏光标
        if self.config.show_cursor:
            print("\033[?25l", end="", flush=True)
        
        try:
            for char in text:
                print(char, end="", flush=True)
                await asyncio.sleep(self.config.speed)
            
            print(end=end)
            
        finally:
            # 恢复光标
            if self.config.show_cursor:
                print("\033[?25h", end="", flush=True)
            
            self._is_streaming = False
    
    async def print_line(self, text: str = ""):
        """打印一行"""
        await self.print(text)
    
    async def print_lines(self, lines: list):
        """打印多行"""
        for i, line in enumerate(lines):
            await self.print(line)
            if i < len(lines) - 1:
                await self.print("\n")
    
    async def print_with_prefix(self, text: str, prefix: str = "▸ "):
        """带前缀打印"""
        await self.print(f"{prefix}{text}")
    
    def print_sync(self, text: str, end: str = "\n"):
        """同步打印（无动画）"""
        print(text, end=end)
    
    def clear_line(self):
        """清除当前行"""
        print("\r\033[K", end="", flush=True)
    
    def clear_screen(self):
        """清屏"""
        print("\033[2J\033[H", end="", flush=True)


class TypewriterEffect:
    """打字机效果"""
    
    def __init__(self, base_delay: float = 0.03, variance: float = 0.02):
        self.base_delay = base_delay
        self.variance = variance
        self._canceled = False
    
    def cancel(self):
        """取消打字效果"""
        self._canceled = True
    
    async def type_text(self, text: str) -> str:
        """逐字符输出"""
        self._canceled = False
        result = ""
        
        for char in text:
            if self._canceled:
                # 立即输出剩余字符
                result += char
                continue
            
            result += char
            print(char, end="", flush=True)
            
            # 可变延迟（更自然）
            import random
            delay = self.base_delay + random.uniform(-self.variance, self.variance)
            await asyncio.sleep(max(0, delay))
        
        return result
    
    async def type_lines(self, lines: list) -> str:
        """逐行输出"""
        result = ""
        
        for i, line in enumerate(lines):
            result += await self.type_text(line)
            if i < len(lines) - 1:
                result += "\n"
                print()
                await asyncio.sleep(0.1)  # 行间暂停
        
        return result


class ProgressStream:
    """进度流"""
    
    def __init__(self, total: int = 100, description: str = "进度"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, delta: int = 1):
        """更新进度"""
        self.current = min(self.current + delta, self.total)
        self._render()
    
    def set(self, value: int):
        """设置进度"""
        self.current = min(value, self.total)
        self._render()
    
    def _render(self):
        """渲染进度条"""
        percent = self.current / self.total if self.total > 0 else 0
        bar_length = 30
        filled = int(bar_length * percent)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        elapsed = time.time() - self.start_time
        speed = self.current / elapsed if elapsed > 0 else 0
        
        # 计算 ETA
        remaining = self.total - self.current
        eta = remaining / speed if speed > 0 else 0
        
        print(f"\r{self.description}: |{bar}| {percent*100:.1f}% "
              f"({self.current}/{self.total}) "
              f"ETA: {eta:.1f}s", end="", flush=True)
    
    def finish(self):
        """完成"""
        self.current = self.total
        self._render()
        print()  # 换行


class TokenStream:
    """Token 流式输出（用于 AI 响应）"""
    
    def __init__(self, on_token: Callable[[str], None] = None):
        self.on_token = on_token
        self.buffer = ""
    
    async def stream_response(self, response_generator: AsyncIterator[str]) -> str:
        """流式响应"""
        self.buffer = ""
        
        async for token in response_generator:
            self.buffer += token
            
            # 回调
            if self.on_token:
                self.on_token(token)
        
        return self.buffer
    
    def get_buffer(self) -> str:
        """获取缓冲区"""
        return self.buffer


class AnsiColors:
    """ANSI 颜色代码"""
    
    # 基础颜色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 亮色
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # 样式
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # 特效
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """着色"""
        return f"{color}{text}{cls.RESET}"
    
    @classmethod
    def gradient(cls, text: str, colors: list) -> str:
        """渐变色"""
        if not colors or not text:
            return text
        
        result = ""
        for i, char in enumerate(text):
            color_index = int(i / len(text) * len(colors))
            result += f"{colors[color_index % len(colors)]}{char}"
        
        return result + cls.RESET


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 流式输出示例 ==={Fore.RESET}\n")
    
    # 1. 基础流式打印
    print("1. 基础流式打印:")
    printer = StreamingPrinter(StreamConfig(speed=OutputSpeed.FAST))
    await printer.print("这是一段流式输出的文字...")
    print()
    
    # 2. 打字机效果
    print("\n2. 打字机效果:")
    typewriter = TypewriterEffect(base_delay=0.02, variance=0.01)
    await typewriter.type_text("Hello, World! 你好世界!")
    print()
    
    # 3. 进度条
    print("\n3. 进度条:")
    progress = ProgressStream(20, "下载文件")
    for i in range(21):
        progress.update(1)
        await asyncio.sleep(0.05)
    progress.finish()
    
    # 4. 带颜色的流式输出
    print("\n4. 带颜色的流式输出:")
    colors = AnsiColors()
    await printer.print(colors.colorize("这是红色", colors.RED))
    await printer.print(colors.colorize("这是绿色", colors.GREEN))
    await printer.print(colors.colorize("这是加粗", colors.BOLD))
    
    # 5. 渐变色
    print("\n5. 渐变色:")
    gradient_text = "Hello, OpenClaw!"
    colors_list = [colors.RED, colors.YELLOW, colors.GREEN]
    print(colors.gradient(gradient_text, colors_list))
    
    print(f"\n{Fore.GREEN}✓ 流式输出示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())