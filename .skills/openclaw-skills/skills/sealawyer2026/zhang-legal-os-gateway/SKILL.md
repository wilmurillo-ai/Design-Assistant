---
name: zhang-legal-os-gateway
version: 1.0.0
description: |
  九章法律智能操作系统 - 统一入口网关

  核心定位：法律服务的"操作系统入口"
  
  设计理念：
  - 统一入口：一个入口，千面服务
  - 身份感知：智能识别用户身份和需求
  - 动态匹配：根据身份+需求匹配最优服务流程
  - 普惠定价：按需定价，分层服务
  
  核心功能模块：
  1. 用户身份识别与认证
  2. 需求意图智能解析
  3. 服务路由与专家匹配
  4. 工作流编排与调度
  5. 计费与权限管理
  6. 多轮对话上下文管理

  服务对象：个人、律师、企业法务、政府机关、法律教育机构
  
  输出价值：让法律服务像使用操作系统一样简单
---

# 九章法律智能操作系统 - 统一入口网关

> 🏛️ **一个入口，千面服务，按需匹配，普惠万家**

## 🎯 核心定位

九章法律智能操作系统（Zhang Legal OS）的统一入口网关，是用户接触九章法律AI帝国的**第一站**。

### 设计哲学

```
┌─────────────────────────────────────────────────────────┐
│                    用户视角                              │
│  "我有法律问题"  →  【九章法律OS】  →  "问题解决了"       │
│                                                         │
│  简单、智能、高效、普惠                                  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   系统内部                               │
│  身份识别 → 需求分析 → 路由匹配 → 服务编排 → 结果交付   │
│                                                         │
│  88+专家技能协同工作，智能调度最优资源                   │
└─────────────────────────────────────────────────────────┘
```

---

## 👤 用户身份体系

### 身份分层模型

```yaml
user_tiers:
  tier_0_public:        # 公益层
    name: "公益用户"
    target: "低收入群体、特殊群体"
    price: "免费"
    features:
      - 基础法律咨询
      - 普法知识问答
      - 标准文书模板
      - 法律援助指引
      
  tier_1_individual:    # 基础层
    name: "个人用户"
    target: "一般市民、法律小白"
    price: "￥9.9/月"
    features:
      - 智能法律咨询
      - 文书自动生成
      - 案件初步评估
      - 法律知识库
      
  tier_2_professional:  # 专业层
    name: "法律从业者"
    target: "律师、法务、法律工作者"
    price: "￥99/月"
    features:
      - 专业法律检索
      - 案例深度分析
      - 合同智能审查
      - 工作流管理工具
      - 专家社群
      
  tier_3_enterprise:    # 企业层
    name: "企业法务"
    target: "公司法务部门、中小企业"
    price: "￥999/月"
    features:
      - 企业合规检查
      - 合同批量审查
      - 风险评估报告
      - 法务管理系统
      - API接入
      
  tier_4_government:    # 政府层
    name: "政府机关"
    target: "公务员、政府部门"
    price: "政府采购"
    features:
      - 依法行政辅助
      - 合规审计工具
      - 政府合同管理
      - 信息公开咨询
      - 私有化部署
      
  tier_5_education:     # 教育层
    name: "法律教育机构"
    target: "法学院、培训机构"
    price: "教育许可"
    features:
      - 教学案例库
      - 模拟实训系统
      - 法考辅导工具
      - 学术研究支持
```

### 身份识别机制

```
用户进入系统
      │
      ▼
┌──────────────────────┐
│ 1. 登录认证          │
│    - 手机号/邮箱     │
│    - 微信/企业微信   │
│    - 政府统一认证    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 2. 身份确认          │
│    - 职业认证        │
│    - 机构绑定        │
│    - 资质验证        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ 3. 权限加载          │
│    - 可用技能列表    │
│    - 服务额度        │
│    - 定价标准        │
└──────────┬───────────┘
           │
           ▼
      进入服务界面
```

---

## 🧠 需求意图解析

### 意图识别流程

