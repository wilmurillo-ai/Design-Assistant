# 根目录文件归类建议

## 📁 当前根目录文件

### 配置文件 (建议保留在根目录)
- ✅ `.env` - 环境变量 (保留)
- ✅ `.env.example` - 环境变量示例 (保留)
- ✅ `.eslintignore` - ESLint 忽略规则 (保留)
- ✅ `.eslintrc.js` - ESLint 配置 (保留)
- ✅ `.gitignore` - Git 忽略规则 (保留)
- ✅ `.prettierignore` - Prettier 忽略规则 (保留)
- ✅ `.prettierrc` - Prettier 配置 (保留)
- ✅ `commitlint.config.js` - Commitlint 配置 (保留)
- ✅ `jest.config.js` - Jest 测试配置 (保留)
- ✅ `nyc.config.js` - NYC 覆盖率配置 (保留)
- ✅ `package.json` - 项目配置 (保留)
- ✅ `package-lock.json` - 依赖锁定 (保留)
- ✅ `LICENSE` - 许可证 (保留)

### 文档文件 (建议移动到 docs/)
- 🔄 `CONFIG.md` → `docs/CONFIG.md`
- 🔄 `CONFIG_UPDATE_REPORT.md` → `docs/CONFIG_UPDATE_REPORT.md`
- 🔄 `DATABASE_MERGED.md` → `docs/DATABASE_MERGED.md`
- 🔄 `DATABASE_MIGRATION.md` → `docs/DATABASE_MIGRATION.md`
- 🔄 `DEPENDENCIES.md` → `docs/DEPENDENCIES.md`
- 🔄 `DIRECTORY_STRUCTURE_BY_SKILL.md` → `docs/DIRECTORY_STRUCTURE_BY_SKILL.md`
- 🔄 `DOCUMENTATION_UPDATE.md` → `docs/DOCUMENTATION_UPDATE.md`
- 🔄 `FULL_DIRECTORY_STRUCTURE.md` → `docs/FULL_DIRECTORY_STRUCTURE.md`
- 🔄 `GITHUB_PUSH_REPORT.md` → `docs/GITHUB_PUSH_REPORT.md`
- 🔄 `MISSING_FILES.md` → `docs/MISSING_FILES.md`
- 🔄 `PROJECT_STRUCTURE.md` → `docs/PROJECT_STRUCTURE.md`
- 🔄 `README.md` → 保留 (项目主文档)
- 🔄 `SKILL.md` → 保留 (Agent 技能说明)

### 测试文件 (建议移动到 src/tests/)
- 🔄 `test-config.js` → `src/tests/test-config.js`
- 🔄 `test-database-config.js` → `src/tests/test-database-config.js`
- 🔄 `test-full.js` → `src/tests/test-full.js`
- 🔄 `test-integration.js` → `src/tests/test-integration.js`

---

## 📋 归类建议

### 1️⃣ **保留在根目录** (13 个文件)

这些是项目配置文件，应该保留在根目录：

| 文件 | 用途 |
|------|------|
| `.env` | 环境变量 |
| `.env.example` | 环境变量示例 |
| `.eslintignore` | ESLint 忽略规则 |
| `.eslintrc.js` | ESLint 配置 |
| `.gitignore` | Git 忽略规则 |
| `.prettierignore` | Prettier 忽略规则 |
| `.prettierrc` | Prettier 配置 |
| `commitlint.config.js` | Commitlint 配置 |
| `jest.config.js` | Jest 测试配置 |
| `nyc.config.js` | NYC 覆盖率配置 |
| `package.json` | 项目配置 |
| `package-lock.json` | 依赖锁定 |
| `LICENSE` | 许可证 |

**建议**: ✅ 全部保留

---

### 2️⃣ **移动到 docs/** (12 个文件)

这些是项目文档和报告，应该移动到 `docs/` 目录：

