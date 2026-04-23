#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 2: 作业管理
"""

import sys
import os
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
def created_job(client):
    """创建并返回作业ID，测试结束后删除"""
    job_config = {
        'job_name': 'unit_test_job',
        'cmd': 'sleep 60',
        'nnodes': '1',
        'ppn': '1',
        'queue': 'comp',
        'wall_time': '00:05:00',
        'work_dir': '/public/home/mockuser'
    }
    
    result = client.submit_job(job_config)
    job_id = result.get('data') if result.get('code') == '0' else None
    
    yield job_id
    
    # 清理
    if job_id:
        try:
            client.delete_job(job_id)
        except:
            pass


class TestJob:
    """作业管理测试"""
    
    def test_get_user_queues(self, client):
        """测试获取用户队列"""
        result = client.get_user_queues()
        assert result is not None
        assert result.get('code') == '0'
    
    def test_submit_job(self, client, created_job):
        """测试提交作业"""
        assert created_job is not None
    
    def test_get_job_detail(self, client, created_job):
        """测试查询作业详情"""
        if not created_job:
            pytest.skip("没有创建的作业")
        
        result = client.get_job_detail(created_job)
        assert result is not None
        assert result.get('code') == '0'
    
    def test_get_running_jobs(self, client):
        """测试查询运行中作业列表"""
        result = client.get_running_jobs()
        assert result is not None
    
    def test_delete_job(self, client):
        """测试删除作业（单独创建并删除）"""
        # 创建一个临时作业用于删除测试
        job_config = {
            'job_name': 'test_delete_job',
            'cmd': 'sleep 10',
            'nnodes': '1',
            'ppn': '1',
            'queue': 'comp',
            'wall_time': '00:02:00',
            'work_dir': '/public/home/mockuser'
        }
        
        result = client.submit_job(job_config)
        job_id = result.get('data') if result.get('code') == '0' else None
        
        if job_id:
            result = client.delete_job(job_id)
            assert result is not None
            assert result.get('code') == '0'
