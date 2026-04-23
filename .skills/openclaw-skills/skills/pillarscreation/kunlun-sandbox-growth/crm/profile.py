"""
智能客户管理龙虾 - AI客户画像
"""
from typing import Dict, List, Any, Optional


class AICustomerProfile:
    """AI客户画像生成器"""
    
    def __init__(self, cdp_client=None):
        self.cdp = cdp_client
        
    def generate_profile_report(self, customer_id: str) -> Dict:
        """生成完整客户画像报告"""
        # 获取客户基础数据
        customer_data = self._get_customer_data(customer_id)
        
        if not customer_data:
            return {'error': '客户不存在'}
            
        # 构建画像报告
        report = {
            'customer_id': customer_id,
            'customer_summary': self._generate_summary(customer_data),
            'financial_overview': self._analyze_financial(customer_data),
            'usage_insights': self._analyze_usage(customer_data),
            'engagement_status': self._analyze_engagement(customer_data),
            'ai_recommendations': self._generate_recommendations(customer_data)
        }
        
        return report
        
    def _get_customer_data(self, customer_id: str) -> Optional[Dict]:
        """获取客户数据"""
        if self.cdp:
            return self.cdp.get_customer_360(customer_id)
        return None
        
    def _generate_summary(self, data: Dict) -> Dict:
        """生成客户摘要"""
        return {
            'company_name': data.get('company_name', ''),
            'industry': data.get('industry', ''),
            'company_size': data.get('company_size', ''),
            'customer_tier': data.get('customer_tier', '普通'),
            'health_score': data.get('health_score', 0),
            'activity_status': data.get('activity_status', '正常')
        }
        
    def _analyze_financial(self, data: Dict) -> Dict:
        """财务分析"""
        return {
            'total_spent': data.get('total_recharge_amount', 0),
            'avg_monthly_spend': data.get('avg_recharge_amount', 0),
            'lifetime_value': data.get('lifetime_value', 0),
            'last_recharge_date': data.get('last_recharge_date'),
            'payment_pattern': self._judge_payment_pattern(data)
        }
        
    def _analyze_usage(self, data: Dict) -> Dict:
        """使用分析"""
        return {
            'total_api_calls': data.get('api_total_calls', 0),
            'total_tokens': data.get('total_tokens_used', 0),
            'most_used_model': data.get('most_used_model', '未知'),
            'usage_scenario': data.get('usage_scenario', '通用'),
            'last_call_date': data.get('last_api_call_date'),
            'daily_avg_usage': data.get('api_daily_avg_usage', 0)
        }
        
    def _analyze_engagement(self, data: Dict) -> Dict:
        """互动分析"""
        return {
            'active_projects': data.get('active_project_count', 0),
            'project_value': data.get('total_project_value', 0),
            'campaigns_joined': data.get('campaign_participation_count', 0),
            'last_campaign': data.get('last_campaign_engagement')
        }
        
    def _generate_recommendations(self, data: Dict) -> List[Dict]:
        """AI行动建议"""
        recommendations = []
        
        # 基于健康度的建议
        health_score = data.get('health_score', 0)
        if health_score < 50:
            recommendations.append({
                'priority': 'high',
                'action': '安排客户成功经理回访',
                'reason': '客户健康度低于50分，存在流失风险'
            })
            
        # 基于充值历史的建议
        last_recharge = data.get('last_recharge_date')
        if last_recharge:
            days_since = (date.today() - last_recharge).days
            if days_since > 60:
                recommendations.append({
                    'priority': 'high',
                    'action': '触发大额充值优惠',
                    'reason': f'已有{days_since}天未充值'
                })
                
        # 基于使用情况的建议
        if data.get('api_total_calls', 0) > 0 and data.get('total_recharge_amount', 0) == 0:
            recommendations.append({
                'priority': 'medium',
                'action': '推广付费套餐',
                'reason': '客户有API使用但未付费'
            })
            
        return recommendations
        
    def _judge_payment_pattern(self, data: Dict) -> str:
        """判断支付模式"""
        recharge_count = data.get('recharge_count', 0)
        amount = data.get('total_recharge_amount', 0)
        
        if recharge_count == 0:
            return '未付费'
        elif recharge_count == 1:
            return '首次付费'
        elif amount > 100000:
            return '大额稳定'
        else:
            return '小额持续'


from datetime import date
