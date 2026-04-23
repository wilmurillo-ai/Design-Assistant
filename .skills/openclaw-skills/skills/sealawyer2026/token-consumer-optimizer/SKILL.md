# Token消费优选技能 v2.0 (Token Consumer Optimizer)

智能AI模型消费决策助手 v2.0，帮你在众多AI模型中选择最经济、最适合的消费方案。

**Version:** 2.0.0

## 新特性 v2.0

- ✅ 智能推荐算法 (基于任务类型/预算/质量)
- ✅ 实时价格抓取 (多平台价格)
- ✅ 成本预测模型 (日/月/年预测)
- ✅ 性价比分析 (质量/成本比值)
- ✅ 节省潜力计算
- ✅ API接口
- ✅ 统一数据模型 (token-ecosys-core)

## 核心功能

### 1. 智能模型推荐
根据任务类型、预算、质量要求，推荐最优AI模型组合

### 2. 实时比价
对比各大平台(AIHub、Claude、GPT、Gemini等)的价格和性能

### 3. 成本计算器
估算不同方案的成本，展示节省金额

### 4. 预算规划
制定Token消费预算，监控使用情况

### 5. 消费优化建议
基于使用历史，提供个性化优化建议

## 支持的模型

| 平台 | 模型 | 输入价格 | 输出价格 |
|------|------|----------|----------|
| OpenAI | GPT-4o | $5/M | $15/M |
| OpenAI | GPT-4o-mini | $0.15/M | $0.6/M |
| Anthropic | Claude-3.5-Sonnet | $3/M | $15/M |
| Anthropic | Claude-3-Haiku | $0.25/M | $1.25/M |
| Google | Gemini-1.5-Pro | $3.5/M | $10.5/M |
| Google | Gemini-1.5-Flash | $0.075/M | $0.3/M |
| 阿里云 | Qwen-Max | ¥0.02/1K | ¥0.06/1K |
| 百度 | ERNIE-4.0 | ¥0.03/1K | ¥0.09/1K |

## 使用示例

```bash
# 智能推荐
./optimizer.py recommend --task "代码审查" --budget 10 --quality high

# 比价查询
./optimizer.py compare --input-tokens 1000 --output-tokens 500

# 成本估算
./optimizer.py estimate --model gpt-4o --input 10000 --output 3000

# 预算规划
./optimizer.py budget --monthly 1000 --usage "daily"

# 查看消费报告
./optimizer.py report --period week
```

## 生态位置

这是Token经济生态的重要组成部分：
- **Token Master**: Token压缩 (已发布)
- **Compute Market**: 算力市场 (已发布)
- **Token Consumer Optimizer**: 消费优选 (本技能) v2.0
- **Token Auditor**: 审计监控 (已发布)
- **Token Exchange**: 交易平台 (已发布)

**Version:** 2.0.0
