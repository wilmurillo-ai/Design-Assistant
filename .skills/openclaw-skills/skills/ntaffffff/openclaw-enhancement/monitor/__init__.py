#!/usr/bin/env python3
"""
状态监控模块

实时监控系统资源、运行状态、性能指标
"""

import asyncio
import psutil
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class Fore:
        CYAN = GREEN = RED = YELLOW = BLUE = ""


class HealthStatus(Enum):
    """健康状态"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class Metric:
    """指标"""
    name: str
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class HealthCheck:
    """健康检查"""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class SystemMonitor:
    """系统监控"""
    
    def __init__(self):
        self.metrics_history: Dict[str, List[Metric]] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._callbacks: Dict[str, List[Callable]] = {
            "on_metric": [],
            "on_health_change": []
        }
        
        # 阈值配置
        self.thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "network_sent_mb": 1000,
        }
    
    def _emit(self, event: str, *args, **kwargs):
        """触发回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"{Fore.YELLOW}⚠ 回调失败: {e}{Fore.RESET}")
    
    def register_callback(self, event: str, callback: Callable):
        """注册回调"""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def collect_system_metrics(self) -> Dict[str, Metric]:
        """收集系统指标"""
        metrics = {}
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        metrics["cpu_percent"] = Metric(
            name="cpu_percent",
            value=cpu_percent,
            unit="%"
        )
        
        # 内存
        mem = psutil.virtual_memory()
        metrics["memory_percent"] = Metric(
            name="memory_percent",
            value=mem.percent,
            unit="%"
        )
        metrics["memory_used_mb"] = Metric(
            name="memory_used_mb",
            value=mem.used / (1024 * 1024),
            unit="MB"
        )
        
        # 磁盘
        disk = psutil.disk_usage('/')
        metrics["disk_percent"] = Metric(
            name="disk_percent",
            value=disk.percent,
            unit="%"
        )
        
        # 网络
        net = psutil.net_io_counters()
        metrics["network_sent_mb"] = Metric(
            name="network_sent_mb",
            value=net.bytes_sent / (1024 * 1024),
            unit="MB"
        )
        metrics["network_recv_mb"] = Metric(
            name="network_recv_mb",
            value=net.bytes_recv / (1024 * 1024),
            unit="MB"
        )
        
        # 进程数
        metrics["process_count"] = Metric(
            name="process_count",
            value=len(psutil.pids()),
            unit="count"
        )
        
        return metrics
    
    def _check_health(self, metrics: Dict[str, Metric]) -> Dict[str, HealthCheck]:
        """检查健康状态"""
        checks = {}
        
        # CPU 检查
        cpu = metrics.get("cpu_percent")
        if cpu:
            if cpu.value >= self.thresholds["cpu_percent"]:
                status = HealthStatus.CRITICAL
            elif cpu.value >= self.thresholds["cpu_percent"] * 0.8:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.HEALTHY
            
            checks["cpu"] = HealthCheck(
                name="CPU",
                status=status,
                message=f"CPU 使用率: {cpu.value:.1f}%",
                details={"value": cpu.value, "threshold": self.thresholds["cpu_percent"]}
            )
        
        # 内存检查
        mem = metrics.get("memory_percent")
        if mem:
            if mem.value >= self.thresholds["memory_percent"]:
                status = HealthStatus.CRITICAL
            elif mem.value >= self.thresholds["memory_percent"] * 0.8:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.HEALTHY
            
            checks["memory"] = HealthCheck(
                name="Memory",
                status=status,
                message=f"内存使用: {mem.value:.1f}%",
                details={"value": mem.value, "threshold": self.thresholds["memory_percent"]}
            )
        
        # 磁盘检查
        disk = metrics.get("disk_percent")
        if disk:
            if disk.value >= self.thresholds["disk_percent"]:
                status = HealthStatus.CRITICAL
            elif disk.value >= self.thresholds["disk_percent"] * 0.8:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.HEALTHY
            
            checks["disk"] = HealthCheck(
                name="Disk",
                status=status,
                message=f"磁盘使用: {disk.value:.1f}%",
                details={"value": disk.value, "threshold": self.thresholds["disk_percent"]}
            )
        
        return checks
    
    async def start_monitoring(self, interval: float = 5.0):
        """开始监控"""
        self._monitoring = True
        
        async def monitor_loop():
            while self._monitoring:
                try:
                    # 收集指标
                    metrics = await self.collect_system_metrics()
                    
                    # 记录历史
                    for name, metric in metrics.items():
                        if name not in self.metrics_history:
                            self.metrics_history[name] = []
                        
                        self.metrics_history[name].append(metric)
                        
                        # 只保留最近100条
                        if len(self.metrics_history[name]) > 100:
                            self.metrics_history[name] = self.metrics_history[name][-100:]
                    
                    # 健康检查
                    health_checks = self._check_health(metrics)
                    
                    # 检查状态变化
                    for name, check in health_checks.items():
                        old_check = self.health_checks.get(name)
                        if old_check and old_check.status != check.status:
                            self._emit("on_health_change", name, old_check.status, check.status)
                        
                        self.health_checks[name] = check
                    
                    # 指标回调
                    for metric in metrics.values():
                        self._emit("on_metric", metric)
                    
                    await asyncio.sleep(interval)
                    
                except Exception as e:
                    print(f"{Fore.RED}✗ 监控错误: {e}{Fore.RESET}")
                    await asyncio.sleep(interval)
        
        self._monitor_task = asyncio.create_task(monitor_loop())
    
    async def stop_monitoring(self):
        """停止监控"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
    
    def get_current_metrics(self) -> Dict[str, Metric]:
        """获取当前指标"""
        result = {}
        for name, history in self.metrics_history.items():
            if history:
                result[name] = history[-1]
        return result
    
    def get_health_status(self) -> Dict[str, HealthCheck]:
        """获取健康状态"""
        return self.health_checks.copy()
    
    def get_overall_health(self) -> HealthStatus:
        """获取整体健康状态"""
        if not self.health_checks:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in self.health_checks.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        elif HealthStatus.HEALTHY in statuses:
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN
    
    def get_metric_history(self, metric_name: str, limit: int = 10) -> List[Metric]:
        """获取指标历史"""
        history = self.metrics_history.get(metric_name, [])
        return history[-limit:]


class ResourceTracker:
    """资源追踪器"""
    
    def __init__(self):
        self.tracked_resources: Dict[str, Dict] = {}
    
    def track(self, resource_id: str, resource_type: str, metadata: Dict = None):
        """追踪资源"""
        self.tracked_resources[resource_id] = {
            "type": resource_type,
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "last_accessed": datetime.now(),
            "access_count": 0
        }
    
    def access(self, resource_id: str):
        """访问资源"""
        if resource_id in self.tracked_resources:
            self.tracked_resources[resource_id]["last_accessed"] = datetime.now()
            self.tracked_resources[resource_id]["access_count"] += 1
    
    def untrack(self, resource_id: str) -> bool:
        """取消追踪"""
        if resource_id in self.tracked_resources:
            del self.tracked_resources[resource_id]
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计"""
        return {
            "total_tracked": len(self.tracked_resources),
            "by_type": self._count_by_type()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """按类型统计"""
        counts = {}
        for res in self.tracked_resources.values():
            t = res["type"]
            counts[t] = counts.get(t, 0) + 1
        return counts


# ============ 使用示例 ============

async def example():
    """示例"""
    print(f"{Fore.CYAN}=== 状态监控示例 ==={Fore.RESET}\n")
    
    # 创建监控器
    monitor = SystemMonitor()
    
    # 注册回调
    def on_metric(metric):
        print(f"   指标: {metric.name} = {metric.value:.1f}{metric.unit}")
    
    def on_health_change(name, old_status, new_status):
        print(f"   ⚠️ 健康状态变化: {name} {old_status.value} → {new_status.value}")
    
    monitor.register_callback("on_metric", on_metric)
    monitor.register_callback("on_health_change", on_health_change)
    
    # 收集一次指标
    print("1. 系统指标:")
    metrics = await monitor.collect_system_metrics()
    for name, metric in metrics.items():
        print(f"   {name}: {metric.value:.1f}{metric.unit}")
    
    # 健康检查
    print("\n2. 健康检查:")
    health = monitor.get_health_status()
    for name, check in health.items():
        color = Fore.GREEN if check.status == HealthStatus.HEALTHY else Fore.YELLOW
        print(f"   {color}{check.name}: {check.message}{Fore.RESET}")
    
    # 资源追踪
    print("\n3. 资源追踪:")
    tracker = ResourceTracker()
    tracker.track("file_1", "file", {"path": "/tmp/test.txt"})
    tracker.track("session_1", "session", {"user": "alice"})
    tracker.access("file_1")
    
    stats = tracker.get_stats()
    print(f"   追踪数量: {stats['total_tracked']}")
    print(f"   按类型: {stats['by_type']}")
    
    print(f"\n{Fore.GREEN}✓ 状态监控示例完成!{Fore.RESET}")


if __name__ == "__main__":
    asyncio.run(example())