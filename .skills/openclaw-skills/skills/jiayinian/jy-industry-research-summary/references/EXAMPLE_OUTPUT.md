# 输出示例

## 完整输出示例

```json
[
  {
    "reportID": "R2026032901",
    "title": "AI 行业 2026 年一季度投资策略：大模型应用落地加速",
    "publishDate": "2026-03-29 09:30:00",
    "orgName": "广发证券",
    "viewResults": [
      {
        "perspectivesOnDimensions": "行业发展趋势",
        "viewOutcomes": "2026 年 AI 行业将进入应用落地加速期，大模型在垂直领域的渗透率预计提升至 35%，企业级 AI 服务市场规模同比增长 120%。"
      },
      {
        "perspectivesOnDimensions": "竞争格局",
        "viewOutcomes": "头部大模型厂商集中度进一步提升，CR5 达到 68%。垂直领域应用层竞争加剧，细分赛道涌现多家独角兽企业。"
      },
      {
        "perspectivesOnDimensions": "技术创新",
        "viewOutcomes": "多模态大模型技术突破显著，推理成本下降 60%。边缘 AI 芯片性能提升 3 倍，功耗降低 45%。"
      },
      {
        "perspectivesOnDimensions": "政策环境",
        "viewOutcomes": "国家层面出台 AI 产业发展指导意见，明确数据要素市场化配置改革方向。地方政府 AI 产业基金规模超 500 亿元。"
      },
      {
        "perspectivesOnDimensions": "投资建议",
        "viewOutcomes": "建议关注三条主线：1）大模型基础设施提供商；2）垂直领域应用龙头；3）AI 芯片及算力产业链。"
      },
      {
        "perspectivesOnDimensions": "风险提示",
        "viewOutcomes": "技术迭代风险、政策监管不确定性、行业竞争加剧、海外技术封锁风险。"
      }
    ]
  },
  {
    "reportID": "R2026032802",
    "title": "半导体行业深度报告：国产替代加速，设备材料迎来黄金期",
    "publishDate": "2026-03-28 14:15:00",
    "orgName": "中信建投证券",
    "viewResults": [
      {
        "perspectivesOnDimensions": "行业发展趋势",
        "viewOutcomes": "半导体设备国产化率从 15% 提升至 28%，2026 年有望突破 35%。成熟制程产能持续扩张，先进封装需求旺盛。"
      },
      {
        "perspectivesOnDimensions": "竞争格局",
        "viewOutcomes": "国内设备厂商在刻蚀、薄膜沉积等核心环节实现突破，市场份额快速提升。材料领域光刻胶、电子特气国产化加速。"
      },
      {
        "perspectivesOnDimensions": "技术创新",
        "viewOutcomes": "28nm 制程设备实现量产验证，14nm 设备进入客户验证阶段。先进封装技术 CoWoS、Chiplet 产业化进程加快。"
      },
      {
        "perspectivesOnDimensions": "政策环境",
        "viewOutcomes": "大基金三期落地，规模超 3000 亿元，重点支持设备材料环节。税收优惠政策延续，研发费用加计扣除比例提升。"
      },
      {
        "perspectivesOnDimensions": "投资建议",
        "viewOutcomes": "重点推荐：1）刻蚀设备龙头；2）薄膜沉积设备厂商；3）光刻胶及电子特气供应商；4）先进封装测试企业。"
      },
      {
        "perspectivesOnDimensions": "风险提示",
        "viewOutcomes": "下游需求不及预期、技术验证进度延迟、海外供应链风险、行业周期波动风险。"
      }
    ]
  }
]
```

## 输出字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| reportID | string | 研报唯一标识符 |
| title | string | 研报标题 |
| publishDate | string | 发布时间，格式：YYYY-MM-DD HH:mm:ss |
| orgName | string | 券商机构名称 |
| viewResults | array | 分析维度观点数组 |
| viewResults[].perspectivesOnDimensions | string | 分析维度名称 |
| viewResults[].viewOutcomes | string | 该维度的分析观点（原文输出） |

## 分析维度列表

常见的分析维度包括但不限于：

- 行业发展趋势
- 竞争格局
- 技术创新
- 政策环境
- 投资建议
- 风险提示
- 市场空间
- 产业链分析
- 财务分析
- 估值分析

**注意：** 接口返回的所有分析维度均应保留，不应过滤或删减。
