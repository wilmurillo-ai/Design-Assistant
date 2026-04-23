#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 6: 高级功能

测试顺序: 6.1 - 6.4
包括: 检查间隔计算、作业监控、历史作业查询
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_test import BaseTestCase
from scnet_chat import calculate_check_interval


class TestAdvanced(BaseTestCase):
    """高级功能测试"""
    
    def test_6_1_calculate_check_interval_short(self):
        """测试检查间隔计算 - 短作业"""
        def test():
            # < 1小时
            interval = calculate_check_interval("00:30:00")
            self.assertEqual(interval, 60)
            
            interval = calculate_check_interval("00:59:59")
            self.assertEqual(interval, 60)
            
            return {"success": True}
        
        return self.run_test(test, "6.1 检查间隔计算 - 短作业", "advanced")
    
    def test_6_2_calculate_check_interval_medium(self):
        """测试检查间隔计算 - 中作业"""
        def test():
            # 1-24小时
            interval = calculate_check_interval("01:00:00")
            self.assertEqual(interval, 300)
            
            interval = calculate_check_interval("12:00:00")
            self.assertEqual(interval, 300)
            
            interval = calculate_check_interval("24:00:00")
            self.assertEqual(interval, 300)
            
            return {"success": True}
        
        return self.run_test(test, "6.2 检查间隔计算 - 中作业", "advanced")
    
    def test_6_3_calculate_check_interval_long(self):
        """测试检查间隔计算 - 长作业"""
        def test():
            # > 24小时
            interval = calculate_check_interval("24:01:00")
            self.assertEqual(interval, 600)
            
            interval = calculate_check_interval("48:00:00")
            self.assertEqual(interval, 600)
            
            return {"success": True}
        
        return self.run_test(test, "6.3 检查间隔计算 - 长作业", "advanced")
    
    def test_6_4_get_history_jobs(self):
        """测试查询历史作业"""
        def test():
            result = self.client.get_history_jobs(days=7)
            self.assertIsNotNone(result)
            return {"success": True}
        
        return self.run_test(test, "6.4 查询历史作业", "advanced")


if __name__ == '__main__':
    unittest.main()
