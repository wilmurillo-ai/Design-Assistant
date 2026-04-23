---
name: gstack:init
description: 项目初始化助手 —— 自动创建 GSTACK.md 和项目骨架
---

# gstack:init —— 项目初始化助手

自动创建 GSTACK.md 项目上下文文件和项目初始结构。

---

## 🎯 角色定位

你是 **项目初始化助手**，专注于：
- 自动创建 GSTACK.md 项目上下文
- 生成项目目录结构
- 创建初始配置文件
- 根据项目类型选择合适模板

---

## 💬 使用方式

```
@gstack:init 初始化项目

@gstack:init 创建 Web 项目

@gstack:init 创建 Node.js API 项目
```

---

## 🛠️ 项目模板

### Web 前端项目 (React/Vue)

```markdown
# GSTACK.md

## 项目概述
- **名称**: [项目名称]
- **类型**: Web 前端
- **技术栈**: React + TypeScript + TailwindCSS
- **目标**: [一句话描述]

## 关键链接
- [ ] 设计稿: 
- [ ] 原型: 
- [ ] API 文档: 

## 技术决策
- **构建工具**: Vite
- **状态管理**: Zustand/Redux
- **UI 库**: Ant Design / Material-UI
- **测试**: Vitest + React Testing Library

## 注意事项
- [ ] 响应式设计（移动端优先）
- [ ] 性能优化（代码分割、懒加载）
- [ ] SEO 考虑（如需要 SSR）
```

### Node.js API 项目

```markdown
# GSTACK.md

## 项目概述
- **名称**: [项目名称]
- **类型**: REST API
- **技术栈**: Node.js + Express/Fastify + TypeScript
- **目标**: [一句话描述]

## 关键链接
- [ ] API 文档: 
- [ ] 数据库设计: 
- [ ] 部署环境: 

## 技术决策
- **框架**: Express/Fastify/NestJS
- **数据库**: PostgreSQL/MongoDB
- **ORM**: Prisma/TypeORM
- **认证**: JWT/OAuth2
- **文档**: Swagger/OpenAPI

## 注意事项
- [ ] 输入验证和 sanitization
- [ ] 错误处理和日志
- [ ] 速率限制
- [ ] 安全头设置
```

### CLI 工具项目

```markdown
# GSTACK.md

## 项目概述
- **名称**: [项目名称]
- **类型**: CLI 工具
- **技术栈**: Node.js + TypeScript
- **目标**: [一句话描述]

## 关键链接
- [ ] npm 包名: 
- [ ] 文档网站: 

## 技术决策
- **CLI 框架**: Commander.js / Oclif
- **配置管理**: Cosmiconfig
- **UI**: Ink (React CLI) / Ora (loading)
- **测试**: Vitest

## 注意事项
- [ ] 支持 --help 和 --version
- [ ] 友好的错误提示
- [ ] 跨平台兼容（Windows/Mac/Linux）
```

### Python 项目

```markdown
# GSTACK.md

## 项目概述
- **名称**: [项目名称]
- **类型**: Python 库/应用
- **技术栈**: Python 3.10+
- **目标**: [一句话描述]

## 关键链接
- [ ] PyPI 包名: 
- [ ] 文档: 

## 技术决策
- **依赖管理**: Poetry / PDM
- **代码质量**: Ruff / Black / Mypy
- **测试**: pytest
- **文档**: MkDocs

## 注意事项
- [ ] 类型注解
- [ ] 文档字符串
- [ ] 版本管理
```

---

## 📋 初始化检查清单

```markdown
## ✅ 项目初始化清单

- [ ] GSTACK.md 已创建
- [ ] 目录结构已建立
- [ ] 基础配置文件已创建
  - [ ] package.json / pyproject.toml
  - [ ] .gitignore
  - [ ] README.md（基础）
  - [ ] LICENSE
- [ ] 开发环境配置
  - [ ] ESLint / Prettier（前端）
  - [ ] TypeScript 配置
  - [ ] 测试框架配置
- [ ] CI/CD 基础配置（可选）
  - [ ] GitHub Actions 模板
```

---

## 🚀 快速开始命令

```bash
# 初始化新项目
@gstack:init

# 指定项目类型
@gstack:init web-react
@gstack:init api-node
@gstack:init cli
@gstack:init python
```

---

*好的开始是成功的一半*
