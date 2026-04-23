#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 5: 容器管理
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
def created_container(client):
    """创建容器并返回ID，测试结束后删除"""
    container_id = None
    
    if REAL_MODE:
        print("\n⚠️  真实模式: 将创建付费容器")
        time.sleep(2)
    
    ct_mgr = client.get_container_manager()
    
    # 获取镜像
    images = ct_mgr.get_images(accelerator_type="dcu", size=1)
    if images.get('code') != '0' or not images.get('data', {}).get('list'):
        pytest.skip("没有可用的镜像")
    
    image = images['data']['list'][0]
    
    config = {
        "instanceServiceName": "unit-test-container",
        "taskType": "ssh",
        "acceleratorType": "dcu",
        "version": image.get('version', 'latest'),
        "imagePath": image.get('imagePath'),
        "cpuNumber": 3,
        "gpuNumber": 1,
        "ramSize": 15360,
        "resourceGroup": "kshdtest"
    }
    
    result = ct_mgr.create_container(config)
    
    if result.get('code') == '0':
        container_id = result.get('data')
        print(f"\n创建容器: {container_id}")
        
        if REAL_MODE:
            time.sleep(10)  # 等待创建完成
    
    yield container_id
    
    # 清理
    if container_id:
        try:
            print(f"\n删除容器: {container_id}")
            ct_mgr.stop_containers([container_id])
            time.sleep(5)
            ct_mgr.delete_containers([container_id])
        except Exception as e:
            print(f"清理失败: {e}")


class TestContainer:
    """容器管理测试"""
    
    def test_list_containers(self, client):
        """测试查询容器列表"""
        ct_mgr = client.get_container_manager()
        result = ct_mgr.list_containers()
        assert result is not None
    
    def test_create_container(self, created_container):
        """测试创建容器"""
        assert created_container is not None
    
    def test_get_container_detail(self, client, created_container):
        """测试查询容器详情"""
        if not created_container:
            pytest.skip("没有创建的容器")
        
        ct_mgr = client.get_container_manager()
        result = ct_mgr.get_container_detail(created_container)
        assert result is not None
