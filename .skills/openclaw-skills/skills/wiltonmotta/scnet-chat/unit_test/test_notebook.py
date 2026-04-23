#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 4: Notebook 管理
⚠️ 真实模式下会产生费用！
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unit_test import MOCK_MODE, REAL_MODE

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
def created_notebook(client):
    """创建 Notebook 并返回ID，测试结束后释放"""
    notebook_id = None
    
    if REAL_MODE:
        print("\n⚠️  真实模式: 将创建付费 Notebook")
        time.sleep(2)
    
    nb_mgr = client.get_notebook_manager()
    
    # 获取镜像
    images = nb_mgr.get_images(accelerator_type="DCU", size=1)
    if images.get('code') != '0' or not images.get('data', {}).get('list'):
        pytest.skip("没有可用的镜像")
    
    image = images['data']['list'][0]
    
    result = nb_mgr.create_notebook(
        cluster_id="11250",
        image_config={
            "path": image.get('imagePath'),
            "name": image.get('imageName'),
            "size": ""
        },
        accelerator_type="DCU",
        accelerator_number="1"
    )
    
    if result.get('code') == '0':
        notebook_id = result['data']['notebookId']
        print(f"\n创建 Notebook: {notebook_id}")
        
        if REAL_MODE:
            time.sleep(10)  # 等待创建完成
    
    yield notebook_id
    
    # 清理
    if notebook_id:
        try:
            print(f"\n释放 Notebook: {notebook_id}")
            nb_mgr.stop_notebook(notebook_id)
            time.sleep(5)
            nb_mgr.release_notebook(notebook_id)
        except Exception as e:
            print(f"清理失败: {e}")


class TestNotebook:
    """Notebook 管理测试"""
    
    def test_list_notebooks(self, client):
        """测试查询 Notebook 列表"""
        nb_mgr = client.get_notebook_manager()
        result = nb_mgr.list_notebooks()
        assert result is not None
        assert result.get('code') == '0'
    
    def test_create_notebook(self, created_notebook):
        """测试创建 Notebook"""
        assert created_notebook is not None
    
    def test_get_notebook_detail(self, client, created_notebook):
        """测试查询 Notebook 详情"""
        if not created_notebook:
            pytest.skip("没有创建的 Notebook")
        
        nb_mgr = client.get_notebook_manager()
        result = nb_mgr.get_notebook_detail(created_notebook)
        assert result is not None
        assert result.get('code') == '0'