```
用户输入
  │
  ▼
┌─────────────────────────────────────┐
│ Stage 1: 预处理                     │
│ - 分词                              │
│ - 实体识别（人名、地名、金额等）    │
│ - 法律术语提取                      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Stage 2: 意图分类                   │
│                                     │
│ ├─ 咨询类 (40%)                    │
│ │   ├─ 法律问题咨询                 │
│ │   ├─ 程序流程咨询                 │
│ │   └─ 权益保障咨询                 │
│ │                                   │
│ ├─ 文书类 (25%)                    │
│ │   ├─ 合同起草/审查                │
│ │   ├─ 诉讼文书生成                 │
│ │   └─ 法律意见书                   │
│ │                                   │
│ ├─ 案件类 (20%)                    │
│ │   ├─ 案件评估                     │
│ │   ├─ 律师匹配                     │
│ │   └─ 案件管理                     │
│ │                                   │
│ ├─ 合规类 (10%)                    │
│ │   ├─ 企业合规检查                 │
│ │   ├─ 政府合规审计                 │
│ │   └─ 风险评估                     │
│ │                                   │
│ └─ 研究类 (5%)                     │
│     ├─ 法律检索                     │
│     ├─ 案例分析                     │
│     └─ 学术研究                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Stage 3: 复杂度评估                 │
│                                     │
│ ├─ 简单 (60%) → AI自助解决         │
│ ├─ 中等 (30%) → AI+专家审核        │
│ └─ 复杂 (10%) → 人工专家介入       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Stage 4: 路由匹配                   │
│ - 匹配最佳技能组合                  │
│ - 确定服务流程                      │
│ - 预估费用                          │
└─────────────────────────────────────┘
```

### 多轮对话管理

```yaml
dialog_context:
  session_id: "uuid"           # 会话ID
  user_id: "user_uuid"         # 用户ID
  user_tier: "individual"      # 用户层级
  
  conversation:
    - turn: 1
      user: "我想离婚"
      intent: "离婚咨询"
      entities:
        - type: "婚姻家事"
          value: "离婚"
      complexity: "medium"
      
    - turn: 2
      user: "有孩子，财产怎么分？"
      intent: "财产分割咨询"
      entities:
        - type: "子女抚养"
          value: "孩子"
        - type: "财产分割"
          value: "财产"
      complexity: "high"
      
    - turn: 3
      system: "根据您的情况，建议..."
      skills_invoked:
        - zhang-family-law
        - zhang-property-division
      
  context_memory:
    - 婚姻状态
    - 子女情况
    - 财产状况
    - 咨询历史
```

---

## 🔄 服务路由与编排

### 智能路由决策树

```
用户请求
    │
    ▼
┌─────────────────────────────────────┐
│ 路由决策引擎                        │
│                                     │
│ IF 用户类型 = 个人:                │
│   IF 需求类型 = 咨询:              │
│     → zhang-legal-advice           │
│   ELIF 需求类型 = 文书:            │
│     → zhang-document-generator     │
│   ELIF 需求类型 = 案件:            │
│     → zhang-case-assessment        │
│                                     │
│ ELIF 用户类型 = 律师:              │
│   IF 需求类型 = 研究:              │
│     → zhang-legal-research         │
│   ELIF 需求类型 = 案件管理:        │
│     → zhang-case-management        │
│   ELIF 需求类型 = 计费:            │
│     → zhang-billing-tracker        │
│                                     │
│ ELIF 用户类型 = 企业:              │
│   IF 需求类型 = 合规:              │
│     → zhang-compliance-audit       │
│   ELIF 需求类型 = 合同:            │
│     → zhang-contract-review        │
│                                     │
│ ELIF 用户类型 = 政府:              │
│   IF 需求类型 = 法务:              │
│     → zhang-government-legal       │
│   ELIF 需求类型 = 合规:            │
│     → zhang-government-compliance  │
│                                     │
└─────────────────────────────────────┘
```

### 工作流编排示例

#### 示例：企业合同审查工作流

