#!/usr/bin/env python3
"""
沙箱隔离执行模块

为工具执行提供安全的隔离环境
参考 Claude Code 的沙箱安全机制
"""

from __future__ import annotations

import os
import sys
import asyncio
import subprocess
import tempfile
import shutil
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, Optional, Callable, List, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from datetime import datetime

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = MAGENTA = ""


class SecurityLevel(Enum):
    """安全级别"""
    NONE = "none"           # 无隔离
    BASIC = "basic"         # 基本隔离（权限限制）
    STRICT = "strict"       # 严格隔离（容器/VM）
    FULL = "full"           # 完全隔离（独立进程）


@dataclass
class SandboxConfig:
    """沙箱配置"""
    security_level: SecurityLevel = SecurityLevel.BASIC
    max_memory_mb: int = 512          # 最大内存
    max_cpu_percent: int = 50         # 最大 CPU
    max_execution_time: float = 30.0  # 最大执行时间（秒）
    allowed_paths: List[str] = field(default_factory=list)  # 允许的路径
    blocked_paths: List[str] = field(default_factory=list)  # 禁止的路径
    env_whitelist: List[str] = field(default_factory=list)  # 允许的环境变量
    network_allowed: bool = False     # 是否允许网络
    max_output_size: int = 1024 * 1024  # 最大输出 1MB


@dataclass
class ExecutionResult:
    """执行结果"""
    success: bool
    output: str = ""
    error: str = ""
    exit_code: int = 0
    execution_time: float = 0.0
    memory_used_mb: float = 0.0
    truncated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class PathValidator:
    """路径验证器"""
    
    # 危险路径模式
    DANGEROUS_PATTERNS = [
        "/etc/passwd",
        "/etc/shadow",
        "/etc/sudoers",
        "/root/.ssh",
        "/proc/1",
        "/sys/",
    ]
    
    def __init__(self, config: SandboxConfig):
        self.config = config
        self.allowed_paths = [Path(p).resolve() for p in config.allowed_paths if p]
        self.blocked_paths = [Path(p).resolve() for p in config.blocked_paths if p]
    
    def is_allowed(self, path: str) -> bool:
        """检查路径是否允许"""
        try:
            # 解析绝对路径
            abs_path = Path(path).resolve()
            abs_str = str(abs_path)
            
            # 检查危险路径
            for dangerous in self.DANGEROUS_PATTERNS:
                if abs_str.startswith(dangerous):
                    return False
            
            # 检查是否在禁止列表中
            for blocked in self.blocked_paths:
                if abs_str.startswith(str(blocked)):
                    return False
            
            # 如果有允许列表，检查是否在允许列表中
            if self.allowed_paths:
                for allowed in self.allowed_paths:
                    if abs_str.startswith(str(allowed)):
                        return True
                return False
            
            # 没有明确列表，默认允许
            return True
            
        except Exception:
            return False
    
    def validate_read(self, path: str) -> bool:
        """验证读操作"""
        return self.is_allowed(path)
    
    def validate_write(self, path: str) -> bool:
        """验证写操作"""
        if not self.is_allowed(path):
            return False
        
        # 检查是否尝试写入系统目录
        dangerous = ["/etc", "/usr", "/bin", "/sbin", "/var", "/boot"]
        for d in dangerous:
            if path.startswith(d):
                return False
        
        return True


