---
name: free-api-discovery
description: Discover and test which free/low-cost LLM and AI APIs are reachable from the current environment, then route tasks to the best available service. Includes network testing, API landscape mapping, and task-to-API routing strategy.
---

# 免费 API 服务发现与任务路由

## 何时使用

- 需要找出当前环境可以访问哪些免费/低成本 AI API
- 需要根据任务类型选择最合适的 API 服务
- 内置工具不可用（如网络受限、本地模型准确率不够）时寻找替代方案
- 用户要求"能用免费的都配上"

## 核心流程

### Step 1: 网络可达性测试

使用 Python `urllib`（无需 curl）测试各服务连通性：

```python
import urllib.request, ssl, socket

socket.setdefaulttimeout(8)
ctx = ssl.create_default_context()

services = {
    "Groq(免费Whisper+LLM)": "https://api.groq.com",
    "SiliconFlow(中文模型)": "https://api.siliconflow.cn/v1/models",
    "DeepSeek": "https://api.deepseek.com",
    "OpenRouter(多模型聚合)": "https://openrouter.ai/api/v1",
    "Together AI": "https://api.together.xyz",
    "Cloudflare Workers AI": "https://api.cloudflare.com/client/v4",
    "Mistral": "https://api.mistral.ai/v1",
    "Google Gemini": "https://generativelanguage.googleapis.com",
    "阿里云百炼": "https://dashscope.aliyuncs.com",
}

for name, url in services.items():
    try:
        r = urllib.request.urlopen(urllib.request.Request(url), context=ctx, timeout=6)
        print(f"✅ {name}: HTTP {r.status}")
    except urllib.error.HTTPError as e:
        print(f"✅ {name}: HTTP {e.code} (可达，需认证)")
    except Exception as e:
        reason = str(e).split(':')[-1].strip()[:50]
        print(f"❌ {name}: {reason}")
```

> ⚠️ **注意**：不要用 `curl`（可能未安装），用 Python `urllib` 替代。超时设为 5-8 秒避免卡住。

### Step 2: 任务 → API 路由映射

根据测试结果和各服务能力，按任务类型分配：

```
🎤 语音转文字（ASR）
   优先级: Groq Whisper API > SiliconFlow > DeepSeek
   原因: Groq 完全免费 + whisper-large-v3 中文准确率高

💬 中文对话 / 聊天
   优先级: SiliconFlow (Qwen系列) > DeepSeek > Groq (Llama)
   原因: 国内服务中文优化更好

💻 代码生成 / 技术推理
   优先级: Groq (Llama) > DeepSeek > Together AI
   原因: 开源代码模型在 Groq 上跑得快且免费

🖼️ 图片分析 / 视觉理解
   优先级: OpenRouter > Cloudflare > Gemini
   原因: 需要多模态模型支持

⚡ 通用快速任务
   优先级: Cloudflare Workers AI (每天1万次免费)
   原因: 免费额度大，延迟低
```

### Step 3: 收集 API Key

向用户说明需要哪些 Key，按优先级排列：

| 优先级 | 服务 | 注册地址 | 免费情况 |
|--------|------|----------|----------|
| P0 ⭐ | **Groq** | https://console.groq.com/keys | 完全免费，无信用卡 |
| P1 | **SiliconFlow** | https://cloud.siliconflow.cn | 注册送额度 |
| P2 | **DeepSeek** | https://platform.deepseek.com | 极低价格 |
| P3 | **OpenRouter** | https://openrouter.ai/keys | 部分模型免费 |

### Step 4: 配置与验证

将 Key 安全存储并验证可用性：

```python
# 使用 Hermes 的 .env 或 config 存储 Keys（通过 write_file 工具）
# 验证每个 Key 是否有效
import urllib.request, json, ssl

def verify_api_key(base_url, api_key, service_name):
    """验证 API Key 是否有效"""
    req = urllib.request.Request(
        f"{base_url}/models",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return True, f"{service_name} Key 有效"
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return False, f"{service_name} Key 无效或过期"
        return True, f"{service_name} 可用 (HTTP {e.code})"
    except Exception as e:
        return False, f"{service_name} 连接失败: {e}"
```

## 已知环境信息（2026-04-17 测试）

