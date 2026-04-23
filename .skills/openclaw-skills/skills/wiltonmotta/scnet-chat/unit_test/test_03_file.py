#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 3: 文件管理

测试顺序: 3.1 - 3.6
资源清理: 3.2 创建的目录和 3.3 创建的文件会在最后清理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tempfile
from base_test import BaseTestCase


class TestFile(BaseTestCase):
    """文件管理测试"""
    
    test_dir = "/public/home/mockuser/unit_test_dir"
    test_file = "/public/home/mockuser/unit_test_file.txt"
    local_test_file = None
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 创建本地测试文件
        cls.local_test_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.txt', 
            delete=False,
            prefix='scnet_test_'
        )
        cls.local_test_file.write("This is a test file for SCNet unit test")
        cls.local_test_file.close()
    
    @classmethod
    def tearDownClass(cls):
        # 清理本地测试文件
        if cls.local_test_file and os.path.exists(cls.local_test_file.name):
            os.unlink(cls.local_test_file.name)
        super().tearDownClass()
    
    def test_3_1_list_dir(self):
        """测试列出目录"""
        def test():
            result = self.client.list_dir("/public/home/mockuser")
            self.assertIsNotNone(result)
            self.assertEqual(result.get('code'), '0')
            return {"success": True}
        
        return self.run_test(test, "3.1 列出目录", "file")
    
    def test_3_2_mkdir(self):
        """测试创建目录"""
        def test():
            result = self.client.mkdir(self.test_dir, create_parents=True)
            self.assertTrue(result)
            return {"resource_id": self.test_dir, "success": True}
        
        return self.run_test(test, "3.2 创建目录", "file")
    
    def test_3_3_touch(self):
        """测试创建空文件"""
        def test():
            result = self.client.touch(self.test_file)
            self.assertTrue(result)
            return {"resource_id": self.test_file, "success": True}
        
        return self.run_test(test, "3.3 创建空文件", "file")
    
    def test_3_4_exists(self):
        """测试检查文件存在"""
        def test():
            result = self.client.exists(self.test_file)
            self.assertTrue(result)
            return {"success": True}
        
        return self.run_test(test, "3.4 检查文件存在", "file")
    
    def test_3_5_upload_file(self):
        """测试上传文件"""
        def test():
            remote_path = f"{self.test_dir}/uploaded_test.txt"
            result = self.client.upload(
                self.local_test_file.name,
                remote_path
            )
            self.assertTrue(result)
            return {"resource_id": remote_path, "success": True}
        
        return self.run_test(test, "3.5 上传文件", "file")
    
    def test_3_6_download_file(self):
        """测试下载文件"""
        def test():
            # 先确保文件存在
            remote_path = f"{self.test_dir}/uploaded_test.txt"
            
            # 下载到临时目录
            download_path = tempfile.mktemp(suffix='.txt')
            result = self.client.download(remote_path, download_path)
            self.assertTrue(result)
            
            # 验证文件内容
            self.assertTrue(os.path.exists(download_path))
            with open(download_path, 'r') as f:
                content = f.read()
                self.assertEqual(content, "This is a test file for SCNet unit test")
            
            # 清理下载的文件
            os.unlink(download_path)
            
            return {"success": True}
        
        return self.run_test(test, "3.6 下载文件", "file")
    
    def test_3_7_remove(self):
        """测试删除文件和目录"""
        def test():
            # 删除文件
            result = self.client.remove(self.test_file)
            self.assertTrue(result)
            
            # 删除目录（递归）
            result = self.client.remove(self.test_dir, recursive=True)
            self.assertTrue(result)
            
            # 从清理列表中移除（已手动删除）
            self.created_resources = [
                r for r in self.created_resources 
                if r.get('id') not in [self.test_file, self.test_dir]
            ]
            
            return {"success": True}
        
        return self.run_test(test, "3.7 删除文件和目录", "file")


if __name__ == '__main__':
    unittest.main()
