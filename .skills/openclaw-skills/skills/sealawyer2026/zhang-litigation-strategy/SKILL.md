---
name: zhang-litigation-strategy
version: "1.1.0"
description: 九章诉讼策略专家V1.1.0 - AI驱动的诉讼决策与策略优化（基于DeepSeek R2 + 5000+真实判例库 + 自我进化）
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
    "tags": ["诉讼", "策略", "判决预测", "案件分析"],
    "evolution_metrics": {
      "usage_tracking": ["案件分析次数", "策略采纳率", "预测准确率"],
      "performance_indicators": ["策略生成时间", "类案匹配精度", "胜诉预测准确率"],
      "feedback_collection": ["策略效果反馈", "新增诉讼技巧", "法官偏好更新"]
    },
    "evolution_plan": {
      "v1.2.0": ["接入实时判例库", "新增仲裁策略模块"],
      "v1.3.0": ["支持跨境诉讼", "AI生成庭审提纲"],
      "v2.0.0": ["全流程诉讼管理", "智能证据组织"]
    },
    "changelog": [
      {
        "version": "1.1.0",
        "date": "2026-03-23",
        "changes": [
          "接入 DeepSeek R2 推理模型",
          "新增 5000+ 真实判例数据库",
          "新增判决结果预测功能",
          "优化诉讼策略推理链",
          "支持类案智能推送",
          "集成自我进化系统（v2.0.0）"
        ]
      }
    ]
  }
---

# 九章诉讼策略专家 V1.1.0

**核心升级**：
- 🎯 **判决预测** - 基于类案的胜诉率预测
- 📊 **5000+判例** - 覆盖全国各级法院
- 🤖 **DeepSeek R2** - 多维度策略推演
- 🔍 **类案检索** - 智能匹配相似案件
- 💡 **策略生成** - 诉讼方案自动生成

## 使用示例

```bash
# 案件策略分析
jiuzhang-cli litigation analyze ./case_materials/

# 判决预测
jiuzhang-cli litigation predict --case-type 合同纠纷 --court 北京

# 类案检索
jiuzhang-cli litigation search "劳动合同解除"

# 策略对比
jiuzhang-cli litigation compare-strategy A方案 B方案
```

## 功能模块

### 1. 案件评估
- 证据完整性分析
- 法律依据评估
- 诉讼风险评估
- 成本效益分析

### 2. 判决预测
- 胜诉率预测
- 赔偿金额估算
- 审理周期预测
- 上诉可能性分析

### 3. 类案检索
- 相似案件匹配
- 判决结果统计
- 法官裁判倾向
- 法院地域差异

### 4. 策略生成
- 诉讼方案设计
- 证据组织建议
- 庭审策略规划
- 调解策略建议
