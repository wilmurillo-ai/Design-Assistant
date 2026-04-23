---
name: kunlun-sandbox-growth
description: 昆仑巢第三期算能+增长 - 企业级客户增长技能套件。包含数据基座、智能获客、客户管理、流失预警、决策驾驶舱五大模块。适用于销售、CRM、客户成功团队。
version: 1.0.0
author: 丛珊
tags:
  - growth
  - crm
  - customer-success
  - sales
  - marketing
  - analytics
  - ai
---

# 🦞 昆仑巢第三期算能+增长

> 企业级客户增长技能套件 | 五大龙虾模块 | 全链路增长闭环

---

## 📊 项目概览

本技能套件针对 **IT行业销售领域**，构建 AI 驱动的全链路智能营销与客户成功解决方案。

### 核心成果
- ✅ **数据基座龙虾** - 客户 360°视图宽表
- ✅ **智能标签体系** - 6 类客户自动打标
- ✅ **健康度评分** - 0-100 分实时监控
- ✅ **五大模块** - 全部可运行调用

### 预期效果
| 指标 | 预期提升 |
|------|----------|
| 获客成本降低 | 30-40% |
| 销售人效提升 | 50% |
| 客户流失率降低 | 25% |
| 决策响应提升 | 70% |

---

## 🦞 五大核心模块

### 1️⃣ 数据基座龙虾

统一客户数据平台 (CDP)，构建客户 360° 视图。

**功能：**
- 客户 360 度宽表自动构建
- RFM 模型分层（最近消费、消费频率、消费金额）
- 智能标签动态计算
- 多源数据整合

**数据模型：**
```sql
-- 客户360度宽表视图
CREATE TABLE cdp_customer_360 (
 customer_id VARCHAR(50) PRIMARY KEY,
 company_name VARCHAR(200),
 industry VARCHAR(50),
 company_size VARCHAR(20),
 
 -- 财务指标
 total_recharge_amount DECIMAL(15,2),
 last_recharge_date DATE,
 current_token_balance DECIMAL(15,2),
 
 -- 使用行为
 api_daily_avg_usage DECIMAL(15,2),
 api_total_calls BIGINT,
 most_used_model VARCHAR(50),
 
 -- 项目参与
 active_project_count INT,
 total_project_value DECIMAL(15,2),
 
 -- 自动计算标签
 customer_tier VARCHAR(20),  -- 高价值/普通/免费
 activity_status VARCHAR(20), -- 高活跃/正常/沉睡
 customer_type VARCHAR(20),  -- 项目型/API型/混合型
 risk_score DECIMAL(5,2)
);
```

**智能标签计算：**
```python
class CustomerIntelligenceEngine:
 def calculate_customer_tags(self, customer_data):
 tags = []
 
 # 高价值客户标签
 if customer_data['total_recharge_amount'] > 100000:
 tags.append({
 'tag_name': '高价值客户',
 'category': '价值分层',
 'confidence': 1.0
 })
 
 # 高活跃客户标签
 if customer_data['api_daily_avg_usage'] > 1000:
 tags.append({
 'tag_name': '高活跃客户',
 'category': '活跃度',
 'confidence': 0.9
 })
 
 # 沉睡客户标签
 if self._is_dormant(customer_data):
 tags.append({
 'tag_name': '沉睡客户',
 'category': '风险预警',
 'confidence': 0.85
 })
 
 return tags
```

---

### 2️⃣ 多渠道获客龙虾

AI 驱动的精准引流与线索管理。

**功能：**
- 潜在客户线索评分
- 个性化内容生成（AIGC）
- 自动化触达工作流
- 智能落地页动态展示

**线索评分模型：**
```python
class LeadScoringModel:
 def __init__(self):
 self.industry_weights = {
 '金融': 1.2,
 '政务': 1.1,
 '医疗': 1.15,
 '教育': 1.0,
 '其他': 0.8
 }
 
 def calculate_lead_score(self, lead_data):
 score = 50  # 基础分
 
 # 行业加分
 industry = lead_data.get('industry', '其他')
 score += self.industry_weights.get(industry, 0.8) * 10
 
 # 公司规模加分
 company_size = lead_data.get('company_size', '小型企业')
 score += self.company_size_weights.get(company_size, 0.9) * 10
 
 # 行为数据加分
 if lead_data.get('viewed_api_docs', False):
 score += 15
 if lead_data.get('demo_requested', False):
 score += 20
 
 return min(score, 100)
```

**个性化触达：**
```python
class MultiChannelAcquisitionWorkflow:
 def trigger_welcome_email(self, customer):
 """AI生成个性化欢迎邮件"""
 prompt = f"""
 为{customer['industry']}行业的客户{customer['company_name']}生成欢迎邮件：
 1. 介绍我们AI服务在{customer['industry']}的应用案例
 2. 提供Token使用指南
 3. 个性化问候
 """
 return self.openclaw.generate_content(prompt)
```