| 文件 | 目标路径 |
|------|----------|
| `CONFIG.md` | `docs/CONFIG.md` |
| `CONFIG_UPDATE_REPORT.md` | `docs/CONFIG_UPDATE_REPORT.md` |
| `DATABASE_MERGED.md` | `docs/DATABASE_MERGED.md` |
| `DATABASE_MIGRATION.md` | `docs/DATABASE_MIGRATION.md` |
| `DEPENDENCIES.md` | `docs/DEPENDENCIES.md` |
| `DIRECTORY_STRUCTURE_BY_SKILL.md` | `docs/DIRECTORY_STRUCTURE_BY_SKILL.md` |
| `DOCUMENTATION_UPDATE.md` | `docs/DOCUMENTATION_UPDATE.md` |
| `FULL_DIRECTORY_STRUCTURE.md` | `docs/FULL_DIRECTORY_STRUCTURE.md`
| `GITHUB_PUSH_REPORT.md` | `docs/GITHUB_PUSH_REPORT.md` |
| `MISSING_FILES.md` | `docs/MISSING_FILES.md` |
| `PROJECT_STRUCTURE.md` | `docs/PROJECT_STRUCTURE.md` |

**建议**: 🔄 移动到 docs/

**例外**:
- `README.md` - 保留 (项目主文档)
- `SKILL.md` - 保留 (Agent 技能说明)

---

### 3️⃣ **移动到 src/tests/** (4 个文件)

这些是测试文件，应该移动到 `src/tests/` 目录：

| 文件 | 目标路径 |
|------|----------|
| `test-config.js` | `src/tests/test-config.js` |
| `test-database-config.js` | `src/tests/test-database-config.js` |
| `test-full.js` | `src/tests/test-full.js` |
| `test-integration.js` | `src/tests/test-integration.js` |

**建议**: 🔄 移动到 src/tests/

---

## 🚀 执行计划

### 步骤 1: 移动文档文件到 docs/

```bash
# 移动文档文件
mv CONFIG.md docs/
mv CONFIG_UPDATE_REPORT.md docs/
mv DATABASE_MERGED.md docs/
mv DATABASE_MIGRATION.md docs/
mv DEPENDENCIES.md docs/
mv DIRECTORY_STRUCTURE_BY_SKILL.md docs/
mv DOCUMENTATION_UPDATE.md docs/
mv FULL_DIRECTORY_STRUCTURE.md docs/
mv GITHUB_PUSH_REPORT.md docs/
mv MISSING_FILES.md docs/
mv PROJECT_STRUCTURE.md docs/
```

### 步骤 2: 移动测试文件到 src/tests/

```bash
# 移动测试文件
mv test-config.js src/tests/
mv test-database-config.js src/tests/
mv test-full.js src/tests/
mv test-integration.js src/tests/
```

### 步骤 3: 更新 .gitignore

确保 `.gitignore` 包含以下内容：

```gitignore
# 依赖
node_modules/

# 测试覆盖率
coverage/
.nyc_output/

# Jest 缓存
.jest_cache/

# 数据库文件
*.db
*.sqlite

# 日志
*.log

# 临时文件
*.tmp
*.temp

# IDE
.vscode/
.idea/
*.swp
*.swo

# 环境
.env.local
.env.*.local
```

---

## ✅ 归类后根目录文件

归类后，根目录将只保留以下文件：

```
/workspace/gitwork/
├── .env
├── .env.example
├── .eslintignore
├── .eslintrc.js
├── .gitignore
├── .prettierignore
├── .prettierrc
├── commitlint.config.js
├── jest.config.js
├── nyc.config.js
├── package.json
├── package-lock.json
├── LICENSE
├── README.md
├── SKILL.md
├── config/
├── docs/
├── memory/
├── references/
├── scripts/
└── src/
```

**总计**: 15 个文件 + 6 个目录

---

## 📊 归类统计

| 分类 | 文件数 | 说明 |
|------|--|------|
| **保留在根目录** | 15 | 配置文件和主文档 |
| **移动到 docs/** | 11 | 项目文档和报告 |
| **移动到 src/tests/** | 4 | 测试文件 |
| **总计** | 30 | 所有根目录文件 |

---

**报告生成时间**: 2026-03-27 11:05 GMT+8  
**报告状态**: ✅ 归类建议已生成  
**下一步**: 确认是否执行文件移动
