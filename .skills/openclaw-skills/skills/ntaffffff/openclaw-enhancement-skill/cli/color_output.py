#!/usr/bin/env python3
"""
CLI 彩色输出模块

终端彩色输出、进度条、表格、动画
参考 Claude Code 的 CLI 美化
"""

from __future__ import annotations

import sys
import time
import itertools
from typing import Optional, List, Dict, Any, Callable, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

if TYPE_CHECKING:
    from datetime import datetime

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
    class Fore:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    class Back:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    class Style:
        BRIGHT = DIM = NORMAL = RESET_ALL = ""


class ColorTheme(Enum):
    """配色主题"""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    MONO = "mono"


# 全局配置
_config = {
    "theme": ColorTheme.DEFAULT,
    "enabled": True,
    "use_emoji": True,
}


def set_theme(theme: ColorTheme) -> None:
    """设置主题"""
    _config["theme"] = theme


def disable_colors() -> None:
    """禁用颜色"""
    _config["enabled"] = False


def enable_colors() -> None:
    """启用颜色"""
    _config["enabled"] = True


def _get_color(color: str) -> str:
    """获取颜色"""
    if not _config["enabled"]:
        return ""
    return getattr(Fore, color.upper(), "")


def _get_colored(text: str, color: str) -> str:
    """获取着色文本"""
    if not _config["enabled"]:
        return text
    return f"{_get_color(color)}{text}{Style.RESET_ALL}"


# ============ 基础输出函数 ============

def info(message: str) -> None:
    """信息输出"""
    print(_get_colored(f"ℹ {message}", "cyan"))


def success(message: str) -> None:
    """成功输出"""
    print(_get_colored(f"✓ {message}", "green"))


def warning(message: str) -> None:
    """警告输出"""
    print(_get_colored(f"⚠ {message}", "yellow"))


def error(message: str) -> None:
    """错误输出"""
    print(_get_colored(f"✗ {message}", "red"))


def debug(message: str) -> None:
    """调试输出"""
    print(_get_colored(f"🔍 {message}", "magenta"))


def header(title: str, width: int = 60) -> None:
    """标题"""
    print()
    print(_get_colored(f"╔{'═' * (width - 2)}╗", "cyan"))
    print(_get_colored(f"║ {title:^{width - 4}} ║", "cyan"))
    print(_get_colored(f"╚{'═' * (width - 2)}╝", "cyan"))
    print()


def subheader(title: str) -> None:
    """子标题"""
    print()
    print(_get_colored(f"━━━ {title} ━━━", "cyan"))
    print()


def step(current: int, total: int, message: str = "") -> None:
    """步骤输出"""
    if message:
        print(_get_colored(f"  [{current}/{total}] {message}", "cyan"))
    else:
        print(_get_colored(f"  [{current}/{total}]", "cyan"))


def progress_bar(
    current: int,
    total: int,
    prefix: str = "",
    length: int = 40,
    fill: str = "█",
    empty: str = "░"
) -> None:
    """进度条"""
    percent = current / total if total > 0 else 0
    filled = int(length * percent)
    bar = fill * filled + empty * (length - filled)
    
    #\r 回到行首覆盖
    print(f"\r{prefix}|{bar}| {percent*100:.1f}%", end="", flush=True)
    
    if current >= total:
        print()  # 换行


def spinner(message: str = "加载中", frames: List[str] = None) -> "Spinner":
    """创建加载动画"""
    return Spinner(message, frames)


class Spinner:
    """加载动画"""
    
    DEFAULT_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, message: str, frames: List[str] = None):
        self.message = message
        self.frames = frames or self.DEFAULT_FRAMES
        self._running = False
        self._thread = None
    
    def _spin(self) -> None:
        """旋转"""
        for frame in itertools.cycle(self.frames):
            if not self._running:
                break
            print(f"\r{_get_colored(frame, 'cyan')} {self.message}", end="", flush=True)
            time.sleep(0.1)
    
    def start(self) -> None:
        """开始"""
        import threading
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
    
    def stop(self, message: str = "完成") -> None:
        """停止"""
        self._running = False
        time.sleep(0.1)
        print(f"\r{_get_colored('✓', 'green')} {message}")


def table(
    headers: List[str],
    rows: List[List[str]],
    max_width: int = 100
) -> None:
    """表格输出"""
    if not rows:
        print(_get_colored("无数据", "yellow"))
        return
    
    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 限制总宽度
    total_width = sum(col_widths) + len(headers) * 3 + 1
    if total_width > max_width:
        scale = (max_width - len(headers) * 3 - 1) / total_width
        col_widths = [max(10, int(w * scale)) for w in col_widths]
    
    # 分隔线
    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    
    # 表头
    print(separator)
    header_cells = " | ".join(
        h.ljust(col_widths[i]) for i, h in enumerate(headers)
    )
    print(f"| {header_cells} |")
    print(separator)
    
    # 数据行
    for row in rows:
        cells = " | ".join(
            str(cell).ljust(col_widths[i])[:col_widths[i]] 
            for i, cell in enumerate(row)
        )
        print(f"| {cells} |")
    
    print(separator)


