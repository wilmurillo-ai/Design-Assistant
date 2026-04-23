#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 2: 作业管理

测试顺序: 2.1 - 2.5
资源清理: 2.1 创建的作业会在 2.5 中删除
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from base_test import BaseTestCase


class TestJob(BaseTestCase):
    """作业管理测试"""
    
    created_job_id = None
    
    def test_2_1_get_user_queues(self):
        """测试获取用户队列"""
        def test():
            result = self.client.get_user_queues()
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            self.assertIn('data', result)
            return {"success": True}
        
        return self.run_test(test, "2.1 获取用户队列", "job")
    
    def test_2_2_submit_job(self):
        """测试提交作业"""
        def test():
            job_config = {
                'job_name': 'unit_test_job',
                'cmd': 'sleep 60',  # 短作业，快速完成
                'nnodes': '1',
                'ppn': '1',
                'queue': 'comp',
                'wall_time': '00:05:00',
                'work_dir': '/public/home/mockuser'
            }
            
            result = self.client.submit_job(job_config)
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            
            job_id = result.get('data')
            self.assertIsNotNone(job_id)
            TestJob.created_job_id = job_id
            
            return {"resource_id": job_id, "success": True}
        
        return self.run_test(test, "2.2 提交作业", "job")
    
    def test_2_3_get_job_detail(self):
        """测试查询作业详情"""
        def test():
            if not TestJob.created_job_id:
                self.skipTest("没有创建的作业")
            
            result = self.client.get_job_detail(TestJob.created_job_id)
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            
            return {"success": True}
        
        return self.run_test(test, "2.3 查询作业详情", "job")
    
    def test_2_4_get_running_jobs(self):
        """测试查询运行中作业列表"""
        def test():
            result = self.client.get_running_jobs()
            self.assertIsNotNone(result)
            return {"success": True}
        
        return self.run_test(test, "2.4 查询运行中作业", "job")
    
    def test_2_5_delete_job(self):
        """测试删除作业"""
        def test():
            if not TestJob.created_job_id:
                self.skipTest("没有创建的作业")
            
            result = self.client.delete_job(TestJob.created_job_id)
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            
            # 从清理列表中移除（已手动删除）
            self.created_resources = [
                r for r in self.created_resources 
                if r.get('id') != TestJob.created_job_id
            ]
            
            return {"success": True}
        
        return self.run_test(test, "2.5 删除作业", "job")


if __name__ == '__main__':
    unittest.main()
