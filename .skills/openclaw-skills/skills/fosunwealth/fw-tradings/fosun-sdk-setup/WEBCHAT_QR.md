# WebChat / Control UI 里如何展示二维码

## 目标（必须达成）

**用户在对话气泡里直接看到一张二维码图片**，掏出手机就能扫；**禁止**只发「已生成」、只发本地路径文字、或只发裸链接而不渲染成图。

助手回复中必须出现 **Markdown 图片语法** `![](…)` 所渲染出的图（HTTPS 或 data URI），并**同时附上开通页链接明文**（脚本 `--- 申请链接（可复制）---` 一段），方便无法扫码时复制打开。

---

## 推荐顺序（按稳定性与 OpenClaw 腾讯云实测，依次尝试直到气泡里能看到图）

| 优先级 | 方式 | 说明 |
|--------|------|------|
| **1. 首选** | **HTTPS 公网图** | 将脚本生成的 PNG（路径见 `<<<FOSUN_QR_PNG_FOR_CHAT>>>`）通过 **平台自带上传** 得到 `https://…` 地址；在回复里**单独一段**写 `![开通二维码](https://…/qr.png)`。**腾讯云 OpenClaw 下通常最稳。** |
| **2. 备选** | **`--markdown-data-uri`** | 运行 `gen_access_url.py` 时加该参数；从 **`<<<FOSUN_QR_MARKDOWN_DATA_URI>>>`** 块取出以 `![` 开头的**完整一行**（含全部 base64），**作为独立段落**贴进助手回复（前后各空一行）。部分环境可能对超长 base64 有限制。 |
| **3. 兜底** | **Read 本地 PNG** | 在 **具备读图能力** 的助手环境（如 Cursor）中，用 Read 读取 `<<<FOSUN_QR_PNG_FOR_CHAT>>>` 指向的 PNG，在回复中展示图片。 |
| **4. 再兜底** | **本机路径 + 说明** | 明确告知用户在本机打开该 PNG；**不指望**对方会话里同路径存在——仅作最后手段。 |

**容错**：若用户反馈「看不到图」，按上表 **1 → 2 → 3** 换一条路，直到对话里出现可扫的图。

---

## Markdown 写法（否则图不显示）

- `![](…)` 必须作为 **独立段落**（**前后各一个空行**）。
- **禁止**把图片行放进 `` ``` `` 代码块、**禁止**放进 `>` 引用块或 `- ` 列表项里（多数 WebChat 不渲染）。
- **禁止**只输出 `https://…` 纯文本链接而不写 `![](https://…)` —— 裸链通常不会变成图。

---

## 仍不推荐的（勿优先）

| 能力 | 说明 |
|------|------|
| **`message` 工具 + WebChat 附件** | 当前 **无法** 稳定把附件回显成气泡内图片；**不要**优先走这条。 |
| **仅路径 / 仅说明** | 不满足「对话里直接可扫」的目标。 |

---

## 脚本与依赖

```bash
# 对「将要执行 gen_access_url.py 的 Python」安装依赖
pip install -r skills/fw-tradings/fosun-sdk-setup/scripts/requirements-gen-access-url.txt

# 需已配置 FSOPENAPI_OPEN_URL（如 source fosun.env）或显式传 --url
python3 skills/fw-tradings/fosun-sdk-setup/scripts/gen_access_url.py --markdown-data-uri
```

若未输出 `<<<FOSUN_QR_MARKDOWN_DATA_URI>>>`（PNG 超字节上限等），可调大 **`--markdown-data-uri-max-bytes`** 或略减小 **`--max-edge`**，并**优先改用优先级 1（HTTPS 上传后 `![](https://…)`）**。

---

## 外部 IM（微信 / 钉钉等，非 WebChat 内嵌）

`openclaw message send … --media` 依赖 **本机已安装且已配置的 OpenClaw CLI**；**多数环境未接入**，不作为「对话内展示」的主方案。若环境确认可用，可参考脚本 **`<<<FOSUN_OPENCLAW_MEDIA_TEMPLATE>>>`** 或 `--openclaw-to "<接收者>"` 生成的命令；**执行前自行验证 CLI 与通道**。

```bash
# 仅当 openclaw 可用时再试
openclaw message send --to <接收者> --media /绝对路径/生成的.png --message "OpenAPI申请二维码"
```

---

## 历史备注

**2026-03-18** 起：同一套 Control UI 上 **data URI 与 HTTPS 图** 表现因版本/策略而异；**以「气泡内必须出现可扫描的图」为准**，按本文优先级切换，勿固守单一方式。
