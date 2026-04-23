---
name: yixiaoer-rotator
version: 2.0.0
description: "蚁小二账号轮询管理器 - 多账号矩阵自动轮询发布，支持按平台独立维护索引、状态持久化"
author: lsx1205
---

# yixiaoer-rotator - 账号轮询 Skill

## 功能说明

本 Skill 用于管理蚁小二多账号矩阵的**自动轮询发布**，解决以下问题：

- ❌ 忘记上次用哪个账号发布了
- ❌ 多个平台各自维护索引很麻烦
- ❌ 发布时手动选账号容易出错

## 核心能力

| 功能 | 说明 |
|------|------|
| **自动同步账号** | 从蚁小二 API 获取所有已绑定账号 |
| **按平台独立轮询** | 哔哩哔哩、头条号、百家号等各自维护索引 |
| **状态持久化** | JSON 文件记录，重启不丢失 |
| **CLI 命令** | 方便的命令行工具，可集成到发布流程 |

## 安装

```bash
cd /root/.openclaw/workspace/skills/yixiaoer-rotator
npm install  # 本技能无外部依赖
```

## 配置

### 环境变量

**两个环境变量都是必需的：**

```bash
export YIXIAOER_API_KEY="你的蚁小二 API Key"
export YIXIAOER_MEMBER_ID="你的成员 ID"
```

> ⚠️ **重要**：请先设置环境变量再使用，API Key 和成员 ID 需要从蚁小二后台获取。

### 如何获取 API Key 和 成员 ID

1. 登录蚁小二后台：https://www.yixiaoer.cn
2. 进入 **团队管理** → **成员管理**
3. 找到你的成员账号
4. 复制 **成员 ID**（如：`69xxxxxxxxxxxxxxxxxxxxxx`）
5. 生成或复制 **API Key**

> 💡 **说明**：必须同时配置 API Key 和 成员 ID，系统会同步该成员有运营权限的所有账号。

---

### 配置示例

```bash
export YIXIAOER_API_KEY="你的蚁小二 API Key"
export YIXIAOER_MEMBER_ID="你的成员 ID"

node account-rotator.js sync
# 同步该成员有运营权限的账号
```

### 依赖

本技能依赖 `yixiaoer-skill`，请确保已安装：
```bash
clawhub install yixiaoer-skill
clawhub install yixiaoer-rotator
```

---

## 安全说明

### 数据来源

- **yixiaoer-skill**: 蚁小二官方 API 封装，源码公开可审计
  - 仓库：https://github.com/yixiaoer888/yixiaoer-skill
  - 建议：安装前查看源码，确认无恶意代码

### API Key 安全

- ✅ API Key 通过环境变量传递，不硬编码在代码中
- ✅ API Key 通过 `execSync` 的 `env` 选项传递，避免 shell 注入
- ✅ 临时 payload 文件使用后立即删除
- ⚠️ API Key 格式验证：仅允许字母、数字、下划线、连字符

### 状态文件

- **位置**: `account-rotator-state.json`（技能目录下）
- **内容**: 账号列表和轮询索引（不含 API Key）
- **安全**: 可安全存储，不含敏感凭据

### 建议

- 🔒 在隔离环境（容器/虚拟机）中运行，如果不完全信任技能来源
- 🔍 安装前查看 `account-rotator.js` 和 `yixiaoer-skill/scripts/api.ts` 源码
- 🔑 仅使用蚁小二官方 API Key，不使用来源不明的密钥

## 使用

### 1. 同步账号列表（首次使用或定期更新）

```bash
cd /root/.openclaw/workspace/skills/yixiaoer-rotator
node account-rotator.js sync
```

输出示例：
```
正在从蚁小二同步账号列表...
✅ 同步完成！共 23 个账号，分布在 5 个平台

平台分布:
  - 哔哩哔哩：16 个账号
  - 百家号：1 个账号
  - 头条号：1 个账号
  - 网易号：3 个账号
  - 搜狐号：2 个账号
```

### 2. 获取下一个账号（发布前调用）

```bash
node account-rotator.js next 哔哩哔哩
# 输出：69c9e5cd398e5ae930212379
```

