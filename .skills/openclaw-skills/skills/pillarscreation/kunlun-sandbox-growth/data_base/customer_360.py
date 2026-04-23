"""
数据基座龙虾 - 客户360视图构建
"""
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime, date


class Customer360Builder:
    """构建客户360度视图宽表"""
    
    def __init__(self):
        self.data_sources = {}
        
    def add_customer_data(self, df: pd.DataFrame):
        """添加客户基础数据"""
        self.data_sources['customers'] = df
        return self
        
    def add_recharge_data(self, df: pd.DataFrame):
        """添加充值记录数据"""
        self.data_sources['recharges'] = df
        return self
        
    def add_api_usage(self, df: pd.DataFrame):
        """添加API使用日志"""
        self.data_sources['api_usage'] = df
        return self
        
    def add_project_data(self, df: pd.DataFrame):
        """添加项目交付数据"""
        self.data_sources['projects'] = df
        return self
        
    def add_campaign_data(self, df: pd.DataFrame):
        """添加营销活动数据"""
        self.data_sources['campaigns'] = df
        return self
        
    def build(self) -> pd.DataFrame:
        """构建客户360视图"""
        if 'customers' not in self.data_sources:
            raise ValueError("需要先添加客户基础数据")
            
        customers = self.data_sources['customers'].copy()
        
        # 计算财务指标
        if 'recharges' in self.data_sources:
            customers = self._calculate_financial_metrics(customers)
            
        # 计算使用行为指标
        if 'api_usage' in self.data_sources:
            customers = self._calculate_usage_metrics(customers)
            
        # 计算项目指标
        if 'projects' in self.data_sources:
            customers = self._calculate_project_metrics(customers)
            
        # 计算营销互动指标
        if 'campaigns' in self.data_sources:
            customers = self._calculate_campaign_metrics(customers)
            
        return customers
        
    def _calculate_financial_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算财务指标"""
        recharges = self.data_sources['recharges']
        
        agg = recharges.groupby('customer_id').agg({
            'amount': ['sum', 'mean', 'count'],
            'recharge_date': 'max'
        }).reset_index()
        agg.columns = ['customer_id', 'total_recharge_amount', 
                      'avg_recharge_amount', 'recharge_count', 'last_recharge_date']
        
        df = df.merge(agg, on='customer_id', how='left')
        df['total_recharge_amount'] = df['total_recharge_amount'].fillna(0)
        df['avg_recharge_amount'] = df['avg_recharge_amount'].fillna(0)
        
        return df
        
    def _calculate_usage_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算使用行为指标"""
        usage = self.data_sources['api_usage']
        
        agg = usage.groupby('customer_id').agg({
            'api_calls': 'sum',
            'tokens_used': 'sum',
            'call_date': ['max', 'mean']
        }).reset_index()
        agg.columns = ['customer_id', 'api_total_calls', 'total_tokens',
                      'last_api_call_date', 'avg_call_date']
        
        df = df.merge(agg, on='customer_id', how='left')
        
        return df
        
    def _calculate_project_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算项目指标"""
        projects = self.data_sources['projects']
        
        agg = projects.groupby('customer_id').agg({
            'project_id': 'count',
            'project_value': 'sum'
        }).reset_index()
        agg.columns = ['customer_id', 'active_project_count', 'total_project_value']
        
        df = df.merge(agg, on='customer_id', how='left')
        df['active_project_count'] = df['active_project_count'].fillna(0)
        df['total_project_value'] = df['total_project_value'].fillna(0)
        
        return df
        
    def _calculate_campaign_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算营销互动指标"""
        campaigns = self.data_sources['campaigns']
        
        agg = campaigns.groupby('customer_id').agg({
            'campaign_id': 'count',
            'engagement_date': 'max'
        }).reset_index()
        agg.columns = ['customer_id', 'campaign_participation_count', 
                      'last_campaign_engagement']
        
        df = df.merge(agg, on='customer_id', how='left')
        
        return df
        
    def calculate_ltv(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算客户生命周期价值"""
        # 简化版 LTV = 总充值金额 + 项目价值 * 0.3
        df['lifetime_value'] = df['total_recharge_amount'] + df['total_project_value'] * 0.3
        return df
        
    def calculate_health_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算客户健康度评分 (0-100)"""
        scores = []
        
        for _, row in df.iterrows():
            score = 50  # 基础分
            
            # 充值金额加分
            if row.get('total_recharge_amount', 0) > 100000:
                score += 20
            elif row.get('total_recharge_amount', 0) > 10000:
                score += 10
                
            # 活跃度加分
            if row.get('api_total_calls', 0) > 1000:
                score += 15
            elif row.get('api_total_calls', 0) > 100:
                score += 10
                
            # 项目加分
            if row.get('active_project_count', 0) > 0:
                score += 15
                
            scores.append(min(score, 100))
            
        df['health_score'] = scores
        return df


def build_customer_360(
    customers: pd.DataFrame,
    recharges: pd.DataFrame = None,
    api_usage: pd.DataFrame = None,
    projects: pd.DataFrame = None,
    campaigns: pd.DataFrame = None
) -> pd.DataFrame:
    """快速构建客户360视图"""
    builder = Customer360Builder()
    builder.add_customer_data(customers)
    
    if recharges is not None:
        builder.add_recharge_data(recharges)
    if api_usage is not None:
        builder.add_api_usage(api_usage)
    if projects is not None:
        builder.add_project_data(projects)
    if campaigns is not None:
        builder.add_campaign_data(campaigns)
        
    result = builder.build()
    result = builder.calculate_ltv(result)
    result = builder.calculate_health_score(result)
    
    return result
