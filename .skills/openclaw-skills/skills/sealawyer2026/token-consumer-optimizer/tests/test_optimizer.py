# Token消费优选师 - 测试套件

import unittest
import json
import os
from optimizer import TokenConsumerOptimizer, BudgetLevel


class TestTokenConsumerOptimizer(unittest.TestCase):
    """测试Token消费优选师"""
    
    @classmethod
    def setUpClass(cls):
        """测试前准备"""
        cls.optimizer = TokenConsumerOptimizer('price_data.json')
    
    def test_load_data(self):
        """测试数据加载"""
        self.assertGreater(len(self.optimizer.models), 0)
        self.assertIn('gpt-4o', self.optimizer.models)
        self.assertIn('kimi-k2', self.optimizer.models)
    
    def test_calculate_cost(self):
        """测试成本计算"""
        # 测试GPT-4o
        cost_cny, cost_usd = self.optimizer.calculate_cost('gpt-4o', 1000000, 500000)
        self.assertGreater(cost_cny, 0)
        self.assertGreater(cost_usd, 0)
        
        # 测试Kimi K2 (人民币计价)
        cost_cny, cost_usd = self.optimizer.calculate_cost('kimi-k2', 1000000, 500000)
        self.assertGreater(cost_cny, 0)
        self.assertGreater(cost_usd, 0)
    
    def test_recommend(self):
        """测试推荐功能"""
        recommendations = self.optimizer.recommend(
            task_type='code_generation',
            input_tokens=2000,
            output_tokens=1000,
            budget_level=BudgetLevel.BALANCED
        )
        
        self.assertGreater(len(recommendations), 0)
        
        # 检查推荐结果结构
        top = recommendations[0]
        self.assertIsNotNone(top.model)
        self.assertGreaterEqual(top.total_cost_cny, 0)
        self.assertGreaterEqual(top.score, 0)
    
    def test_compare_all(self):
        """测试对比功能"""
        results = self.optimizer.compare_all(1000, 500)
        
        self.assertGreater(len(results), 0)
        
        # 检查是否按价格排序
        for i in range(len(results) - 1):
            self.assertLessEqual(results[i]['cost_cny'], results[i+1]['cost_cny'])
    
    def test_analyze_budget(self):
        """测试预算分析"""
        analysis = self.optimizer.analyze_budget(
            monthly_budget_cny=1000,
            daily_calls=100,
            avg_input_tokens=2000
        )
        
        self.assertEqual(analysis['budget_cny'], 1000)
        self.assertIn('model_options', analysis)
        self.assertIn('recommended', analysis)
        
        # 检查是否有推荐
        recommended = analysis.get('recommended')
        if recommended:
            self.assertIn('model_name', recommended)
    
    def test_different_task_types(self):
        """测试不同任务类型"""
        task_types = ['simple_qa', 'code_generation', 'document_processing']
        
        for task_type in task_types:
            recommendations = self.optimizer.recommend(
                task_type=task_type,
                input_tokens=1000
            )
            self.assertGreater(len(recommendations), 0, f"{task_type} 应该返回推荐")
    
    def test_invalid_model(self):
        """测试无效模型"""
        with self.assertRaises(ValueError):
            self.optimizer.calculate_cost('invalid-model', 1000)
    
    def test_currency_conversion(self):
        """测试货币转换"""
        # USD to CNY
        cny = self.optimizer.to_cny(1.0, 'USD')
        self.assertAlmostEqual(cny, 7.20, places=2)
        
        # CNY to USD
        usd = self.optimizer.to_usd(7.20, 'CNY')
        self.assertAlmostEqual(usd, 1.0, places=2)
        
        # CNY stays CNY
        cny = self.optimizer.to_cny(10.0, 'CNY')
        self.assertEqual(cny, 10.0)


class TestCLIFunctions(unittest.TestCase):
    """测试CLI功能"""
    
    def test_price_data_exists(self):
        """测试价格数据文件存在"""
        self.assertTrue(os.path.exists('price_data.json'))
    
    def test_price_data_format(self):
        """测试价格数据格式"""
        with open('price_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn('models', data)
        self.assertIn('exchange_rate', data)
        self.assertIn('task_type_mapping', data)
        
        # 检查模型数据结构
        for model in data['models']:
            self.assertIn('id', model)
            self.assertIn('name', model)
            self.assertIn('input_price', model)
            self.assertIn('output_price', model)
            self.assertIn('currency', model)


if __name__ == '__main__':
    unittest.main(verbosity=2)
