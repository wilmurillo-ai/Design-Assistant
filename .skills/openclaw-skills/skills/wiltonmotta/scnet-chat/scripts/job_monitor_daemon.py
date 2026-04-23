#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet 作业持久化监控服务

使用方法:
    python3 job_monitor_daemon.py --job-id 27871 --interval 180

功能:
    1. 持续监控作业状态直到完成
    2. 支持飞书通知
    3. 记录完整监控日志
    4. 可后台运行 (nohup)
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime

# 添加技能目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scnet_chat import SCNetClient, query_job_detail, query_history_jobs
import config_manager
from notifications import send_feishu_text


def monitor_job(job_id: str, check_interval: int = 180):
    """监控作业直到完成"""
    
    print(f"🔍 开始监控作业 {job_id}")
    print(f"   检查间隔: {check_interval}秒")
    print(f"   开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # 初始化客户端
    config = config_manager.load_config()
    client = SCNetClient(config['access_key'], config['secret_key'], config['user'])
    client.init_tokens()
    
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
        print("❌ 未找到默认计算中心")
        return
    
    hpc_url = default_cluster['hpcUrls'][0]['url']
    token = default_cluster['token']
    scheduler_id = default_cluster.get('clusterId', '')
    cluster_name = default_cluster.get('clusterName', 'Unknown')
    
    STATUS_MAP = {
        "statR": "运行中", "statQ": "排队中", "statW": "等待中",
        "statH": "保留", "statS": "挂起", "statE": "退出",
        "statC": "完成", "statT": "终止", "statDE": "删除",
        "unknown": "未知"
    }
    
    ACTIVE_STATUSES = ['statR', 'statQ', 'statW']
    
    last_status = None
    check_count = 0
    archived_mode = False
    
    try:
        while True:
            check_count += 1
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 查询实时作业
            try:
                result = query_job_detail(hpc_url, token, scheduler_id, job_id)
                if result and result.get('code') == '0' and result.get('data'):
                    data = result.get('data')
                    status = data.get('jobStatus', 'unknown')
                    source = 'realtime'
                else:
                    # 实时查不到，查询历史
                    from datetime import timedelta
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
                        data = None
                        for job in job_list:
                            if job.get('jobId') == job_id:
                                data = job
                                status = job.get('jobState', 'unknown')
                                source = 'history'
                                break
                        else:
                            print(f"[{current_time}] 未找到作业 {job_id}")
                            time.sleep(check_interval)
                            continue
                    else:
                        print(f"[{current_time}] 查询失败")
                        time.sleep(check_interval)
                        continue
            except Exception as e:
                print(f"[{current_time}] 查询异常: {e}")
                time.sleep(check_interval)
                continue
            
            # 状态变化通知
            if status != last_status:
                print(f"[{current_time}] 状态变化: {last_status} -> {status}")
                
                # 发送飞书通知
                message = f"【SCNet作业状态变化】\n" \
                         f"作业ID: {job_id}\n" \
                         f"当前状态: {STATUS_MAP.get(status, status)} ({status})\n" \
                         f"计算中心: {cluster_name}\n" \
                         f"检查次数: {check_count}\n" \
                         f"时间: {current_time}"
                send_feishu_text(message)
                
                last_status = status
            
            # 检查是否归档
            if source == 'history' and not archived_mode:
                print(f"[{current_time}] 作业已归档，切换监控模式")
                archived_mode = True
            
            # 检查是否结束
            if status not in ACTIVE_STATUSES:
                print(f"[{current_time}] 作业已结束")
                
                # 发送完成通知
                runtime = "N/A"
                node = "N/A"
                if data:
                    runtime = data.get('jobWalltimeUsed', data.get('jobRunTime', 'N/A'))
                    node = data.get('jobExecHost', data.get('nodeUsed', 'N/A'))
                
                message = f"【SCNet作业完成】🎉\n" \
                         f"作业ID: {job_id}\n" \
                         f"作业名称: {data.get('jobName', data.get('job_name', 'N/A')) if data else 'N/A'}\n" \
                         f"最终状态: {STATUS_MAP.get(status, status)} ({status})\n" \
                         f"运行时长: {runtime}\n" \
                         f"执行节点: {node}\n" \
                         f"计算中心: {cluster_name}\n" \
                         f"总检查次数: {check_count}"
                send_feishu_text(message)
                
                print("-" * 60)
                print(f"✅ 监控结束（共检查 {check_count} 次）")
                print(f"   结束时间: {current_time}")
                break
            
            # 等待下一次检查
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n⚠️ 监控被用户中断")
    except Exception as e:
        print(f"\n❌ 监控异常: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SCNet 作业监控服务')
    parser.add_argument('--job-id', required=True, help='作业ID')
    parser.add_argument('--interval', type=int, default=180, help='检查间隔（秒），默认180')
    
    args = parser.parse_args()
    
    monitor_job(args.job_id, args.interval)
