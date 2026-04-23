"""
数据基座龙虾 - 智能标签计算引擎
"""
from typing import Dict, List, Any
from datetime import datetime, date


class CustomerIntelligenceEngine:
    """智能客户标签计算引擎"""
    
    def __init__(self):
        self.tag_rules = {
            '高价值客户': {'field': 'total_recharge_amount', 'operator': '>', 'value': 100000},
            '中价值客户': {'field': 'total_recharge_amount', 'operator': '>', 'value': 10000},
            '潜力客户': {'field': 'lifetime_value', 'operator': '>', 'value': 50000},
            '普通客户': {'field': 'total_recharge_amount', 'operator': '>', 'value': 0},
            '免费客户': {'field': 'total_recharge_amount', 'operator': '==', 'value': 0},
        }
        
    def calculate_customer_tags(self, customer_data: Dict) -> List[Dict]:
        """计算客户的所有标签"""
        tags = []
        
        # 价值分层标签
        if customer_data.get('total_recharge_amount', 0) > 100000:
            tags.append({
                'tag_name': '高价值客户',
                'tag_category': '价值分层',
                'confidence': 1.0
            })
        elif customer_data.get('total_recharge_amount', 0) > 10000:
            tags.append({
                'tag_name': '中价值客户',
                'tag_category': '价值分层',
                'confidence': 0.95
            })
            
        # 活跃度标签
        if self._is_high_activity(customer_data):
            tags.append({
                'tag_name': '高活跃客户',
                'tag_category': '活跃度',
                'confidence': 0.9
            })
            
        if self._is_dormant(customer_data):
            tags.append({
                'tag_name': '沉睡客户',
                'tag_category': '风险预警',
                'confidence': 0.85
            })
            
        # 业务模式标签
        if customer_data.get('active_project_count', 0) > 0:
            tags.append({
                'tag_name': '项目型客户',
                'tag_category': '业务模式',
                'confidence': 0.95
            })
            
        # 行业标签
        industry = customer_data.get('industry', '')
        if industry:
            tags.append({
                'tag_name': f'{industry}行业',
                'tag_category': '行业特征',
                'confidence': 1.0
            })
            
        # 风险标签
        health_score = customer_data.get('health_score', 100)
        if health_score < 50:
            tags.append({
                'tag_name': '高风险客户',
                'tag_category': '风险预警',
                'confidence': 0.9
            })
            
        return tags
        
    def _is_high_activity(self, customer: Dict) -> bool:
        """判断是否高活跃客户"""
        return customer.get('api_daily_avg_usage', 0) > 1000
        
    def _is_dormant(self, customer: Dict) -> bool:
        """判断是否沉睡客户"""
        # 注册后无充值或30天无调用
        if customer.get('total_recharge_amount', 0) == 0:
            return True
            
        last_call = customer.get('last_api_call_date')
        if last_call:
            if isinstance(last_call, str):
                last_call = datetime.fromisoformat(last_call).date()
            days_since = (date.today() - last_call).days
            if days_since > 30:
                return True
                
        return False
        
    def assign_customer_tier(self, customer: Dict) -> str:
        """自动分配客户等级"""
        recharge = customer.get('total_recharge_amount', 0)
        
        if recharge > 100000:
            return '高价值'
        elif recharge > 10000:
            return '普通'
        else:
            return '免费'
            
    def assign_activity_status(self, customer: Dict) -> str:
        """自动分配活跃状态"""
        if self._is_high_activity(customer):
            return '高活跃'
        elif self._is_dormant(customer):
            return '沉睡'
        else:
            return '正常'
            
    def assign_customer_type(self, customer: Dict) -> str:
        """自动分配客户类型"""
        has_project = customer.get('active_project_count', 0) > 0
        has_api_usage = customer.get('api_total_calls', 0) > 0
        
        if has_project and has_api_usage:
            return '混合型'
        elif has_project:
            return '项目型'
        elif has_api_usage:
            return 'API型'
        else:
            return '待激活'