```yaml
workflow_name: "企业合同智能审查"
trigger: "企业用户上传合同文件"

steps:
  - step: 1
    name: "合同解析"
    skill: zhang-contract-parser
    output: contract_structure
    
  - step: 2
    name: "类型识别"
    skill: zhang-contract-classifier
    input: contract_structure
    output: contract_type
    
  - step: 3
    name: "风险扫描"
    skill: zhang-contract-risk-scan
    input: 
      - contract_structure
      - contract_type
    output: risk_report
    
  - step: 4
    name: "合规检查"
    skill: zhang-compliance-checker
    input:
      - contract_structure
      - contract_type
      - user_industry
    output: compliance_report
    condition: "if user_tier in ['enterprise', 'government']"
    
  - step: 5
    name: "条款比对"
    skill: zhang-clause-comparison
    input:
      - contract_structure
      - industry_templates
    output: comparison_report
    
  - step: 6
    name: "修改建议"
    skill: zhang-contract-revision
    input:
      - risk_report
      - compliance_report
      - comparison_report
    output: revision_suggestions
    
  - step: 7
    name: "报告生成"
    skill: zhang-report-generator
    input:
      - contract_structure
      - risk_report
      - compliance_report
      - revision_suggestions
    output: final_report
    format: "PDF/Word"
    
  - step: 8
    name: "专家复核"
    skill: zhang-expert-review
    input: final_report
    condition: "if risk_level == 'high'"
    output: expert_opinion
    
pricing:
  base: ￥99
  expert_review: +￥500
  total: dynamic
```

---

## 💰 计费与定价引擎

### 定价策略

```python
class PricingEngine:
    """
    九章法律OS定价引擎
    """
    
    TIER_PRICING = {
        'public': {
            'monthly': 0,           # 免费
            'per_query': 0,
            'features': ['basic_advice', 'templates']
        },
        'individual': {
            'monthly': 9.9,
            'per_query': 0,
            'quota': {'queries': 100, 'documents': 10},
            'features': ['ai_advice', 'doc_generation']
        },
        'professional': {
            'monthly': 99,
            'per_query': 0,
            'quota': {'queries': 1000, 'documents': 100, 'research': 50},
            'features': ['all_tools', 'case_analysis', 'api_access']
        },
        'enterprise': {
            'monthly': 999,
            'per_query': 0,
            'quota': {'unlimited': True},
            'features': ['all_tools', 'dedicated_support', 'custom_development']
        },
        'government': {
            'pricing': 'custom',    # 政府采购
            'features': ['all_tools', 'on_premise', 'security_audit']
        }
    }
    
    def calculate_price(self, user_tier, service_type, complexity, urgency):
        """
        动态定价计算
        """
        base = self.TIER_PRICING[user_tier]['monthly']
        
        # 服务类型系数
        service_multiplier = {
            'consultation': 1.0,
            'document': 1.5,
            'case_assessment': 2.0,
            'compliance_audit': 3.0,
            'expert_review': 5.0
        }
        
        # 复杂度系数
        complexity_multiplier = {
            'simple': 1.0,
            'medium': 1.5,
            'complex': 2.5,
            'expert': 5.0
        }
        
        # 紧急程度系数
        urgency_multiplier = {
            'normal': 1.0,
            'urgent': 1.5,
            'emergency': 2.0
        }
        
        price = base * service_multiplier[service_type] * \
                complexity_multiplier[complexity] * \
                urgency_multiplier[urgency]
        
        return round(price, 2)
```

---

## 🔐 权限与安全

### 权限控制矩阵

| 功能 | 公益层 | 个人层 | 专业层 | 企业层 | 政府层 |
|:---|:---:|:---:|:---:|:---:|:---:|
| 基础咨询 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 文书生成 | ❌ | ✅(10份) | ✅(100份) | ✅(无限) | ✅(无限) |
| 案例检索 | ❌ | 基础 | 完整 | 完整 | 完整 |
| 合同审查 | ❌ | 基础 | 完整 | 完整+批量 | 完整+定制 |
| API接入 | ❌ | ❌ | ✅ | ✅ | ✅ |
| 私有化部署 | ❌ | ❌ | ❌ | ❌ | ✅ |
| 专家对接 | ❌ | 付费 | 优惠 | 优先 | 专属 |

---

## 🚀 使用示例

### 示例1：个人用户法律咨询

**用户输入**："我被公司违法辞退了，能拿多少赔偿？"