---

### 3️⃣ 智能客户管理龙虾

销售/SDR 提效助手，客户全生命周期管理。

**功能：**
- AI 客户画像自动生成
- 商机阶段自动化管理
- 销售对话自动填单
- 智能待办与行动建议

**客户画像报告：**
```python
class AICustomerProfile:
 def generate_profile_report(self, customer_id):
 customer_data = self.cdp.get_customer_360(customer_id)
 
 report = {
 'customer_summary': {
 'name': customer_data['company_name'],
 'tier': customer_data['customer_tier'],
 'health_score': self.calculate_health_score(customer_data)
 },
 'financial_overview': {
 'total_spent': customer_data['total_recharge_amount'],
 'lifetime_value': self.calculate_ltv(customer_data)
 },
 'ai_recommendations': self.generate_ai_recommendations(customer_data)
 }
 return report
```

**商机阶段管理：**
```python
class OpportunityStageManager:
 STAGES = {
 '识别': {'order': 1, 'duration': 7},
 '确认': {'order': 2, 'duration': 14},
 '方案': {'order': 3, 'duration': 21},
 '谈判': {'order': 4, 'duration': 14},
 '签约': {'order': 5, 'duration': 7}
 }
 
 def get_stage_recommendations(self, stage):
 return {
 '识别': ['完善客户画像', '初步需求调研', '安排初次会议'],
 '确认': ['深入需求分析', '技术可行性评估', '制定初步方案'],
 '方案': ['详细方案设计', '技术架构评审', '报价方案准备'],
 '谈判': ['商务条款协商', '法律条款审核', '最终方案确认'],
 '签约': ['合同准备', '内部审批流程', '签约仪式安排']
 }.get(stage, [])
```

---

### 4️⃣ 流失预警雷达龙虾

主动客户留存，预测与干预系统。

**功能：**
- 多维度健康度监控
- 流失风险预测模型
- 自动干预策略触发
- 客户成功工作流自动化

**流失信号监测：**
```python
class ChurnSignalDetector:
 def __init__(self):
 self.signals_config = {
 'usage_drop': {'threshold': 0.7, 'time_window': 14},
 'inactivity': {'threshold_days': 30, 'check_interval': 7},
 'token_stagnation': {'threshold': 1000, 'duration_days': 60},
 'support_tickets': {'recent_tickets': 3, 'negative_sentiment': True}
 }
 
 def monitor_customer_health(self, customer_data):
 signals = []
 
 if self._check_usage_drop(customer_data):
 signals.append({
 'type': 'usage_drop',
 'severity': 'high',
 'description': 'API调用频率显著下降'
 })
 
 if self._check_inactivity(customer_data):
 signals.append({
 'type': 'inactivity',
 'severity': 'medium',
 'description': '客户长期无活动'
 })
 
 return signals
```

**流失预测模型：**
```python
class ChurnPredictionModel:
 def predict_churn_risk(self, customer_features):
 churn_probability = self.model.predict_proba([processed_features])[0][1]
 
 risk_level = self._determine_risk_level(churn_probability)
 
 return {
 'customer_id': customer_features['customer_id'],
 'churn_probability': churn_probability,
 'risk_level': risk_level,  # critical/high/medium/low
 'key_factors': self._extract_key_factors(customer_features)
 }
 
 def _determine_risk_level(self, probability):
 if probability >= 0.8: return 'critical'
 elif probability >= 0.6: return 'high'
 elif probability >= 0.4: return 'medium'
 else: return 'low'
```

**自动干预系统：**
```python
class AutomatedInterventionSystem:
 def trigger_interventions(self, churn_prediction):
 interventions = []
 
 if churn_prediction['risk_level'] in ['high', 'critical']:
 interventions.append(self.notification.notify_csm(churn_prediction))
 interventions.append(self.send_care_email(churn_prediction))
 
 if churn_prediction['risk_level'] == 'critical':
 interventions.append(self.schedule_phone_call(churn_prediction))
 
 return interventions
```

---

### 5️⃣ 增长数据驾驶舱龙虾

决策智能中枢，可视化与 AI 洞察。

**功能：**
- 多维度数据看板
- KPI 实时监控
- AI 洞察报告自动生成
- 收入预测

