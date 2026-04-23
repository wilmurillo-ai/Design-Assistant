---
name: zhang-new-energy-law
version: "1.0.0"
description: 九章新能源法专家 - 光伏、储能、电动车产业合规与政策解读（基于DeepSeek R2 + 600+新能源案例库）
metadata:
  {
    "openclaw": {
      "requires": { "env": ["DEEPSEEK_API_KEY"] },
      "capabilities": ["reasoning", "web_search", "file_read"],
      "evolution": {
        "enabled": true,
        "version": "2.0.0",
        "data_collection": true,
        "auto_update": false,
        "feedback_loop": true
      }
    },
    "author": "张律师",
    "category": "legal",
    "tags": ["新能源", "光伏", "储能", "电动车", "绿电", "碳中和"],
    "focus_areas": [
      "光伏项目开发与并网合规",
      "储能电站审批与运营合规",
      "新能源汽车产业政策",
      "绿电交易与绿证规则",
      "碳达峰碳中和政策法规",
      "可再生能源补贴与 pricing",
      "新能源投资并购合规",
      "新能源项目EPC合同"
    ],
    "regulatory_sources": [
      "《可再生能源法》",
      "《新能源汽车产业发展规划(2021-2035年)》",
      "《关于促进储能技术与产业发展的指导意见》",
      "《绿色电力交易试点工作方案》",
      "《2030年前碳达峰行动方案》"
    ],
    "case_library_target": 600,
    "changelog": [
      {
        "version": "1.0.0",
        "date": "2026-03-23",
        "changes": ["初始版本发布", "集成自我进化系统"]
      }
    ]
  }
---

# 九章新能源法专家

新能源产业法律专家，专注光伏、储能、电动车合规。

## 核心能力

### 1. 光伏项目合规
- 项目备案与核准要求
- 用地合规审查
- 并网协议审查
- EPC合同风险识别

### 2. 储能电站合规
- 储能项目审批流程
- 电力业务许可要求
- 安全标准合规审查
- 并网调度协议

### 3. 电动车产业
- 生产资质与准入
- 动力电池回收合规
- 充换电设施合规
- 智能驾驶法规

### 4. 绿电与碳合规
- 绿电交易规则解读
- 绿证申领与交易
- 碳排放权交易
- 碳足迹核算

## 使用示例

```bash
# 光伏项目合规审查
jiuzhang-cli energy-law solar-review ./project_docs/

# 储能电站审批指南
jiuzhang-cli energy-law storage-approval --capacity 100MWh

# 绿电交易分析
jiuzhang-cli energy-law green-power --province 广东

# 碳中和路径规划
jiuzhang-cli energy-law carbon-roadmap ./company_profile.json
```

## 数据飞轮

- 收集：新能源企业合规咨询数据
- 分析：政策变化对行业影响
- 进化：实时更新产业政策库

## 版本规划

- v1.1.0：接入DeepSeek R2，扩展至1200+案例
- v1.2.0：新增氢能源法律模块
- v2.0.0：支持全球新能源政策对比
