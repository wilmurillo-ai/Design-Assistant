# Commit Message 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
{type}({scope}): {description}

[optional body]

[optional footer]
```

## 类型

| Type | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `docs` | 文档更新 |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具/依赖 |

## 示例

```
feat(auth): add JWT token validation

fix(api): handle null response from database

docs(readme): update installation instructions
```
