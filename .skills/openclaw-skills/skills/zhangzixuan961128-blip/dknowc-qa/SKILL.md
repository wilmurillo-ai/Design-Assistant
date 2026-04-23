---
name: dknowc-qa
description: "深知可信问答 - 政策法规权威知识问答引擎。触发条件：(1) 用户咨询政策、法规、条例、规章的详细解读，(2) 用户查询政务办事流程、办理材料、办理条件，(3) 用户说'问一下'、'可信问答'、'深知问答'，(4) 需要带溯源引用的权威回答。"
metadata: { "openclaw": { "emoji": "💬", "requires": { "bins": ["python3"], "env": ["DKNOWC_QA_API_KEY", "DKNOWC_QA_ENDPOINT"] }, "primaryEnv": "DKNOWC_QA_API_KEY" } }
---

# 深知可信问答

基于深知智能 1.7 亿公开文件和 16 亿知识切片的政策法规问答引擎，回答可溯源到官方权威网站。

## 配置

通过环境变量注入（OpenClaw 自动管理）：

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `DKNOWC_QA_API_KEY` | API 密钥 | `sk-xxxxx` |
| `DKNOWC_QA_ENDPOINT` | 统一接口地址 | `https://open.dknowc.cn/chat/trusted/unification/{appid}` |

首次触发时，如检测到环境变量未配置：

1. 告知用户：「请提供深知可信问答的 API Key 和调用地址。可在 https://platform.dknowc.cn 注册并实名认证（送 100 元）后获取。获取指南见 `references/apikey-guide.md`。」
2. 用户提供了 API Key 和调用地址后，AI 自动调用 `gateway config.patch` 写入配置：

```json
{
  "skills": {
    "entries": {
      "dknowc-qa": {
        "env": {
          "DKNOWC_QA_API_KEY": "{用户提供的key}",
          "DKNOWC_QA_ENDPOINT": "{用户提供的地址}"
        }
      }
    }
  }
}
```

3. 配置完成后 OpenClaw 会自动重启，重启后即可使用。

## 接口调用

```bash
python3 {baseDir}/scripts/ask.py "问题内容"
```

**请求参数**：

| 参数 | 命令行参数 | 说明 | 示例 |
|------|-----------|------|------|
| input | 位置参数 | 问题内容（必填） | `"高新技术企业认定标准"` |
| area | `--area` | 用户地域 | `--area 北京市` |
| credibleChatScope | `--scope` | 问答范围 | `onlyNorms` / `needNorms` / `all` |
| material | `--material` | 返回参考材料 | 加上即启用 |
| recommendedQuestions | `--recommended` | 返回猜你想问 | 加上即启用 |
| sessionId | `--session-id` | 会话ID（多轮对话） | UUID 格式 |

**调用示例**：

```bash
# 最简问答
python3 {baseDir}/scripts/ask.py "高新技术企业认定的标准是什么？"

# 指定地域
python3 {baseDir}/scripts/ask.py "社保卡怎么办？" --area 北京市

# 带参考材料和引用
python3 {baseDir}/scripts/ask.py "第三代社保卡怎么办？" --area 北京市 --material
```

## 返回结构

脚本自动输出格式化结果，包含：
- 安全状态（safeType）
- 知识范围（knowledgeScope：Norms/Mix/ChitChat/Other）
- 识别地域
- 完整回答内容（带 `[^1^]` 引用角标）
- 参考材料（需传 `--material`）
- 原始 JSON（`RAW_JSON_START` / `RAW_JSON_END` 之间，供程序化使用）

**知识范围处理建议**：
- Norms / Mix：深知回答，政策法规领域
- ChitChat / Other：建议使用通用模型回答

**错误码**：401 密钥无效、403 权限不足、429 余额不足、500 服务异常

## 使用流程

1. 从用户问题中提取核心问题和地域信息
2. 调用脚本获取权威回答
3. 整理呈现结果，如有参考材料展示引用来源
4. 当 knowledgeScope 为 ChitChat 或 Other 时，建议转通用模型回复

## 使用建议

- 建议传入 `--area` 提高地域匹配精度
- 建议传入 `--material` 以展示引用来源，增强可信度
