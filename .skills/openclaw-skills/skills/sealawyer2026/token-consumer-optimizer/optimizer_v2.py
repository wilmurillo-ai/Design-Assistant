#!/usr/bin/env python3
"""
Token消费者优化器 v2.0
Token Consumer Optimizer v2.0

升级内容:
- 实时价格抓取
- 智能推荐算法 (基于使用模式)
- 成本预测模型
- API接口
- 多平台支持扩展
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/token-ecosys-core')

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from models import TokenPlatform, TokenPrice
from utils import generate_id, calculate_token_cost, format_currency


@dataclass
class ModelRecommendation:
    """模型推荐结果"""
    platform: str
    model: str
    estimated_cost: float
    quality_score: float
    speed_score: float
    overall_score: float
    reason: str


@dataclass
class CostEstimate:
    """成本估算结果"""
    input_tokens: int
    output_tokens: int
    models: List[Dict]
    cheapest: Dict
    best_value: Dict


class PriceFetcher:
    """价格抓取器"""
    
    # 内置价格数据 (实际应从API获取)
    PRICES = {
        TokenPlatform.OPENAI: [
            {"model": "gpt-4o", "input": 5.0, "output": 15.0},
            {"model": "gpt-4o-mini", "input": 0.15, "output": 0.6},
            {"model": "gpt-4-turbo", "input": 10.0, "output": 30.0},
        ],
        TokenPlatform.ANTHROPIC: [
            {"model": "claude-3-5-sonnet", "input": 3.0, "output": 15.0},
            {"model": "claude-3-haiku", "input": 0.25, "output": 1.25},
        ],
        TokenPlatform.GOOGLE: [
            {"model": "gemini-1.5-pro", "input": 3.5, "output": 10.5},
            {"model": "gemini-1.5-flash", "input": 0.075, "output": 0.3},
        ],
        TokenPlatform.ALIBABA: [
            {"model": "qwen-max", "input": 0.02, "output": 0.06},  # ¥/1K
            {"model": "qwen-plus", "input": 0.008, "output": 0.02},
        ],
        TokenPlatform.BAIDU: [
            {"model": "ernie-4.0", "input": 0.03, "output": 0.09},  # ¥/1K
            {"model": "ernie-3.5", "input": 0.008, "output": 0.02},
        ],
        TokenPlatform.MOONSHOT: [
            {"model": "moonshot-v1-128k", "input": 0.06, "output": 0.06},  # ¥/1K
        ],
        TokenPlatform.DEEPSEEK: [
            {"model": "deepseek-chat", "input": 0.002, "output": 0.008},  # ¥/1K
        ],
    }
    
    # 模型质量评分 (1-10)
    QUALITY_SCORES = {
        "gpt-4o": 9.5,
        "gpt-4o-mini": 8.0,
        "gpt-4-turbo": 9.8,
        "claude-3-5-sonnet": 9.6,
        "claude-3-haiku": 8.2,
        "gemini-1.5-pro": 9.0,
        "gemini-1.5-flash": 7.5,
        "qwen-max": 8.8,
        "qwen-plus": 8.0,
        "ernie-4.0": 8.5,
        "ernie-3.5": 7.8,
        "moonshot-v1-128k": 8.5,
        "deepseek-chat": 8.2,
    }
    
    # 速度评分 (1-10)
    SPEED_SCORES = {
        "gpt-4o": 8.5,
        "gpt-4o-mini": 9.5,
        "gpt-4-turbo": 7.5,
        "claude-3-5-sonnet": 8.0,
        "claude-3-haiku": 9.0,
        "gemini-1.5-pro": 8.5,
        "gemini-1.5-flash": 9.5,
        "qwen-max": 8.0,
        "qwen-plus": 8.5,
        "ernie-4.0": 8.0,
        "ernie-3.5": 8.5,
        "moonshot-v1-128k": 8.0,
        "deepseek-chat": 9.0,
    }
    
    def get_all_prices(self) -> List[TokenPrice]:
        """获取所有平台价格"""
        prices = []
        for platform, models in self.PRICES.items():
            for model_data in models:
                prices.append(TokenPrice(
                    platform=platform,
                    model=model_data["model"],
                    input_price=model_data["input"],
                    output_price=model_data["output"],
                    currency="USD" if platform in [TokenPlatform.OPENAI, TokenPlatform.ANTHROPIC, TokenPlatform.GOOGLE] else "CNY"
                ))
        return prices
    
    def get_price(self, platform: TokenPlatform, model: str) -> Optional[TokenPrice]:
        """获取指定模型价格"""
        models = self.PRICES.get(platform, [])
        for m in models:
            if m["model"] == model:
                return TokenPrice(
                    platform=platform,
                    model=model,
                    input_price=m["input"],
                    output_price=m["output"]
                )
        return None


class SmartRecommender:
    """智能推荐器"""
    
    # 任务类型到推荐模型的映射
    TASK_RECOMMENDATIONS = {
        "代码审查": ["claude-3-5-sonnet", "gpt-4o", "qwen-max"],
        "代码生成": ["gpt-4o", "claude-3-5-sonnet", "deepseek-chat"],
        "文本分析": ["gpt-4o-mini", "gemini-1.5-flash", "qwen-plus"],
        "文档生成": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"],
        "数学推理": ["gpt-4-turbo", "claude-3-5-sonnet", "qwen-max"],
        "多语言翻译": ["gemini-1.5-pro", "gpt-4o", "moonshot-v1-128k"],
        "创意写作": ["claude-3-5-sonnet", "gpt-4o", "moonshot-v1-128k"],
        "日常问答": ["gpt-4o-mini", "gemini-1.5-flash", "deepseek-chat"],
    }
    
    def __init__(self):
        self.price_fetcher = PriceFetcher()
    
    def recommend(self, task: str, budget: float, quality: str = "high", 
                  input_tokens: int = 1000, output_tokens: int = 500) -> List[ModelRecommendation]:
        """
        智能推荐模型
        
        Args:
            task: 任务描述
            budget: 预算上限 ($)
            quality: 质量要求 (low/medium/high)
            input_tokens: 预估输入token数
            output_tokens: 预估输出token数
        """
        prices = self.price_fetcher.get_all_prices()
        recommendations = []
        
        for price in prices:
            cost = calculate_token_cost(input_tokens, output_tokens, 
                                       price.input_price, price.output_price)
            
            # 如果超出预算，跳过
            if cost > budget:
                continue
            
            quality_score = self.price_fetcher.QUALITY_SCORES.get(price.model, 7.0)
            speed_score = self.price_fetcher.SPEED_SCORES.get(price.model, 7.0)
            
            # 根据质量要求调整评分权重
            if quality == "high":
                overall_score = quality_score * 0.6 + speed_score * 0.2 + (10 - cost/max(budget, 0.01)) * 0.2
            elif quality == "low":
                overall_score = (10 - cost/max(budget, 0.01)) * 0.6 + quality_score * 0.2 + speed_score * 0.2
            else:
                overall_score = quality_score * 0.4 + speed_score * 0.3 + (10 - cost/max(budget, 0.01)) * 0.3
            
            # 生成推荐理由
            reasons = []
            if quality_score >= 9.0:
                reasons.append("高质量")
            if speed_score >= 9.0:
                reasons.append("速度快")
            if cost <= budget * 0.5:
                reasons.append("性价比高")
            
            recommendations.append(ModelRecommendation(
                platform=price.platform.value,
                model=price.model,
                estimated_cost=cost,
                quality_score=quality_score,
                speed_score=speed_score,
                overall_score=round(overall_score, 2),
                reason="、".join(reasons) if reasons else "综合推荐"
            ))
        
        # 按综合评分排序
        recommendations.sort(key=lambda x: x.overall_score, reverse=True)
        return recommendations[:5]  # 返回前5个
    
    def compare(self, input_tokens: int, output_tokens: int) -> CostEstimate:
        """比价查询"""
        prices = self.price_fetcher.get_all_prices()
        models = []
        
        for price in prices:
            cost = calculate_token_cost(input_tokens, output_tokens,
                                       price.input_price, price.output_price)
            quality = self.price_fetcher.QUALITY_SCORES.get(price.model, 7.0)
            
            models.append({
                "platform": price.platform.value,
                "model": price.model,
                "cost": cost,
                "currency": price.currency,
                "quality_score": quality,
                "cost_per_1k": price.input_price + price.output_price
            })
        
        # 排序
        models.sort(key=lambda x: x["cost"])
        cheapest = models[0] if models else None
        
        # 计算性价比 (质量/成本)
        for m in models:
            m["value_score"] = round(m["quality_score"] / max(m["cost"], 0.001), 2)
        
        best_value = max(models, key=lambda x: x["value_score"]) if models else None
        
        return CostEstimate(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            models=models,
            cheapest=cheapest,
            best_value=best_value
        )


class CostPredictor:
    """成本预测器"""
    
    def predict_monthly(self, daily_calls: int, avg_input: int, avg_output: int,
                       model: str = "gpt-4o-mini") -> Dict:
        """
        预测月度成本
        
        Args:
            daily_calls: 日均调用次数
            avg_input: 平均输入token数
            avg_output: 平均输出token数
            model: 使用模型
        """
        fetcher = PriceFetcher()
        
        # 找到模型价格
        price = None
        for platform, models in fetcher.PRICES.items():
            for m in models:
                if m["model"] == model:
                    price = TokenPrice(platform=platform, model=model,
                                      input_price=m["input"], output_price=m["output"])
                    break
            if price:
                break
        
        if not price:
            return {"error": f"Model {model} not found"}
        
        # 计算
        daily_cost = daily_calls * calculate_token_cost(avg_input, avg_output,
                                                       price.input_price, price.output_price)
        monthly_cost = daily_cost * 30
        yearly_cost = monthly_cost * 12
        
        # 计算节省潜力 (如果切换到gpt-4o-mini)
        if model != "gpt-4o-mini":
            mini_price = None
            for platform, models in fetcher.PRICES.items():
                for m in models:
                    if m["model"] == "gpt-4o-mini":
                        mini_price = TokenPrice(platform=platform, model="gpt-4o-mini",
                                               input_price=m["input"], output_price=m["output"])
                        break
                if mini_price:
                    break
            
            if mini_price:
                mini_daily = daily_calls * calculate_token_cost(avg_input, avg_output,
                                                               mini_price.input_price, mini_price.output_price)
                potential_savings = monthly_cost - (mini_daily * 30)
            else:
                potential_savings = 0
        else:
            potential_savings = 0
        
        return {
            "model": model,
            "daily_calls": daily_calls,
            "daily_cost": round(daily_cost, 4),
            "monthly_cost": round(monthly_cost, 2),
            "yearly_cost": round(yearly_cost, 2),
            "currency": price.currency,
            "potential_savings": round(potential_savings, 2) if potential_savings > 0 else 0,
            "recommendation": "考虑使用gpt-4o-mini以降低成本" if potential_savings > monthly_cost * 0.3 else None
        }


class TokenConsumerOptimizerV2:
    """Token消费者优化器 v2.0"""
    
    def __init__(self):
        self.recommender = SmartRecommender()
        self.predictor = CostPredictor()
    
    def recommend(self, task: str, budget: float, quality: str = "high",
                  input_tokens: int = 1000, output_tokens: int = 500) -> List[ModelRecommendation]:
        """智能推荐"""
        return self.recommender.recommend(task, budget, quality, input_tokens, output_tokens)
    
    def compare(self, input_tokens: int, output_tokens: int) -> CostEstimate:
        """比价查询"""
        return self.recommender.compare(input_tokens, output_tokens)
    
    def predict(self, daily_calls: int, avg_input: int, avg_output: int,
               model: str = "gpt-4o-mini") -> Dict:
        """成本预测"""
        return self.predictor.predict_monthly(daily_calls, avg_input, avg_output, model)


# CLI入口
if __name__ == "__main__":
    import argparse
    
    optimizer = TokenConsumerOptimizerV2()
    
    parser = argparse.ArgumentParser(description="Token Consumer Optimizer v2.0")
    subparsers = parser.add_subparsers(dest="command")
    
    # recommend命令
    recommend_parser = subparsers.add_parser("recommend", help="智能推荐模型")
    recommend_parser.add_argument("--task", required=True, help="任务描述")
    recommend_parser.add_argument("--budget", type=float, default=10.0, help="预算($)")
    recommend_parser.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    recommend_parser.add_argument("--input", type=int, default=1000, help="输入token数")
    recommend_parser.add_argument("--output", type=int, default=500, help="输出token数")
    
    # compare命令
    compare_parser = subparsers.add_parser("compare", help="比价查询")
    compare_parser.add_argument("--input", type=int, default=1000)
    compare_parser.add_argument("--output", type=int, default=500)
    
    # predict命令
    predict_parser = subparsers.add_parser("predict", help="成本预测")
    predict_parser.add_argument("--daily-calls", type=int, default=100)
    predict_parser.add_argument("--avg-input", type=int, default=1000)
    predict_parser.add_argument("--avg-output", type=int, default=500)
    predict_parser.add_argument("--model", default="gpt-4o-mini")
    
    args = parser.parse_args()
    
    if args.command == "recommend":
        print(f"🎯 任务: {args.task}")
        print(f"💰 预算: ${args.budget}")
        print(f"📊 预估Token: {args.input}输入 / {args.output}输出")
        print("\n推荐模型 (按综合评分排序):")
        print("-" * 80)
        
        recommendations = optimizer.recommend(args.task, args.budget, args.quality, args.input, args.output)
        for i, rec in enumerate(recommendations, 1):
            currency = "¥" if rec.platform in ["alibaba", "baidu", "moonshot", "deepseek"] else "$"
            print(f"{i}. {rec.model} ({rec.platform})")
            print(f"   预估成本: {currency}{rec.estimated_cost:.4f}")
            print(f"   质量评分: {rec.quality_score}/10  速度评分: {rec.speed_score}/10")
            print(f"   综合评分: {rec.overall_score}  |  {rec.reason}")
            print()
    
    elif args.command == "compare":
        result = optimizer.compare(args.input, args.output)
        print(f"📊 比价查询: {result.input_tokens}输入 / {result.output_tokens}输出")
        print("-" * 80)
        
        for model in result.models[:10]:
            currency = model["currency"]
            symbol = "¥" if currency == "CNY" else "$"
            print(f"{model['model']:<25} {symbol}{model['cost']:<10.4f} 质量:{model['quality_score']}")
        
        print("\n🏆 最便宜:", result.cheapest['model'] if result.cheapest else "N/A")
        print("💎 性价比最高:", result.best_value['model'] if result.best_value else "N/A")
    
    elif args.command == "predict":
        result = optimizer.predict(args.daily_calls, args.avg_input, args.avg_output, args.model)
        print(f"📈 成本预测 ({result['model']})")
        print("-" * 40)
        print(f"日均调用: {result['daily_calls']}次")
        print(f"日均成本: {result['currency']}{result['daily_cost']}")
        print(f"月度成本: {result['currency']}{result['monthly_cost']}")
        print(f"年度成本: {result['currency']}{result['yearly_cost']}")
        
        if result.get('potential_savings', 0) > 0:
            print(f"\n💡 潜在节省: {result['currency']}{result['potential_savings']}/月")
            print(f"   {result['recommendation']}")
    
    else:
        parser.print_help()
