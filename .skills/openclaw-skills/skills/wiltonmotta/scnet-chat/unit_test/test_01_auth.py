#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 1: 认证和账户管理

测试顺序: 1.1 - 1.3
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_test import BaseTestCase


class TestAuth(BaseTestCase):
    """认证测试"""
    
    def test_1_1_init_tokens(self):
        """测试 Token 初始化"""
        def test():
            result = self.client.init_tokens()
            self.assertTrue(result)
            return {"success": True}
        
        return self.run_test(test, "1.1 Token 初始化", "auth")
    
    def test_1_2_get_default_cluster(self):
        """测试获取默认计算中心"""
        def test():
            cluster_name = self.client.get_default_cluster_name()
            self.assertIsNotNone(cluster_name)
            self.assertIsInstance(cluster_name, str)
            return {"cluster_name": cluster_name}
        
        return self.run_test(test, "1.2 获取默认计算中心", "auth")
    
    def test_1_3_get_home_path(self):
        """测试获取家目录"""
        def test():
            home_path = self.client.get_home_path()
            self.assertIsNotNone(home_path)
            self.assertTrue(home_path.startswith('/'))
            return {"home_path": home_path}
        
        return self.run_test(test, "1.3 获取家目录", "auth")
    
    def test_1_4_get_account_info(self):
        """测试获取账户信息"""
        def test():
            result = self.client.get_account_info()
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            return {"success": True}
        
        return self.run_test(test, "1.4 获取账户信息", "auth")


if __name__ == '__main__':
    unittest.main()
