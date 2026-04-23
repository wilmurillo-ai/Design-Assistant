#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 1: 认证和账户管理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unit_test import MOCK_MODE

# 根据模式选择客户端
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


class TestAuth:
    """认证测试类"""
    
    def test_init_tokens(self, client):
        """测试 Token 初始化"""
        result = client.init_tokens()
        assert result is True
    
    def test_get_default_cluster(self, client):
        """测试获取默认计算中心"""
        cluster_name = client.get_default_cluster_name()
        assert cluster_name is not None
        assert isinstance(cluster_name, str)
    
    def test_get_home_path(self, client):
        """测试获取家目录"""
        home_path = client.get_home_path()
        assert home_path is not None
        assert home_path.startswith('/')
    
    def test_get_account_info(self, client):
        """测试获取账户信息"""
        result = client.get_account_info()
        assert result is not None
        assert result.get('code') == '0'
