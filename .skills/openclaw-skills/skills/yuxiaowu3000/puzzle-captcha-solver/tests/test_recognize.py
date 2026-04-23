#!/usr/bin/env python3
"""
拼图滑块验证码识别 - 单元测试

运行测试：
    python3 -m pytest tests/test_recognize.py -v
    
或：
    python3 tests/test_recognize.py
"""

import unittest
import sys
from pathlib import Path
import cv2
import numpy as np
import os

# 添加脚本目录到路径
script_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(script_dir))


def create_mock_image(width=600, height=400, filename="/tmp/test_captcha.png", color=255):
    """创建模拟图片用于测试"""
    image = np.ones((height, width, 3), dtype=np.uint8) * color
    cv2.imwrite(filename, image)
    return filename


class TestPuzzleCaptchaSolver(unittest.TestCase):
    """测试拼图验证码识别器"""
    
    @classmethod
    def setUpClass(cls):
        """创建测试用的临时文件"""
        cls.test_files = []
        
        # 创建正常尺寸的测试图片
        cls.normal_image = create_mock_image(600, 400, "/tmp/test_normal.png")
        cls.test_files.append(cls.normal_image)
        
        # 创建小尺寸测试图片
        cls.small_image = create_mock_image(50, 50, "/tmp/test_small.png")
        cls.test_files.append(cls.small_image)
        
        # 创建全黑图片（用于测试无检测）
        cls.black_image = create_mock_image(600, 400, "/tmp/test_black.png", color=0)
        cls.test_files.append(cls.black_image)
    
    @classmethod
    def tearDownClass(cls):
        """清理临时文件"""
        for f in cls.test_files:
            if Path(f).exists():
                os.remove(f)
    
    def setUp(self):
        """测试前准备 - 重新加载模块"""
        if 'recognize_puzzle' in sys.modules:
            del sys.modules['recognize_puzzle']
        from recognize_puzzle import PuzzleCaptchaSolver
        self.SolverClass = PuzzleCaptchaSolver
    
    def test_init_with_valid_image(self):
        """测试正常初始化"""
        solver = self.SolverClass(self.normal_image)
        
        self.assertEqual(solver.width, 600)
        self.assertEqual(solver.height, 400)
        self.assertIsNone(solver.captcha_area)
    
    def test_init_with_nonexistent_file(self):
        """测试文件不存在时的错误处理"""
        with self.assertRaises(FileNotFoundError):
            self.SolverClass("/nonexistent/path/captcha.png")
    
    def test_init_with_small_image(self):
        """测试小尺寸图片的警告"""
        solver = self.SolverClass(self.small_image)
        self.assertEqual(solver.width, 50)
        self.assertEqual(solver.height, 50)
    
    def test_detect_captcha_popup_no_detection(self):
        """测试未检测到验证码弹窗（全黑图片）"""
        solver = self.SolverClass(self.black_image)
        result = solver.detect_captcha_popup()
        
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_solve_returns_dict(self):
        """测试 solve 方法返回字典"""
        solver = self.SolverClass(self.normal_image)
        result = solver.solve()
        
        # 检查返回的是字典
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
    
    def test_solve_has_steps(self):
        """测试 solve 方法返回步骤信息"""
        solver = self.SolverClass(self.normal_image)
        result = solver.solve()
        
        # 即使失败，也应该有 steps 字段
        self.assertIn("steps", result)
        self.assertIsInstance(result["steps"], list)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    @classmethod
    def setUpClass(cls):
        """创建测试图片"""
        cls.test_image = create_mock_image(600, 400, "/tmp/test_edge.png")
    
    @classmethod
    def tearDownClass(cls):
        """清理临时文件"""
        if Path(cls.test_image).exists():
            os.remove(cls.test_image)
    
    def setUp(self):
        if 'recognize_puzzle' in sys.modules:
            del sys.modules['recognize_puzzle']
        from recognize_puzzle import PuzzleCaptchaSolver
        self.SolverClass = PuzzleCaptchaSolver
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        solver = self.SolverClass(self.test_image)
        result = solver.solve()
        
        # 验证返回了完整的结果字典
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("steps", result)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestPuzzleCaptchaSolver))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 所有测试通过！")
    else:
        print(f"❌ {len(result.failures)} 个测试失败，{len(result.errors)} 个错误")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