### 当前网络可达的服务（国际）
| 服务 | 状态 | 备注 |
|------|------|------|
| ✅ Groq | 可达 | 首选！免费 Whisper + LLM |
| ✅ OpenRouter | 可达 | 返回 200，多模型聚合（30个免费模型）|
| ✅ SiliconFlow | 可达 | 国内直连，中文强 |
| ✅ DeepSeek | 可达 | 国内直连 |
| ✅ Together AI | 可达 | 免费$1额度 |
| ✅ Cloudflare | 可达 | 每天1万次免费 |
| ❌ Mistral | 不通 | Network unreachable |
| ❌ Google Gemini | 不通 | Network unreachable |
| ❌ HuggingFace Inference | 不通 | Network unreachable |
| ❌ Perplexity | 不通 | Network unreachable |

### 当前网络可达的服务（国内平台）— 2026-04-17 全面测试
| 服务 | 状态 | 免费政策 | 注册方式 |
|------|------|----------|----------|
| ✅ **智谱 GLM** | HTTP 401(可达) | **GLM-4-Flash 完全免费不限量** | 手机号 |
| ✅ **阿里 DashScope** | HTTP 401(可达) | 通义千问新用户免费 | 阿里云账号 |
| ✅ **百度千帆** | HTTP 401(可达) | 新用户免费额度 | 百度账号 |
| ✅ **DeepSeek** | HTTP 401(可达) | 极低价格（几乎免费）| 手机号 |
| ✅ **硅基流动 SiliconFlow** | HTTP 401(可达) | 注册送额度 | 手机号 |
| ✅ **月之暗面 Kimi** | HTTP 401(可达) | 新用户免费额度 | 手机号/邮箱 |
| ✅ **字节豆包 Volcengine** | HTTP 401(可达) | 新用户免费额度 | 火山引擎账号 |
| ✅ **百川智能** | HTTP 401(可达) | 有免费模型 | 手机号 |
| ✅ **阶跃星辰 StepFun** | HTTP 401(可达) | 有免费额度 | 手机号 |
| ✅ **零一万物 Yi** | HTTP 400(可达) | 有免费额度 | 手机号 |
| ❌ 讯飞星火 | DNS 解析失败 | — | — |
| ❌ 腾讯混元 | DNS 解析失败 | — | — |
| ⚠️ **MiniMax** | HTTP 404(域名可达) | 路径待确认 | — |

### 妙搭（Miaoda）聚合平台
用户截图显示「妙搭」是一个**国产大模型聚合平台**，一个 Key 可调用多厂商模型：
- 域名：`api.miaoda.cn`（网络可达 ✅）
- 支持模型：妙搭(默认)、GLM-5.1(智谱)、Qwen 3.6(阿里)、MiniMax M2.7、豆包 Seed 2.0 Pro、妙搭多模态
- ⚠️ 所有路径返回 404，需要认证后才能使用
- 如果用户有妙搭 Key → **最简方案，一键配全部模型**

### OpenRouter 免费模型清单（30个，2026-04-17）
重点推荐：
- `meta-llama/llama-3.3-70b-instruct:free` — 通用对话
- `z-ai/glm-4.5-air:free` — 中文对话
- `qwen/qwen3-coder:free` — 代码能力
- `moonshotai/kimi-k2.5` — 长文本
- `nvidia/nemotron-3-super-120b-a12b:free` — 推理
- `openai/gpt-oss-120b:free` / `gpt-oss-20b:free` — OpenAI 开源
- `nousresearch/hermes-3-llama-3.1-405b:free` — 超大参数

> ⚠️ **OpenRouter Key 验证坑**：`/models` 接口可能返回 200（能列模型），但 `/chat/completions` 返回 401 `"User not found"`。说明 Key 可能无效/过期/未完成注册。需要分别验证。

### SiliconFlow 详细配置经验（2026-04-17 实测）

**Key 有效但余额不足的处理**：
- SiliconFlow 返回 `403 + "Sorry, your account balance is insufficient"` 表示余额耗尽
- **Pro 前缀模型**（如 `Pro/zai-org/GLM-5.1`）消耗额度更快，普通模型也可能因余额不足被拒
- 解决方案：去 https://m.siliconflow.cn 签到领每日免费额度，或充值小额

**SiliconFlow 可用模型分类（共111个）**：
```
💬 对话模型: 91个 — Qwen3.5、DeepSeek-V3.2、GLM-5/4.6、MiniMax-M2.5 等
🎤 语音转文字: 3个 — FunAudioLLM/SenseVoiceSmall(中文最佳)、TeleAI/TeleSpeechASR、FunAudioLLM/CosyVoice2
📊 嵌入模型: 10个 — Qwen3-Embedding系列、BAAI/bge-m3等
🖼️ 图像生成: 3个 — Qwen/Qwen-Image系列
🔍 重排序: 4个 — BAAI/bge-reranker等
```

