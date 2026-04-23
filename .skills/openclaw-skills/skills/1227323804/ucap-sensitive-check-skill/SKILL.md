# 敏感信息检测 Skill

name: 错敏信息检测
description: 通过调用 UCAP 平台的安全防护接口，快速识别文本内容中的敏感数据。

## 简介

这是一个用于检测文本敏感信息的 Skill，通过调用 UCAP 平台的安全防护接口，快速识别文本内容中的敏感数据，适用于内容审核、数据合规等场景。

本技能支持从 URL 获取网页内容进行检测。

## 功能特性

- 支持多种敏感类型检测（可自定义检测类型列表）
- 支持从网页 URL 获取内容进行检测（使用 Selenium 渲染动态页面）
- **SSRF 防护**：阻止访问内网地址和私有 IP
- 标准化的 JSON 格式输入输出
- 完善的错误处理和超时机制
- 兼容 OpenClaw 对话式调用
- 启用 SSL 证书验证确保通信安全

## 安全说明

### URL 访问限制

本技能实施安全检查，防止 SSRF 攻击：

| 限制类型 | 说明 |
|---------|------|
| 内网地址 | 阻止访问 localhost、127.0.0.1、私有 IP 等内网地址 |

### SSL/TLS 安全

- 默认启用 SSL 证书验证
- 不禁用 SSL 警告
- 遇到证书问题时返回友好错误提示

## 技术实现

### 使用的技术栈

| 技术 | 用途 |
|------|------|
| Python 3.8+ | 主要开发语言 |
| Selenium | 用于渲染 JavaScript 动态页面 |
| Chrome WebDriver | 无头浏览器模式 |
| webdriver-manager | 自动下载和管理 ChromeDriver |
| requests | HTTP 请求库 |

### 依赖安装

```bash
pip install -r requirements.txt
```

或单独安装：

```bash
pip install requests>=2.31.0
pip install selenium>=4.15.0
pip install webdriver-manager>=4.0.0
```

系统还需安装：
- Chrome 浏览器（ChromeDriver 会由 webdriver-manager 自动下载）

## 使用方法

### 对话式调用

```
请帮我检测这段文本是否包含敏感信息：{待检测文本内容}
```

或从 URL 检测：

```
请帮我检测这个网页的内容：https://example.com
```

### 参数说明

| 参数名 | 类型 | 必传 | 说明 |
|--------|------|------|------|
| content | string | 是 | 待检测的文本内容 或 URL |
| userKey | string | 否 | UCAP 平台用户密钥（可选） |
| sensitive_code_list | array | 否 | 检测类型列表，不传则检测所有类型 |

### 返回格式

```json
{
  "code": 0,
  "message": "检测成功",
  "data": {
    // UCAP 接口返回的检测结果
  },
  "source_url": "https://example.com",
  "source_type": "url"
}
```

### 错误码说明

#### 通用错误码
| 错误码 | 说明 |
|--------|------|
| 0 | 检测成功 |
| -1 | 待检测文本不能为空 |

#### API 调用错误（check_sensitive）
| 错误码 | 说明 |
|--------|------|
| -3 | 接口调用超时（15秒） |
| -4 | 接口返回错误 |
| -5 | 网络连接失败 |
| -6 | 接口调用失败 |
| -7 | 接口返回非 JSON 格式数据 |
| -8 | SSL 证书验证失败 |

#### URL 访问错误（fetch_url_content）
| 错误码 | 说明 |
|--------|------|
| -100 | **URL 安全检查失败**（内网地址） |
| -101 | 访问超时（30秒内无法加载页面） |
| -102 | 连接失败（无法解析域名或建立连接） |
| -103 | 浏览器驱动错误（Chrome 浏览器未安装或驱动问题） |
| -104 | 访问失败（其他未知错误） |

## 示例代码

```python
from main import check_sensitive, fetch_url_content, run

# 基础检测
result = check_sensitive(
    content="这是一段待检测的文本内容",
    userKey="your_user_key_here"
)

# 指定检测类型
result = check_sensitive(
    content="这是一段待检测的文本内容",
    userKey="your_user_key_here",
    sensitive_code_list=["TYPE_1", "TYPE_2"]
)

# 通过 run() 函数自动识别 URL 或文本
# 检测 URL
result = run({
    "content": "https://example.com",
    "userKey": "your_user_key_here"
})

# 检测文本
result = run({
    "content": "这是一段待检测的文本内容",
    "userKey": "your_user_key_here"
})
```

## 注意事项

1. 使用前需要获取有效的 UCAP 平台 userKey
2. 接口调用超时时间为 15 秒
3. 网页加载超时时间为 30 秒
4. 所有 URL 请求均经过安全验证，防止访问内网地址
5. 启用了 SSL 验证确保通信安全
6. 使用 Selenium 和 webdriver-manager 自动管理浏览器驱动

## 申请 userKey

访问 https://safeguard-pre.ucap.com.cn/ 申请专属 userKey
