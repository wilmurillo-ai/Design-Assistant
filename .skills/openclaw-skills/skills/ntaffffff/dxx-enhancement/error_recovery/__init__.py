#!/usr/bin/env python3
"""
错误自动恢复模块

多层异常处理 + 自我修复机制
参考 Claude Code 的错误处理
"""

import asyncio
import traceback
import sys
from typing import Callable, Any, Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import functools

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


class ErrorLevel(Enum):
    """错误级别"""
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"           # 重试
    FALLBACK = "fallback"     # 降级处理
    SKIP = "skip"             # 跳过
    ROLLBACK = "rollback"     # 回滚
    NOTIFY = "notify"         # 通知用户


@dataclass
class ErrorRecord:
    """错误记录"""
    id: str
    error_type: str
    message: str
    traceback: str
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    recovered: bool = False
    recovery_strategy: Optional[str] = None


@dataclass
class RetryConfig:
    """重试配置"""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0


class ErrorRecovery:
    """错误恢复"""
    
    def __init__(self):
        self.error_history: List[ErrorRecord] = []
        self.max_history = 100
    
    def record_error(self, error: Exception, context: Dict = None) -> ErrorRecord:
        """记录错误"""
        record = ErrorRecord(
            id=f"err_{len(self.error_history)}",
            error_type=type(error).__name__,
            message=str(error),
            traceback=traceback.format_exc(),
            context=context or {}
        )
        
        self.error_history.append(record)
        
        # 保持历史大小
        if len(self.error_history) > self.max_history:
            self.error_history = self.error_history[-self.max_history:]
        
        return record
    
    def get_recent_errors(self, limit: int = 10) -> List[ErrorRecord]:
        """获取最近的错误"""
        return self.error_history[-limit:]
    
    def get_error_count(self, since: datetime = None) -> int:
        """获取错误数量"""
        if since:
            return len([e for e in self.error_history if e.timestamp >= since])
        return len(self.error_history)


def retry_on_error(
    config: RetryConfig = None,
    on_retry: Callable = None,
    on_failure: Callable = None
):
    """重试装饰器"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            delay = config.initial_delay
            last_error = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    if attempt < config.max_retries:
                        if on_retry:
                            on_retry(attempt, e, delay)
                        
                        await asyncio.sleep(delay)
                        
                        # 指数退避
                        if config.exponential_backoff:
                            delay = min(delay * config.backoff_multiplier, config.max_delay)
                    else:
                        if on_failure:
                            on_failure(e)
                        raise
            
            raise last_error
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            delay = config.initial_delay
            last_error = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    
                    if attempt < config.max_retries:
                        if on_retry:
                            on_retry(attempt, e, delay)
                        
                        import time
                        time.sleep(delay)
                        
                        if config.exponential_backoff:
                            delay = min(delay * config.backoff_multiplier, config.max_delay)
                    else:
                        if on_failure:
                            on_failure(e)
                        raise
            
            raise last_error
        
        # 根据函数类型返回对应包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def fallback_on_error(fallback_value: Any = None, fallback_func: Callable = None):
    """降级处理装饰器"""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ {func.__name__} 执行失败，使用降级处理: {e}{Fore.RESET}")
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                return fallback_value
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ {func.__name__} 执行失败，使用降级处理: {e}{Fore.RESET}")
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                return fallback_value
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


class CircuitBreaker:
    """熔断器 - 防止连续失败"""
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """调用函数"""
        if self.state == "open":
            # 检查是否应该进入半开状态
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                if time_since_failure >= self.recovery_timeout:
                    self.state = "half-open"
                else:
                    raise Exception(f"熔断器打开，拒绝调用: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            
            # 成功，关闭熔断器
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
                print(f"{Fore.GREEN}✓ 熔断器已关闭{Fore.RESET}")
            
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                print(f"{Fore.RED}✗ 熔断器打开，连续 {self.failure_count} 次失败{Fore.RESET}")
            
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """异步调用"""
        if self.state == "open":
            if self.last_failure_time:
                time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
                if time_since_failure >= self.recovery_timeout:
                    self.state = "half-open"
                else:
                    raise Exception(f"熔断器打开，拒绝调用: {func.__name__}")
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise
    
    def reset(self):
        """重置熔断器"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"


class ErrorHandler:
    """全局错误处理器"""
    
    def __init__(self):
        self.handlers: Dict[type, Callable] = {}
        self.global_handler: Optional[Callable] = None
    
    def register_handler(self, error_type: type, handler: Callable):
        """注册错误处理器"""
        self.handlers[error_type] = handler
    
    def set_global_handler(self, handler: Callable):
        """设置全局处理器"""
        self.global_handler = handler
    
    def handle(self, error: Exception, context: Dict = None) -> Any:
        """处理错误"""
        error_type = type(error)
        
        # 查找特定处理器
        handler = self.handlers.get(error_type)
        if handler:
            return handler(error, context)
        
        # 查找父类处理器
        for err_type, h in self.handlers.items():
            if isinstance(error, err_type):
                return h(error, context)
        
        # 全局处理器
        if self.global_handler:
            return self.global_handler(error, context)
        
        # 默认处理
        print(f"{Fore.RED}✗ 未处理的错误: {error_type.__name__}: {error}{Fore.RESET}")
        return None


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 错误自动恢复示例 ==={Fore.RESET}\n")
    
    recovery = ErrorRecovery()
    
    # 1. 重试装饰器
    print("1. 重试装饰器:")
    
    config = RetryConfig(max_retries=3, initial_delay=0.5)
    attempt_count = 0
    
    @retry_on_error(config)
    async def unreliable_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ValueError("模拟失败")
        return "成功!"
    
    result = await unreliable_function()
    print(f"   结果: {result}")
    
    # 2. 降级处理
    print("\n2. 降级处理:")
    
    @fallback_on_error(fallback_value="默认值")
    async def might_fail():
        raise ValueError("失败了")
    
    result = await might_fail()
    print(f"   结果: {result}")
    
    # 3. 熔断器
    print("\n3. 熔断器:")
    
    cb = CircuitBreaker(failure_threshold=3, recovery_timeout=10)
    fail_count = 0
    
    def might_fail_func():
        nonlocal fail_count
        fail_count += 1
        if fail_count <= 3:
            raise ValueError("失败")
        return "成功"
    
    for i in range(6):
        try:
            cb.call(might_fail_func)
            print(f"   第{i+1}次: 成功")
        except Exception as e:
            print(f"   第{i+1}次: 失败 - {e}")
    
    # 4. 记录错误
    print("\n4. 错误记录:")
    
    try:
        raise ValueError("测试错误")
    except Exception as e:
        record = recovery.record_error(e, {"source": "test"})
        print(f"   错误ID: {record.id}")
        print(f"   类型: {record.error_type}")
        print(f"   消息: {record.message}")
    
    # 5. 错误处理器
    print("\n5. 错误处理器:")
    
    handler = ErrorHandler()
    
    def handle_value_error(error, context):
        print(f"   捕获 ValueError: {error}")
        return "已处理"
    
    handler.register_handler(ValueError, handle_value_error)
    handler.handle(ValueError("测试"), {})
    
    print(f"\n{Fore.GREEN}✓ 错误自动恢复示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())