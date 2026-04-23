# ClawHub 发布指南

> **版本**：v1.0.0
> **依据**：ClawHub CLI 文档

---

## 目录

1. [发布前准备](#1-发布前准备)
2. [打包命令](#2-打包命令)
3. [发布命令](#3-发布命令)
4. [版本管理](#4-版本管理)
5. [常见问题](#5-常见问题)

---

## 1. 发布前准备

### 1.1 检查清单

```markdown
- [ ] Skill 已通过全部 Quality Gate（G0-G7）
- [ ] CISO 安全审查报告已生成
- [ ] 版本号符合 semver 规范（X.Y.Z）
- [ ] description 已完整编写（>50字）
- [ ] 无禁止文件（README.md 等）
- [ ] 所有脚本已测试
```

### 1.2 环境要求

```bash
# 安装 ClawHub CLI（仅发布需要）
npm i -g clawhub

# 验证安装
clawhub --version
```

### 1.3 认证

```bash
# 登录 ClawHub
clawhub login

# 验证身份
clawhub whoami
```

---

## 2. 打包命令

### 2.1 标准打包

```bash
# 打包单个 Skill
clawhub package <path/to/skill-folder>

# 指定输出目录
clawhub package <path/to/skill-folder> --output ./dist

# 打包并指定版本
clawhub package <path/to/skill-folder> --version 1.0.0
```

### 2.2 打包验证

打包脚本自动执行以下验证：
- ✅ YAML frontmatter 格式
- ✅ 必需字段存在（name/version/description）
- ✅ 目录结构正确
- ✅ description 完整性
- ✅ 文件组织

---

## 3. 发布命令

### 3.1 发布到 ClawHub

```bash
# 标准发布
clawhub publish ./<skill-name> \
  --slug <skill-name> \
  --name "<Skill 显示名称>" \
  --version X.Y.Z \
  --changelog "<变更说明>"

# 示例
clawhub publish ./pdf-processor \
  --slug pdf-processor \
  --name "PDF Processor" \
  --version 1.0.0 \
  --changelog "Initial release"
```

### 3.2 发布参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--slug` | ✅ | 唯一标识符（小写+连字符） |
| `--name` | ✅ | 显示名称（可含空格/emoji） |
| `--version` | ✅ | 语义化版本（X.Y.Z）|
| `--changelog` | ✅ | 本次变更说明 |
| `--tag` | ❌ | 标签（stable/beta/alpha）|
| `--registry` | ❌ | 指定仓库地址 |

### 3.3 发布后验证

```bash
# 查看已发布的 Skill
clawhub list

# 检查特定 Skill
clawhub info <skill-name>
```

---

## 4. 版本管理

### 4.1 版本号规范

遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)：

```
主版本.次版本.修订号
MAJOR.MINOR.PATCH

MAJOR：不兼容的 API 变更
MINOR：向后兼容的功能新增
PATCH：向后兼容的缺陷修复
```

### 4.2 版本更新规则

| 变更类型 | 版本升级 | 示例 |
|---------|---------|------|
| 新功能 | MINOR + 1 | 1.0.0 → 1.1.0 |
| Bug 修复 | PATCH + 1 | 1.0.0 → 1.0.1 |
| 不兼容变更 | MAJOR + 1 | 1.0.0 → 2.0.0 |

### 4.3 更新已发布的 Skill

```bash
# 更新到最新版本
clawhub update <skill-name>

# 指定版本
clawhub update <skill-name> --version 1.2.0

# 强制更新
clawhub update <skill-name> --force
```

---

## 5. 常见问题

### 5.1 slug 已被使用

```
Error: Slug '<slug>' is already taken
```

**解决方案**：使用不同的 slug，或检查是否已发布过

### 5.2 版本号冲突

```
Error: Version <version> already exists
```

**解决方案**：更新版本号

### 5.3 未登录

```
Error: Not authenticated
```

**解决方案**：执行 `clawhub login`

### 5.4 打包验证失败

```
Error: Validation failed
```

**解决方案**：检查 G0-G7 质量门禁，确保全部通过

---

## 附录：发布脚本模板

```bash
#!/bin/bash
# publish-skill.sh

SKILL_PATH="./$1"
SKILL_NAME="$1"
VERSION="${2:-1.0.0}"
CHANGELOG="${3:-Initial release}"

echo "Packaging $SKILL_NAME..."
clawhub package "$SKILL_PATH" --output ./dist

echo "Publishing $SKILL_NAME v$VERSION..."
clawhub publish "./dist/$SKILL_NAME.skill" \
  --slug "$SKILL_NAME" \
  --name "$SKILL_NAME" \
  --version "$VERSION" \
  --changelog "$CHANGELOG"

echo "Done!"
```

---

## 附录：Registry 配置

```bash
# 使用默认 ClawHub
clawhub publish ./my-skill ...

# 使用自定义 Registry
clawhub publish ./my-skill \
  --registry https://custom.clawhub.com \
  --slug my-skill \
  --name "My Skill" \
  --version 1.0.0 \
  --changelog "Initial release"

# 或通过环境变量
export CLAWHUB_REGISTRY=https://custom.clawhub.com
clawhub publish ./my-skill ...
```
