# 🦞 昆仑巢第三期算能+增长

> 企业级客户增长技能套件 | 五大龙虾模块 | 全链路增长闭环

## 📦 安装

```bash
# 克隆或下载本技能包
cp -r kunlun-sandbox-growth /your/workspace/skills/

# 安装依赖
pip install pandas numpy scikit-learn
```

## 🚀 快速开始

```python
from kunlun_sandbox_growth import (
    Customer360Builder,
    CustomerIntelligenceEngine,
    LeadScoringModel,
    AICustomerProfile,
    ChurnSignalDetector,
    GrowthDataPipeline,
    AIInsightsGenerator
)

# 1. 构建客户360视图
builder = Customer360Builder()
builder.add_customer_data(customers_df)
builder.add_recharge_data(recharges_df)
customer_360 = builder.build()

# 2. 计算客户标签
engine = CustomerIntelligenceEngine()
tags = engine.calculate_customer_tags(customer_data)

# 3. 线索评分
scorer = LeadScoringModel()
score_result = scorer.calculate_lead_score(lead_data)

# 4. 流失预警
detector = ChurnSignalDetector()
signals = detector.monitor_customer_health(customer_data)

# 5. 生成洞察报告
pipeline = GrowthDataPipeline()
pipeline.add_data_source('customers', customers)
pipeline.add_data_source('recharges', recharges)
result = pipeline.build_data_warehouse()

insights_gen = AIInsightsGenerator()
report = insights_gen.generate_weekly_report(result['kpis'])
```

## 📁 模块结构

```
kunlun-sandbox-growth/
├── SKILL.md                    # 技能定义
├── README.md                   # 使用文档
├── __init__.py                 # 包入口
├── data_base/
│   ├── customer_360.py         # 客户360视图
│   └── tags.py                 # 智能标签计算
├── acquisition/
│   ├── lead_scoring.py         # 线索评分
│   └── outreach.py             # 个性化触达
├── crm/
│   ├── profile.py              # 客户画像
│   └── opportunity.py          # 商机管理
├── churn/
│   ├── detector.py             # 流失信号监测
│   ├── prediction.py           # 流失预测
│   └── intervention.py         # 自动干预
└── dashboard/
    ├── etl.py                  # 数据管道
    └── insights.py             # AI洞察报告
```

## 📊 五大模块

| 模块 | 功能 |
|------|------|
| 数据基座龙虾 | 客户360视图、智能标签 |
| 多渠道获客龙虾 | 线索评分、个性化触达 |
| 智能客户管理龙虾 | 客户画像、商机管理 |
| 流失预警雷达龙虾 | 健康监测、流失预测 |
| 增长数据驾驶舱龙虾 | 数据看板、AI洞察 |

## 📋 依赖

- Python 3.8+
- pandas
- numpy
- scikit-learn

## 📞 作者

- **作者：** 丛珊
- **邮箱：** 504714924@qq.com
- **手机：** 13020024267

---

🦞 Built with ❤️ for 昆仑巢黑客松第三期
