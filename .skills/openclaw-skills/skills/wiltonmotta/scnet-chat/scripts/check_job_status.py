#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet 作业状态检查脚本

用于 cron 定时任务检查作业状态，作业完成后发送飞书通知

使用方法:
    python3 check_job_status.py <job_id>
    
示例:
    python3 check_job_status.py 27871
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# 添加技能目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scnet_chat import SCNetClient, query_job_detail, query_history_jobs
import config_manager
from notifications import send_feishu_text


def get_job_status(job_id: str, client: SCNetClient) -> tuple:
    """
    获取作业状态
    
    Returns:
        (status, data, source)
    """
    # 获取计算中心信息
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
    
    # 先查询实时作业
    try:
        result = query_job_detail(hpc_url, token, scheduler_id, job_id)
        if result and result.get('code') == '0' and result.get('data'):
            data = result.get('data')
            status = data.get('jobStatus', 'unknown')
            return status, data, 'realtime'
    except Exception as e:
        pass
    
    # 查询历史作业
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
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
                    return job.get('jobState', 'unknown'), job, 'history'
    except Exception as e:
        pass
    
    return None, None, None


def check_and_notify(job_id: str):
    """检查作业状态并发送通知"""
    
    STATUS_MAP = {
        "statR": "运行中", "statQ": "排队中", "statW": "等待中",
        "statH": "保留", "statS": "挂起", "statE": "退出",
        "statC": "完成", "statT": "终止", "statDE": "删除",
        "unknown": "未知"
    }
    
    ACTIVE_STATUSES = ['statR', 'statQ', 'statW']
    
    # 记录文件路径
    notified_file = os.path.expanduser(f"~/.scnet-job-notified-{job_id}.json")
    
    # 检查是否已通知过
    if os.path.exists(notified_file):
        print(f"作业 {job_id} 已通知过，跳过")
        return
    
    # 初始化客户端
    config = config_manager.load_config()
    client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
    client.init_tokens()
    
    # 获取作业状态
    status, data, source = get_job_status(job_id, client)
    
    if not status:
        print(f"未找到作业 {job_id}")
        return
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cluster_name = client.get_default_cluster_name()
    
    print(f"[{current_time}] 作业 {job_id} 状态: {STATUS_MAP.get(status, status)} ({source})")
    
    # 如果作业仍在运行中，不发送通知
    if status in ACTIVE_STATUSES:
        print(f"作业仍在运行中，继续监控...")
        return
    
    # 作业已结束，发送通知
    runtime = "N/A"
    node = "N/A"
    job_name = "N/A"
    
    if data:
        runtime = data.get('jobWalltimeUsed', data.get('jobRunTime', 'N/A'))
        node = data.get('jobExecHost', data.get('nodeUsed', 'N/A'))
        job_name = data.get('jobName', data.get('job_name', 'N/A'))
    
    # 构建通知消息
    if status == 'statC':
        emoji = "🎉"
        status_text = "已完成"
    elif status == 'statT':
        emoji = "⚠️"
        status_text = "已终止"
    elif status == 'statE':
        emoji = "❌"
        status_text = "已退出"
    else:
        emoji = "ℹ️"
        status_text = STATUS_MAP.get(status, status)
    
    message = f"【SCNet作业完成通知】{emoji}\n" \
             f"作业ID: {job_id}\n" \
             f"作业名称: {job_name}\n" \
             f"最终状态: {status_text} ({status})\n" \
             f"运行时长: {runtime}\n" \
             f"执行节点: {node}\n" \
             f"计算中心: {cluster_name}\n" \
             f"检查时间: {current_time}"
    
    print(f"发送飞书通知...")
    if send_feishu_text(message):
        print(f"✅ 通知发送成功")
        
        # 记录已通知
        notified_data = {
            'job_id': job_id,
            'status': status,
            'notified_at': current_time,
            'cluster': cluster_name
        }
        with open(notified_file, 'w', encoding='utf-8') as f:
            json.dump(notified_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已记录通知状态到 {notified_file}")
    else:
        print(f"❌ 通知发送失败")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 check_job_status.py <job_id>")
        print("示例: python3 check_job_status.py 27871")
        sys.exit(1)
    
    job_id = sys.argv[1]
    check_and_notify(job_id)
