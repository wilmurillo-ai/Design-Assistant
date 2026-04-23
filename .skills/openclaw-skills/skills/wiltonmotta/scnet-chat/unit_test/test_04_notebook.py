#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 4: Notebook 管理

测试顺序: 4.1 - 4.6
⚠️ 重要: 此测试套件会实际创建/删除 Notebook，产生费用（真实模式）
资源生命周期: 创建(4.2) -> 查询(4.3) -> 关机(4.5) -> 释放(4.6)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from base_test import BaseTestCase
import os
MOCK_MODE = os.environ.get('SCNET_TEST_MODE', 'mock').lower() == 'mock'


class TestNotebook(BaseTestCase):
    """Notebook 管理测试"""
    
    notebook_id = None
    cluster_id = "11250"  # 昆山
    
    def test_4_1_list_notebooks(self):
        """测试查询 Notebook 列表"""
        def test():
            nb_mgr = self.client.get_notebook_manager()
            result = nb_mgr.list_notebooks()
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            return {"success": True}
        
        return self.run_test(test, "4.1 查询 Notebook 列表", "notebook")
    
    def test_4_2_create_notebook(self):
        """测试创建 Notebook 实例"""
        def test():
            if not MOCK_MODE:
                print("\n     ⚠️  真实模式: 将创建付费 Notebook 实例")
                print("     5秒后继续...")
                time.sleep(5)
            
            nb_mgr = self.client.get_notebook_manager()
            
            # 获取可用镜像
            images_result = nb_mgr.get_images(accelerator_type="DCU", size=1)
            if images_result.get('code') != '0' or not images_result.get('data', {}).get('list'):
                self.skipTest("没有可用的镜像")
            
            image = images_result['data']['list'][0]
            
            result = nb_mgr.create_notebook(
                cluster_id=self.cluster_id,
                image_config={
                    "path": image.get('imagePath'),
                    "name": image.get('imageName'),
                    "size": ""
                },
                accelerator_type="DCU",
                accelerator_number="1"
            )
            
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            
            TestNotebook.notebook_id = result['data']['notebookId']
            print(f"\n     创建 Notebook: {TestNotebook.notebook_id}")
            
            # 等待创建完成
            if not MOCK_MODE:
                time.sleep(10)
            
            return {"resource_id": TestNotebook.notebook_id, "success": True}
        
        return self.run_test(test, "4.2 创建 Notebook", "notebook")
    
    def test_4_3_get_notebook_detail(self):
        """测试查询 Notebook 详情"""
        def test():
            if not TestNotebook.notebook_id:
                self.skipTest("没有创建的 Notebook")
            
            nb_mgr = self.client.get_notebook_manager()
            result = nb_mgr.get_notebook_detail(TestNotebook.notebook_id)
            
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            
            return {"success": True}
        
        return self.run_test(test, "4.3 查询 Notebook 详情", "notebook")
    
    def test_4_4_start_notebook(self):
        """测试 Notebook 开机"""
        def test():
            if not TestNotebook.notebook_id:
                self.skipTest("没有创建的 Notebook")
            
            nb_mgr = self.client.get_notebook_manager()
            result = nb_mgr.start_notebook(TestNotebook.notebook_id)
            
            self.assertIsNotNone(result)
            # 开机操作可能返回不同状态码
            
            # 等待启动
            if not MOCK_MODE:
                time.sleep(5)
            
            return {"success": True}
        
        return self.run_test(test, "4.4 Notebook 开机", "notebook")
    
    def test_4_5_stop_notebook(self):
        """测试 Notebook 关机"""
        def test():
            if not TestNotebook.notebook_id:
                self.skipTest("没有创建的 Notebook")
            
            print(f"\n     正在关机: {TestNotebook.notebook_id}...")
            nb_mgr = self.client.get_notebook_manager()
            result = nb_mgr.stop_notebook(TestNotebook.notebook_id, save_env=False)
            
            self.assertIsNotNone(result)
            
            # 等待关机完成
            if not MOCK_MODE:
                time.sleep(10)
            
            return {"success": True}
        
        return self.run_test(test, "4.5 Notebook 关机", "notebook")
    
    def test_4_6_release_notebook(self):
        """测试 Notebook 释放"""
        def test():
            if not TestNotebook.notebook_id:
                self.skipTest("没有创建的 Notebook")
            
            print(f"\n     正在释放: {TestNotebook.notebook_id}...")
            nb_mgr = self.client.get_notebook_manager()
            result = nb_mgr.release_notebook(TestNotebook.notebook_id)
            
            self.assertIsNotNone(result)
            
            # 从清理列表中移除（已手动释放）
            self.created_resources = [
                r for r in self.created_resources 
                if r.get('id') != TestNotebook.notebook_id
            ]
            
            return {"success": True}
        
        return self.run_test(test, "4.6 Notebook 释放", "notebook")


if __name__ == '__main__':
    unittest.main()
