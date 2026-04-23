---
name: qq-email
description: QQ 邮箱智能管理工具。支持收发邮件、搜索筛选、附件处理，以及 AI 智能整理功能（自动摘要、分类、优先级排序、待办提取）。当用户需要操作 QQ 邮箱、查收邮件、发送邮件、整理收件箱或处理邮件相关任务时使用此技能。
---

# QQ 邮箱智能助手

## 功能概览

本技能提供完整的 QQ 邮箱管理能力，结合 AI 智能整理功能：

| 功能 | 说明 |
|------|------|
| 📥 **收件管理** | 读取收件箱、未读邮件、指定文件夹 |
| ✉️ **发送邮件** | 发送纯文本/HTML 邮件，支持附件 |
| 🔍 **智能搜索** | 按关键词、发件人、时间、主题搜索 |
| 🗂️ **邮件管理** | 标记已读/未读、删除、移动、归档 |
| 📎 **附件处理** | 下载附件、发送附件 |
| 🤖 **AI 整理** | 自动摘要、智能分类、优先级排序、待办提取 |

## 快速开始

### 配置邮箱账号

首次使用需要配置 QQ 邮箱的 IMAP/SMTP 授权码：

1. 登录 QQ 邮箱网页版
2. 设置 → 账户 → 开启 IMAP/SMTP 服务
3. 获取 **授权码**（不是登录密码）
4. 配置环境变量或配置文件

### 环境变量配置

```bash
export QQ_EMAIL="your_qq@qq.com"
export QQ_EMAIL_AUTH_CODE="your_auth_code"  # 16位授权码
```

## 核心功能

### 1. 读取邮件

**读取最新邮件：**
```python
# 读取收件箱最新 10 封邮件
python scripts/fetch_emails.py --limit 10

# 读取未读邮件
python scripts/fetch_emails.py --unread

# 读取指定文件夹
python scripts/fetch_emails.py --folder "Sent Messages" --limit 5
```

**输出格式：**
```json
{
  "emails": [
    {
      "id": "msg_001",
      "subject": "会议通知",
      "sender": "boss@company.com",
      "date": "2024-03-19 14:30:00",
      "body_text": "邮件正文...",
      "body_html": "<html>...</html>",
      "attachments": ["report.pdf"],
      "flags": ["\\Seen"]
    }
  ]
}
```

### 2. 发送邮件

**发送纯文本邮件：**
```python
python scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "测试邮件" \
  --body "这是一封测试邮件"
```

**发送带附件邮件：**
```python
python scripts/send_email.py \
  --to "recipient@example.com" \
  --cc "cc@example.com" \
  --subject "报告附件" \
  --body "请查收附件" \
  --attachments "/path/to/report.pdf,/path/to/data.xlsx"
```

**发送 HTML 邮件：**
```python
python scripts/send_email.py \
  --to "recipient@example.com" \
  --subject "HTML 邮件" \
  --html "<h1>标题</h1><p>内容</p>"
```

### 3. 搜索邮件

**基础搜索：**
```python
# 按关键词搜索主题和内容
python scripts/search_emails.py --query "项目进度"

# 按发件人搜索
python scripts/search_emails.py --from "boss@company.com"

# 按时间范围搜索
python scripts/search_emails.py --since "2024-03-01" --before "2024-03-20"

# 组合条件
python scripts/search_emails.py \
  --query "合同" \
  --from "legal@company.com" \
  --unread
```

### 4. 邮件管理

**标记和移动：**
```python
# 标记已读
python scripts/manage_email.py --id "msg_001" --action mark_read

# 标记未读
python scripts/manage_email.py --id "msg_001" --action mark_unread

# 删除邮件
python scripts/manage_email.py --id "msg_001" --action delete

# 移动到文件夹
python scripts/manage_email.py --id "msg_001" --action move --folder "Archive"

# 批量操作（逗号分隔 ID）
python scripts/manage_email.py --id "msg_001,msg_002,msg_003" --action mark_read
```

### 5. 附件处理

**下载附件：**
```python
# 下载邮件的所有附件
python scripts/download_attachments.py \
  --email-id "msg_001" \
  --output-dir "./downloads"

# 下载指定附件
python scripts/download_attachments.py \
  --email-id "msg_001" \
  --filename "report.pdf" \
  --output-path "./downloads/report.pdf"
```

## AI 智能整理

### 自动摘要

为每封邮件生成简洁摘要：
```python
python scripts/ai_summarize.py --limit 20
```

