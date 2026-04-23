"""
多渠道获客龙虾 - 个性化触达工作流
"""
from typing import Dict, List, Any, Optional, Callable


class MultiChannelAcquisitionWorkflow:
    """多渠道获客自动化工作流"""
    
    def __init__(self, openclaw_client=None):
        self.openclaw = openclaw_client
        self.templates = self._load_templates()
        
    def _load_templates(self) -> Dict:
        """加载触达模板"""
        return {
            'welcome': {
                'subject': '欢迎 {company_name} 加入我们的AI平台',
                'prompt_template': '为{industry}行业的客户{company_name}生成欢迎邮件...'
            },
            'nurture': {
                'subject': '{company_name}，您的AI使用指南请查收',
                'prompt_template': '为{industry}行业生成培育邮件...'
            },
            'reengagement': {
                'subject': '{company_name}，我们想您了',
                'prompt_template': '生成唤回邮件...'
            }
        }
        
    def trigger_welcome_email(self, customer: Dict) -> Dict:
        """触发欢迎邮件"""
        if self.openclaw:
            email_content = self._generate_email_content(
                customer, 
                self.templates['welcome']['prompt_template']
            )
        else:
            email_content = self._default_welcome_content(customer)
            
        return {
            'channel': 'email',
            'to': customer.get('email', ''),
            'subject': self.templates['welcome']['subject'].format(
                company_name=customer.get('company_name', '')
            ),
            'content': email_content
        }
        
    def trigger_nurture_sequence(self, lead: Dict) -> List[Dict]:
        """触发培育序列"""
        sequence = []
        
        # 第1天：欢迎邮件
        sequence.append(self.trigger_welcome_email(lead))
        
        # 第3天：使用指南
        if self.openclaw:
            content = self._generate_email_content(
                lead,
                '生成产品使用指南邮件...'
            )
        else:
            content = f"亲爱的{lead.get('company_name')}，这里是我们为您准备的使用指南..."
            
        sequence.append({
            'channel': 'email',
            'to': lead.get('email', ''),
            'subject': f"{lead.get('company_name')}，您的AI使用指南请查收",
            'content': content,
            'delay_days': 3
        })
        
        return sequence
        
    def generate_outbound_call_script(self, lead: Dict) -> str:
        """生成外呼话术"""
        if self.openclaw:
            prompt = f"""
            为{lead.get('industry')}行业的潜在客户生成外呼话术：
            客户特征：{lead.get('company_size')}规模
            关注场景：{lead.get('usage_scenario', '通用')}
            目标：引导客户完成首次充值
            话术要求：专业、亲切、有针对性
            """
            return self.openclaw.generate_content(prompt)
        else:
            return f"""
            开场白：您好，我是XX公司的...
            背景：了解到贵公司在{lead.get('industry')}行业...
            价值：我们的AI服务可以帮助您...
            CTA：建议您先免费试用我们的API...
            """
            
    def _generate_email_content(self, customer: Dict, template: str) -> str:
        """AI生成邮件内容"""
        if not self.openclaw:
            return self._default_welcome_content(customer)
            
        prompt = template.format(
            industry=customer.get('industry', ''),
            company_name=customer.get('company_name', '')
        )
        
        return self.openclaw.generate_content(prompt)
        
    def _default_welcome_content(self, customer: Dict) -> str:
        """默认欢迎邮件内容"""
        return f"""
        亲爱的{customer.get('company_name', '客户')}团队：
        
        欢迎加入我们的AI平台！
        
        我们专注于为{customer.get('industry', '各行业')}提供最前沿的AI解决方案。
        
        您的专属客户成功经理将很快与您联系，帮助您快速上手。
        
        立即开始探索我们的产品吧！
        
        祝好，
        增长生产力团队
        """