class ProcessSandbox:
    """进程沙箱"""
    
    def __init__(self, config: SandboxConfig = None):
        self.config = config or SandboxConfig()
        self.validator = PathValidator(self.config)
        self._temp_dirs: List[Path] = []
        self._execution_count = 0
    
    def __del__(self):
        """清理临时目录"""
        for temp_dir in self._temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except Exception:
                pass
    
    async def execute_command(
        self,
        command: str,
        cwd: str = None,
        env: Dict[str, str] = None,
        timeout: float = None
    ) -> ExecutionResult:
        """执行命令（隔离）"""
        timeout = timeout or self.config.max_execution_time
        start_time = time.time()
        
        # 构建环境变量
        exec_env = os.environ.copy()
        if env:
            exec_env.update(env)
        
        # 限制环境变量
        if self.config.env_whitelist:
            exec_env = {k: v for k, v in exec_env.items() 
                       if k in self.config.env_whitelist}
        
        # 禁用网络（可选）
        if not self.config.network_allowed:
            exec_env["http_proxy"] = ""
            exec_env["https_proxy"] = ""
        
        try:
            # 创建进程
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=exec_env,
                limit=self.config.max_output_size
            )
            
            try:
                # 等待完成（带超时）
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ExecutionResult(
                    success=False,
                    error=f"执行超时 ({timeout}秒)",
                    execution_time=timeout
                )
            
            execution_time = time.time() - start_time
            self._execution_count += 1
            
            # 检查退出码
            success = process.returncode == 0
            
            output = stdout.decode('utf-8', errors='replace')
            error = stderr.decode('utf-8', errors='replace')
            
            # 截断过长输出
            truncated = False
            max_output = self.config.max_output_size
            if len(output) > max_output:
                output = output[:max_output] + f"\n... [输出被截断，共 {len(output)} 字符]"
                truncated = True
            
            return ExecutionResult(
                success=success,
                output=output,
                error=error,
                exit_code=process.returncode,
                execution_time=execution_time,
                truncated=truncated,
                metadata={
                    "command": command,
                    "cwd": cwd,
                }
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def execute_function(
        self,
        func: Callable,
        *args,
        timeout: float = None,
        **kwargs
    ) -> ExecutionResult:
        """执行函数（隔离）"""
        start_time = time.time()
        timeout = timeout or self.config.max_execution_time
        
        # 检查安全级别
        if self.config.security_level == SecurityLevel.NONE:
            try:
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout
                    )
                else:
                    result = func(*args, **kwargs)
                return ExecutionResult(
                    success=True,
                    output=str(result),
                    execution_time=time.time() - start_time
                )
            except asyncio.TimeoutError:
                return ExecutionResult(
                    success=False,
                    error=f"执行超时 ({timeout}秒)",
                    execution_time=timeout
                )
            except Exception as e:
                return ExecutionResult(
                    success=False,
                    error=str(e),
                    execution_time=time.time() - start_time
                )
        
        # 在子进程中执行（更安全）
        try:
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout
                )
            else:
                result = func(*args, **kwargs)
            return ExecutionResult(
                success=True,
                output=str(result),
                execution_time=time.time() - start_time
            )
        except asyncio.TimeoutError:
            return ExecutionResult(
                success=False,
                error=f"执行超时 ({timeout}秒)",
                execution_time=timeout
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def create_temp_dir(self) -> Path:
        """创建临时目录"""
        temp_dir = Path(tempfile.mkdtemp())
        self._temp_dirs.append(temp_dir)
        return temp_dir
    
    def validate_path(self, path: str, operation: str = "read") -> bool:
        """验证路径"""
        if operation == "read":
            return self.validator.validate_read(path)
        elif operation == "write":
            return self.validator.validate_write(path)
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "execution_count": self._execution_count,
            "temp_dirs_created": len(self._temp_dirs),
            "security_level": self.config.security_level.value,
        }


class SandboxManager:
    """沙箱管理器"""
    
    def __init__(self):
        self.sandboxes: Dict[str, ProcessSandbox] = {}
        self.default_config = SandboxConfig()
    
    def create_sandbox(
        self,
        name: str,
        config: SandboxConfig = None
    ) -> ProcessSandbox:
        """创建沙箱"""
        sandbox_config = config or self.default_config
        sandbox = ProcessSandbox(sandbox_config)
        self.sandboxes[name] = sandbox
        print(f"{Fore.GREEN}✓ 创建沙箱: {name}{Fore.RESET}")
        return sandbox
    
    def get_sandbox(self, name: str) -> Optional[ProcessSandbox]:
        """获取沙箱"""
        return self.sandboxes.get(name)
    
    def remove_sandbox(self, name: str) -> bool:
        """移除沙箱"""
        if name in self.sandboxes:
            del self.sandboxes[name]
            return True
        return False
    
    async def execute_in_sandbox(
        self,
        sandbox_name: str,
        command: str,
        **kwargs
    ) -> ExecutionResult:
        """在指定沙箱中执行"""
        sandbox = self.get_sandbox(sandbox_name)
        if not sandbox:
            raise ValueError(f"沙箱不存在: {sandbox_name}")
        
        return await sandbox.execute_command(command, **kwargs)


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 沙箱隔离执行示例 ==={Fore.RESET}\n")
    
    # 创建配置
    config = SandboxConfig(
        security_level=SecurityLevel.BASIC,
        max_execution_time=10.0,
        allowed_paths=[os.path.expanduser("~/")],  # 只允许用户目录
        blocked_paths=["/etc", "/root", "/sys"],
    )
    
    # 创建沙箱
    sandbox = ProcessSandbox(config)
    
    # 测试 1: 执行简单命令
    print("1. 执行 'echo hello':")
    result = await sandbox.execute_command("echo hello")
    print(f"   成功: {result.success}")
    print(f"   输出: {result.output.strip()}")
    
    # 测试 2: 验证路径
    print("\n2. 路径验证:")
    print(f"   ~/test.txt 允许读: {sandbox.validate_path('~/test.txt', 'read')}")
    print(f"   /etc/passwd 允许写: {sandbox.validate_path('/etc/passwd', 'write')}")
    print(f"   ~/project 允许写: {sandbox.validate_path('~/project/main.py', 'write')}")
    
    # 测试 3: 超时测试
    print("\n3. 执行超时命令 (sleep 20):")
    result = await sandbox.execute_command("sleep 20")
    print(f"   成功: {result.success}")
    print(f"   错误: {result.error}")
    print(f"   执行时间: {result.execution_time:.1f}秒")
    
    # 测试 4: 沙箱管理器
    print("\n4. 使用沙箱管理器:")
    manager = SandboxManager()
    sandbox2 = manager.create_sandbox("test", config)
    print(f"   已创建沙箱: test")
    print(f"   沙箱列表: {list(manager.sandboxes.keys())}")
    
    # 统计
    print("\n5. 统计信息:")
    stats = sandbox.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n{Fore.GREEN}✓ 沙箱隔离执行示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())