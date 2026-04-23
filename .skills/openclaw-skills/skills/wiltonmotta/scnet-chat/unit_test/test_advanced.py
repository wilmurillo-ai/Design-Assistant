#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件 6: 高级功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unit_test import MOCK_MODE
if MOCK_MODE:
    from unit_test.mocks.mock_client import MockSCNetClient as TestClient
    def calculate_check_interval(wall_time):
        # Mock 实现 - 与真实实现一致
        try:
            parts = wall_time.split(':')
            if len(parts) == 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                total_hours = hours + minutes / 60 + seconds / 3600
                
                if total_hours < 1:
                    return 60
                elif total_hours <= 24:
                    return 300
                else:
                    return 600
        except:
            pass
        return 180
else:
    from scnet_chat import SCNetClient as TestClient
    from scnet_chat import config_manager
    from scnet_chat import calculate_check_interval


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


class TestAdvanced:
    """高级功能测试"""
    
    def test_calculate_check_interval_short(self):
        """测试检查间隔计算 - 短作业"""
        # < 1小时
        assert calculate_check_interval("00:30:00") == 60
        assert calculate_check_interval("00:59:59") == 60
    
    def test_calculate_check_interval_medium(self):
        """测试检查间隔计算 - 中作业"""
        # 1-24小时
        assert calculate_check_interval("01:00:00") == 300
        assert calculate_check_interval("12:00:00") == 300
        assert calculate_check_interval("24:00:00") == 300
    
    def test_calculate_check_interval_long(self):
        """测试检查间隔计算 - 长作业"""
        # > 24小时
        assert calculate_check_interval("24:01:00") == 600
        assert calculate_check_interval("48:00:00") == 600
    
    def test_calculate_check_interval_invalid(self):
        """测试检查间隔计算 - 无效格式"""
        # 无效格式应返回默认值
        assert calculate_check_interval("invalid") == 180
    
    def test_get_history_jobs(self, client):
        """测试查询历史作业"""
        result = client.get_history_jobs(days=7)
        assert result is not None
