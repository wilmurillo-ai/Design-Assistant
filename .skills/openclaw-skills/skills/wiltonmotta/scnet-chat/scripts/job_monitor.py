#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet 作业监控器

功能：
1. 监控作业状态变化
2. 实时作业和历史作业自动切换查询
3. 状态结束时主动通知
4. 支持长时间运行作业（几小时到几天）

设计原则：
- 可靠性：异常恢复、网络重试
- 稳定性：状态机管理、避免重复通知
- 低资源：合理的轮询间隔
"""

import time
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
import threading
import requests

# 导入通知模块
from notifications import FeishuNotifier


class JobStatus(Enum):
    """作业状态枚举"""
    RUNNING = "statR"      # 运行中
    QUEUED = "statQ"       # 排队中
    WAITING = "statW"      # 等待中
    HELD = "statH"         # 保留
    SUSPENDED = "statS"    # 挂起
    EXITED = "statE"       # 退出
    COMPLETED = "statC"    # 完成
    TERMINATED = "statT"   # 终止
    DELETED = "statDE"     # 删除
    UNKNOWN = "unknown"    # 未知


class JobMonitor:
    """
    SCNet 作业监控器
    
    使用示例：
        monitor = JobMonitor(client)
        monitor.start_monitoring(
            job_id="110230634",
            on_status_change=callback_function,
            check_interval=60
        )
    """
    
    # 活跃状态列表（作业还在运行中）
    ACTIVE_STATUSES = [JobStatus.RUNNING, JobStatus.QUEUED, JobStatus.WAITING]
    
    # 状态中文映射
    STATUS_MAP = {
        "statR": "运行中",
        "statQ": "排队中",
        "statW": "等待中",
        "statH": "保留",
        "statS": "挂起",
        "statE": "退出",
        "statC": "完成",
        "statT": "终止",
        "statDE": "删除",
        "unknown": "未知"
    }
    
    def __init__(self, client, enable_feishu: bool = True):
        """
        初始化监控器
        
        Args:
            client: SCNetClient 实例
            enable_feishu: 是否启用飞书通知（默认启用，需配置webhook）
        """
        self.client = client
        self.monitoring_jobs = {}  # {job_id: monitor_thread}
        self.stop_flags = {}       # {job_id: bool}
        
        # 检查飞书是否已配置
        if enable_feishu:
            notifier = FeishuNotifier()
            self.feishu_enabled = notifier.webhook_url is not None
            if not self.feishu_enabled:
                print("💡 飞书通知未配置，仅使用会话窗口提示")
        else:
            self.feishu_enabled = False
        
    def _get_cluster_info(self) -> tuple:
        """获取当前计算中心信息"""
        cache_path = os.path.expanduser("~/.scnet-chat-cache.json")
        with open(cache_path, 'r') as f:
            cache = json.load(f)
        
        default_cluster = None
        for cluster in cache['clusters']:
            if cluster.get('default', False):
                default_cluster = cluster
                break
        
        if not default_cluster:
            return None, None, None
        
        hpc_url = default_cluster['hpcUrls'][0]['url']
        token = default_cluster['token']
        scheduler_id = default_cluster.get('clusterId', '')
        
        return hpc_url, token, scheduler_id
    
    def _query_realtime_job(self, job_id: str) -> Optional[Dict]:
        """查询实时作业详情"""
        from scnet_chat import query_job_detail
        
        hpc_url, token, scheduler_id = self._get_cluster_info()
        if not hpc_url or not token:
            return None
        
        try:
            result = query_job_detail(hpc_url, token, scheduler_id, job_id)
            if result and result.get('code') == '0':
                return result.get('data')
            return None
        except Exception as e:
            print(f"❌ 查询实时作业失败: {e}")
            return None
    
    def _query_history_job(self, job_id: str) -> Optional[Dict]:
        """查询历史作业详情"""
        from scnet_chat import query_history_jobs
        
        hpc_url, token, scheduler_id = self._get_cluster_info()
        if not hpc_url or not token:
            return None
        
        # 查询最近7天的历史作业
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        try:
            result = query_history_jobs(
                hpc_url, token, scheduler_id,
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                start=0, limit=100
            )
            
            if result and result.get('code') == '0':
                job_list = result.get('data', {}).get('list', [])
                for job in job_list:
                    if job.get('jobId') == job_id:
                        return job
            return None
        except Exception as e:
            print(f"❌ 查询历史作业失败: {e}")
            return None
    
    def _get_job_status(self, job_id: str) -> tuple:
        """
        获取作业状态（自动切换实时/历史查询）
        
        Returns:
            (status_code, job_data, source)
            status_code: statR/statQ/statC 等
            job_data: 完整作业数据
            source: 'realtime' 或 'history'
        """
        # 先查询实时作业
        job_data = self._query_realtime_job(job_id)
        if job_data:
            status = job_data.get('jobStatus', 'unknown')
            return status, job_data, 'realtime'
        
        # 实时查询不到，尝试历史作业
        job_data = self._query_history_job(job_id)
        if job_data:
            status = job_data.get('jobState', 'unknown')
            return status, job_data, 'history'
        
        return 'unknown', None, None
    
    def _is_active_status(self, status: str) -> bool:
        """检查状态是否为活跃状态（运行中/排队中/等待中）"""
        return status in [s.value for s in self.ACTIVE_STATUSES]
    
    def _monitor_loop(self, job_id: str, on_status_change: Callable, 
                      check_interval: int = 60, on_completed: Callable = None):
        """
        监控循环（在独立线程中运行）
        
        Args:
            job_id: 作业ID
            on_status_change: 状态变化回调函数
            check_interval: 检查间隔（秒）
            on_completed: 作业结束回调函数
        """
        print(f"🔍 开始监控作业 {job_id}")
        print(f"   检查间隔: {check_interval}秒")
        
        last_status = None
        last_source = None
        check_count = 0
        
        # 归档检测：当实时查询不到但之前查到时，增加历史查询频率
        archived_mode = False
        archived_check_interval = min(30, check_interval)  # 归档后更频繁检查
        
        while not self.stop_flags.get(job_id, False):
            check_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            try:
                status, job_data, source = self._get_job_status(job_id)
                
                # 状态变化时通知
                if status != last_status:
                    print(f"[{current_time}] 作业 {job_id} 状态变化: {last_status} -> {status}")
                    
                    status_info = {
                        'job_id': job_id,
                        'status': status,
                        'status_name': self.STATUS_MAP.get(status, status),
                        'previous_status': last_status,
                        'source': source,
                        'check_count': check_count,
                        'timestamp': current_time,
                        'data': job_data
                    }
                    
                    # 调用状态变化回调
                    if on_status_change:
                        try:
                            on_status_change(status_info)
                        except Exception as e:
                            print(f"❌ 状态回调执行失败: {e}")
                    
                    last_status = status
                    last_source = source
                
                # 检测是否进入归档模式（实时查不到，但历史能查到）
                if source == 'history' and not archived_mode:
                    print(f"[{current_time}] 作业已归档到历史记录，切换监控模式")
                    archived_mode = True
                
                # 检查作业是否结束（非活跃状态）
                if not self._is_active_status(status):
                    print(f"[{current_time}] 作业 {job_id} 已结束，状态: {status}")
                    
                    if on_completed:
                        try:
                            on_completed({
                                'job_id': job_id,
                                'final_status': status,
                                'status_name': self.STATUS_MAP.get(status, status),
                                'data': job_data,
                                'check_count': check_count
                            })
                        except Exception as e:
                            print(f"❌ 完成回调执行失败: {e}")
                    
                    break  # 退出监控循环
                
                # 等待下一次检查
                sleep_time = archived_check_interval if archived_mode else check_interval
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"[{current_time}] 监控异常: {e}")
                time.sleep(check_interval)  # 异常后等待一段时间再试
        
        print(f"✅ 作业 {job_id} 监控结束（共检查 {check_count} 次）")
        self.monitoring_jobs.pop(job_id, None)
        self.stop_flags.pop(job_id, None)
    
    def start_monitoring(self, job_id: str, 
                         on_status_change: Callable = None,
                         on_completed: Callable = None,
                         check_interval: int = 180) -> bool:
        """
        开始监控作业
        
        Args:
            job_id: 作业ID
            on_status_change: 状态变化回调，接收状态信息字典
            on_completed: 作业完成回调，接收完成信息字典
            check_interval: 检查间隔（秒），默认180秒
            
        Returns:
            是否成功启动监控
        """
        # 设置默认回调
        if on_status_change is None:
            on_status_change = lambda info: default_status_callback(info, self)
        if on_completed is None:
            on_completed = lambda info: default_completed_callback(info, self)
        
        if job_id in self.monitoring_jobs:
            print(f"⚠️ 作业 {job_id} 已经在监控中")
            return False
        
        # 先验证作业存在
        status, job_data, source = self._get_job_status(job_id)
        if not job_data:
            print(f"❌ 无法找到作业 {job_id}，请检查作业ID是否正确")
            return False
        
        print(f"✅ 找到作业 {job_id}，当前状态: {self.STATUS_MAP.get(status, status)} ({source})")
        
        # 如果作业已经结束，直接回调
        if not self._is_active_status(status):
            print(f"⚠️ 作业 {job_id} 已经结束，状态: {status}")
            if on_completed:
                on_completed({
                    'job_id': job_id,
                    'final_status': status,
                    'status_name': self.STATUS_MAP.get(status, status),
                    'data': job_data,
                    'check_count': 0
                })
            return True
        
        # 启动监控线程
        self.stop_flags[job_id] = False
        monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(job_id, on_status_change, check_interval, on_completed),
            daemon=True
        )
        monitor_thread.start()
        
        self.monitoring_jobs[job_id] = monitor_thread
        return True
    
    def stop_monitoring(self, job_id: str) -> bool:
        """停止监控指定作业"""
        if job_id not in self.monitoring_jobs:
            print(f"⚠️ 作业 {job_id} 未在监控中")
            return False
        
        self.stop_flags[job_id] = True
        self.monitoring_jobs[job_id].join(timeout=5)
        print(f"✅ 已停止监控作业 {job_id}")
        return True
    
    def stop_all(self):
        """停止所有监控"""
        for job_id in list(self.monitoring_jobs.keys()):
            self.stop_monitoring(job_id)

    def feishu_notify(self, title: str, content: str, template: str = "blue") -> bool:
        """
        发送飞书文字卡片通知
        
        Args:
            title: 卡片标题
            content: 卡片内容（支持 Markdown）
            template: 卡片颜色主题 (blue/green/red/orange/purple)
            
        Returns:
            是否发送成功
        """
        if not self.feishu_enabled:
            return False
        
        notifier = FeishuNotifier()
        return notifier.send_card(title, content, template)


# ============== 通知回调示例 ==============

def default_status_callback(info: Dict, monitor=None):
    """默认状态变化回调 - 会话窗口通知 + 飞书通知（可选）"""
    job_id = info['job_id']
    status = info['status']
    status_name = info['status_name']
    
    # ========== 会话窗口主动消息提示（默认通知方式）==========
    # 使用醒目的格式输出到控制台，确保用户能看到
    print("\n" + "="*60)
    print(f"  🔔 【作业状态变化】")
    print("="*60)
    print(f"  📋 作业ID:     {job_id}")
    print(f"  📊 当前状态:   {status_name} ({status})")
    print(f"  📡 数据来源:   {info['source']}")
    print(f"  🔢 检查次数:   {info['check_count']}")
    print(f"  🕐 时间:       {info['timestamp']}")
    print("="*60)
    
    # 根据状态添加提示信息
    if status == 'statR':
        print("  💡 作业开始运行")
    elif status == 'statQ':
        print("  ⏳ 作业正在排队，请稍候...")
    elif status == 'statW':
        print("  ⏸️  作业处于等待状态")
    elif status == 'statC':
        print("  ✅ 作业已完成")
    elif status == 'statT':
        print("  ⚠️  作业被终止")
    elif status == 'statE':
        print("  ❌ 作业异常退出")
    print("="*60)
    
    # 刷新输出确保消息立即显示
    sys.stdout.flush()
    
    # ========== 飞书通知（可选，需配置webhook）==========
    if monitor and monitor.feishu_enabled:
        # 根据状态选择颜色主题
        if status == 'statR':
            template = "green"   # 运行中 - 绿色
        elif status in ['statQ', 'statW']:
            template = "orange"  # 排队/等待 - 橙色
        else:
            template = "blue"    # 其他 - 蓝色
        
        title = f"作业状态变化 - {status_name}"
        
        content = f"**作业ID:** {job_id}\n\n" \
                  f"**当前状态:** {status_name} ({status})\n\n" \
                  f"**数据来源:** {info['source']}\n\n" \
                  f"**检查次数:** {info['check_count']}\n\n" \
                  f"**时间:** {info['timestamp']}"
        
        monitor.feishu_notify(title, content, template)


def default_completed_callback(info: Dict, monitor=None):
    """默认完成回调 - 会话窗口通知 + 飞书通知（可选）"""
    job_id = info['job_id']
    final_status = info['final_status']
    status_name = info['status_name']
    
    # 根据最终状态选择图标
    if final_status == 'statC':
        status_icon = "✅"
        status_desc = "作业成功完成"
    elif final_status == 'statT':
        status_icon = "⚠️ "
        status_desc = "作业被终止"
    elif final_status == 'statE':
        status_icon = "❌"
        status_desc = "作业异常退出"
    else:
        status_icon = "ℹ️ "
        status_desc = "作业结束"
    
    # ========== 会话窗口主动消息提示（默认通知方式）==========
    print("\n" + "="*60)
    print(f"  {status_icon} 【作业完成通知】")
    print("="*60)
    print(f"  📋 作业ID:     {job_id}")
    print(f"  📊 最终状态:   {status_name} ({final_status})")
    print(f"  🔢 总检查次数: {info['check_count']}")
    
    # 作业详细信息
    data = info.get('data', {})
    if data:
        job_name = data.get('jobName', data.get('job_name', 'N/A'))
        runtime = data.get('jobWalltimeUsed', data.get('jobRunTime', 'N/A'))
        node = data.get('jobExecHost', data.get('nodeUsed', 'N/A'))
        print(f"  📝 作业名称:   {job_name}")
        print(f"  ⏱️  运行时长:   {runtime}")
        print(f"  🖥️  执行节点:   {node}")
    
    print("="*60)
    print(f"  {status_desc}")
    print("="*60)
    
    # 刷新输出确保消息立即显示
    sys.stdout.flush()
    
    # ========== 飞书通知（可选，需配置webhook）==========
    if monitor and monitor.feishu_enabled:
        # 根据最终状态选择颜色主题
        if final_status == 'statC':
            template = "green"   # 完成 - 绿色
            emoji = "🎉"
        elif final_status == 'statT':
            template = "red"     # 终止 - 红色
            emoji = "⚠️"
        elif final_status == 'statE':
            template = "orange"  # 退出 - 橙色
            emoji = "❌"
        else:
            template = "blue"    # 其他 - 蓝色
            emoji = "ℹ️"
        
        title = f"{emoji} 作业完成通知"
        
        content = f"**作业ID:** {job_id}\n\n" \
                  f"**最终状态:** {status_name} ({final_status})\n\n" \
                  f"**总检查次数:** {info['check_count']}"
        
        if data:
            job_name = data.get('jobName', data.get('job_name', 'N/A'))
            runtime = data.get('jobWalltimeUsed', data.get('jobRunTime', 'N/A'))
            node = data.get('jobExecHost', data.get('nodeUsed', 'N/A'))
            content += f"\n\n**作业名称:** {job_name}\n\n" \
                      f"**运行时长:** {runtime}\n\n" \
                      f"**执行节点:** {node}"
        
        monitor.feishu_notify(title, content, template)


# ============== 测试用例 ==============

def test_monitor_new_job():
    """测试监控新提交的作业"""
    print("="*60)
    print("测试1: 监控新提交的作业")
    print("="*60)
    
    from scnet_chat import SCNetClient
    import config_manager
    
    config = config_manager.load_config()
    client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
    client.init_tokens()
    
    # 提交一个短作业用于测试
    job_config = {
        'job_name': 'test_monitor_job',
        'cmd': 'sleep 30',  # 30秒的测试作业
        'nnodes': '1',
        'ppn': '1',
        'queue': 'comp',
        'wall_time': '00:05:00',
        'work_dir': '/public/home/ac1npa3sf2/job_example/'
    }
    
    result = client.submit_job(job_config)
    if result and result.get('code') == '0':
        job_id = result.get('data')
        print(f"✅ 测试作业已提交: {job_id}")
        
        # 开始监控
        monitor = JobMonitor(client)
        monitor.start_monitoring(
            job_id=job_id,
            on_status_change=default_status_callback,
            on_completed=default_completed_callback,
            check_interval=180  # 测试用10秒间隔
        )
        
        # 等待监控完成
        time.sleep(60)
        monitor.stop_all()
    else:
        print(f"❌ 作业提交失败: {result}")


def test_monitor_existing_job():
    """测试监控已存在的作业"""
    print("="*60)
    print("测试2: 监控已存在的作业")
    print("="*60)
    
    from scnet_chat import SCNetClient
    import config_manager
    
    config = config_manager.load_config()
    client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
    client.init_tokens()
    
    # 使用已知作业ID测试
    job_id = '110230634'  # 已完成的作业
    
    monitor = JobMonitor(client)
    
    # 测试查询
    status, data, source = monitor._get_job_status(job_id)
    print(f"查询结果: {status} ({source})")
    
    if data:
        print(f"作业名称: {data.get('jobName', data.get('job_name', 'N/A'))}")
        print(f"状态: {JobMonitor.STATUS_MAP.get(status, status)}")


def test_auto_archive_detection():
    """测试归档自动检测"""
    print("="*60)
    print("测试3: 归档自动检测")
    print("="*60)
    
    from scnet_chat import SCNetClient
    import config_manager
    
    config = config_manager.load_config()
    client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
    client.init_tokens()
    
    monitor = JobMonitor(client)
    
    # 测试已完成的作业（应该在历史中）
    job_id = '110230634'
    
    print(f"查询作业 {job_id}:")
    
    # 实时查询
    realtime_data = monitor._query_realtime_job(job_id)
    print(f"  实时查询: {'找到' if realtime_data else '未找到'}")
    
    # 历史查询
    history_data = monitor._query_history_job(job_id)
    print(f"  历史查询: {'找到' if history_data else '未找到'}")
    
    if history_data:
        print(f"  状态: {history_data.get('jobState', 'N/A')}")
        print(f"  开始时间: {history_data.get('jobStartTime', 'N/A')}")
        print(f"  结束时间: {history_data.get('jobEndTime', 'N/A')}")


def test_long_running_job():
    """测试长时间运行作业的监控"""
    print("="*60)
    print("测试4: 长时间运行作业监控（模拟）")
    print("="*60)
    
    print("长时间作业监控要点:")
    print("1. 使用较长的检查间隔（默认60秒，可配置为300秒/5分钟）")
    print("2. 网络异常时自动重试")
    print("3. 归档后自动切换到历史查询模式")
    print("4. 系统资源占用低（单线程轮询）")
    print()
    print("建议配置:")
    print("  - 短作业（<1小时）: check_interval=60")
    print("  - 中作业（1-24小时）: check_interval=300")
    print("  - 长作业（>24小时）: check_interval=600")


if __name__ == "__main__":
    print("SCNet 作业监控器测试")
    print("="*60)
    print()
    
    # 运行测试
    test_monitor_existing_job()
    print()
    
    test_auto_archive_detection()
    print()
    
    test_long_running_job()
    print()
    
    # 可选：测试新作业提交和监控
    # test_monitor_new_job()
