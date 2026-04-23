"""
智能客户管理龙虾 - 商机阶段管理
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class OpportunityStageManager:
    """商机阶段管理"""
    
    STAGES = {
        '识别': {'order': 1, 'duration': 7, 'actions': ['完善客户画像', '初步需求调研']},
        '确认': {'order': 2, 'duration': 14, 'actions': ['深入需求分析', '技术可行性评估']},
        '方案': {'order': 3, 'duration': 21, 'actions': ['详细方案设计', '报价方案准备']},
        '谈判': {'order': 4, 'duration': 14, 'actions': ['商务条款协商', '合同审核']},
        '签约': {'order': 5, 'duration': 7, 'actions': ['合同准备', '签约仪式']}
    }
    
    def __init__(self, db=None):
        self.db = db
        
    def update_stage(self, customer_id: str, new_stage: str) -> Dict:
        """更新商机阶段"""
        current_stage = self._get_current_stage(customer_id)
        
        # 验证阶段转换
        if not self._validate_transition(current_stage, new_stage):
            return {
                'success': False,
                'error': f'无效的阶段转换: {current_stage} -> {new_stage}'
            }
            
        # 更新数据库
        if self.db:
            self.db.update_opportunity_stage(customer_id, new_stage)
            
        # 获取建议
        recommendations = self.get_stage_recommendations(new_stage)
        
        return {
            'success': True,
            'previous_stage': current_stage,
            'new_stage': new_stage,
            'recommendations': recommendations,
            'expected_duration': self.STAGES[new_stage]['duration']
        }
        
    def _get_current_stage(self, customer_id: str) -> Optional[str]:
        """获取当前阶段"""
        if self.db:
            return self.db.get_opportunity_stage(customer_id)
        return '识别'
        
    def _validate_transition(self, current: str, new: str) -> bool:
        """验证阶段转换有效性"""
        if not current:
            return True  # 新商机
            
        current_order = self.STAGES.get(current, {}).get('order', 0)
        new_order = self.STAGES.get(new, {}).get('order', 0)
        
        # 只能前进或跳过相邻阶段
        return new_order >= current_order and new_order - current_order <= 1
        
    def get_stage_recommendations(self, stage: str) -> List[str]:
        """获取阶段建议"""
        return self.STAGES.get(stage, {}).get('actions', [])
        
    def get_pipeline_summary(self, opportunities: List[Dict]) -> Dict:
        """获取管道汇总"""
        summary = {stage: {'count': 0, 'value': 0} for stage in self.STAGES}
        
        for opp in opportunities:
            stage = opp.get('stage', '识别')
            if stage in summary:
                summary[stage]['count'] += 1
                summary[stage]['value'] += opp.get('value', 0)
                
        return summary
        
    def predict_close_date(self, customer_id: str) -> Optional[datetime]:
        """预测签约日期"""
        current_stage = self._get_current_stage(customer_id)
        
        if not current_stage:
            return None
            
        remaining_days = 0
        for stage, info in self.STAGES.items():
            if info['order'] > self.STAGES[current_stage]['order']:
                remaining_days += info['duration']
                
        return datetime.now() + timedelta(days=remaining_days)


from datetime import date
