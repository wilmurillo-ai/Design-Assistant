# QQ 邮箱配置指南

## 开启 IMAP/SMTP 服务

### 步骤 1: 登录 QQ 邮箱

访问 [mail.qq.com](https://mail.qq.com) 并登录你的 QQ 邮箱账号。

### 步骤 2: 进入设置

1. 点击页面顶部的 **设置**
2. 选择 **账户** 标签页

### 步骤 3: 开启服务

找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV 服务** 部分：

1. 开启 **IMAP/SMTP 服务**
2. 开启 **POP3/SMTP 服务**（可选）

### 步骤 4: 获取授权码

点击 **生成授权码**，按提示操作：

1. 可能需要短信验证
2. 获得 16 位授权码（类似：`abcd1234efgh5678`）

**重要：** 授权码只显示一次，请妥善保存！

## 服务器配置

### IMAP 设置（接收邮件）

| 配置项 | 值 |
|--------|-----|
| 服务器 | `imap.qq.com` |
| 端口 | `993` |
| 加密 | `SSL` |
| 用户名 | 完整 QQ 邮箱地址 |
| 密码 | 授权码（不是 QQ 密码） |

### SMTP 设置（发送邮件）

| 配置项 | 值 |
|--------|-----|
| 服务器 | `smtp.qq.com` |
| 端口 | `465` |
| 加密 | `SSL` |
| 用户名 | 完整 QQ 邮箱地址 |
| 密码 | 授权码（不是 QQ 密码） |

## 环境变量配置

### Linux/macOS

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
export QQ_EMAIL="your_qq@qq.com"
export QQ_EMAIL_AUTH_CODE="your_16_char_auth_code"
export DASHSCOPE_API_KEY="your_dashscope_api_key"  # AI 功能需要
```

然后执行：
```bash
source ~/.bashrc  # 或 source ~/.zshrc
```

### Windows

在系统环境变量中添加：

1. 右键 **此电脑** → **属性** → **高级系统设置**
2. 点击 **环境变量**
3. 新建系统变量：
   - `QQ_EMAIL` = `your_qq@qq.com`
   - `QQ_EMAIL_AUTH_CODE` = `your_auth_code`
   - `DASHSCOPE_API_KEY` = `your_api_key`

### 临时配置（当前会话）

```bash
export QQ_EMAIL="your_qq@qq.com"
export QQ_EMAIL_AUTH_CODE="your_auth_code"
```

## 测试连接

### 测试 IMAP 连接

```bash
python scripts/fetch_emails.py --limit 1
```

预期输出：
```json
{
  "success": true,
  "folder": "INBOX",
  "count": 1,
  "emails": [...]
}
```

### 测试 SMTP 发送

```bash
python scripts/send_email.py \
  --to "test@example.com" \
  --subject "测试邮件" \
  --body "这是一封测试邮件"
```

## 常见问题

### Q1: 登录失败/认证错误

**可能原因：**
- 使用了 QQ 登录密码而非授权码
- 授权码已过期
- IMAP/SMTP 服务未开启

**解决方案：**
1. 确认使用的是 16 位授权码
2. 重新生成授权码
3. 检查是否开启了 IMAP/SMTP 服务

### Q2: 连接超时

**可能原因：**
- 防火墙阻止了 993/465 端口
- 网络问题

**解决方案：**
```bash
# 测试端口连通性
telnet imap.qq.com 993
telnet smtp.qq.com 465
```

### Q3: 中文乱码

确保终端使用 UTF-8 编码：

```bash
# Linux/macOS
export LANG=en_US.UTF-8

# Windows PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### Q4: AI 功能不可用

需要配置通义千问 API Key：

1. 访问 [阿里云百炼](https://bailian.console.aliyun.com/)
2. 开通 DashScope 服务
3. 创建 API Key
4. 设置环境变量：`export DASHSCOPE_API_KEY="sk-xxx"`

## 安全建议

1. **不要泄露授权码** - 授权码等同于密码
2. **定期更换授权码** - 建议每 3-6 个月更换
3. **使用环境变量** - 不要在代码中硬编码敏感信息
4. **限制脚本权限** - 确保脚本文件只有所有者可执行

## 文件夹结构

QQ 邮箱标准文件夹名称（IMAP）：

| 文件夹 | 说明 | IMAP 名称 |
|--------|------|----------|
| 收件箱 | 收到的邮件 | `INBOX` |
| 已发送 | 发出的邮件 | `Sent Messages` |
| 草稿箱 | 未完成的邮件 | `Drafts` |
| 垃圾箱 | 垃圾邮件 | `Junk` |
| 已删除 | 删除的邮件 | `Deleted Messages` |
| 归档 | 归档邮件 | `Archive` |

自定义文件夹可以直接使用中文名称。