**输出示例：**
```json
{
  "summary": {
    "total": 20,
    "processed": 20,
    "results": [
      {
        "id": "msg_001",
        "subject": "Q1 季度总结会议通知",
        "summary": "3月25日下午2点召开Q1总结会议，需准备部门汇报PPT，地点：会议室A",
        "key_points": ["时间：3月25日 14:00", "需准备PPT", "地点：会议室A"]
      }
    ]
  }
}
```

### 智能分类

自动将邮件分类到不同类别：
```python
# 分类最新邮件
python scripts/ai_classify.py --limit 50

# 分类指定邮件
python scripts/ai_classify.py --email-ids "msg_001,msg_002"
```

**分类类别：**
- `work` - 工作相关
- `promotion` - 推广/营销
- `social` - 社交/通知
- `important` - 重要邮件
- `newsletter` - 订阅邮件
- `spam` - 垃圾邮件

**输出示例：**
```json
{
  "classifications": [
    {
      "id": "msg_001",
      "category": "work",
      "confidence": 0.95,
      "reason": "包含会议通知、工作安排等关键词"
    },
    {
      "id": "msg_002", 
      "category": "promotion",
      "confidence": 0.88,
      "reason": "来自电商平台，包含优惠信息"
    }
  ]
}
```

### 优先级排序

根据内容和发件人智能排序邮件优先级：
```python
python scripts/ai_prioritize.py --limit 30
```

**优先级等级：**
- `urgent` - 紧急（需立即处理）
- `high` - 高优先级（24小时内处理）
- `medium` - 中优先级（本周处理）
- `low` - 低优先级（可延后）

### 待办事项提取

从邮件中提取待办任务：
```python
python scripts/ai_extract_todos.py --limit 50
```

**输出示例：**
```json
{
  "todos": [
    {
      "email_id": "msg_001",
      "subject": "项目进度汇报",
      "todos": [
        {
          "task": "完成项目进度报告",
          "deadline": "2024-03-22",
          "priority": "high"
        },
        {
          "task": "准备周五汇报PPT",
          "deadline": "2024-03-24",
          "priority": "medium"
        }
      ]
    }
  ]
}
```

### 一键智能整理

执行完整的 AI 整理流程：
```python
python scripts/ai_organize.py --limit 50
```

此命令会依次执行：
1. 读取最新邮件
2. 生成摘要
3. 智能分类
4. 优先级排序
5. 提取待办事项
6. 生成整理报告

## 工作流示例

### 场景 1：早晨快速处理邮件

```python
# 1. 获取未读邮件并生成摘要
python scripts/ai_summarize.py --unread

# 2. 提取待办事项
python scripts/ai_extract_todos.py --unread

# 3. 标记已处理的不重要邮件
python scripts/manage_email.py --id "msg_003,msg_004" --action mark_read
```

### 场景 2：周末清理收件箱

```python
# 1. 智能分类所有邮件
python scripts/ai_classify.py --limit 100

# 2. 批量删除推广邮件（根据分类结果）
python scripts/manage_email.py --id "msg_005,msg_006" --action delete

# 3. 归档已处理的旧邮件
python scripts/manage_email.py --id "msg_007,msg_008" --action move --folder "Archive"
```

### 场景 3：查找重要邮件

```python
# 1. 搜索老板发来的未读邮件
python scripts/search_emails.py --from "boss@company.com" --unread

# 2. 对搜索结果进行优先级排序
python scripts/ai_prioritize.py --email-ids "msg_010,msg_011"
```

## 文件夹说明

QQ 邮箱标准文件夹名称：

| 文件夹 | 说明 |
|--------|------|
| `INBOX` | 收件箱 |
| `Sent Messages` | 已发送 |
| `Drafts` | 草稿箱 |
| `Deleted Messages` | 已删除 |
| `Junk` | 垃圾箱 |
| `Archive` | 归档（需手动创建）|

## 常见问题

**Q: 连接失败怎么办？**
- 确认已开启 QQ 邮箱 IMAP/SMTP 服务
- 检查使用的是授权码而非登录密码
- 确认网络可以访问 imap.qq.com:993 和 smtp.qq.com:465

**Q: 中文显示乱码？**
- 脚本已自动处理 UTF-8 编码，如遇乱码请检查终端编码设置

**Q: 附件大小限制？**
- QQ 邮箱普通附件最大 50MB
- 超大附件最大 3GB（通过中转站）

## 参考资料

- [QQ 邮箱 IMAP/SMTP 设置指南](references/qq_email_setup.md)
- [AI 整理算法说明](references/ai_organization.md)
