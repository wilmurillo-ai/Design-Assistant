# AI 智能整理算法说明

## 概述

本技能提供完整的 AI 邮件智能整理能力，包含四个核心功能模块：

1. **AI 摘要生成** - 自动生成邮件内容摘要
2. **智能分类** - 自动将邮件分类到预定义类别
3. **优先级排序** - 评估邮件处理优先级
4. **待办事项提取** - 从邮件中提取可执行任务

## 算法架构

### 1. AI 摘要生成 (ai_summarize.py)

**技术方案：**
- 主要使用通义千问 Qwen-Plus 大模型
- 降级方案：基于规则的简单摘要

**提示词设计：**
```
请为以下邮件生成简洁摘要：

主题：{subject}

内容：
{body}

要求：
1. 用一句话概括邮件核心内容（50 字以内）
2. 提取 3-5 个关键信息点（时间、地点、任务等）
3. 如果有明确的行动要求，请标注

输出 JSON 格式...
```

**输出格式：**
```json
{
  "one_sentence": "一句话摘要",
  "key_points": ["关键点 1", "关键点 2", ...],
  "action_required": "需要做什么" 或 null
}
```

### 2. 智能分类 (ai_classify.py)

**分类体系：**
- `work` - 工作相关（会议、项目、汇报、同事沟通）
- `important` - 重要邮件（老板、客户、紧急事项）
- `promotion` - 推广营销（广告、优惠、电商）
- `social` - 社交通知（朋友圈、社交软件、活动邀请）
- `newsletter` - 订阅邮件（资讯、周报、公众号）
- `finance` - 财务金融（银行、账单、发票、报销）
- `travel` - 出行旅游（机票、酒店、订单确认）
- `spam` - 垃圾邮件（可疑、诈骗、无关内容）

**双层分类策略：**
1. **规则层**：基于关键词快速匹配（高性能）
2. **AI 层**：大模型深度理解（高准确率）

**规则关键词示例：**
- 工作类：["会议", "项目", "汇报", "工作", "任务", "deadline"]
- 推广类：["优惠", "折扣", "促销", "限时", "购买", "下单"]

### 3. 优先级排序 (ai_prioritize.py)

**评分维度：**

| 维度 | 权重 | 说明 |
|------|------|------|
| 紧急关键词 | +30 | 包含"紧急"、"ASAP"、"截止"等 |
| 重要发件人 | +25 | 发件人包含 boss、manager、hr 等 |
| 时效性 | +20 | 2小时内新邮件得高分 |
| 未读状态 | +10 | 未读邮件优先级更高 |
| 附件存在 | +5 | 有附件通常更重要 |
| 请求/问题 | +10 | 主题包含问号或请求 |

**优先级映射：**
- **紧急 (70-100分)**：需立即处理（今天内）
- **高 (50-69分)**：24 小时内处理
- **中 (30-49分)**：本周内处理  
- **低 (0-29分)**：可延后处理

### 4. 待办事项提取 (ai_extract_todos.py)

**提取策略：**
1. **正则模式匹配**：识别常见任务句式
   - "请 (.+?)[。.!]"
   - "需要 (.+?)[。.!]"
   - "记得 (.+?)[。.!]"
   
2. **AI 深度理解**：大模型语义分析

**日期识别：**
- 支持多种日期格式：YYYY-MM-DD、MM月DD日、今天/明天
- 自动标准化为 YYYY-MM-DD 格式

**优先级评估：**
- 包含"紧急"、"ASAP" → high
- 包含"最好"、"有空" → low
- 默认 → medium

## 性能优化

### 缓存机制
- 邮件内容缓存避免重复下载
- 分类结果缓存减少 AI 调用

### 批量处理
- 支持批量邮件处理
- 异步并行处理（未来扩展）

### 降级策略
- AI 服务不可用时自动降级到规则引擎
- 保证基础功能可用性

## 使用建议

### 日常使用场景

**早晨快速处理：**
```bash
# 获取未读邮件摘要和待办
python scripts/ai_organize.py --unread --limit 20
```

**周末清理收件箱：**
```bash
# 分类所有邮件，批量删除推广邮件
python scripts/ai_classify.py --limit 100
python scripts/manage_email.py --id "msg_001,msg_002" --action delete
```

**查找重要邮件：**
```bash
# 搜索老板邮件并评估优先级
python scripts/search_emails.py --from "boss@company.com" --unread
python scripts/ai_prioritize.py --email-ids "msg_001,msg_002"
```

### AI 功能配置

**获取 DashScope API Key：**
1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 开通 DashScope 服务
3. 在 API Key 管理页面创建 Key

**环境变量设置：**
```bash
export DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
```

**无 AI 模式：**
```bash
# 禁用 AI，仅使用规则引擎
python scripts/ai_extract_todos.py --no-ai
```

## 扩展性

### 自定义分类
修改 `ai_classify.py` 中的 `CATEGORIES` 和 `KEYWORDS` 字典。

### 自定义优先级规则
调整 `ai_prioritize.py` 中的 `URGENT_KEYWORDS` 和 `IMPORTANT_SENDER_PATTERNS`。

### 添加新功能
在 `scripts/` 目录下创建新的 Python 脚本，遵循现有代码风格。

## 技术依赖

- **Python 3.8+**
- **imaplib** - IMAP 协议支持
- **smtplib** - SMTP 协议支持
- **dashscope** - 阿里云大模型 API（可选）
- **email** - 邮件解析

## 限制与注意事项

1. **API 调用限制**：DashScope 有调用频率限制
2. **邮件大小限制**：正文截断到 2000 字符用于 AI 处理
3. **中文支持**：完全支持中文邮件处理
4. **安全性**：敏感信息通过环境变量配置，不硬编码
