#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 5: 容器管理

测试顺序: 5.1 - 5.6
⚠️ 重要: 此测试套件会实际创建/删除容器，产生费用（真实模式）
资源生命周期: 创建(5.2) -> 查询(5.3) -> 停止(5.5) -> 删除(5.6)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from base_test import BaseTestCase
import os
MOCK_MODE = os.environ.get('SCNET_TEST_MODE', 'mock').lower() == 'mock'


class TestContainer(BaseTestCase):
    """容器管理测试"""
    
    container_id = None
    
    def test_5_1_list_containers(self):
        """测试查询容器列表"""
        def test():
            ct_mgr = self.client.get_container_manager()
            result = ct_mgr.list_containers()
            self.assertIsNotNone(result)
            return {"success": True}
        
        return self.run_test(test, "5.1 查询容器列表", "container")
    
    def test_5_2_create_container(self):
        """测试创建容器实例"""
        def test():
            if not MOCK_MODE:
                print("\n     ⚠️  真实模式: 将创建付费容器实例")
                print("     5秒后继续...")
                time.sleep(5)
            
            ct_mgr = self.client.get_container_manager()
            
            # 获取资源分组
            resource_groups = ct_mgr.get_resource_groups()
            if resource_groups.get('code') != '0':
                self.skipTest("无法获取资源分组")
            
            # 获取镜像列表
            images = ct_mgr.get_images(accelerator_type="dcu", size=1)
            if images.get('code') != '0' or not images.get('data', {}).get('list'):
                self.skipTest("没有可用的镜像")
            
            image = images['data']['list'][0]
            
            # 创建容器配置
            config = {
                "instanceServiceName": "unit-test-container",
                "taskType": "ssh",
                "acceleratorType": "dcu",
                "version": image.get('version', 'latest'),
                "imagePath": image.get('imagePath'),
                "cpuNumber": 3,
                "gpuNumber": 1,
                "ramSize": 15360,
                "resourceGroup": "kshdtest"  # 默认资源组
            }
            
            result = ct_mgr.create_container(config)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            
            TestContainer.container_id = result.get('data')
            print(f"\n     创建容器: {TestContainer.container_id}")
            
            # 等待创建
            if not MOCK_MODE:
                time.sleep(10)
            
            return {"resource_id": TestContainer.container_id, "success": True}
        
        return self.run_test(test, "5.2 创建容器", "container")
    
    def test_5_3_get_container_detail(self):
        """测试查询容器详情"""
        def test():
            if not TestContainer.container_id:
                self.skipTest("没有创建的容器")
            
            ct_mgr = self.client.get_container_manager()
            result = ct_mgr.get_container_detail(TestContainer.container_id)
            
            self.assertIsNotNone(result)
            return {"success": True}
        
        return self.run_test(test, "5.3 查询容器详情", "container")
    
    def test_5_4_start_container(self):
        """测试启动容器"""
        def test():
            if not TestContainer.container_id:
                self.skipTest("没有创建的容器")
            
            ct_mgr = self.client.get_container_manager()
            result = ct_mgr.start_container(TestContainer.container_id)
            
            self.assertIsNotNone(result)
            
            if not MOCK_MODE:
                time.sleep(5)
            
            return {"success": True}
        
        return self.run_test(test, "5.4 启动容器", "container")
    
    def test_5_5_stop_container(self):
        """测试停止容器"""
        def test():
            if not TestContainer.container_id:
                self.skipTest("没有创建的容器")
            
            print(f"\n     正在停止: {TestContainer.container_id}...")
            ct_mgr = self.client.get_container_manager()
            result = ct_mgr.stop_containers([TestContainer.container_id])
            
            self.assertIsNotNone(result)
            
            if not MOCK_MODE:
                time.sleep(10)
            
            return {"success": True}
        
        return self.run_test(test, "5.5 停止容器", "container")
    
    def test_5_6_delete_container(self):
        """测试删除容器"""
        def test():
            if not TestContainer.container_id:
                self.skipTest("没有创建的容器")
            
            print(f"\n     正在删除: {TestContainer.container_id}...")
            ct_mgr = self.client.get_container_manager()
            result = ct_mgr.delete_containers([TestContainer.container_id])
            
            self.assertIsNotNone(result)
            
            # 从清理列表中移除（已手动删除）
            self.created_resources = [
                r for r in self.created_resources 
                if r.get('id') != TestContainer.container_id
            ]
            
            return {"success": True}
        
        return self.run_test(test, "5.6 删除容器", "container")


if __name__ == '__main__':
    unittest.main()
