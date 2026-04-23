---
name: wiznote
version: 1.0.0
description: WizNote private API connector for reading and writing notes via RESTful API. Use when the user mentions "为知笔记", "WizNote", "Wiz", or needs to search, create, update, or delete notes, manage folders, or search by keywords/tags in WizNote private deployments.
author: wangfengxiang
tags: [wiznote, notes, api, private-deployment]
---

# WizNote 私有化 Skill

## 概述

此 Skill 为 OpenClaw 提供为知笔记（WizNote）私有化部署的 API 连接能力，支持：
- ✅ 通过密码登录获取认证 token
- ✅ 笔记的创建、读取、更新、删除（CRUD）
- ✅ 文件夹/分类管理
- ✅ 关键词和标签搜索
- ✅ 完整的错误处理和重试机制

## 触发条件

当用户提到以下关键词时，自动触发此 Skill：
- "为知笔记"
- "WizNote"
- "Wiz"
- "笔记管理"
- "创建笔记" / "搜索笔记"

## API 调研结果

### 1. 核心 Endpoint 清单（私有化部署 - 已验证）

| Endpoint | 方法 | 用途 | 认证要求 | 状态 |
|---------|------|------|---------|------|
| `/as/user/login` | POST | 用户登录，获取 token | ❌ 无需 | ✅ 已验证 |
| `/as/user/keep` | GET | 保持登录状态 | ✅ 需要 | ✅ 已验证 |
| `/wizas/a/users/get_info` | GET | 获取用户信息 | ✅ 需要 | ✅ 已验证 |
| `/share/api/shares` | GET | 获取分享列表 | ✅ 需要 | ✅ 已验证 |
| `/ks/category/all/{kbGuid}` | GET | 获取所有目录 | ✅ 需要 | ✅ 已验证 |
| `/ks/tag/all/{kbGuid}` | GET | 获取所有标签 | ✅ 需要 | ✅ 已验证 |
| `/ks/note/list/category/{kbGuid}` | GET | 按目录获取笔记列表 | ✅ 需要 | ✅ 已验证 |
| `/ks/note/list/tag/{kbGuid}` | GET | 按标签获取笔记列表 | ✅ 需要 | ✅ 已验证 |
| `/ks/note/download/{kbGuid}/{docGuid}` | GET | 下载笔记详情 | ✅ 需要 | ⚠️ 待测试 |
| `/ks/note/create/{kbGuid}` | POST | 创建笔记 | ✅ 需要 | ⚠️ 待测试 |
| `/ks/note/update/{kbGuid}/{docGuid}` | PUT | 更新笔记 | ✅ 需要 | ⚠️ 待测试 |
| `/ks/note/delete/{kbGuid}/{docGuid}` | DELETE | 删除笔记 | ✅ 需要 | ⚠️ 待测试 |