**系统处理**：
1. **身份识别**：个人用户（Tier 1）
2. **意图解析**：劳动争议咨询 + 赔偿计算
3. **复杂度评估**：中等复杂度
4. **技能调用**：
   - `zhang-labor-law` - 劳动法分析
   - `zhang-compensation-calc` - 赔偿计算
5. **服务输出**：
   - 法律依据说明
   - 赔偿金额计算
   - 维权流程指引
   - 相关文书模板
6. **计费**：￥9.9（已含在月费中）

### 示例2：企业合同审查

**用户输入**：上传《采购合同》文件

**系统处理**：
1. **身份识别**：企业法务（Tier 3）
2. **意图解析**：合同审查
3. **工作流编排**：
   - 合同解析 → 类型识别 → 风险扫描 → 合规检查 → 条款比对 → 修改建议 → 报告生成
4. **技能调用**：7个技能协同
5. **服务输出**：
   - 风险评估报告
   - 合规检查结果
   - 条款修改建议
   - 修改后合同文本
6. **计费**：￥299（基础审查）+ ￥500（专家复核）= ￥799

### 示例3：政府依法行政咨询

**用户输入**："这个行政处罚决定书是否合法？"

**系统处理**：
1. **身份识别**：政府机关（Tier 4）
2. **意图解析**：执法文书合法性审查
3. **技能调用**：
   - `zhang-government-legal` - 政府法务
   - `zhang-administrative-law` - 行政法
4. **服务输出**：
   - 合法性审查意见
   - 程序合规检查
   - 改进建议
5. **计费**：政府采购合同内

---

## 📊 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    九章法律智能操作系统                           │
│                     Zhang Legal OS Gateway                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  用户身份层  │  │  需求解析层  │  │  服务编排层  │            │
│  │             │  │             │  │             │            │
│  │ • 身份认证  │  │ • 意图识别  │  │ • 路由匹配  │            │
│  │ • 角色识别  │  │ • 复杂度评估│  │ • 工作流编排│            │
│  │ • 权限管理  │  │ • 场景匹配  │  │ • 技能调度  │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                │                │                    │
│         └────────────────┼────────────────┘                    │
│                          │                                     │
│                          ▼                                     │
│              ┌─────────────────────┐                          │
│              │    核心调度引擎      │                          │
│              │   Core Dispatcher   │                          │
│              └──────────┬──────────┘                          │
│                         │                                      │
│    ┌────────────────────┼────────────────────┐                │
│    │                    │                    │                │
│    ▼                    ▼                    ▼                │
│ ┌──────────┐      ┌──────────┐      ┌──────────┐            │
│ │ 个人服务  │      │ 专业服务  │      │ 机构服务  │            │
│ │  门户    │      │  工作台   │      │  管理台   │            │
│ └──────────┘      └──────────┘      └──────────┘            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│   │zhang-   │ │zhang-   │ │zhang-   │ │zhang-   │ ... 88+    │
│   │family   │ │labor    │ │contract │ │compliance│  skills    │
│   │-law     │ │-law     │ │-review  │ │-audit   │            │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 相关技能

- `zhang-user-auth` - 用户认证系统
- `zhang-intent-parser` - 意图解析引擎
- `zhang-workflow-engine` - 工作流引擎
- `zhang-pricing-engine` - 定价引擎
- `zhang-dialog-manager` - 对话管理器
- `zhang-skill-registry` - 技能注册中心

---

## 📈 版本规划

### V1.0.0 (当前)
- ✅ 基础网关架构
- ✅ 用户身份识别
- ✅ 需求意图解析
- ✅ 技能路由匹配

### V1.1.0 (规划中)
- 🔄 多轮对话管理
- 🔄 工作流编排引擎
- 🔄 计费系统集成
- 🔄 权限精细控制

### V2.0.0 (未来)
- 📝 智能推荐系统
- 📝 用户画像分析
- 📝 A/B测试框架
- 📝 数据看板

---

**版本**: 1.0.0
**作者**: 九章法律AI帝国
**定位**: 法律智能操作系统统一入口
**愿景**: 让法律服务像使用操作系统一样简单

---
