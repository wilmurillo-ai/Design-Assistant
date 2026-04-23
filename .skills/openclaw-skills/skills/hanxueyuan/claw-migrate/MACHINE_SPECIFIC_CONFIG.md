# 机器特定配置迁移设计

**问题**：OpenClaw 有些配置是与**特定机器/环境**绑定的，不能简单覆盖。

**解决方案**：区分"通用配置"和"机器特定配置"，采用不同的迁移策略。

---

## 📋 配置分类

### 1. 机器特定配置（保留本地）

这些配置与当前机器的环境、认证、pairing 相关，**不应该被覆盖**：

| 文件/路径 | 说明 | 迁移策略 |
|----------|------|---------|
| `feishu/dedup/*.json` | 飞书消息去重 ID | ❌ 保留本地 |
| `feishu/pairing/*.json` | 飞书 pairing 信息 | ❌ 保留本地 |
| `telegram/sessions/*.json` | Telegram 会话 | ❌ 保留本地 |
| `discord/pairing/*.json` | Discord pairing | ❌ 保留本地 |
| `openclaw.json` 中的 `browser.executablePath` | 浏览器路径 | ❌ 保留本地 |
| `openclaw.json` 中的 `channel.*.pairing` | Channel pairing | ❌ 保留本地 |
| `.env` | 环境变量（API keys） | ❌ 保留本地 |
| `*.log` | 日志文件 | ❌ 不迁移 |
| `sessions/*.jsonl` | 会话数据 | ❌ 不迁移 |

### 2. 通用配置（可以覆盖）

这些配置是业务逻辑相关，**可以从远端同步**：

| 文件/路径 | 说明 | 迁移策略 |
|----------|------|---------|
| `AGENTS.md` | Agent 配置 | ✅ 智能合并 |
| `SOUL.md` | 角色定义 | ✅ 智能合并 |
| `USER.md` | 用户信息 | ✅ 智能合并 |
| `TOOLS.md` | 工具配置 | ✅ 智能合并 |
| `HEARTBEAT.md` | 定时任务 | ✅ 智能合并 |
| `skills/**/SKILL.md` | 技能定义 | ✅ 增量同步 |
| `MEMORY.md` | 记忆 | ✅ 合并 |
| `.learnings/*.md` | 学习记录 | ✅ 追加 |
| `IDENTITY.md` | 身份定义 | ✅ 覆盖 |

### 3. 混合配置（部分覆盖）

`openclaw.json` 需要**字段级**的精细控制：

```json
{
  // ✅ 可以覆盖的配置（通用）
  "models": {},           // 模型配置
  "skills": {},           // 技能开关
  "gateway": {},          // Gateway 配置
  "agents": {},           // Agent 配置
  
  // ❌ 保留本地的配置（机器特定）
  "browser.executablePath": "保留本地",
  "channel.feishu.pairing": "保留本地",
  "channel.telegram.pairing": "保留本地",
  "channel.*.auth": "保留本地"
}
```

---

## 🔧 迁移策略设计

### 策略 1：文件级过滤

```javascript
// 不迁移的文件（机器特定）
const MACHINE_SPECIFIC_FILES = [
  'feishu/dedup/*.json',
  'feishu/pairing/*.json',
  'telegram/sessions/*.json',
  'discord/pairing/*.json',
  '.env',
  '*.log',
  'sessions/*.jsonl'
];

// 迁移策略
const MIGRATION_STRATEGY = {
  // 跳过：本地已有则不迁移
  SKIP: MACHINE_SPECIFIC_FILES,
  
  // 合并：智能合并
  MERGE: ['MEMORY.md', '.learnings/*.md'],
  
  // 覆盖：直接用远端内容
  OVERWRITE: ['AGENTS.md', 'SOUL.md', 'USER.md', ...],
  
  // 字段级合并：openclaw.json 特殊处理
  FIELD_MERGE: ['openclaw.json']
};
```

### 策略 2：openclaw.json 字段级合并

```javascript
// openclaw.json 字段分类
const OPENCLAW_JSON_FIELDS = {
  // 可以覆盖的字段
  overwrite: [
    'models',
    'skills',
    'gateway',
    'agents.defaults',
    'browser.headless',
    'browser.noSandbox'
  ],
  
  // 保留本地的字段
  keepLocal: [
    'browser.executablePath',
    'browser.defaultProfile',
    'channel.*.pairing',
    'channel.*.auth',
    'channel.*.sessionId'
  ]
};

// 合并逻辑
function mergeOpenClawConfig(local, remote) {
  const result = { ...local };  // 以本地为基础
  
  // 覆盖可覆盖的字段
  for (const field of OPENCLAW_JSON_FIELDS.overwrite) {
    if (remote[field] !== undefined) {
      result[field] = remote[field];
    }
  }
  
  // 保留本地字段（不处理，已经在 result 中）
  
  return result;
}
```

### 策略 3：Pairing 信息特殊处理

