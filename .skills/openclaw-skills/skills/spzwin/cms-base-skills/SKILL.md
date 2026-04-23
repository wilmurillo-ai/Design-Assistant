---
name: cms-base-skills
description: cms基础 Skill — 登录授权、appKey/token 获取、七牛文件上传/下载、Skill 发现/安装、依赖检查
---

# cms基础 Skill — 公共基础能力层

**版本**: v1.0

---

## 能力总览

| # | 能力 | 脚本 | 需要 token |
|---|------|------|-----------|
| 1 | 登录授权 / 获取 appKey / 获取 token | `scripts/auth/login.py` | 否 |
| 2 | 上传七牛文件 | `scripts/file_storage/qiniu_upload.py` | 是 |
| 3 | 下载七牛文件 | `scripts/file_storage/qiniu_download.py` | 否 |
| 4 | Skill 发现 | `scripts/skill_registry/find_skills.py` | 否 |
| 5 | Skill 安装 | `scripts/skill_registry/install_skill.py` | 否 |
| 6 | 依赖检查 | `scripts/dependency/check_deps.py` | 否 |

---

## 意图路由

| 用户说 | 执行 | token |
|---|---|---|
| "登录" / "获取 token" / "获取 access-token" / "重新授权" | `login.py --ensure` | 否 |
| "获取 appKey" / "获取 APPK" / "获取 APK" / "获取工作协同 key" / "获取协同 K" / "获取协同 key" / "获取 CWork Key" | `login.py --resolve-app-key` | 否 |
| "上传文件到七牛" / "传到七牛" | `qiniu_upload.py <file>` | 是 |
| "下载七牛文件" / "从七牛下载" | `qiniu_download.py <url>` | 否 |
| "搜索 Skill" / "有哪些 Skill" | `find_skills.py --search <kw>` | 否 |
| "安装 Skill" / "下载 xxx" | `install_skill.py --code <code>` | 否 |
| "检查依赖" | `check_deps.py --skill-path <path>` | 否 |

鉴权相关扩展意图：

- 用户提到“授权一下”“拿一下授权 key”“帮我取一下协同 key”“帮我拿 appKey”“帮我查一下工作协同 key”，都应优先路由到 `scripts/auth/login.py`
- 需要 `appKey` 时执行 `login.py --resolve-app-key`
- 需要 `access-token` 时执行 `login.py --ensure`
- 若获取 `appKey` 时当前 workspace 下存在 `appkey_manager.py`，应在 Python 脚本内动态加载并执行 `get_appkey()`
- 若扫描失败或执行失败，则继续向用户索要 `CWork Key`

---

## 鉴权

详见 `common/auth.md`。核心要点：

- 不再假设所有接口都只用 `access-token`
- 按接口文档声明选择 `appKey` 或 `access-token`
- `appKey` 优先级：`XG_BIZ_API_KEY` / `XG_APP_KEY` → 上下文 `appKey` → 扫描当前 workspace 下的 `appkey_manager.py` → 向用户索要 `CWork Key`
- `access-token` 优先级：`XG_USER_TOKEN` → 上下文 token → `appKey` 换 token → 向用户索要 `CWork Key`
- `xgjk-base-skills` 不维护内部 appKey manager；需要时扫描当前 workspace 下的 `appkey_manager.py`，失败就继续向用户索要 `CWork Key`

---

## 被其他 Skill 引用

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'xgjk-base-skills', 'scripts'))
from auth.login import ensure_token, resolve_app_key, build_auth_headers
from file_storage.qiniu_upload import get_qiniu_token, upload_file
from skill_registry.find_skills import call_api, search_skills
from dependency.check_deps import ensure_dependencies

# 一行代码确保依赖就绪
ensure_dependencies("/path/to/my-skill", auto_install=True)

# access-token 接口
token = ensure_token(context=context)
headers = build_auth_headers("access-token", context=context)

# appKey 接口
app_key = resolve_app_key(context=context)
headers = build_auth_headers("appKey", context=context)
```

上层 Skill 在 `SKILL.md` frontmatter 中声明依赖即可：

```yaml
---
name: my-skill
dependencies:
  - xgjk-base-skills
---
```

---

## 约束

1. **零依赖** — 仅 Python 标准库
2. **stdout = 结果，stderr = 日志** — 便于管道组合
3. **重试 3 次，间隔 1 秒** — 网络请求容错
4. **禁止落盘 token** — 仅环境变量/内存传递

---

## 能力树

```
cms-base-skills/
├── SKILL.md                                # 技能定义（本文件）
├── common/
│   ├── auth.md                             # 鉴权规范（按优先级解析 appKey / access-token）
│   └── conventions.md                      # 通用约束
├── openapi/
│   ├── auth/login.md                       # AppKey 登录接口
│   ├── file-storage/
│   │   ├── qiniu-upload.md                 # 七牛上传接口
│   │   └── qiniu-download.md               # 七牛下载接口
│   └── skill-registry/find-skills.md       # Skill 发现接口
└── scripts/
    ├── auth/login.py                       # appKey/token 解析 + header 组装
    ├── file_storage/
    │   ├── qiniu_upload.py                 # 获取凭证 + 上传七牛
    │   └── qiniu_download.py               # 下载七牛文件
    ├── skill_registry/
    │   ├── find_skills.py                  # 搜索 / 浏览 / 详情
    │   └── install_skill.py                # 下载并安装到本地
    └── dependency/
        └── check_deps.py                   # 依赖检查 + 自动补装
```
