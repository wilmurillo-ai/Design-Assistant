"""
流失预警雷达龙虾 - 自动干预系统
"""
from typing import Dict, List, Any, Callable, Optional


class AutomatedInterventionSystem:
    """自动干预系统"""
    
    def __init__(
        self, 
        notification_service: Optional[Callable] = None,
        email_service: Optional[Callable] = None,
        crm_service: Optional[Callable] = None
    ):
        self.notification = notification_service
        self.email = email_service
        self.crm = crm_service
        
    def trigger_interventions(self, churn_prediction: Dict) -> List[Dict]:
        """根据流失预测触发干预措施"""
        interventions = []
        risk_level = churn_prediction.get('risk_level', 'low')
        
        # 高风险和严重风险
        if risk_level in ['high', 'critical']:
            # 1. 通知客户成功经理
            interventions.append(self._notify_csm(churn_prediction))
            
            # 2. 发送关怀邮件
            interventions.append(self._send_care_email(churn_prediction))
            
            # 3. 创建CRM待办
            if self.crm:
                interventions.append(self._create_crm_todo(churn_prediction))
                
            # 4. 严重风险安排电话回访
            if risk_level == 'critical':
                interventions.append(self._schedule_phone_call(churn_prediction))
                
        # 中等风险
        elif risk_level == 'medium':
            # 1. 发送教育内容
            interventions.append(self._send_educational_content(churn_prediction))
            
            # 2. 推送优惠活动
            interventions.append(self._send_offer(churn_prediction))
            
        # 低风险
        else:
            # 常规维护
            interventions.append(self._add_to_nurture_sequence(churn_prediction))
            
        return interventions
        
    def _notify_csm(self, prediction: Dict) -> Dict:
        """通知客户成功经理"""
        if not self.notification:
            return {'action': 'notify_csm', 'status': 'skipped'}
            
        message = f"""
        高风险客户预警
        
        客户ID: {prediction.get('customer_id')}
        流失概率: {prediction.get('churn_probability', 0):.1%}
        风险等级: {prediction.get('risk_level')}
        关键因素: {', '.join([f['factor'] for f in prediction.get('key_factors', [])[:3]])}
        
        请尽快安排客户回访！
        """
        
        return {
            'action': 'notify_csm',
            'status': 'sent',
            'message': message
        }
        
    def _send_care_email(self, prediction: Dict) -> Dict:
        """发送关怀邮件"""
        if not self.email:
            return {'action': 'send_care_email', 'status': 'skipped'}
            
        customer_id = prediction.get('customer_id')
        
        # 生成个性化邮件内容
        email_content = self._generate_personalized_email(prediction)
        
        return {
            'action': 'send_care_email',
            'status': 'queued',
            'to': customer_id,
            'subject': '我们关心您的使用体验',
            'content': email_content[:200]
        }
        
    def _create_crm_todo(self, prediction: Dict) -> Dict:
        """创建CRM待办"""
        if not self.crm:
            return {'action': 'create_crm_todo', 'status': 'skipped'}
            
        todo = {
            'customer_id': prediction.get('customer_id'),
            'title': f"高风险客户回访 - {prediction.get('risk_level')}级别",
            'priority': 'high' if prediction.get('risk_level') == 'critical' else 'medium',
            'due_days': 1 if prediction.get('risk_level') == 'critical' else 3,
            'description': f"流失概率: {prediction.get('churn_probability', 0):.1%}"
        }
        
        return {
            'action': 'create_crm_todo',
            'status': 'created',
            'todo': todo
        }
        
    def _schedule_phone_call(self, prediction: Dict) -> Dict:
        """安排电话回访"""
        return {
            'action': 'schedule_phone_call',
            'status': 'queued',
            'customer_id': prediction.get('customer_id'),
            'priority': 'urgent',
            'reason': '高流失风险'
        }
        
    def _send_educational_content(self, prediction: Dict) -> Dict:
        """发送教育内容"""
        return {
            'action': 'send_educational_content',
            'status': 'queued',
            'customer_id': prediction.get('customer_id'),
            'content_type': 'usage_guide'
        }
        
    def _send_offer(self, prediction: Dict) -> Dict:
        """推送优惠"""
        return {
            'action': 'send_offer',
            'status': 'queued',
            'customer_id': prediction.get('customer_id'),
            'offer_type': 'retention_discount'
        }
        
    def _add_to_nurture_sequence(self, prediction: Dict) -> Dict:
        """添加到培育序列"""
        return {
            'action': 'add_to_nurture',
            'status': 'queued',
            'customer_id': prediction.get('customer_id'),
            'sequence': 'standard'
        }
        
    def _generate_personalized_email(self, prediction: Dict) -> str:
        """生成个性化关怀邮件"""
        key_factors = prediction.get('key_factors', [])
        factors_text = '、'.join([f['factor'] for f in key_factors[:2]])
        
        return f"""
        亲爱的客户：
        
        我们注意到您最近的使用体验可能有些不尽如人意。
        
        了解到您目前的情况：{factors_text}
        
        我们非常重视每一位客户的使用体验。
        您的专属客户成功经理将尽快与您联系，
        了解您的需求，并提供针对性的解决方案。
        
        如果您有任何问题，也可以直接回复此邮件联系我们。
        
        感谢您对我们的支持！
        
        增长生产力团队
        """
