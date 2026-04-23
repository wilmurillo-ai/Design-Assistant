# Quality Gate 质量门禁检查表

> **版本**：v1.0.0
> **依据**：CTO-001 MLOOps 生命周期质量门禁标准

---

## 质量门禁总览

| 门禁编号 | 名称 | 通过标准 | 责任人 |
|---------|------|---------|--------|
| **G0** | 文件结构 | 目录结构符合规范 | 开发者 |
| **G1** | Frontmatter | YAML 格式正确，必需字段齐全 | 开发者 |
| **G2** | 描述质量 | description > 50字，含触发关键词 | 开发者 |
| **G3** | 安全扫描 | CISO 审查通过（CVSS < 7.0）| CISO |
| **G4** | 文档完整性 | 无悬空引用，references 有链接 | 开发者 |
| **G5** | 脚本测试 | 所有脚本可执行，零报错 | 开发者 |
| **G6** | 文档长度 | SKILL.md < 500行 | 开发者 |
| **G7** | 禁止文件 | 无 README.md/CHANGELOG.md | 开发者 |

---

## G0 — 文件结构检查

```markdown
检查清单：
- [ ] 根目录有且仅有 SKILL.md（必需）
- [ ] scripts/ 目录存在（可选，但如存在则需有效文件）
- [ ] references/ 目录存在（可选，但如存在则需有效文件）
- [ ] assets/ 目录存在（可选，但如存在则需有效文件）
- [ ] 无 README.md（禁止）
- [ ] 无 CHANGELOG.md（禁止）
- [ ] 无 INSTALLATION_GUIDE.md（禁止）
- [ ] 目录深度 ≤ 2 层
```

**通过标准**：全部 ✅

---

## G1 — Frontmatter 检查

```yaml
必需字段：
- [ ] name:        非空，英文小写+连字符
- [ ] version:     符合 semver（X.Y.Z）
- [ ] description: 非空，> 50字
- [ ] metadata.openclaw.emoji: 存在，非空
- [ ] metadata.openclaw.os:   存在，数组格式

可选字段（建议有）：
- [ ] metadata.openclaw.compatibility
```

**验证命令**：
```bash
# 手动检查 YAML 语法
# 解析 YAML 并验证字段
```

**通过标准**：name + version + description + emoji 全部存在且格式正确

---

## G2 — 描述质量检查

| 检查项 | 标准 | 示例 |
|--------|------|------|
| 字数 | > 50字 | 描述完整说明触发时机 |
| 触发关键词 | 包含 | "当用户说...时触发" |
| 功能说明 | 包含 | "执行...操作" |
| 文件格式 | 提及（如适用） | ".xlsx 文件" |

**自检问题**：
1. 描述能否让人不看 SKILL.md 就能判断是否需要激活此 Skill？
2. 触发关键词是否包含用户可能说的话？

---

## G3 — 安全扫描（详见 security-review.md）

> ⚠️ **CISO 审查是强制门禁**，必须通过后才能进入 G4

```markdown
- [ ] 无 RED FLAGS（STRIDE 六项全 PASS）
- [ ] CVSS 评分 < 7.0
- [ ] 权限范围最小化
- [ ] 无硬编码密钥
- [ ] 依赖无已知高危 CVE
```

---

## G4 — 文档完整性检查

```markdown
- [ ] SKILL.md 中引用的文件路径均存在
- [ ] references/ 中每个文件在 SKILL.md 中有链接说明
- [ ] 无悬空的 <!-- TODO --> 注释
- [ ] 代码示例有注释说明用途
- [ ] 错误处理有说明
```

---

## G5 — 脚本测试检查

**测试原则**：实际运行，不仅仅是静态审查

```bash
# 对每个脚本执行：
# 1. 语法检查（python -m py_compile 或 node --check）
# 2. 导入检查（验证依赖可导入）
# 3. dry-run 测试（传入无效参数，验证错误处理）
```

**测试报告模板**：
```markdown
## 脚本测试报告

脚本：<name>
测试时间：<ISO date>
测试者：<name>

| 测试用例 | 输入 | 预期输出 | 实际输出 | 结果 |
|---------|------|---------|---------|------|
| 正常路径 | valid input | expected | actual | ✅/❌ |
| 错误路径 | invalid input | error msg | actual | ✅/❌ |
| 边界条件 | empty input | graceful | actual | ✅/❌ |

总体结果：[✅ PASS / ❌ FAIL]
```

**通过标准**：所有测试用例通过（✅），无未处理异常

---

## G6 — SKILL.md 长度检查

```bash
# 统计非空行数
wc -l SKILL.md   # 应 < 500 行

# 建议：详细文档移到 references/
```

**通过标准**：非空行数 < 500

---

## G7 — 禁止文件检查

```bash
# 检查是否存在禁止文件
ls -la *.md | grep -v SKILL.md
```

**禁止文件列表**：
- README.md
- CHANGELOG.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CONTRIBUTING.md
- LICENSE（除非是 skill 许可声明）

---

## 最终检查清单

```markdown
## 最终发布前检查

### 必选（全部 ✅ 才可发布）
- [ ] G0 文件结构 ✅
- [ ] G1 Frontmatter ✅
- [ ] G2 描述质量 ✅
- [ ] G3 安全扫描 ✅（CISO 签字）
- [ ] G4 文档完整性 ✅
- [ ] G5 脚本测试 ✅
- [ ] G6 SKILL.md 长度 ✅
- [ ] G7 禁止文件 ✅

### 可选（建议完成）
- [ ] 版本号已更新
- [ ] changelog 记录（如适用）
- [ ] 发布前在本地测试过触发场景

### 发布准备
- [ ] .skill 包已生成
- [ ] ClawHub slug 唯一性已确认
- [ ] 权限清单已记录
```

---

## 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-13 | 初始版本 |
