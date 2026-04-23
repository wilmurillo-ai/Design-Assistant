# 发布指南

## 发布到 ClawHub

### 1. 更新版本号

编辑 `package.json`：
```json
{
  "version": "1.1.0"  // 递增版本号
}
```

### 2. 更新更新日志

编辑 `CHANGELOG.md`，添加新版本的更新内容。

### 3. 提交到 Git

```bash
git add .
git commit -m "chore: release v1.1.0"
git tag v1.1.0
git push origin main --tags
```

### 4. 发布到 ClawHub

```bash
npx clawhub@latest publish
```

### 5. 验证发布

```bash
# 查看技能信息
clawhub inspect weixin-send-media

# 查看版本历史
clawhub inspect weixin-send-media --versions

# 搜索技能
clawhub search weixin-send-media
```

---

## 手动发布（备用）

如果自动发布失败：

```bash
# 1. 打包
tar -czf weixin-send-media-1.1.0.tar.gz \
  SKILL.md README.md CHANGELOG.md \
  scripts/ patches/ references/ tests/

# 2. 上传到 ClawHub 网站
# https://clawhub.com/publish
```

---

## 发布清单

发布前检查：

- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] 所有文件都已提交
- [ ] 测试脚本通过
- [ ] 文档中的示例代码已验证
- [ ] 许可证文件存在

---

## 版本规范

遵循语义化版本（SemVer）：

- **MAJOR.MINOR.PATCH** (如：1.1.0)
- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的问题修复

### 示例

- `1.0.0` → `1.0.1` : 修复 bug
- `1.0.0` → `1.1.0` : 新增功能
- `1.0.0` → `2.0.0` : 不兼容变更
