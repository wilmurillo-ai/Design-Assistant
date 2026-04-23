"""
流失预警雷达龙虾 - 流失信号监测
"""
from typing import Dict, List, Any
from datetime import datetime, date, timedelta


class ChurnSignalDetector:
    """流失信号检测器"""
    
    def __init__(self):
        self.signals_config = {
            'usage_drop': {
                'threshold': 0.7,
                'time_window': 14,
                'description': '使用量下降70%以上'
            },
            'inactivity': {
                'threshold_days': 30,
                'check_interval': 7,
                'description': '30天无活动'
            },
            'token_stagnation': {
                'threshold': 1000,
                'duration_days': 60,
                'description': 'Token余额长期未消耗'
            },
            'support_tickets': {
                'recent_tickets': 3,
                'negative_sentiment': True,
                'description': '近期多个负面工单'
            },
            'payment_delays': {
                'delays_count': 2,
                'description': '多次付款延迟'
            }
        }
        
    def monitor_customer_health(self, customer_data: Dict) -> List[Dict]:
        """监控客户健康度"""
        signals = []
        
        # 检查使用量下降
        if self._check_usage_drop(customer_data):
            signals.append({
                'type': 'usage_drop',
                'severity': 'high',
                'description': self.signals_config['usage_drop']['description'],
                'action_required': '安排客户成功经理联系'
            })
            
        # 检查长期不活跃
        if self._check_inactivity(customer_data):
            signals.append({
                'type': 'inactivity',
                'severity': 'medium',
                'description': self.signals_config['inactivity']['description'],
                'action_required': '发送激活邮件'
            })
            
        # 检查Token停滞
        if self._check_token_stagnation(customer_data):
            signals.append({
                'type': 'token_stagnation',
                'severity': 'medium',
                'description': self.signals_config['token_stagnation']['description'],
                'action_required': '推荐合适的使用场景'
            })
            
        # 检查支持工单
        if self._check_support_tickets(customer_data):
            signals.append({
                'type': 'support_tickets',
                'severity': 'high',
                'description': self.signals_config['support_tickets']['description'],
                'action_required': '安排技术支持回访'
            })
            
        return signals
        
    def _check_usage_drop(self, customer: Dict) -> bool:
        """检查使用量是否大幅下降"""
        current_usage = customer.get('api_daily_avg_usage', 0)
        historical_usage = customer.get('historical_avg_usage', 0)
        
        if historical_usage and historical_usage > 0:
            drop_ratio = current_usage / historical_usage
            return drop_ratio < self.signals_config['usage_drop']['threshold']
            
        return False
        
    def _check_inactivity(self, customer: Dict) -> bool:
        """检查是否长期不活跃"""
        last_call = customer.get('last_api_call_date')
        
        if not last_call:
            return True
            
        if isinstance(last_call, str):
            last_call = datetime.fromisoformat(last_call).date()
            
        days_since = (date.today() - last_call).days
        return days_since > self.signals_config['inactivity']['threshold_days']
        
    def _check_token_stagnation(self, customer: Dict) -> bool:
        """检查Token余额是否长期未消耗"""
        balance = customer.get('current_token_balance', 0)
        last_recharge = customer.get('last_recharge_date')
        
        if not last_recharge or balance < self.signals_config['token_stagnation']['threshold']:
            return False
            
        if isinstance(last_recharge, str):
            last_recharge = datetime.fromisoformat(last_recharge).date()
            
        days_since = (date.today() - last_recharge).days
        return days_since > self.signals_config['token_stagnation']['duration_days']
        
    def _check_support_tickets(self, customer: Dict) -> bool:
        """检查是否有负面支持工单"""
        recent_tickets = customer.get('recent_support_tickets', 0)
        has_negative = customer.get('has_negative_sentiment', False)
        
        return (recent_tickets >= self.signals_config['support_tickets']['recent_tickets'] 
                and has_negative)
                
    def calculate_health_score(self, signals: List[Dict]) -> int:
        """根据信号计算健康度分数"""
        if not signals:
            return 100
            
        score = 100
        
        for signal in signals:
            if signal['severity'] == 'high':
                score -= 25
            elif signal['severity'] == 'medium':
                score -= 15
            else:
                score -= 5
                
        return max(score, 0)
