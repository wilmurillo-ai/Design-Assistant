# 🎨 Design Inspiration Collector

一键从 Behance、Dribbble、Pinterest 三大设计平台收集灵感，自动生成腾讯智能文档

---

## 简介

设计师和产品经理的灵感收集神器！只需说出设计方向，即可自动从全球三大顶级设计平台获取精选案例，并整理成美观的腾讯文档。

### 核心能力

✨ **三平台同步搜索**
   - Pinterest：视觉灵感、配色参考
   - Dribbble：UI设计、交互案例  
   - Behance：完整项目、设计系统

📝 **智能文档生成**
   - 自动创建腾讯智能文档
   - 按平台分类整理，带星级评分
   - 包含设计趋势分析和配色建议

🎯 **方向推荐**
   - 基于主题智能推荐细分方向
   - 帮助拓展设计思路

---

## 适用场景

- 🚀 产品原型设计前的灵感收集
- 🎨 UI/UX 设计参考
- 📱 移动端/App 界面设计
- 💼 B端/Dashboard 设计
- 🏥 垂直行业应用设计（医疗、金融、教育等）

---

## 安装

```bash
# 通过 SkillHub 安装
skillhub install design-inspiration-collector

# 配置 API Key
export TAVILY_API_KEY="tvly-你的密钥"
```

---

## 使用方法

直接说出设计方向即可触发：

- "帮我收集医疗App的设计灵感"
- "找一下金融Dashboard的参考"
- "收集移动端UI设计趋势"
- "Behance 上有啥好的医疗 UI"

---

## 输出示例

```
✅ 已从三大平台收集 15 条精选灵感！

📄 腾讯文档：AI医疗移动端设计参考_20260319
🔗 https://docs.qq.com/aio/xxx

📊 包含内容：
• Pinterest 精选 5 条 - 视觉风格、配色方案
• Dribbble 精选 5 条 - UI组件、交互设计  
• Behance 精选 5 条 - 完整项目案例

💡 相关推荐：
1. AI 心理健康 App 设计
2. 智能问诊聊天界面
3. 健康数据可视化
```

---

## 功能特性

| 特性 | 说明 |
|------|------|
| 🔍 多平台搜索 | 同时搜索 Behance、Dribbble、Pinterest |
| ⭐ 智能评分 | 按相关度给出 1-5 星推荐 |
| 📄 自动文档 | 生成格式化的腾讯智能文档 |
| 🔗 直达链接 | 每条灵感附带原始链接 |
| 💡 方向推荐 | 智能推荐相关设计方向 |

---

## 触发词

```
找灵感、收集灵感、设计参考、UI参考、视觉灵感、设计趋势、
Behance、Dribbble、Pinterest、帮我找设计、设计灵感
```

---

## 依赖要求

### 工具依赖

| 工具 | 用途 | 安装命令 |
|------|------|----------|
| Tavily API | 搜索三大设计平台 | `pip install tavily-python` |
| tencent-docs | 创建腾讯文档 | `skillhub install tencent-docs` |

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `TAVILY_API_KEY` | Tavily API 密钥 | ✅ |

---

## 热门设计方向

| 方向 | 搜索关键词 |
|------|------------|
| 移动 App | mobile app, ios, android, app ui |
| 网页设计 | web design, landing page, website |
| 仪表盘 | dashboard, admin panel, data viz |
| 电商 | ecommerce, shop, checkout |
| 金融 | fintech, banking, crypto, payment |
| 健康 | health, medical, fitness, wellness |
| 风格 | glassmorphism, neumorphism, minimal |

---

## 项目信息

```yaml
name: design-inspiration-collector
version: 1.0.0
author: your-name
category: productivity
tags: [design, ui, ux, inspiration, behance, dribbble, pinterest, tencent-docs]
emoji: 🎨
```

---

## 目录结构

```
design-inspiration-collector/
├── README.md              # 本文件
├── SKILL.md               # 技能详细文档
└── scripts/
    └── design_collector.py # 核心脚本
```

---

## 许可证

MIT License