**数据仓库与 KPI 计算：**
```python
class GrowthDataPipeline:
 def calculate_kpis(self, data_cube):
 return {
 'financial': {
 'total_revenue': self.sum_revenue(data_cube),
 'mrr': self.calculate_mrr(data_cube),
 'arr': self.calculate_arr(data_cube),
 'cac': self.calculate_cac(data_cube),
 'ltv': self.calculate_ltv(data_cube)
 },
 'customer': {
 'new_customers': self.count_new_customers(data_cube),
 'churned_customers': self.count_churned_customers(data_cube),
 'nps_score': self.calculate_nps(data_cube)
 },
 'product': {
 'total_api_calls': self.sum_api_calls(data_cube),
 'active_users': self.count_active_users(data_cube)
 }
 }
```

**AI 洞察报告生成：**
```python
class AIInsightsGenerator:
 def generate_weekly_report(self, growth_data):
 trends = self.analyze_trends(growth_data)
 anomalies = self.detect_anomalies(growth_data)
 insights = self.generate_insights(trends, anomalies)
 
 report = {
 'period': {...},
 'executive_summary': self.generate_executive_summary(insights),
 'trend_analysis': trends,
 'anomaly_alerts': anomalies,
 'deep_dive_insights': insights,
 'actionable_recommendations': recommendations,
 'risk_assessment': self.assess_risks(growth_data)
 }
 return report
```

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│ 前端展示层 │
│ 销售工作台 │ 管理驾驶舱 │ 客户门户 │
└─────────────────────────────────────────────────────┘
 │
┌─────────────────────────────────────────────────────┐
│ API网关层 │
│ 认证 │ 限流 │ 监控 │ 日志 │ 路由 │ 缓存 │
└─────────────────────────────────────────────────────┘
 |
┌─────────────────────────────────────────────────────┐
│ 业务服务层 │
│ 数据基座 │ 获客引擎 │ 客户管理 │ 流失预警 │
│ AI能力中心 (OpenClaw) │
└─────────────────────────────────────────────────────┘
 |
┌─────────────────────────────────────────────────────┐
│ 数据存储层 │
│ CDP宽表 │ 数据湖 │ 数仓 │ 缓存 │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 安装依赖
```bash
pip install pandas numpy scikit-learn
```

### 基本使用
```python
from kunlun_sandbox_growth import (
    CustomerIntelligenceEngine,
    LeadScoringModel,
    AICustomerProfile,
    ChurnSignalDetector,
    GrowthDataPipeline
)

# 1. 构建客户标签
engine = CustomerIntelligenceEngine()
tags = engine.calculate_customer_tags(customer_data)

# 2. 线索评分
scorer = LeadScoringModel()
score = scorer.calculate_lead_score(lead_data)

# 3. 生成客户画像
profiler = AICustomerProfile(cdp_client)
report = profiler.generate_profile_report(customer_id)

# 4. 流失预警
detector = ChurnSignalDetector()
signals = detector.monitor_customer_health(customer_data)

# 5. 数据驾驶舱
pipeline = GrowthDataPipeline()
kpis = pipeline.calculate_kpis(data_cube)
```

---

## 📁 文件结构

```
kunlun-sandbox-growth/
├── SKILL.md                    # 技能定义（本文件）
├── README.md                   # 使用文档
├── data_base/
│   ├── customer_360.py         # 客户360视图
│   └── tags.py                 # 智能标签计算
├── acquisition/
│   ├── lead_scoring.py         # 线索评分
│   └── outreach.py             # 个性化触达
├── crm/
│   ├── profile.py              # 客户画像
│   ├── opportunity.py          # 商机管理
│   └── autofill.py             # 自动填单
├── churn/
│   ├── detector.py             # 流失信号监测
│   ├── prediction.py           # 流失预测
│   └── intervention.py         # 自动干预
└── dashboard/
    ├── etl.py                   # 数据管道
    ├── metrics.py              # KPI计算
    └── insights.py             # AI洞察报告
```

---

## 📅 实施路线图

| 阶段 | 时间 | 内容 |
|------|------|------|
| 第一阶段 | 1-2月 | 数据基础建设 |
| 第二阶段 | 2-3月 | 获客优化 |
| 第三阶段 | 3-4月 | 销售赋能 |
| 第四阶段 | 4-5月 | 留存提升 |
| 第五阶段 | 5-6月 | 决策智能化 |

---

## 📞 作者

- **作者：** 丛珊
- **邮箱：** 504714924@qq.com
- **手机：** 13020024267

---

## 🦞 关于

**昆仑巢第三期算能+增长** 是基于 OpenClaw 构建的企业级客户增长技能套件。

五大龙虾模块覆盖：
- 📊 数据基座 → 统一客户视图
- 🎯 智能获客 → 精准引流转化
- 👤 客户管理 → 销售提效
- ⚠️ 流失预警 → 主动留存
- 📈 决策驾驶舱 → 智能洞察

让增长持续、自动、可优化。

---

*Built with ❤️ for 昆仑巢黑客松第三期*
