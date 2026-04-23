#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet 作业监控器 - 跨平台版本

支持: macOS, Linux, Windows

使用方法:
    python3 job_monitor_service.py --job-id 27894 --interval 180

后台运行:
    macOS/Linux: nohup python3 job_monitor_service.py --job-id 27894 &
    Windows:     start pythonw job_monitor_service.py --job-id 27894
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime, timedelta

# 添加技能目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
skill_dir = os.path.join(script_dir, '..')
sys.path.insert(0, skill_dir)

from scnet_chat import SCNetClient, query_job_detail, query_history_jobs
import config_manager
from notifications import send_feishu_text


class JobMonitorService:
    """跨平台作业监控服务"""

    STATUS_MAP = {
        "statR": "运行中", "statQ": "排队中", "statW": "等待中",
        "statH": "保留", "statS": "挂起", "statE": "退出",
        "statC": "完成", "statT": "终止", "statDE": "删除",
        "unknown": "未知"
    }

    ACTIVE_STATUSES = ['statR', 'statQ', 'statW']

    def __init__(self, enable_feishu: bool = True):
        """
        初始化监控服务

        Args:
            enable_feishu: 是否启用飞书通知（默认True，需配置webhook）
        """
        self.config = config_manager.load_config()
        self.client = SCNetClient(
            self.config['access_key'],
            self.config['secret_key'],
            self.config['user']
        )
        self.client.init_tokens()

        # 获取计算中心信息
        cache_path = os.path.expanduser("~/.scnet-chat-cache.json")
        with open(cache_path, 'r') as f:
            cache = json.load(f)

        self.default_cluster = None
        for cluster in cache['clusters']:
            if cluster.get('default', False):
                self.default_cluster = cluster
                break

        if self.default_cluster:
            self.hpc_url = self.default_cluster['hpcUrls'][0]['url']
            self.token = self.default_cluster['token']
            self.scheduler_id = self.default_cluster.get('clusterId', '')
            self.cluster_name = self.default_cluster.get('clusterName', 'Unknown')

        # 飞书通知设置
        self.enable_feishu = enable_feishu
        if enable_feishu:
            from notifications import FeishuNotifier
            notifier = FeishuNotifier()
            self.feishu_enabled = notifier.webhook_url is not None
            if not self.feishu_enabled:
                print("💡 飞书通知未配置，仅使用会话窗口提示")
        else:
            self.feishu_enabled = False

    def get_job_status(self, job_id: str):
        """获取作业状态"""
        # 查询实时作业
        try:
            result = query_job_detail(self.hpc_url, self.token, self.scheduler_id, job_id)
            if result and result.get('code') == '0' and result.get('data'):
                data = result.get('data')
                return data.get('jobStatus', 'unknown'), data, 'realtime'
        except:
            pass

        # 查询历史作业
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)

            result = query_history_jobs(
                self.hpc_url, self.token, self.scheduler_id,
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S'),
                start=0, limit=100
            )

            if result and result.get('code') == '0':
                job_list = result.get('data', {}).get('list', [])
                for job in job_list:
                    if job.get('jobId') == job_id:
                        return job.get('jobState', 'unknown'), job, 'history'
        except:
            pass

        return None, None, None

    def monitor(self, job_id: str, check_interval: int = 180):
        """监控作业直到完成"""

        print(f"🔍 开始监控作业 {job_id}")
        print(f"   计算中心: {self.cluster_name}")
        print(f"   检查间隔: {check_interval}秒")
        print(f"   飞书通知: {'已启用' if self.feishu_enabled else '未启用'}")
        print(f"   开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)

        # 记录文件
        notified_file = os.path.expanduser(f"~/.scnet-job-notified-{job_id}.json")

        # 如果已通知过，跳过
        if os.path.exists(notified_file):
            print(f"✅ 作业 {job_id} 已通知过，退出")
            return

        last_status = None
        check_count = 0

        try:
            while True:
                check_count += 1
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                status, data, source = self.get_job_status(job_id)

                if not status:
                    print(f"[{current_time}] 未找到作业，稍后重试...")
                    time.sleep(check_interval)
                    continue

                # 状态变化时输出
                if status != last_status:
                    print(f"[{current_time}] 状态: {self.STATUS_MAP.get(status, status)} ({source})")
                    last_status = status

                # 检查是否结束
                if status not in self.ACTIVE_STATUSES:
                    print(f"[{current_time}] 作业已结束")

                    # 获取作业信息
                    runtime = "N/A"
                    node = "N/A"
                    job_name = "N/A"

                    if data:
                        runtime = data.get('jobWalltimeUsed', data.get('jobRunTime', 'N/A'))
                        node = data.get('jobExecHost', data.get('nodeUsed', 'N/A'))
                        job_name = data.get('jobName', data.get('job_name', 'N/A'))

                    # ========== 会话窗口通知（默认）==========
                    print("\n" + "="*60)
                    status_icon = "✅" if status == 'statC' else "⚠️"
                    print(f"  {status_icon} 【作业完成通知】")
                    print("="*60)
                    print(f"  📋 作业ID:     {job_id}")
                    print(f"  📝 作业名称:   {job_name}")
                    print(f"  📊 最终状态:   {self.STATUS_MAP.get(status, status)} ({status})")
                    print(f"  ⏱️  运行时长:   {runtime}")
                    print(f"  🖥️  执行节点:   {node}")
                    print(f"  🏢 计算中心:   {self.cluster_name}")
                    print(f"  🔢 检查次数:   {check_count}")
                    print("="*60)

                    # ========== 飞书通知（可选）==========
                    if self.feishu_enabled:
                        emoji = "🎉" if status == 'statC' else "⚠️"
                        message = f"【SCNet作业完成】{emoji}\n" \
                                 f"作业ID: {job_id}\n" \
                                 f"作业名称: {job_name}\n" \
                                 f"最终状态: {self.STATUS_MAP.get(status, status)} ({status})\n" \
                                 f"运行时长: {runtime}\n" \
                                 f"执行节点: {node}\n" \
                                 f"计算中心: {self.cluster_name}\n" \
                                 f"检查次数: {check_count}"

                        print(f"发送飞书通知...")
                        if send_feishu_text(message):
                            print("✅ 飞书通知发送成功")
                        else:
                            print("❌ 飞书通知发送失败")
                    else:
                        print("💡 飞书通知未启用")

                    # 记录已通知
                    notified_data = {
                        'job_id': job_id,
                        'status': status,
                        'notified_at': current_time,
                        'cluster': self.cluster_name,
                        'feishu_notified': self.feishu_enabled
                    }
                    with open(notified_file, 'w', encoding='utf-8') as f:
                        json.dump(notified_data, f, ensure_ascii=False, indent=2)

                    print("-" * 60)
                    print(f"✅ 监控结束（共检查 {check_count} 次）")
                    break

                # 等待下一次检查
                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n⚠️ 监控被用户中断")
        except Exception as e:
            print(f"\n❌ 监控异常: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SCNet 作业监控服务（跨平台）')
    parser.add_argument('--job-id', required=True, help='作业ID')
    parser.add_argument('--interval', type=int, default=180, help='检查间隔（秒），默认180')
    parser.add_argument('--enable-feishu', action='store_true', help='启用飞书通知（需配置webhook）')

    args = parser.parse_args()

    service = JobMonitorService(enable_feishu=args.enable_feishu)
    service.monitor(args.job_id, args.interval)
