"""
多渠道获客龙虾 - 线索评分模型
"""
from typing import Dict, List, Any, Optional


class LeadScoringModel:
    """潜在客户线索评分模型"""
    
    def __init__(self):
        # 行业权重
        self.industry_weights = {
            '金融': 1.2,
            '政务': 1.1,
            '医疗': 1.15,
            '教育': 1.0,
            '制造': 1.05,
            '零售': 0.9,
            '其他': 0.8
        }
        
        # 公司规模权重
        self.company_size_weights = {
            '大型企业': 1.3,
            '中型企业': 1.1,
            '小型企业': 0.9,
            '初创公司': 0.8
        }
        
        # 基础分
        self.base_score = 50
        
    def calculate_lead_score(self, lead_data: Dict) -> Dict:
        """计算线索评分"""
        score = self.base_score
        details = []
        
        # 行业加分
        industry = lead_data.get('industry', '其他')
        industry_weight = self.industry_weights.get(industry, 0.8)
        industry_score = industry_weight * 10
        score += industry_score
        details.append({
            'factor': '行业',
            'value': industry,
            'score': industry_score
        })
        
        # 公司规模加分
        company_size = lead_data.get('company_size', '小型企业')
        size_weight = self.company_size_weights.get(company_size, 0.9)
        size_score = size_weight * 10
        score += size_score
        details.append({
            'factor': '公司规模',
            'value': company_size,
            'score': size_score
        })
        
        # 行为数据加分
        if lead_data.get('viewed_api_docs', False):
            score += 15
            details.append({'factor': '浏览API文档', 'score': 15})
            
        if lead_data.get('demo_requested', False):
            score += 20
            details.append({'factor': '申请演示', 'score': 20})
            
        if lead_data.get('pricing_viewed', False):
            score += 10
            details.append({'factor': '查看定价', 'score': 10})
            
        # 注册后活跃度
        if lead_data.get('registered_days', 0) < 7 and lead_data.get('api_calls', 0) > 0:
            score += 15
            details.append({'factor': '新客活跃', 'score': 15})
            
        # 邮箱验证
        if lead_data.get('email_verified', False):
            score += 5
            details.append({'factor': '邮箱已验证', 'score': 5})
            
        # 最终评分
        final_score = min(score, 100)
        
        return {
            'lead_id': lead_data.get('lead_id', ''),
            'total_score': final_score,
            'grade': self._get_grade(final_score),
            'details': details
        }
        
    def _get_grade(self, score: float) -> str:
        """根据评分获取等级"""
        if score >= 80:
            return 'A'
        elif score >= 60:
            return 'B'
        elif score >= 40:
            return 'C'
        else:
            return 'D'
            
    def batch_score(self, leads: List[Dict]) -> List[Dict]:
        """批量评分"""
        return [self.calculate_lead_score(lead) for lead in leads]
        
    def get_top_leads(self, leads: List[Dict], n: int = 10) -> List[Dict]:
        """获取Top N优质线索"""
        scored = self.batch_score(leads)
        return sorted(scored, key=lambda x: x['total_score'], reverse=True)[:n]
