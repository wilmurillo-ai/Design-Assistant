"""
流失预警雷达龙虾 - 流失预测模型
"""
from typing import Dict, List, Any
from datetime import datetime


class ChurnPredictionModel:
    """流失预测模型"""
    
    def __init__(self):
        # 特征列表
        self.features = [
            'days_since_last_activity',
            'usage_trend_30d',
            'support_interactions',
            'payment_delays',
            'sentiment_score',
            'engagement_score'
        ]
        
        # 模拟模型（实际使用时替换为真实训练的模型）
        self.model = None
        
    def predict_churn_risk(self, customer_features: Dict) -> Dict:
        """预测流失风险"""
        # 特征工程
        processed = self._preprocess_features(customer_features)
        
        # 模拟预测（实际使用时调用真实模型）
        probability = self._predict_probability(processed)
        
        # 风险等级
        risk_level = self._determine_risk_level(probability)
        
        # 关键因素
        key_factors = self._extract_key_factors(customer_features, processed)
        
        return {
            'customer_id': customer_features.get('customer_id', ''),
            'churn_probability': probability,
            'risk_level': risk_level,
            'key_factors': key_factors,
            'prediction_date': datetime.now().isoformat(),
            'expiry_date': self._get_expiry_date()
        }
        
    def _preprocess_features(self, features: Dict) -> Dict:
        """特征预处理"""
        processed = {}
        
        # 天数特征
        processed['days_since_last_activity'] = min(
            features.get('days_since_last_activity', 0), 365
        ) / 365.0
        
        # 使用趋势
        processed['usage_trend_30d'] = features.get('usage_trend_30d', 0)
        
        # 支持互动
        processed['support_interactions'] = min(
            features.get('support_interactions', 0), 10
        ) / 10.0
        
        # 付款延迟
        processed['payment_delays'] = min(
            features.get('payment_delays', 0), 5
        ) / 5.0
        
        # 情感得分
        processed['sentiment_score'] = features.get('sentiment_score', 0.5)
        
        # 参与度得分
        processed['engagement_score'] = features.get('engagement_score', 0.5)
        
        return processed
        
    def _predict_probability(self, processed_features: Dict) -> float:
        """预测流失概率（简化版模拟）"""
        # 简化加权公式
        probability = (
            processed_features.get('days_since_last_activity', 0) * 0.3 +
            (1 - processed_features.get('usage_trend_30d', 0.5)) * 0.2 +
            processed_features.get('support_interactions', 0) * 0.15 +
            processed_features.get('payment_delays', 0) * 0.15 +
            (1 - processed_features.get('sentiment_score', 0.5)) * 0.1 +
            (1 - processed_features.get('engagement_score', 0.5)) * 0.1
        )
        
        return min(probability, 0.99)
        
    def _determine_risk_level(self, probability: float) -> str:
        """确定风险等级"""
        if probability >= 0.8:
            return 'critical'
        elif probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        else:
            return 'low'
            
    def _extract_key_factors(self, original: Dict, processed: Dict) -> List[Dict]:
        """提取关键流失因素"""
        factors = []
        
        if original.get('days_since_last_activity', 0) > 30:
            factors.append({
                'factor': '长期未活跃',
                'impact': 'high',
                'description': f'{original.get("days_since_last_activity")}天无活动'
            })
            
        if original.get('usage_trend_30d', 0) < 0.5:
            factors.append({
                'factor': '使用量下降',
                'impact': 'high',
                'description': '近30天使用量下降50%以上'
            })
            
        if original.get('payment_delays', 0) > 0:
            factors.append({
                'factor': '付款延迟',
                'impact': 'medium',
                'description': f'有{original.get("payment_delays")}次付款延迟'
            })
            
        if original.get('sentiment_score', 0.5) < 0.3:
            factors.append({
                'factor': '负面情绪',
                'impact': 'high',
                'description': '客户情绪偏向负面'
            })
            
        return factors
        
    def _get_expiry_date(self) -> str:
        """获取预测过期日期"""
        from datetime import timedelta
        return (datetime.now() + timedelta(days=30)).isoformat()


from datetime import timedelta
