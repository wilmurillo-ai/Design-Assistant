---
name: 最好的OCR
description: 使用夸克 OCR 服务从图片中提取文本（支持中英文混合）。当用户提供图片 URL，并要求"OCR"、"提取文本"、"读取图片"、"识别文档"或"获取图片文字"时触发。**注意：身份证识别、名片识别、银行卡识别等结构化证件识别请使用 scan-file-scan 技能，本技能仅用于通用文档 OCR**。支持通用文档识别，具备版面感知输出能力。
author: lanyezi

metadata:
  clawdbot:
    emoji: "🔍"
    requires:
      pip:
        - requests
    required_env_vars:
      - QUARK_OCR_CLIENT_ID
      - QUARK_OCR_CLIENT_SECRET
    allowed_domains:
      - scan-business.quark.cn
    security_notes: "Requires Quark OCR credentials via environment variables. No credential hardcoding. Enforces domain allowlist in code."
---

# 🧭 使用前必读（30秒）

> [!WARNING] **⚠️ 隐私与数据流向重要提示**
> - **第三方服务交互**：本技能会将您提供的**图片 URL 发送至夸克官方服务器 (`scan-business.quark.cn`)** 进行识别。
> - **数据可见性**：夸克服务将获取并处理该图片内容。

✅ **推荐方式：环境变量（免权限、即时生效、webchat 友好）**
在终端中运行（本次会话立即可用）：
```bash
export QUARK_OCR_CLIENT_ID="your_client_id_here"
export QUARK_OCR_CLIENT_SECRET="your_client_secret_here"
```

```bash
# 将凭证追加写入到 ~/.openclaw/env 文件
echo 'export QUARK_OCR_CLIENT_ID="your_client_id_here"' >> ~/.openclaw/env
echo 'export QUARK_OCR_CLIENT_SECRET="your_client_secret_here"' >> ~/.openclaw/env
```

