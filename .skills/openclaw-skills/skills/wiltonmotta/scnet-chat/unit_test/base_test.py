#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基类
"""

import unittest
import time
import os
import json
import sys
from datetime import datetime
from typing import List, Dict, Any

# 获取测试模式
TEST_MODE = os.environ.get('SCNET_TEST_MODE', 'mock').lower()
MOCK_MODE = TEST_MODE == 'mock'
REAL_MODE = TEST_MODE == 'real'

# 根据模式选择客户端
if MOCK_MODE:
    from .mocks import MockSCNetClient as TestClient
    print("🧪 使用 Mock 客户端进行测试")
else:
    from scnet_chat import SCNetClient as TestClient
    from scnet_chat import config_manager
    print("⚠️  使用真实 SCNet 客户端进行测试")


class TestResult:
    """测试结果记录"""
    
    def __init__(self, test_name: str, status: str = "pending", 
                 message: str = "", duration: float = 0.0,
                 resource_id: str = None, resource_type: str = None):
        self.test_name = test_name
        self.status = status  # pending/running/passed/failed/skipped
        self.message = message
        self.duration = duration
        self.resource_id = resource_id  # 创建的资源ID
        self.resource_type = resource_type  # 资源类型：notebook/container/job
        self.timestamp = datetime.now().isoformat()
        self.cleanup_status = None  # 资源清理状态
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "status": self.status,
            "message": self.message,
            "duration": self.duration,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "timestamp": self.timestamp,
            "cleanup_status": self.cleanup_status
        }


class TestReport:
    """测试报告"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = datetime.now()
    
    def end(self):
        self.end_time = datetime.now()
    
    def add_result(self, result: TestResult):
        self.results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")
        total = len(self.results)
        
        duration = 0
        if self.end_time and self.start_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
            "total_duration": duration
        }
    
    def generate_report(self, output_path: str = None):
        """生成测试报告"""
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(__file__), 
                "reports", 
                f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        report = {
            "summary": self.get_summary(),
            "test_mode": "mock" if MOCK_MODE else "real",
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": [r.to_dict() for r in self.results]
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_path


class BaseTestCase(unittest.TestCase):
    """测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类开始前执行"""
        cls.client = None
        cls.report = TestReport()
        cls.report.start()
        cls.created_resources = []  # 记录创建的资源
        
        # 初始化客户端
        if MOCK_MODE:
            cls.client = TestClient()
            cls.client.init_tokens()
        else:
            # 真实模式需要加载配置
            config = config_manager.load_config()
            if not config.get('access_key'):
                raise RuntimeError("真实模式需要配置 ~/.scnet-chat.env")
            cls.client = TestClient(
                config['access_key'],
                config['secret_key'],
                config['user']
            )
            cls.client.init_tokens()
    
    @classmethod
    def tearDownClass(cls):
        """测试类结束后执行"""
        cls.report.end()
        
        # 清理所有资源
        print("\n" + "="*60)
        print("资源清理阶段")
        print("="*60)
        
        for resource in cls.created_resources:
            cls._cleanup_resource(resource)
        
        # 生成报告
        report_path = cls.report.generate_report()
        print(f"\n📊 测试报告已保存: {report_path}")
        
        # 打印摘要
        summary = cls.report.get_summary()
        print(f"\n{'='*60}")
        print(f"测试摘要")
        print(f"{'='*60}")
        print(f"总用例数: {summary['total']}")
        print(f"通过: {summary['passed']} ✅")
        print(f"失败: {summary['failed']} ❌")
        print(f"跳过: {summary['skipped']} ⏭️")
        print(f"通过率: {summary['pass_rate']}")
        print(f"总耗时: {summary['total_duration']:.2f}秒")
        print(f"{'='*60}")
    
    @classmethod
    def _cleanup_resource(cls, resource: Dict[str, Any]):
        """清理资源"""
        resource_id = resource.get('id')
        resource_type = resource.get('type')
        
        if not resource_id or not resource_type:
            return
        
        print(f"  清理 {resource_type}: {resource_id}...", end=" ")
        
        try:
            if resource_type == 'notebook':
                # 先关机再释放
                cls.client.get_notebook_manager().stop_notebook(resource_id)
                time.sleep(2)
                cls.client.get_notebook_manager().release_notebook(resource_id)
            
            elif resource_type == 'container':
                # 先停止再删除
                cls.client.get_container_manager().stop_containers([resource_id])
                time.sleep(2)
                cls.client.get_container_manager().delete_containers([resource_id])
            
            elif resource_type == 'job':
                # 删除作业
                cls.client.delete_job(resource_id)
            
            # 更新报告中的清理状态
            for result in cls.report.results:
                if result.resource_id == resource_id:
                    result.cleanup_status = "success"
            
            print("✅")
            
        except Exception as e:
            print(f"❌ ({str(e)})")
            # 更新报告中的清理状态
            for result in cls.report.results:
                if result.resource_id == resource_id:
                    result.cleanup_status = f"failed: {str(e)}"
    
    def record_result(self, test_name: str, status: str, message: str = "",
                     duration: float = 0.0, resource_id: str = None, 
                     resource_type: str = None):
        """记录测试结果"""
        result = TestResult(
            test_name=test_name,
            status=status,
            message=message,
            duration=duration,
            resource_id=resource_id,
            resource_type=resource_type
        )
        self.report.add_result(result)
        
        # 如果创建了资源，记录到清理列表
        if resource_id and resource_type:
            self.created_resources.append({
                'id': resource_id,
                'type': resource_type
            })
    
    def run_test(self, test_func, test_name: str, resource_type: str = None):
        """
        运行单个测试并记录结果
        
        Args:
            test_func: 测试函数
            test_name: 测试名称
            resource_type: 资源类型（notebook/container/job）
        """
        print(f"\n  执行: {test_name}...", end=" ")
        start_time = time.time()
        
        try:
            result = test_func()
            duration = time.time() - start_time
            
            # 检查是否返回了资源ID
            resource_id = None
            if isinstance(result, dict):
                resource_id = result.get('resource_id') or result.get('id')
            
            self.record_result(
                test_name=test_name,
                status="passed",
                message="测试通过",
                duration=duration,
                resource_id=resource_id,
                resource_type=resource_type
            )
            print(f"✅ ({duration:.2f}s)")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            self.record_result(
                test_name=test_name,
                status="failed",
                message=str(e),
                duration=duration,
                resource_type=resource_type
            )
            print(f"❌ ({duration:.2f}s)")
            print(f"     错误: {str(e)}")
            raise
