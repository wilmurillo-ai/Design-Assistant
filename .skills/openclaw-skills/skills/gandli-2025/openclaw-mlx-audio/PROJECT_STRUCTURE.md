# OpenClaw mlx-audio 项目结构

## 项目定位

**OpenClaw mlx-audio** = mlx-audio 引擎 + OpenClaw 集成层

```
┌─────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                      │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐    │
│  │     OpenClaw mlx-audio Plugin (本项目的核心)      │    │
│  │  ┌─────────────┐  ┌─────────────┐               │    │
│  │  │   Tools     │  │  Commands   │               │    │
│  │  │  voice_tts  │  │  /mlx-tts   │               │    │
│  │  │  voice_stt  │  │  /mlx-stt   │               │    │
│  │  └──────┬──────┘  └──────┬──────┘               │    │
│  │         │                │                       │    │
│  │         └───────┬────────┘                       │    │
│  │                 │                                │    │
│  │         ┌───────▼────────┐                       │    │
│  │         │  Python Server │                       │    │
│  │         │   (mlx-audio)  │                       │    │
│  │         └───────┬────────┘                       │    │
│  └─────────────────┼────────────────────────────────┘    │
│                    │                                      │
│                    ▼                                      │
│         ┌──────────────────────┐                          │
│         │   mlx-audio CLI/API  │                          │
│         │   (Blaizzy/mlx-audio)│                         │
│         └──────────────────────┘                          │
└─────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1️⃣ OpenClaw Plugin (`src/index.ts`)

**职责：** OpenClaw 集成层

- 注册 Tools (`voice_tts`, `voice_stt`, `voice_status`)
- 注册 Commands (`/mlx-tts`, `/mlx-stt`)
- 管理 Python 子进程 (mlx-audio server)
- 处理配置加载和热重载
- 提供 OpenAI 兼容 API 代理

**文件：**
```
src/
├── index.ts              # 主入口
├── tts-server.ts         # TTS 服务器管理
├── stt-server.ts         # STT 服务器管理
├── config.ts             # 配置管理
└── types.ts              # 类型定义
```

---

### 2️⃣ Skills (`skills/`)

**职责：** 用户交互层 - 教会 Agent 如何使用工具

**文件：**
```
skills/
├── mlx-tts/
│   └── SKILL.md          # TTS 使用指南 (触发条件、工具调用、示例)
└── mlx-stt/
    └── SKILL.md          # STT 使用指南
```

**SKILL.md 内容：**
- 触发条件 (什么情况下使用)
- 工具定义 (参数、返回值)
- 使用示例 (JSON 调用示例)
- 可用模型列表
- CLI 命令说明
- 配置方法
- 故障排除

---

### 3️⃣ Python Runtime (`python-runtime/`)

**职责：** 封装 mlx-audio，提供本地 HTTP 服务

**不重新发明轮子** - 直接调用 `mlx-audio` 库：

```python
# TTS Server (基于 mlx-audio)
from mlx_audio.tts.utils import load_model
from mlx_audio.tts.generate import generate_audio

# STT Server (基于 mlx-audio)
from mlx_audio.stt.utils import load
from mlx_audio.stt.generate import generate_transcription
```

**文件：**
```
python-runtime/
├── tts_server.py         # TTS HTTP 服务
├── stt_server.py         # STT HTTP 服务
├── requirements.txt      # Python 依赖
└── pyproject.toml        # Python 项目配置
```

---

## 数据流

### TTS 流程

```
用户请求
  │
  ▼
OpenClaw Agent (通过 SKILL.md 学习)
  │
  ▼
调用 Tool: voice_tts
  │
  ▼
Plugin (src/index.ts)
  │
  ▼
HTTP POST → localhost:19280/v1/audio/speech
  │
  ▼
Python TTS Server (python-runtime/tts_server.py)
  │
  ▼
mlx-audio.generate() → 生成音频
  │
  ▼
返回 MP3 文件路径
```

### STT 流程

```
用户上传音频
  │
  ▼
OpenClaw Agent (通过 SKILL.md 学习)
  │
  ▼
调用 Tool: voice_stt
  │
  ▼
Plugin (src/index.ts)
  │
  ▼
HTTP POST → localhost:19290/v1/audio/transcriptions
  │
  ▼
Python STT Server (python-runtime/stt_server.py)
  │
  ▼
mlx-audio.transcribe() → 转录文本
  │
  ▼