**语音转文字正确调用方式（multipart/form-data）**：
```python
import uuid, urllib.request, ssl, json

api_key = "sk-xxx"
base = "https://api.siliconflow.cn/v1"
audio_file = "/path/to/audio.ogg"
boundary = uuid.uuid4().hex

with open(audio_file, 'rb') as f:
    file_data = f.read()

# 构建正确的 multipart body（注意 bytes 拼接，不要用 f-string 处理 bytes）
body_data = (
    '--' + boundary + '\r\n'
    'Content-Disposition: form-data; name="file"; filename="voice.ogg"\r\n'
    'Content-Type: audio/ogg\r\n\r\n'
).encode() + file_data + b'\r\n' + (
    '--' + boundary + '\r\n'
    'Content-Disposition: form-data; name="model"\r\n\r\n'
    'FunAudioLLM/SenseVoiceSmall\r\n'
    '--' + boundary + '--\r\n'
).encode()

req = urllib.request.Request(
    base + "/audio/transcriptions",
    data=body_data,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "multipart/form-data; boundary=" + boundary
    }
)
resp = urllib.request.urlopen(req, context=ctx, timeout=30)
result = json.loads(resp.read())
print(result["text"])  # 转录文本
```

> ⚠️ **坑**：不能用 JSON body 发送音频文件（返回 422），必须用 multipart/form-data。构建 body 时注意 bytes 和 str 的拼接，不要在 f-string 中混用。

**SenseVoiceSmall 转录效果**：中文识别准确率明显优于本地 Whisper（faster-whisper base 模型）。

---

### Groq 配置经验与排错（2026-04-17 实测）

**Groq Key 格式**：`gsk_` 前缀 + 56 字符（如 `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`）

**403 Forbidden 排查清单**：
1. **邮箱未验证** → 最常见原因！注册后必须点击邮件中的验证链接
2. **账户未完全激活** → 登录 console.groq.com 检查是否有提示
3. **地区限制** → 部分网络环境可能受限
4. **Key 已撤销或过期** → 去 console.groq.com/keys 重新生成

**注册流程**：
1. 打开 https://groq.com （主页通常可达）
2. Sign In → Google/GitHub/邮箱登录
3. ⚠️ **关键：检查邮箱，点击验证链接**
4. Console → API Keys → Create API Key
5. 无需信用卡、无需手机号

**Groq 免费模型**：
- 对话: `llama-3.3-70b-versatile`, `llama-3.1-8b-instant`, `mixtral-8x7b-32768`, `gemma2-9b-it`
- 语音: `whisper-large-v3`（支持中文，设置 language=zh）

---

### OpenRouter Key 排错经验

**现象**：`/models` 接口返回 200（能列出 345 个模型），但 `/chat/completions` 返回 `401 "User not found"`
**原因**：Key 无效 / 未完成邮箱验证 / Key 已被撤销
**解决**：登录 openrouter.ai/keys 检查 Key 状态，重新生成

---

### 配置文件结构

所有 API 配置统一存储在 `~/.hermes/api-config.json`：

```json
{
  "services": {
    "siliconflow": { "base_url", "api_key", "status", "models" },
    "groq": { "base_url", "api_key", "status" },
    "openrouter": { ... },
    ...
  },
  "task_routing": {
    "语音转文字": "Groq > SiliconFlow",
    "中文对话": "智谱 > SiliconFlow > DeepSeek",
    ...
  }
}
```

---

### 当前环境限制
- 无 root 权限（无法 apt install curl 等）
- 无 pip（用 uv pip 代替）
- Python 3.13.5 + Node.js 20 + uv 可用
- HuggingFace Hub 直连不通（需用 hf-mirror.com 镜像）
- **无 curl**（必须用 Python urllib 做所有网络请求）
- faster-whisper 可安装但需从 hf-mirror.com 下载模型（首次 ~35s 加载）

## 注意事项

1. **用户偏好**：大型安装/下载任务需要主动监控进度并反馈
2. **不要静默等待**：耗时操作要有进度汇报
3. **本地 vs 云端**：本地模型准确率不够时，优先推荐免费云端 API
4. **Key 安全**：API Key 通过安全方式存储，不在日志中明文输出完整 Key
5. **网络测试用 urllib**：环境中可能没有 curl，始终用 Python urllib 做网络请求
6. **余额优先消耗 Pro 模型**：SiliconFlow 的 Pro 前缀模型消耗额度更快，测试时慎用
7. **multipart 构建陷阱**：Python 中拼接 multipart body 时，bytes 和 str 不能直接混用 f-string，要用 `.encode()` 统一或分别拼接后再合并
