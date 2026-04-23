#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 3: 文件管理
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unit_test import MOCK_MODE

if MOCK_MODE:
    from unit_test.mocks.mock_client import MockSCNetClient as TestClient
else:
    from scnet_chat import SCNetClient as TestClient
    from scnet_chat import config_manager


@pytest.fixture(scope="module")
def client():
    """测试客户端 fixture"""
    if MOCK_MODE:
        c = TestClient()
        c.init_tokens()
    else:
        config = config_manager.load_config()
        c = TestClient(config['access_key'], config['secret_key'], config['user'])
        c.init_tokens()
    return c


@pytest.fixture(scope="module")
def test_paths(client):
    """创建测试目录和文件路径"""
    test_dir = "/public/home/mockuser/unit_test_dir"
    test_file = "/public/home/mockuser/unit_test_file.txt"
    
    # 创建本地测试文件
    local_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    local_file.write("Test content for SCNet")
    local_file.close()
    
    yield {
        'test_dir': test_dir,
        'test_file': test_file,
        'local_file': local_file.name
    }
    
    # 清理
    try:
        os.unlink(local_file.name)
        client.remove(test_file)
        client.remove(test_dir, recursive=True)
    except:
        pass


class TestFile:
    """文件管理测试"""
    
    def test_list_dir(self, client):
        """测试列出目录"""
        result = client.list_dir("/public/home/mockuser")
        assert result is not None
        assert result.get('code') == '0'
    
    def test_mkdir(self, client, test_paths):
        """测试创建目录"""
        result = client.mkdir(test_paths['test_dir'], create_parents=True)
        assert result is True
    
    def test_touch(self, client, test_paths):
        """测试创建空文件"""
        result = client.touch(test_paths['test_file'])
        assert result is True
    
    def test_exists(self, client, test_paths):
        """测试检查文件存在"""
        result = client.exists(test_paths['test_file'])
        assert result is True
    
    def test_upload_file(self, client, test_paths):
        """测试上传文件"""
        remote_path = f"{test_paths['test_dir']}/uploaded.txt"
        result = client.upload(test_paths['local_file'], remote_path)
        assert result is True
    
    def test_download_file(self, client, test_paths):
        """测试下载文件"""
        remote_path = f"{test_paths['test_dir']}/uploaded.txt"
        download_path = tempfile.mktemp(suffix='.txt')
        
        result = client.download(remote_path, download_path)
        assert result is True
        assert os.path.exists(download_path)
        
        # 清理
        os.unlink(download_path)