**集成到发布流程：**
```bash
# 获取账号 ID
ACCOUNT_ID=$(node account-rotator.js next 哔哩哔哩)

# 使用账号 ID 发布
node scripts/api.ts --payload="{
  \"action\": \"publish\",
  \"publishType\": \"article\",
  \"platforms\": [\"哔哩哔哩\"],
  \"publishArgs\": {
    \"accountForms\": [{
      \"platformAccountId\": \"$ACCOUNT_ID\",
      ...
    }]
  }
}"
```

### 3. 查看轮询状态

```bash
node account-rotator.js status
```

输出示例：
```
最后同步时间：2026/4/1 14:00:00

📱 哔哩哔哩
   账号总数：16
   当前索引：3 (下次使用：4)
   当前账号：账号名称 A
   下次账号：账号名称 B

📱 头条号
   账号总数：1
   当前索引：0 (下次使用：0)
   当前账号：账号名称 C
   下次账号：账号名称 C
```

### 4. 查看所有平台下次发布账号

```bash
node account-rotator.js all
```

### 5. 列出指定平台的所有账号

```bash
node account-rotator.js accounts 哔哩哔哩
```

### 6. 重置索引

```bash
# 重置指定平台
node account-rotator.js reset 哔哩哔哩

# 重置所有平台
node account-rotator.js reset
```

## 状态文件

状态保存在 `account-rotator-state.json`，格式：

```json
{
  "platforms": {
    "哔哩哔哩": {
      "accounts": [
        {"id": "xxx", "name": "账号 A", "platform": "哔哩哔哩", "fansTotal": 100},
        {"id": "yyy", "name": "账号 B", "platform": "哔哩哔哩", "fansTotal": 200}
      ],
      "totalAccounts": 2,
      "currentIndex": 0,
      "accountCount": 2
    }
  },
  "lastUpdated": 1774937104585
}
```

> ⚠️ **不要手动修改状态文件**，使用 `reset` 命令重置索引。

## 与 yixiaoer-skill 配合使用

本 Skill 负责**决定用哪个账号**，`yixiaoer-skill` 负责**真正执行发布**。

典型工作流：

```bash
# 1. 获取下一个账号
ACCOUNT_ID=$(node account-rotator.js next 哔哩哔哩)

# 2. 上传封面图
COVER_RESULT=$(node ../yixiaoer-skill/scripts/api.ts --payload='{
  "action": "upload",
  "url": "https://example.com/cover.jpg"
}')
COVER_KEY=$(echo $COVER_RESULT | jq -r '.key')

# 3. 发布文章
node ../yixiaoer-skill/scripts/api.ts --payload="{
  \"action\": \"publish\",
  \"publishType\": \"article\",
  \"platforms\": [\"哔哩哔哩\"],
  \"publishArgs\": {
    \"accountForms\": [{
      \"platformAccountId\": \"$ACCOUNT_ID\",
      \"coverKey\": \"$COVER_KEY\",
      ...
    }]
  }
}"
```

## 命令参考

| 命令 | 说明 |
|------|------|
| `sync` | 从蚁小二同步账号列表 |
| `next <平台名>` | 获取指定平台的下一个账号（返回账号 ID） |
| `all` | 查看所有平台下次发布的账号 |
| `status` | 查看轮询状态 |
| `platforms` | 列出所有平台 |
| `accounts <平台名>` | 列出指定平台的所有账号 |
| `reset [平台名]` | 重置索引（不指定平台则重置所有） |

## 注意事项

1. **首次使用必须先 sync** - 同步后才能获取账号列表
2. **定期 sync 更新** - 如果蚁小二后台添加了新账号，需要重新 sync
3. **不要手动改状态文件** - 使用 `reset` 命令重置索引
4. **发布成功后再更新索引** - 本脚本在调用 `next` 时立即更新索引，如果发布失败需要手动 `reset`

---

## 更新日志

### v2.0.0
- 重构为独立 Skill，与 yixiaoer-skill 解耦
- 支持按平台独立维护索引
- 添加 CLI 命令，方便集成
- 状态文件结构优化