```javascript
// Pairing 信息迁移策略
class PairingHandler {
  // 检测当前机器的 pairing 状态
  async checkPairingStatus() {
    const pairingFiles = [
      'feishu/pairing/*.json',
      'telegram/sessions/*.json'
    ];
    
    const hasPairing = pairingFiles.some(pattern => {
      return globSync(pattern).length > 0;
    });
    
    return {
      isPaired: hasPairing,
      files: pairingFiles.flatMap(p => globSync(p))
    };
  }
  
  // 迁移时保留 pairing
  async migrateWithPairingPreserve(options) {
    const status = await this.checkPairingStatus();
    
    if (status.isPaired) {
      console.log('⚠️  检测到当前机器已配对，保留 pairing 配置...');
      console.log('   仅迁移通用配置，不覆盖 pairing 信息');
      
      // 跳过 pairing 相关文件
      options.exclude = [
        ...(options.exclude || []),
        ...status.files
      ];
    }
    
    return await this.migrate(options);
  }
  
  // 迁移后提示
  async postMigrateNotice() {
    const status = await this.checkPairingStatus();
    
    if (!status.isPaired) {
      console.log('\n📌 后续步骤:');
      console.log('   • 当前机器未配对，需要重新配置 Channel');
      console.log('   • 运行 openclaw configure 完成配对');
    } else {
      console.log('\n✅ Pairing 配置已保留，Channel 可正常使用');
    }
  }
}
```

---

## 📝 用户交互设计

### 场景 1：已配对机器 → 新机器

```
用户：迁移配置到新机器

claw-migrate:
📋 检测到当前机器已配对 Feishu
   • 配对状态：✅ 已配对
   • 配对文件：feishu/pairing/default.json

❓ 迁移策略选择：
   1. 仅迁移通用配置（推荐）- 保留当前 pairing
   2. 完整迁移（覆盖 pairing）- 需要重新配对
   3. 取消

用户选择：1

claw-migrate:
✅ 已选择"仅迁移通用配置"
   • 将迁移：AGENTS.md, SOUL.md, skills/, ...
   • 将跳过：feishu/pairing/, .env, sessions/
   
   迁移完成后，新机器需要：
   1. 配置 Feishu pairing
   2. 验证 API keys
```

### 场景 2：新机器 → 已配对机器

```
用户：从 GitHub 拉取配置

claw-migrate:
📋 检测到当前机器已配对 Feishu
   • 配对状态：✅ 已配对

✅ 自动保留 pairing 配置
   • 远端 pairing 文件将跳过
   • 本地 pairing 配置不受影响

迁移完成！
✅ Pairing 配置已保留，Channel 可正常使用
```

---

## 🔒 安全增强

### 敏感信息检测

```javascript
// 迁移前扫描敏感信息
function scanSensitiveInfo(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  
  const patterns = [
    /ghp_[a-zA-Z0-9]{36}/,  // GitHub Token
    /sk-[a-zA-Z0-9]{48}/,   // OpenAI Key
    /Bearer [a-zA-Z0-9\-_]+/, // Bearer Token
    /password\s*[:=]\s*\S+/  // 密码
  ];
  
  const findings = [];
  for (const pattern of patterns) {
    const matches = content.match(pattern);
    if (matches) {
      findings.push({
        file: filePath,
        type: 'sensitive_data',
        pattern: pattern.toString()
      });
    }
  }
  
  return findings;
}

// 迁移前提示
const sensitiveFiles = scanSensitiveInfo('openclaw.json');
if (sensitiveFiles.length > 0) {
  console.log('⚠️  检测到敏感信息:');
  sensitiveFiles.forEach(f => console.log(`   • ${f.file}`));
  console.log('   建议：使用环境变量替代硬编码密钥');
}
```

---

## 📊 迁移流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 检测本地状态                                             │
│     • 检查 pairing 状态                                      │
│     • 检查敏感文件                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 用户确认迁移策略                                         │
│     • 仅通用配置（推荐）                                     │
│     • 完整迁移（覆盖 pairing）                               │
│     • 自定义选择                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 执行迁移                                                 │
│     • 跳过机器特定文件                                       │
│     • 合并通用配置                                           │
│     • 字段级处理 openclaw.json                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  4. 迁移后验证                                               │
│     • 检查 pairing 状态                                      │
│     • 提示后续步骤                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ 实现清单

### P0: 核心功能

- [ ] 定义 `MACHINE_SPECIFIC_FILES` 列表
- [ ] 实现 `openclaw.json` 字段级合并
- [ ] 实现 pairing 状态检测
- [ ] 添加迁移策略选择交互

### P1: 增强功能

- [ ] 敏感信息扫描
- [ ] 迁移前预览（显示将跳过哪些文件）
- [ ] 迁移后验证报告

### P2: 文档

- [ ] 更新 README.md
- [ ] 添加配置迁移指南
- [ ] 编写故障排除文档

---

**设计状态**: 待实现  
**预计版本**: v2.1.0