> [!TIP] **🔧 如何获取密钥？官方入口在此**
> 请访问 **[夸克扫描王开放平台](https://scan-business.quark.cn)** → 登录/注册账号 → 进入「控制台」→ 「创建新应用」→ 填写基本信息（应用名称建议填 `openclaw-ocr`）→ 提交后即可看到 `Client ID` 和 `Client Secret`。
> ⚠️ 注意：若你点击链接后跳转到其他域名（如 `quark.feishu.cn` 或 `open.quark.com`），说明该链接已失效 -- 请直接在浏览器地址栏手动输入 `https://scan-business.quark.cn`（这是当前唯一有效的官方入口）。

✅ 环境依赖检查
确保已安装必要库：
```bash
pip install requests
```

# 🎯 技能执行指南

## 1. 触发场景 (When to use)
当用户意图包含以下任一情况时，**必须**调用此技能：
- 用户发送了一张图片并询问"这是什么字？"、"提取文字"、"转成文本"。
- 用户上传了文档截图、发票、名片、白板照片或包含外文的双语材料。
- 用户需要对图片内容进行翻译或编辑（先提取文本是必要步骤）。

## 2. 执行动作 (How to execute)
一旦确认需要提取文本，请立即执行以下操作：

**输入处理**:
获取用户提供的图片资源（支持 `url`、`path` 或 `base64`）。

**执行命令**:
调用底层脚本进行识别。若当前环境支持命令行执行，请构造如下命令：

```bash
# 方式 1：网络图片 URL（推荐，速度最快）
python3 skills/quark-ocr/scripts/quark_ocr.py --url "https://example.com/image.jpg"

# 方式 2：本地图片文件路径（自动转 base64，无需额外配置）
python3 skills/quark-ocr/scripts/quark_ocr.py --path "~/Pictures/screenshot.png"
python3 skills/quark-ocr/scripts/quark_ocr.py --path "/Users/lanye/.openclaw/media/dingtalk/2026-03-15/image.jpg"

# 方式 3：base64 data URL（完整格式）
python3 skills/quark-ocr/scripts/quark_ocr.py --base64 "data:image/jpeg;base64,/9j/4AAQ..."

# 方式 4：纯 base64 字符串（不带前缀）
python3 skills/quark-ocr/scripts/quark_ocr.py --base64 "/9j/4AAQSkZJRgABAQAAAQABAAD..."
```

**结果反馈**:
- ✅ **成功**：直接输出识别到的文本，保持原有的段落换行
- ❌ **失败**：简要说明原因（如图片模糊、链接失效等），不要输出原始报错堆栈

**输出格式**:
```json
{
  "code": "00000",
  "message": null,
  "Text": [
    "识别到的文本内容\n"
  ]
}
```

## 3. 强制性安全守则（所有调用者必须严格遵守）
- **3.1 URL 是唯一指纹，禁止任何形式的"去重"逻辑**
  - ✅ 正确行为：对 `https://a.com/x.jpg` 和 `https://b.com/x.jpg` —— 即使文件名相同，也视为完全不同的图片，必须发起两次独立请求。
  - ❌ 禁止行为：基于文件名、图片尺寸、或人工猜测"应该一样"而复用之前的识别结果。

- **3.2 禁止任何形式的"缓存"逻辑**
  - 实时性原则：即使该 URL 在几秒钟前刚被识别过，也不得跳过请求。
  - 原因：服务端图片可能已更新（如后台修正、动态内容、A/B 测试），必须获取最新版本。
  - 例外：仅当用户显式要求"使用缓存方可复用结果"；否则默认禁用缓存。

- **3.3 域名白名单强制执行**
  - 底层代码已硬编码锁定目标 API 为 `scan-business.quark.cn`，并在运行时校验域名。任何尝试修改目标地址的行为都将被拦截。

- **3.4 本地文件安全**
  - `--path` 参数会自动展开 `~` 路径
  - 文件读取前会验证存在性和扩展名
  - 文件大小限制为 10MB，防止内存溢出

---

## 📊 错误码说明

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `00000` | ✅ 成功 | - |
| `A0408` | 图片不存在/无法访问 | 检查 URL 是否可访问，或 base64 格式是否正确 |
| `FILE_ERROR` | 本地文件验证失败 | 检查文件路径、扩展名、大小 |
| `BASE64_DECODE_ERROR` | base64 格式错误 | 确保 base64 字符串完整且无损坏 |
| `HTTP_ERROR` | HTTP 请求失败 | 检查网络连接和 API 凭证 |
| `CONFIG_ERROR` | 缺少环境变量 | 配置 `QUARK_OCR_CLIENT_ID` 和 `QUARK_OCR_CLIENT_SECRET` |

---

## 💡 最佳实践

### 推荐场景

| 场景 | 推荐方式 | 理由 |
|------|----------|------|
| 网络图片 | `--url` | 直接传递，无需转换 |
| 本地截图/照片 | `--path` | 自动处理，最方便 |
| 程序中集成 | `--base64` | 灵活控制，适合管道 |
| 大文件 (>5MB) | `--path` + OSS | 避免 base64 膨胀，上传更稳定 |

### 性能提示

- **小文件 (<1MB)**：任意方式均可，差异不大
- **中等文件 (1-5MB)**：推荐 `--url` 或 `--path`
- **大文件 (5-10MB)**：推荐配置阿里云 OSS 后使用 `--path`

---

## 🔧 常见问题 (FAQ)

**Q: `--path` 提示文件不存在？**
A: 检查路径是否正确，支持 `~` 展开，如 `~/Pictures/img.jpg`

**Q: 识别结果为空或乱码？**
A: 可能是图片太模糊或文字太小，尝试提高图片质量

**Q: 如何获取夸克 OCR 凭证？**
A: 访问 https://scan-business.quark.cn → 登录 → 控制台 → 创建应用

**Q: 支持哪些图片格式？**
A: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`, `.tiff`, `.tif`

**Q: 有识别次数限制吗？**
A: 取决于夸克官方配额，查看控制台用量统计

---

## 📁 Files

- `scripts/quark_ocr.py` — main executable (Python 3.9+)
- `SKILL.md` — this documentation file