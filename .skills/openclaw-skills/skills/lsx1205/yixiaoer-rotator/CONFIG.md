# 配置说明

## 环境变量

本技能需要从环境变量获取蚁小二 API Key。

### 设置方式

#### 方式一：临时设置（当前终端会话有效）

```bash
export YIXIAOER_API_KEY="你的 API Key"
node account-rotator.js sync
```

#### 方式二：永久设置（推荐）

添加到 `~/.bashrc` 或 `~/.profile`：

```bash
echo 'export YIXIAOER_API_KEY="你的 API Key"' >> ~/.bashrc
source ~/.bashrc
```

#### 方式三：使用 .env 文件

1. 复制示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API Key：
```
YIXIAOER_API_KEY=你的 API Key
```

3. 加载环境变量：
```bash
export $(cat .env | xargs)
node account-rotator.js sync
```

---

## 获取 API Key

1. 登录蚁小二后台：https://www.yixiaoer.cn
2. 进入 **设置** → **API 管理**（或 **团队管理** → **成员管理**）
3. 找到你的成员账号，复制或生成 API Key

> 💡 **说明**：API Key 是按成员生成的，系统会自动关联到你的成员身份，**不需要额外配置成员 ID**。

---

## 验证配置

```bash
# 检查环境变量是否设置
echo $YIXIAOER_API_KEY

# 测试同步
node account-rotator.js sync
```

如果输出账号列表，说明配置成功。

---

## 安全提示

- ⚠️ **不要将 `.env` 文件提交到 Git**（已添加到 `.gitignore`）
- ⚠️ **不要将 API Key 泄露给他人**
- ⚠️ **仅使用蚁小二官方 API Key**，不使用来源不明的密钥
- 🔒 API Key 通过环境变量传递，不硬编码在代码中
- 🔒 API Key 通过 `execSync` 的 `env` 选项传递，避免 shell 注入风险
- 🔍 建议安装前查看源码（`account-rotator.js` 和 `yixiaoer-skill/scripts/api.ts`）

## 安全架构

```
┌─────────────────────────────────────┐
│  account-rotator.js                 │
│  - 读取环境变量 YIXIAOER_API_KEY    │
│  - 通过 env 选项传递给子进程        │
│  - 临时文件使用后立即删除           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  yixiaoer-skill/scripts/api.ts      │
│  - 从环境变量读取 API Key           │
│  - 调用蚁小二官方 API               │
│  - 返回账号数据                     │
└─────────────────────────────────────┘
```

**安全特性：**
- ✅ API Key 不通过命令行参数传递
- ✅ API Key 不嵌入 shell 字符串
- ✅ 临时文件使用后立即删除
- ✅ 状态文件不含敏感凭据
