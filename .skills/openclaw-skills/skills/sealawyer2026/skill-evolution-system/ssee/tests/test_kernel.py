#!/usr/bin/env python3
"""
SSE Core 单元测试
"""

import sys
import unittest
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, '/root/.openclaw/workspace/skills/skill-evolution-system')

from ssee.core import EvolutionKernel, KernelConfig


class TestEvolutionKernel(unittest.TestCase):
    """测试进化内核"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.config = KernelConfig(
            data_dir=self.test_dir,
            auto_evolve=False,
            sync_enabled=True,
        )
        self.kernel = EvolutionKernel(self.config)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """测试内核初始化"""
        result = self.kernel.initialize()
        self.assertTrue(result)
        self.assertTrue(self.test_dir.exists())
    
    def test_register_skill(self):
        """测试技能注册"""
        self.kernel.initialize()
        result = self.kernel.register_skill("test-skill", {
            "name": "Test Skill",
            "version": "1.0.0",
        })
        self.assertTrue(result)
        self.assertIn("test-skill", self.kernel._skill_registry)
    
    def test_track_usage(self):
        """测试使用追踪"""
        self.kernel.initialize()
        result = self.kernel.track("test-skill", {
            "duration": 1.5,
            "success": True,
        })
        self.assertEqual(result["status"], "success")
    
    def test_analyze(self):
        """测试性能分析"""
        self.kernel.initialize()
        # 先添加一些数据
        for i in range(5):
            self.kernel.track("test-skill", {
                "duration": 1.0 + i * 0.1,
                "success": True,
            })
        
        result = self.kernel.analyze("test-skill")
        self.assertEqual(result["status"], "analyzed")
        self.assertIn("summary", result)
    
    def test_plan_generation(self):
        """测试进化计划生成"""
        self.kernel.initialize()
        analysis = {
            "summary": {
                "health_score": 70.0,
            },
            "bottlenecks": [],
            "recommendations": ["优化性能"],
        }
        
        plan = self.kernel.plan("test-skill", analysis)
        self.assertIn("tasks", plan)
        self.assertIn("priority", plan)
    
    def test_sync_skills(self):
        """测试技能同步"""
        self.kernel.initialize()
        result = self.kernel.sync_skills(["skill-a", "skill-b", "skill-c"])
        self.assertIn("patterns_discovered", result)
        self.assertIn("patterns_applied", result)


class TestAdapters(unittest.TestCase):
    """测试适配器"""
    
    def test_openclaw_adapter(self):
        """测试OpenClaw适配器"""
        from ssee.adapters import OpenClawAdapter, AdapterRegistry
        
        adapter = OpenClawAdapter({
            "skills_dir": "~/.openclaw/workspace/skills"
        })
        
        # 测试连接
        connected = adapter.connect()
        self.assertTrue(connected)
        
        # 测试获取技能列表
        skills = adapter.get_skill_list()
        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)
    
    def test_adapter_registry(self):
        """测试适配器注册表"""
        from ssee.adapters import AdapterRegistry
        
        adapters = AdapterRegistry.list_adapters()
        self.assertIn("openclaw", adapters)
        self.assertIn("gpts", adapters)
        self.assertIn("dingtalk", adapters)
        self.assertIn("feishu", adapters)


if __name__ == "__main__":
    unittest.main()
