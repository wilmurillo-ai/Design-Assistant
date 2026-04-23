# Token审计监控技能 v2.0 (Token Auditor)

全方位Token使用审计与监控系统，实时追踪消费、检测异常、预警风险。

## 核心功能

### 1. 实时监控
- 实时Token使用量追踪
- 多项目/多模型消费汇总
- API调用次数统计

### 2. 异常检测
- 异常消费模式识别
- 突发流量告警
- 异常模型调用检测

### 3. 预算告警
- 自定义预算阈值
- 多层级告警（50%/80%/100%）
- 邮件/通知推送

### 4. 审计报告
- 日/周/月度消费报告
- 成本趋势分析
- 异常事件记录

### 5. 优化建议
- 基于使用模式的优化方案
- 模型切换建议
- 成本节约潜力分析

## 监控维度

| 维度 | 说明 |
|------|------|
| 时间 | 小时/天/周/月粒度 |
| 模型 | 按AI模型分组统计 |
| 项目 | 按业务项目分组 |
| 用户 | 按调用者分组 |
| 类型 | 输入/输出Token区分 |

## 告警规则

- **预算告警**: 达到预算的50%/80%/100%
- **异常告警**: 单小时消费超过平均值3倍
- **趋势告警**: 连续3天消费增长超过20%
- **模型告警**: 使用了高价模型但未充分利用

## 使用示例

```bash
# 启动监控
token-auditor monitor --project myapp --budget 1000

# 查看实时状态
token-auditor status

# 生成审计报告
token-auditor report --period week --format html

# 检查异常
token-auditor check --sensitivity high

# 设置预算告警
token-auditor alert --budget 500 --thresholds 50,80,100
```

## Token经济生态

- **Token Master**: Token压缩优化
- **Compute Market**: 算力交易市场
- **Token Consumer Optimizer**: 消费优选决策
- **Token Auditor**: 审计监控 (本技能)
- **Token Exchange**: Token交易平台 (规划中)

**Version:** 2.0.0

## 新特性 v2.0

- ✅ 实时监控 dashboard
- ✅ 异常检测算法 (Z-Score/趋势分析/模型误用检测)
- ✅ 告警通知系统 (多级别/可扩展)
- ✅ 审计报告生成 (HTML/PDF/JSON)
- ✅ 预算管理 (日/周/月)
- ✅ API接口
- ✅ 统一数据模型 (token-ecosys-core)