def tree(
    items: Dict[str, Any],
    prefix: str = "",
    is_last: bool = True
) -> None:
    """树形输出"""
    connectors = "└── " if is_last else "├── "
    
    items_list = list(items.items())
    for i, (key, value) in enumerate(items_list):
        is_last_item = i == len(items_list) - 1
        connector = "└── " if is_last_item else "├── "
        
        if isinstance(value, dict):
            print(f"{prefix}{connector}{_get_colored(key, 'cyan')}")
            new_prefix = prefix + ("    " if is_last_item else "│   ")
            tree(value, new_prefix, is_last_item)
        else:
            print(f"{prefix}{connector}{key}: {value}")


def code_block(code: str, language: str = "") -> None:
    """代码块"""
    print(_get_colored("```" + language, "dim"))
    print(code)
    print(_get_colored("```", "dim"))


def link(url: str, text: str = None) -> None:
    """链接（终端中可能不显示）"""
    if text:
        print(f"{text}: {url}")
    else:
        print(url)


def list_items(
    items: List[str],
    numbered: bool = True,
    emoji_prefix: bool = True
) -> None:
    """列表输出"""
    for i, item in enumerate(items, 1):
        if numbered:
            prefix = f"{i}."
        elif emoji_prefix:
            prefix = "•"
        else:
            prefix = "-"
        
        print(f"  {prefix} {item}")


def confirm(prompt: str, default: bool = False) -> bool:
    """确认提示"""
    suffix = " [Y/n]: " if default else " [y/N]: "
    default_str = "Y" if default else "n"
    
    while True:
        try:
            response = input(_get_colored(prompt, "cyan") + suffix)
            response = response.strip().lower()
            
            if not response:
                return default
            
            if response in ["y", "yes", "是"]:
                return True
            elif response in ["n", "no", "否"]:
                return False
            else:
                print(_get_colored("请输入 y 或 n", "yellow"))
        except (KeyboardInterrupt, EOFError):
            print()
            return default


def prompt(prompt_text: str, default: str = "") -> str:
    """输入提示"""
    default_str = f" ({default})" if default else ""
    result = input(_get_colored(f"{prompt_text}{default_str}: ", "cyan"))
    return result or default


# ============ 进度条类 ============

class Progress:
    """进度条"""
    
    def __init__(
        self,
        total: int,
        description: str = "",
        bar_length: int = 40
    ):
        self.total = total
        self.description = description
        self.bar_length = bar_length
        self.current = 0
        self.start_time = time.time()
        self._closed = False
    
    def update(self, n: int = 1) -> None:
        """更新进度"""
        self.current = min(self.current + n, self.total)
        self._render()
    
    def set(self, value: int) -> None:
        """设置进度"""
        self.current = min(value, self.total)
        self._render()
    
    def _render(self) -> None:
        """渲染"""
        if self._closed:
            return
        
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(self.bar_length * percent)
        bar = "█" * filled + "░" * (self.bar_length - filled)
        
        # 计算速度和 ETA
        elapsed = time.time() - self.start_time
        speed = self.current / elapsed if elapsed > 0 else 0
        remaining = self.total - self.current
        eta = remaining / speed if speed > 0 else 0
        
        info = f" {self.current}/{self.total} | ETA: {eta:.0f}s"
        
        print(f"\r{self.description}: |{bar}| {percent*100:.0f}%{info}", end="", flush=True)
        
        if self.current >= self.total:
            print()
            self._closed = True
    
    def close(self) -> None:
        """关闭"""
        if not self._closed:
            print()
            self._closed = True


# ============ 动画效果 ============

class Animation:
    """动画效果"""
    
    @staticmethod
    def typing(text: str, delay: float = 0.05) -> None:
        """打字机效果"""
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
        print()
    
    @staticmethod
    def fade_in(text: str, steps: int = 5) -> None:
        """淡入效果"""
        for i in range(steps + 1):
            alpha = int(255 * i / steps)
            # 注意：终端不一定支持 alpha
            print(text)
            time.sleep(0.1)


# ============ 使用示例 ============

def example():
    """示例"""
    header("CLI 彩色输出示例")
    
    # 基础输出
    info("这是一条信息")
    success("操作成功")
    warning("警告信息")
    error("错误信息")
    debug("调试信息")
    
    # 标题
    subheader("标题示例")
    
    # 步骤
    print()
    for i in range(1, 4):
        step(i, 3, f"步骤 {i}")
    
    # 进度条
    print()
    progress = Progress(20, "下载文件")
    for i in range(21):
        progress.update(1)
        time.sleep(0.05)
    
    # 表格
    print()
    subheader("表格示例")
    table(
        ["姓名", "年龄", "城市"],
        [
            ["张三", "28", "北京"],
            ["李四", "32", "上海"],
            ["王五", "25", "深圳"],
        ]
    )
    
    # 列表
    print()
    subheader("列表示例")
    list_items(["项目 A", "项目 B", "项目 C"])
    
    # 确认
    print()
    if confirm("确认继续?", default=True):
        success("用户确认")
    else:
        warning("用户取消")
    
    # 输入
    print()
    name = prompt("请输入你的名字", "Guest")
    success(f"你好, {name}!")


if __name__ == "__main__":
    example()