返回文本结果
```

---

## 与原始 mlx-audio 的关系

| 组件 | Blaizzy/mlx-audio | openclaw-mlx-audio (本项目) |
|------|-------------------|---------------------------|
| **核心引擎** | ✅ 提供 | ❌ 直接使用 |
| **Python 库** | ✅ `pip install mlx-audio` | ❌ 作为依赖 |
| **CLI 工具** | ✅ `mlx_audio.tts.generate` | ⚠️ 封装为 Plugin |
| **HTTP API** | ✅ 可选 | ✅ 主要集成方式 |
| **OpenClaw 集成** | ❌ | ✅ **核心价值** |
| **Skills 文档** | ❌ | ✅ **教会 Agent 使用** |
| **配置管理** | ⚠️ 基础 | ✅ OpenClaw config 集成 |
| **命令扩展** | ⚠️ 基础 | ✅ `/mlx-tts`, `/mlx-stt` |

---

## 安装流程

### 1. 安装 mlx-audio (底层引擎)

```bash
uv tool install mlx-audio --prerelease=allow
```

### 2. 安装 OpenClaw Plugin (本项目的集成层)

```bash
cd ~/.openclaw/workspace/projects/openclaw-mlx-audio
bun install
bun run build
```

### 3. 启用 Plugin

在 `openclaw.json` 添加：

```json
{
  "plugins": {
    "entries": {
      "openclaw-mlx-audio": {
        "enabled": true
      }
    }
  }
}
```

### 4. 自动安装 Skills

Plugin 启动时自动注册 Skills 路径：
- `~/.openclaw/workspace/projects/openclaw-mlx-audio/skills/mlx-tts/SKILL.md`
- `~/.openclaw/workspace/projects/openclaw-mlx-audio/skills/mlx-stt/SKILL.md`

---

## 目录结构 (最终版)

```
openclaw-mlx-audio/
├── 📄 README.md                    # 项目介绍
├── 📄 README.zh-CN.md              # 中文介绍
├── 📄 PROJECT_STRUCTURE.md         # 本文档
├── 📄 MODELS.md                    # 支持的模型列表
├── 📄 QUICK_REFERENCE.md           # 快速参考
│
├── 📦 package.json                 # Node.js 项目配置
├── 📦 tsconfig.json                # TypeScript 配置
├── 📦 openclaw.plugin.json         # OpenClaw 插件清单
│
├── 📂 src/                         # Plugin 源代码 (TypeScript)
│   ├── index.ts                    # 主入口
│   ├── tts-server.ts               # TTS 服务器管理
│   ├── stt-server.ts               # STT 服务器管理
│   ├── config.ts                   # 配置管理
│   └── types.ts                    # 类型定义
│
├── 📂 python-runtime/              # Python 运行时 (封装 mlx-audio)
│   ├── tts_server.py               # TTS HTTP 服务
│   ├── stt_server.py               # STT HTTP 服务
│   ├── requirements.txt            # Python 依赖
│   └── pyproject.toml              # Python 项目配置
│
├── 📂 skills/                      # OpenClaw Skills (教会 Agent 使用)
│   ├── mlx-tts/
│   │   └── SKILL.md                # TTS 技能文档
│   └── mlx-stt/
│       └── SKILL.md                # STT 技能文档
│
├── 📂 scripts/                     # 构建脚本
│   ├── check-schema-sync.mjs       # 检查 schema 同步
│   └── sync-manifest-version.mjs   # 同步版本号
│
└── 📂 test/                        # 测试
    ├── tts.test.ts
    └── stt.test.ts
```

---

## 关键设计决策

### ✅ 做什么

1. **OpenClaw 集成** - 注册 Tools 和 Commands
2. **进程管理** - 启动/停止/监控 Python 服务器
3. **配置管理** - 支持热重载，OpenClaw config 集成
4. **Skills 文档** - 教会 Agent 何时/如何使用工具
5. **错误处理** - 友好的错误提示和重试逻辑

### ❌ 不做什么

1. **不重新实现 mlx-audio** - 直接调用官方库
2. **不修改模型代码** - 使用 HuggingFace 上的预训练模型
3. **不处理音频编解码** - 交给 mlx-audio 处理
4. **不实现 Web UI** - 专注 CLI 和 API 集成

---

## 下一步

1. ✅ 完成 Plugin 框架 (已做)
2. ⏳ 实现 Python 服务器 (封装 mlx-audio)
3. ⏳ 实现 TypeScript 主逻辑 (进程管理 + API 调用)
4. ⏳ 完善 Skills 文档 (基于实际 API)
5. ⏳ 端到端测试