**参考项目：** [ConteMan/cwiz](https://github.com/ConteMan/cwiz)

### 2. 认证方式详解

#### 方式一：密码登录获取 Token（推荐）

**请求示例**（私有化部署）：
```bash
POST /as/user/login
Content-Type: application/json

{
  "userId": "your_username",
  "password": "your_password"
}
```

**成功响应**：
```json
{
  "returnCode": 200,
  "returnMessage": "OK",
  "result": {
    "token": "your_auth_token_here",
    "userId": "your_username",
    "kbGuid": "knowledge_base_guid",
    "kbServer": "http://192.168.1.121:30802"
  }
}
```

**流程**：
1. 调用登录接口 `/as/user/login`，传入用户名和密码
2. 从响应中提取 `token` 和 `kbGuid` 字段
3. 将 token 存储在环境变量 `WIZ_TOKEN` 中
4. 将 kbGuid 存储在环境变量 `WIZ_KB_GUID` 中
5. 后续请求在 URL 参数中携带：`token=<token>&kbGuid=<kbGuid>`

#### 方式二：直接使用已有 Token

如果已有 token，直接设置环境变量：
```bash
export WIZ_TOKEN="your_existing_token"
```

#### Token 刷新机制

- Token 有效期：通常为 30 天
- 过期处理：API 返回 401 错误时，需要重新登录获取新 token
- 建议：在脚本中实现自动重新登录逻辑

### 3. API 版本和稳定性

- **当前版本**：v1（无版本号，直接在根路径下）
- **稳定性**：为知笔记 API 相对稳定，向后兼容
- **格式**：RESTful API，请求和响应均为 JSON 格式
- **编码**：UTF-8

### 4. 私有化部署特殊配置

#### 端口配置

为知笔记私有化部署支持两种端口配置：

| 场景 | 默认端口 | 完整 URL |
|------|---------|----------|
| 标准部署 | 80 | `http://your-server:80` 或 `http://your-server` |
| 私有化部署（推荐） | 9269 | `http://your-server:9269` |

**环境变量配置**：
```bash
# 私有化部署（端口 9269）
export WIZ_ENDPOINT="http://your-wiznote-server:9269"

# 标准部署（端口 80）
export WIZ_ENDPOINT="http://your-wiznote-server:80"
# 或简写为
export WIZ_ENDPOINT="http://your-wiznote-server"
```

#### 私有化部署注意事项

1. **网络可达性**：确保 OpenClaw 服务器能访问为知笔记服务器
2. **防火墙配置**：开放相应端口（80 或 9269）
3. **HTTPS 支持**：私有化部署可能使用 HTTP，云服务使用 HTTPS
4. **CORS 配置**：如需浏览器访问，需配置 CORS

## 配置说明

### 环境变量

此 Skill 依赖以下环境变量：

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `WIZ_ENDPOINT` | 是 | 为知笔记 API 地址 | `http://127.0.0.1:80` |
| `WIZ_USER` | 是 | 用户名 | 无 |
| `WIZ_TOKEN` | 推荐 | 认证令牌（也可通过密码登录获取） | 无 |

### 配置方式

**方式一：直接设置环境变量**
```bash
export WIZ_ENDPOINT="http://192.168.1.100:9269"
export WIZ_USER="admin"
export WIZ_TOKEN="your_token_here"
```

**方式二：通过 .env 文件**
```bash
# 在项目根目录创建 .env 文件
WIZ_ENDPOINT=http://192.168.1.100:9269
WIZ_USER=admin
WIZ_TOKEN=your_token_here
```

**方式三：在代码中配置**
```python
import os
os.environ['WIZ_ENDPOINT'] = 'http://192.168.1.100:9269'
os.environ['WIZ_USER'] = 'admin'
os.environ['WIZ_TOKEN'] = 'your_token_here'
```

## 使用示例

### 1. 认证 - 通过密码登录获取 Token

```python
from scripts.wiznote_api import WizNoteAPI

# 初始化 API 客户端
api = WizNoteAPI()

# 通过密码登录获取 token
token = api.login(password="your_password")
print(f"获取到的 token: {token}")
```

### 2. 创建笔记

```python
from scripts.note_ops import create_note

# 创建一篇新笔记
result = create_note(
    title="我的第一篇笔记",
    content="<h1>Hello WizNote</h1><p>这是笔记内容</p>",
    folder="/我的笔记",
    tags=["测试", "OpenClaw"]
)
print(f"笔记创建成功，ID: {result['note_id']}")
```

### 3. 搜索笔记

```python
from scripts.search import search_notes

# 关键词搜索
results = search_notes(keyword="OpenClaw")
for note in results:
    print(f"{note['title']} - {note['created_time']}")

# 标签搜索
results = search_notes(tag="重要")
for note in results:
    print(f"{note['title']}")
```

### 4. 更新笔记

```python
from scripts.note_ops import update_note

# 更新笔记内容
update_note(
    note_id="note_12345",
    title="更新后的标题",
    content="<p>更新后的内容</p>",
    tags=["更新", "重要"]
)
```

### 5. 文件夹管理

```python
from scripts.folder_ops import create_folder, list_folders, delete_folder

# 创建文件夹
create_folder(name="工作笔记", parent="/")

# 列出所有文件夹
folders = list_folders()
for folder in folders:
    print(f"{folder['name']} ({folder['count']} 篇笔记)")

# 删除文件夹（需要先清空笔记）
delete_folder(folder_id="folder_12345")
```

### 6. 获取笔记内容

```python
from scripts.note_ops import get_note

# 获取笔记详情（HTML 格式）
note = get_note(note_id="note_12345")
print(f"标题: {note['title']}")
print(f"内容: {note['content']}")

# 获取 Markdown 格式（如果支持）
note_md = get_note(note_id="note_12345", format="markdown")
print(note_md['content'])
```

## 错误处理和重试策略

### 重试机制

脚本实现了自动重试机制，适用于以下情况：

**需要重试的错误**：
- 网络超时（Timeout）
- 连接错误（ConnectionError）
- 服务器错误（500, 502, 503, 504）

**不需要重试的错误**：
- 认证失败（401）→ 需要重新登录
- 权限不足（403）→ 需要检查权限
- 资源不存在（404）→ 检查 ID 是否正确
- 参数错误（400）→ 检查请求参数

**重试配置**：
```python
# 默认配置
MAX_RETRIES = 3          # 最大重试次数
RETRY_DELAY = 1          # 初始延迟（秒）
RETRY_BACKOFF = 2        # 延迟倍数（指数退避）
```

### 错误处理示例

```python
from scripts.wiznote_api import WizNoteAPI
from requests.exceptions import ConnectionError, Timeout

api = WizNoteAPI()

try:
    token = api.login(password="your_password")
except ConnectionError:
    print("❌ 无法连接到为知笔记服务器，请检查网络和 WIZ_ENDPOINT 配置")
except Timeout:
    print("❌ 连接超时，请检查服务器状态")
except ValueError as e:
    print(f"❌ 认证失败: {e}")
except Exception as e:
    print(f"❌ 未知错误: {e}")
```

### 环境变量缺失提示

```python
import os

required_vars = ['WIZ_ENDPOINT', 'WIZ_USER']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
    print("请设置以下环境变量：")
    print("  export WIZ_ENDPOINT='http://your-server:9269'")
    print("  export WIZ_USER='your_username'")
    print("  export WIZ_TOKEN='your_token'  # 可选，或通过密码登录获取")
    exit(1)
```

### API 不可达降级策略

当 API 不可达时，脚本会：
1. 尝试重试 3 次（指数退避）
2. 如果仍然失败，抛出明确的错误信息
3. 记录错误日志到文件（`wiznote_error.log`）
4. 返回友好的错误提示，而非原始异常

```python
def _request_with_fallback(self, method: str, api: str, data: Dict = None):
    """带降级策略的请求方法"""
    for attempt in range(self.max_retries):
        try:
            response = self.session.request(method, f"{self.endpoint}{api}", 
                                           json=data, headers=self.headers, 
                                           timeout=10)
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            if attempt < self.max_retries - 1:
                time.sleep(self.retry_delay * (2 ** attempt))
                continue
            else:
                # 降级：记录错误并返回友好提示
                self._log_error(f"API 不可达: {self.endpoint}{api}")
                return {
                    "error": "API_UNREACHABLE",
                    "message": f"无法连接到为知笔记服务器 ({self.endpoint})",
                    "suggestion": "请检查网络连接和 WIZ_ENDPOINT 配置"
                }
```

## 日志记录

所有脚本都会记录操作日志到 `wiznote.log` 文件：

```
2026-03-26 11:43:00 INFO  登录成功，用户: admin
2026-03-26 11:43:05 INFO  创建笔记成功，ID: note_12345
2026-03-26 11:43:10 ERROR 搜索失败: 网络超时
2026-03-26 11:43:15 WARN  Token 即将过期，建议重新登录
```

## 脚本说明

### scripts/wiznote_api.py

核心 API 封装类，提供：
- `WizNoteAPI` 类：认证 + 请求封装
- `login(password)` - 密码登录获取 token
- `_request(method, api, data)` - 统一请求方法（含重试）

### scripts/note_ops.py

笔记操作模块，提供：
- `create_note(title, content, folder, tags)` - 创建笔记
- `get_note(note_id, format)` - 获取笔记内容
- `update_note(note_id, **kwargs)` - 更新笔记
- `delete_note(note_id)` - 删除笔记

### scripts/folder_ops.py

文件夹管理模块，提供：
- `create_folder(name, parent)` - 创建文件夹
- `list_folders()` - 列出所有文件夹
- `delete_folder(folder_id)` - 删除文件夹
- `move_note(note_id, target_folder)` - 移动笔记

### scripts/search.py

搜索功能模块，提供：
- `search_notes(keyword, tag, folder)` - 搜索笔记
- `search_by_tag(tag)` - 按标签搜索
- `search_by_keyword(keyword)` - 按关键词搜索

## 最佳实践

### 1. Token 管理

```python
# 推荐：登录后保存 token 到环境变量或配置文件
api = WizNoteAPI()
token = api.login(password="your_password")

# 保存到环境变量（当前会话）
os.environ['WIZ_TOKEN'] = token

# 或保存到配置文件
with open('.wiz_token', 'w') as f:
    f.write(token)
```

### 2. 批量操作

```python
# 批量创建笔记时，复用 API 实例
api = WizNoteAPI()

notes_data = [
    {"title": "笔记1", "content": "内容1"},
    {"title": "笔记2", "content": "内容2"},
]

for note_data in notes_data:
    create_note(**note_data)
    time.sleep(0.5)  # 避免请求过快
```

### 3. 错误处理

```python
# 始终使用 try-except 包裹 API 调用
try:
    result = create_note(title="测试", content="内容")
except Exception as e:
    print(f"操作失败: {e}")
    # 记录日志或发送通知
```

## 故障排查

### 常见问题

**Q1: 提示 "无法连接到为知笔记服务器"**
- 检查 `WIZ_ENDPOINT` 是否正确
- 检查端口是否开放（80 或 9269）
- 使用 `curl` 测试连通性：`curl http://your-server:9269/api/user/info`

**Q2: 提示 "认证失败" (401)**
- 检查 `WIZ_USER` 和密码是否正确
- Token 可能已过期，尝试重新登录
- 检查 token 是否正确设置在 header 中

**Q3: 搜索结果为空**
- 检查搜索关键词是否正确
- 确认笔记确实存在
- 检查是否有权限访问该笔记

**Q4: 创建笔记失败**
- 检查文件夹路径是否存在
- 检查内容格式（HTML 或 Markdown）
- 查看错误日志 `wiznote.log`

## 参考资源

- [为知笔记官网](https://www.wiz.cn/)
- [为知笔记 GitHub](https://github.com/WizTeam)
- 私有化部署文档：请联系为知笔记官方获取

## 版本历史

- **v1.0.0** (2026-03-26)
  - 初始版本
  - 支持认证、笔记 CRUD、文件夹管理、搜索功能
  - 完整的错误处理和重试机制
