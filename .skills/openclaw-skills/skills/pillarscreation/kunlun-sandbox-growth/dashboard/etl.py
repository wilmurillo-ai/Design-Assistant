"""
增长数据驾驶舱龙虾 - 数据管道与ETL
"""
from typing import Dict, List, Any, Optional
from datetime import datetime


class GrowthDataPipeline:
    """增长数据管道"""
    
    def __init__(self):
        self.data_sources = {}
        self.data_cube = {}
        
    def add_data_source(self, name: str, data: Any):
        """添加数据源"""
        self.data_sources[name] = data
        
    def build_data_warehouse(self) -> Dict:
        """构建数据仓库"""
        # 整合数据源
        integrated = self._integrate_data_sources()
        
        # 数据清洗
        cleaned = self._clean_and_transform(integrated)
        
        # 构建数据立方体
        self.data_cube = self._build_data_cube(cleaned)
        
        # 计算KPI
        kpis = self.calculate_kpis(self.data_cube)
        
        return {
            'data_cube': self.data_cube,
            'kpis': kpis,
            'last_updated': datetime.now().isoformat(),
            'data_quality_score': self._calculate_data_quality()
        }
        
    def _integrate_data_sources(self) -> Dict:
        """整合多源数据"""
        return self.data_sources
        
    def _clean_and_transform(self, data: Dict) -> Dict:
        """数据清洗与转换"""
        cleaned = {}
        
        for source_name, source_data in data.items():
            # 简单的数据清洗
            if isinstance(source_data, list):
                cleaned[source_name] = [self._clean_record(r) for r in source_data]
            else:
                cleaned[source_name] = source_data
                
        return cleaned
        
    def _clean_record(self, record: Dict) -> Dict:
        """清洗单条记录"""
        cleaned = {}
        for key, value in record.items():
            if value is None:
                cleaned[key] = 0 if isinstance(value, int) else ''
            else:
                cleaned[key] = value
        return cleaned
        
    def _build_data_cube(self, data: Dict) -> Dict:
        """构建数据立方体"""
        cube = {}
        
        # 客户维度
        if 'customers' in data:
            cube['customers'] = self._aggregate_customers(data['customers'])
            
        # 收入维度
        if 'recharges' in data:
            cube['revenue'] = self._aggregate_revenue(data['recharges'])
            
        # 使用维度
        if 'api_usage' in data:
            cube['usage'] = self._aggregate_usage(data['api_usage'])
            
        return cube
        
    def _aggregate_customers(self, customers: List[Dict]) -> Dict:
        """客户聚合"""
        return {
            'total': len(customers),
            'by_tier': self._group_by(customers, 'customer_tier'),
            'by_industry': self._group_by(customers, 'industry'),
            'by_activity': self._group_by(customers, 'activity_status')
        }
        
    def _aggregate_revenue(self, recharges: List[Dict]) -> Dict:
        """收入聚合"""
        total = sum(r.get('amount', 0) for r in recharges)
        
        return {
            'total': total,
            'mrr': total / 12,  # 简化的MRR计算
            'by_month': self._group_by_time(recharges, 'recharge_date'),
            'avg_order_value': total / len(recharges) if recharges else 0
        }
        
    def _aggregate_usage(self, usage: List[Dict]) -> Dict:
        """使用聚合"""
        return {
            'total_calls': sum(u.get('api_calls', 0) for u in usage),
            'total_tokens': sum(u.get('tokens_used', 0) for u in usage),
            'by_model': self._group_by(usage, 'model')
        }
        
    def _group_by(self, data: List[Dict], field: str) -> Dict:
        """分组统计"""
        groups = {}
        for record in data:
            key = record.get(field, 'unknown')
            groups[key] = groups.get(key, 0) + 1
        return groups
        
    def _group_by_time(self, data: List[Dict], date_field: str) -> Dict:
        """时间分组"""
        groups = {}
        for record in data:
            date_val = record.get(date_field)
            if date_val:
                if isinstance(date_val, str):
                    key = date_val[:7]  # YYYY-MM
                else:
                    key = 'unknown'
                groups[key] = groups.get(key, 0) + record.get('amount', 0)
        return groups
        
    def calculate_kpis(self, data_cube: Dict) -> Dict:
        """计算关键绩效指标"""
        kpis = {
            'financial': {},
            'customer': {},
            'product': {}
        }
        
        # 财务KPI
        if 'revenue' in data_cube:
            rev = data_cube['revenue']
            kpis['financial']['total_revenue'] = rev.get('total', 0)
            kpis['financial']['mrr'] = rev.get('mrr', 0)
            kpis['financial']['avg_order_value'] = rev.get('avg_order_value', 0)
            
        # 客户KPI
        if 'customers' in data_cube:
            cust = data_cube['customers']
            kpis['customer']['total_customers'] = cust.get('total', 0)
            kpis['customer']['active_customers'] = cust.get('by_activity', {}).get('正常', 0)
            
        # 产品KPI
        if 'usage' in data_cube:
            usage = data_cube['usage']
            kpis['product']['total_api_calls'] = usage.get('total_calls', 0)
            kpis['product']['total_tokens'] = usage.get('total_tokens', 0)
            
        return kpis
        
    def _calculate_data_quality(self) -> float:
        """计算数据质量分数"""
        # 简化版数据质量计算
        return 0.95


class GrowthDashboard:
    """增长仪表板"""
    
    def __init__(self, pipeline: GrowthDataPipeline):
        self.pipeline = pipeline
        
    def render(self) -> Dict:
        """渲染仪表板"""
        return {
            'overview': self._render_overview(),
            'revenue_chart': self._render_revenue_chart(),
            'customer_segmentation': self._render_segmentation(),
            'usage_trends': self._render_usage_trends()
        }
        
    def _render_overview(self) -> Dict:
        """渲染概览卡片"""
        return {
            'total_customers': 0,
            'total_revenue': 0,
            'active_rate': 0,
            'health_score': 0
        }
        
    def _render_revenue_chart(self) -> Dict:
        """渲染收入图表"""
        return {'type': 'line', 'data': []}
        
    def _render_segmentation(self) -> Dict:
        """渲染客户分层"""
        return {'type': 'pie', 'data': []}
        
    def _render_usage_trends(self) -> Dict:
        """渲染使用趋势"""
        return {'type': 'bar', 'data': []}
