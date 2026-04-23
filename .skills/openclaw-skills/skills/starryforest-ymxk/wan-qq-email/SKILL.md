---
name: wan-qq-email
description: QQ Email IMAP/SMTP client. Use Python imaplib and smtplib to read and send QQ emails without Himalaya.
metadata:
  openclaw:
    emoji: "📧"
    requires:
      python: ">=3.8"
    install: []
---

# QQ Email Skill

QQ邮箱IMAP/SMTP客户端，使用Python标准库imaplib和smtplib，无需Himalaya。

## Overview

通过Python标准库直接访问QQ邮箱：
- ✅ 读取收件箱邮件（IMAP）
- ✅ 搜索邮件
- ✅ 读取邮件内容和附件
- ✅ 发送新邮件（SMTP）
- ✅ 回复邮件
- ✅ 转发邮件


## Skill Structure

```
qq-email/
├── SKILL.md                    # 使用文档
└── scripts/
    ├── __init__.py           # QQEmailClient类（主要API）
    ├── list_emails.py        # 列出邮件命令行工具
    ├── read_email.py         # 读取邮件内容
    ├── send_email.py         # 发送邮件
    ├── search_emails.py       # 搜索邮件
    └── examples.py           # 使用示例

```

## Quick Start

### 导入模块

```python
import sys
import os

# 获取skill目录
skill_dir = os.path.join(os.path.expanduser('~/.openclaw/workspace/skills/qq-email/scripts'))
sys.path.insert(0, skill_dir)

from __init__ import QQEmailClient
```

### 连接QQ邮箱

```python
# 创建客户端
client = QQEmailClient()

# 自动使用QQ邮箱配置
client.connect_imap()
client.connect_smtp()
```

### 列出邮件

```python
# 获取最近10封邮件
emails = client.list_emails(limit=10)

for email in emails:
    print(f"主题: {email['subject']}")
    print(f"发件人: {email['from']}")
    print(f"日期: {email['date']}")
    print("-" * 80)
```

### 读取邮件内容

```python
# 读取邮件内容
content = client.read_email(email_id)
print(content['text'])
```

### 发送邮件

```python
# 发送新邮件
client.send_email(
    to="recipient@example.com",
    subject="测试邮件",
    body="这是测试邮件正文"
)
```

## API参考

### QQEmailClient类

#### 初始化

```python
from __init__ import QQEmailClient

client = QQEmailClient()
# 自动使用QQ邮箱配置
```

#### IMAP方法（读取邮件）

| 方法 | 说明 | 返回 |
|------|------|------|
| `connect_imap()` | 连接IMAP服务器 | None |
| `disconnect_imap()` | 断开IMAP连接 | None |
| `list_emails(limit=10)` | 列出最近邮件 | List[Dict] |
| `read_email(email_id)` | 读取邮件内容 | Dict |
| `search_emails(criteria)` | 搜索邮件 | List[Dict] |
| `list_folders()` | 列出所有文件夹 | List[Str] |
| `select_folder(folder)` | 选择文件夹 | None |

#### SMTP方法（发送邮件）

| 方法 | 说明 | 返回 |
|------|------|------|
| `connect_smtp()` | 连接SMTP服务器 | None |
| `disconnect_smtp()` | 断开SMTP连接 | None |
| `send_email(to, subject, body)` | 发送新邮件 | None |
| `reply_email(email_id, body)` | 回复邮件 | None |
| `forward_email(email_id, to)` | 转发邮件 | None |

### 邮件数据结构

```python
{
    "id": "12345",              # 邮件ID
    "from": "sender@example.com",  # 发件人
    "to": "recipient@example.com",   # 收件人
    "subject": "邮件主题",         # 主题
    "date": "Wed, 04 Mar 2026 09:36:00 +0800",  # 日期
    "body": "邮件正文",         # 纯文本正文
    "html": "<html>...</html>", # HTML正文
    "attachments": [           # 附件列表
        {
            "filename": "file.pdf",
            "content": bytes
        }
    ]
}
```

## 配置

配置硬编码在`__init__.py`中：

```python
IMAP_CONFIG = {
    "host": "imap.qq.com",
    "port": 993,
    "user": "1911308683@qq.com",
    "password": "nllzqegzklliebbh"
}

SMTP_CONFIG = {
    "host": "smtp.qq.com",
    "port": 465,
    "user": "1911308683@qq.com",
    "password": "nllzqegzklliebbh"
}
```

## 示例

### 示例1：列出最近20封邮件

```python
import sys
import os

skill_dir = os.path.join(os.path.expanduser('~/.openclaw/workspace/skills/qq-email/scripts'))
sys.path.insert(0, skill_dir)

from __init__ import QQEmailClient

client = QQEmailClient()
client.connect_imap()

emails = client.list_emails(limit=20)
for idx, email in enumerate(emails, 1):
    print(f"邮件 #{idx}: {email['subject'][:50]}")
    print(f"  发件人: {email['from']}")
    print(f"  日期: {email['date']}")
    print("-" * 80)

client.disconnect_imap()
```

### 示例2：搜索特定邮件

```python
from __init__ import QQEmailClient

client = QQEmailClient()
client.connect_imap()

# 搜索包含"Unity"的邮件
emails = client.search_emails("Unity")

for email in emails:
    print(f"找到: {email['subject']}")

client.disconnect_imap()
```

### 示例3：发送邮件

```python
from __init__ import QQEmailClient

client = QQEmailClient()
client.connect_smtp()

client.send_email(
    to="recipient@example.com",
    subject="测试邮件",
    body="这是通过QQ邮箱发送的测试邮件"
)

client.disconnect_smtp()
```

### 示例4：读取并回复邮件

```python
from __init__ import QQEmailClient

client = QQEmailClient()
client.connect_imap()

# 读取邮件
email = client.read_email("12345")
print(f"原始邮件: {email['body']}")

# 回复邮件
client.connect_smtp()
client.reply_email("12345", "我已收到你的邮件")

client.disconnect_smtp()
client.disconnect_imap()
```

## 限制和注意事项

### IMAP限制

- ✅ 完全兼容QQ邮箱IMAP服务器
- ✅ 支持所有标准IMAP命令
- ✅ 支持SSL/TLS加密
- ⚠️ 建议使用readonly=True只读访问

### SMTP限制

- ✅ 完全兼容QQ邮箱SMTP服务器
- ✅ 支持SSL/TLS加密
- ⚠️ QQ邮箱有发送频率限制
- ⚠️ 建议批量发送时添加延迟

### 性能建议

- 使用上下文管理器（`with`）自动关闭连接
- 大量邮件时使用分页
- 避免频繁的IMAP SELECT操作
- 邮件搜索使用服务器端搜索

## 故障排除

### IMAP连接失败

```python
# 检查连接
import imaplib
import ssl

try:
    with imaplib.IMAP4_SSL("imap.qq.com", 993, timeout=10) as mail:
        print("✅ 连接成功")
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

### SMTP发送失败

```python
# 检查SMTP
import smtplib

try:
    with smtplib.SMTP_SSL("smtp.qq.com", 465, timeout=10) as server:
        print("✅ 连接成功")
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

## 技术细节

### IMAP协议

- 服务器：imap.qq.com
- 端口：993
- 加密：SSL/TLS1.3
- 认证：PLAIN

### SMTP协议

- 服务器：smtp.qq.com
- 端口：465
- 加密：SSL/TLS
- 认证：PLAIN

## 更新日志

### v1.0.0 (2026-03-04)
- ✅ 初始版本
- ✅ IMAP读取邮件
- ✅ SMTP发送邮件
- ✅ 搜索功能
- ✅ 文件夹管理
