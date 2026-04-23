"""
昆仑巢第三期算能+增长 - 企业级客户增长技能套件

五大模块：
- data_base: 数据基座龙虾
- acquisition: 多渠道获客龙虾
- crm: 智能客户管理龙虾
- churn: 流失预警雷达龙虾
- dashboard: 增长数据驾驶舱龙虾
"""

__version__ = "1.0.0"
__author__ = "丛珊"

from .data_base.customer_360 import Customer360Builder
from .data_base.tags import CustomerIntelligenceEngine
from .acquisition.lead_scoring import LeadScoringModel
from .acquisition.outreach import MultiChannelAcquisitionWorkflow
from .crm.profile import AICustomerProfile
from .crm.opportunity import OpportunityStageManager
from .churn.detector import ChurnSignalDetector
from .churn.prediction import ChurnPredictionModel
from .churn.intervention import AutomatedInterventionSystem
from .dashboard.etl import GrowthDataPipeline
from .dashboard.insights import AIInsightsGenerator

__all__ = [
    "Customer360Builder",
    "CustomerIntelligenceEngine",
    "LeadScoringModel",
    "MultiChannelAcquisitionWorkflow",
    "AICustomerProfile",
    "OpportunityStageManager",
    "ChurnSignalDetector",
    "ChurnPredictionModel",
    "AutomatedInterventionSystem",
    "GrowthDataPipeline",
    "AIInsightsGenerator",
]
