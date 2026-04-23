# Token消费优选师

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/sealawyer2026/skill-token-consumer-optimizer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 智能选择最经济的AI模型消费方案

## 🎯 简介

Token消费优选师是一款智能比价工具，帮助你在众多AI模型中选择最经济、最适合的消费方案。支持9大主流模型实时比价，让你的每一分钱都花在刀刃上。

## ✨ 功能特性

- 📊 **智能比价** - 实时对比9大模型价格
- 🎯 **任务匹配** - 根据任务类型推荐最优模型
- 💰 **成本计算** - 精确预估调用成本
- 📈 **预算规划** - 月度预算分析与预警

## 🚀 快速开始

```bash
# 安装
pip install -r requirements.txt

# 推荐最优模型
python main.py recommend --task code_generation --tokens 2000

# 对比所有模型
python main.py compare --tokens 5000

# 预算分析
python main.py budget --budget 1000 --daily-calls 50
```

## 💡 使用示例

### 场景: 代码生成任务

```bash
$ python main.py recommend --task code_generation --tokens 3000

🥇 #1 Kimi K2.5 (Moonshot)
    💰 预估成本: ¥0.0045 ($0.0006)
    📉 可节省: 95.2% (对比最贵方案)
    ✅ 推荐理由: 价格实惠，稳定可靠，响应快速
```

### 场景: 月度预算规划

```bash
$ python main.py budget --budget 500 --daily-calls 100

豆包Lite            月度成本: ¥5.40        ✅ 支持
豆包Pro             月度成本: ¥28.80       ✅ 支持
Kimi K2             月度成本: ¥13.50       ✅ 支持
GPT-4o              月度成本: ¥1,458.00    ❌ 超预算
```

## 📦 支持平台

| 模型 | 厂商 | 输入价格 | 货币 |
|------|------|----------|------|
| GPT-4o | OpenAI | $2.50 | USD |
| Claude 3.5 | Anthropic | $3.00 | USD |
| Kimi K2 | Moonshot | ¥0.15 | CNY |
| 文心一言 | 百度 | ¥0.30 | CNY |
| 通义千问 | 阿里 | ¥0.40 | CNY |
| 豆包Pro | 字节 | ¥0.08 | CNY |

## 📖 文档

详见 [SKILL.md](SKILL.md)

## 🤝 相关项目

- [Token Master](https://github.com/sealawyer2026/skill-token-master) - Token压缩优化
- [Skill Self-Optimizer](https://github.com/sealawyer2026/skill-self-optimizer) - 技能自优化

## 📄 License

MIT License
