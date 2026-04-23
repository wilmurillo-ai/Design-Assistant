---
name: youclaw
description: 有米云智能营销分析助手，深度拆解广告创意，挖掘品牌投放策略。触发：关键词 分析品牌, 品牌分析, 策略探索, 投放策略；命令 `/creative-chat`、`/youclaw`、`/youmiyun`
homepage: https://www.youcloud.com
metadata:
  {
    "openclaw": {
      "slug": "youclaw",
      "version": "1.0.2",
      "author": "youcloud",
      "emoji": "📊",
      "requires": {
        "env": ["YOUCLOUD_API_KEY"]
      }
    }
  }
---

# youclaw

有米云智能营销分析助手，对接有数AI API提供品牌投放和创意策略分析。

## 权限说明
仅对**有数 365 策略pro 版**和**有数 365 至尊版**用户开放。获取API Key方式：登录有数 → 个人中心 → 企业信息。

## 触发方式
- 关键词：分析品牌、品牌分析、策略探索、投放策略
- 命令：`/creative-chat`、`/youclaw`、`/youmiyun`

## 执行流程
1. **检查API Key**（按优先级）：
   - 当前对话用户提供了新Key → 覆盖`config.json` → 继续
   - 本地`config.json`已有Key → 直接读取 → 继续
   - 本地为空 → 读取环境变量`YOUCLOUD_API_KEY`：
     - 为空 → 提示用户配置：
       ```
       请先配置API Key：
       1. 登录有数 → 个人中心 → 企业信息获取API Key
       2. 选项一：配置为OpenClaw环境变量 YOUCLOUD_API_KEY；选项二：直接发送给我，我帮你保存到本地。
       ```
     - 有值 → 保存到`config.json` → 继续
   - ✅ 规则：**没有有效 API Key，绝不发送请求**


2. **检查分析目标**：
   - 仅触发，没有具体品牌 → 提示用户：
     ```
     你想分析什么？可以告诉我品牌、店铺或产品，例如：
     "帮我分析一下丝塔芙近半年的广告创意投放策略和人群画像，并生成表格形式的可落地投放方案"
     ```
   - 有具体目标 → 调用API，响应返回后直接展示结果。

3. **重要提醒**
   - API 请求超时为 **600秒**，包括 tool exec 和 curl 等
   - **未到超时时间不得中断请求，不得给用户发送任何消息，必须等待API返回结果。**


4. **跟进处理**：
   - 相关跟进提问（关于之前的分析） → 复用之前的`session_id`
   - 新的分析请求 → 开启新会话，不携带`session_id`


## API Specification
- URL: `https://aichat.youshu.youcloud.com/aichat/claw`
- Method: POST JSON
- Headers: `Authorization: Bearer {KEY}`, `Content-Type: application/json`
- Parameters:
  - `input`: User question (required)
  - `session_id`: For follow-up questions, omit for new conversations
- Response: Output `output` (markdown) **as-is, DO NOT modify**; save `session_id` for future follow-ups
- Timeout: ≥600s

## PowerShell 调用模板
```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$apiKey = (Get-Content config.json | ConvertFrom-Json).api_key
$body = @{input="Your analysis request"} | ConvertTo-Json -Compress
$params = @{
    Uri = "https://aichat.youshu.youcloud.com/aichat/claw"
    Method = "Post"
    ContentType = "application/json; charset=utf-8"
    Headers = @{Authorization="Bearer $apiKey"}
    Body = $body
    TimeoutSec = 600
}
Invoke-RestMethod @params | Select-Object -ExpandProperty output
```

## 错误处理
- 401/认证失败：
  ```
  API Key 认证失败，请检查密钥是否激活/过期？请在个人中心-企业信息 获取Api Key，或向售后人员咨询。
  ```
- 超时："还在分析中，稍后再问我结果或者再次请求。"
- 其他错误："请求返回错误 (code={code})，请检查API Key权限、账号配额或联系客服"

## 示例
完整输入输出示例请看 [references/example.md](references/example.md)
