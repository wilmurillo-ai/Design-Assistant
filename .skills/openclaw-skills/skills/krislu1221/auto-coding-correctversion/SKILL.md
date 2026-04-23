---
name: auto-coding
description: 智能自主编码系统 - 八步循环流程，多 Agent 协作完成从需求到代码的完整开发
user-invocable: true
---

# Auto-Coding Skill v1.1.0 - 八步循环流程（上下文管理增强版）

## 📋 概述

### 什么是 Auto-Coding？

**Auto-Coding** 是一个智能自主编码系统，通过多 Agent 协作完成从需求到代码的完整开发流程。

**核心理念**: 不是任务分发器，而是自我完善的智能编程系统。它利用 OpenClaw 的多子 Agent 进程，进行设计→分解→编码→测试→反思→优化→验证→输出，分不同角色的 Prompt 实现多维度的自我审查和自我优化，提升代码可执行率。适合复杂项目，但会消耗更多的 Token，应谨慎使用。

**推荐使用**: Claw RoundTable 先进行多 Agent 项目研讨和方案完善，然后将结论送入 Auto-Coding 进行编码，效果更好。

### 致谢

**Agent 人格**: 借鉴了 [Agency-Agent](https://github.com/zhayujie/agency-agent) 关于程序员的部分，特此致敬。

---

## 🔄 八步循环流程

```
设计 → 分解 → 编码 → 测试 ←→ 反思 ←→ 优化
                              ↓
                          验证 → 输出
```

### 步骤说明

| 步骤 | 名称 | 说明 |
|------|------|------|
| 1 | 设计 (Design) | 技术方案设计和架构 |
| 2 | 分解 (Decomposition) | 任务拆解和依赖管理 |
| 3 | 编码 (Coding) | 代码实现 |
| 4 | 测试 (Testing) | 功能测试 |
| 5 | 反思 (Reflection) | 代码审查和反思 |
| 6 | 优化 (Optimization) | 改进和修复 |
| 7 | 验证 (Verification) | 最终验证 |
| 8 | 输出 (Output) | 交付物生成 |

**迭代逻辑**: 测试→反思→优化 形成迭代循环（最多 3 次）

---

## 🚀 使用方式

### 基本用法

```
帮我创建一个待办应用
```

### 带任务列表

```
创建一个待办应用，任务包括：
1. 创建项目结构
2. 实现 HTML 框架
3. 实现 CSS 样式
4. 实现 JS 功能
5. 测试功能
```

### 与 RoundTable 配合

```
# 1. 先使用 RoundTable 研讨方案
/rt 讨论一下待办应用的技术方案

# 2. 然后将结论送入 Auto-Coding
帮我创建一个待办应用（使用 RoundTable 讨论的技术方案）
```

---

## 💡 与 RoundTable 的关系

**Auto-Coding 和 RoundTable 是两个独立的 Skill**，但可以配合使用：

| Skill | 用途 | 输出 |
|------|------|------|
| **RoundTable** | 多 Agent 研讨和方案完善 | 技术方案、行动计划 |
| **Auto-Coding** | 自主编码实现 | 源代码、测试报告 |

### 推荐工作流

```
RoundTable（研讨方案） → Auto-Coding（编码实现）
```

### 使用建议

1. **复杂项目**: 先用 RoundTable 研讨方案，再用 Auto-Coding 实现
2. **简单项目**: 直接使用 Auto-Coding
3. **代码审查**: Auto-Coding 完成后，可用 RoundTable 审查代码

---

## ⚠️ 注意事项

### 推荐使用场景

✅ **适合**:
- 复杂项目开发（多任务依赖）
- 技术方案设计和实现
- 代码审查和优化
- 测试用例生成
- RoundTable 研讨后的编码实现

❌ **不适合**:
- 简单单文件修改
- 需要立即回答的问题
- 纯咨询类问题
- Token 预算有限的场景

### Token 消耗

**Auto-Coding 会消耗较多 Token**，因为：
- 多 Agent 协作（8 个步骤，每个步骤调用不同 Agent）
- 迭代循环（测试→反思→优化，最多 3 次）
- 完整的自我审查和优化流程

**建议**: 对于简单任务，直接使用普通对话；对于复杂项目，先使用 RoundTable 研讨方案，再使用 Auto-Coding 实现。

---

## 📁 输出

### 交付物

- 📦 源代码
- 📄 README 文档
- 📊 测试报告
- 📖 部署指南

### 项目位置

```
/tmp/auto-coding-projects/<项目名>/
```

---

## 🔒 安全说明

### 数据流向

**Auto-Coding 的数据处理**:

1. **本地处理**: 所有代码生成在本地完成
2. **模型调用**: 通过 OpenClaw 的 `sessions_spawn` 调用子 Agent
3. **Prompt 内容**: 包含需求描述、任务说明、Agent 人格 Prompt
4. **输出内容**: 代码、测试报告、文档等保存在 `/tmp/auto-coding-projects/`

**数据安全**:
- ✅ 不存储 API Key、密码等敏感信息
- ✅ 不读取用户个人文件
- ✅ 只读取编程相关的 Agent 人格（engineering/design/testing/product）
- ✅ 项目文件保存在临时目录，手动清理

### 权限说明

**Auto-Coding 的权限**:
- ✅ 读取：agency-agents-zh 中的编程相关 Agent 人格
- ✅ 写入：`/tmp/auto-coding-projects/<项目名>/`
- ✅ 调用：OpenClaw 的 `sessions_spawn` 工具

**不执行的权限**:
- ❌ 不修改系统文件
- ❌ 不读取其他技能配置
- ❌ 不访问网络（除模型调用外）
- ❌ 不执行 shell 命令（通过安全沙箱）

---

## 🔧 配置

### 基本配置

```python
AutoCodingWorkflow(
    requirements: str,           # 需求描述（必需）
    tasks: List[Dict] = None,    # 任务列表（可选）
    project_dir: str = None,     # 项目目录（可选，默认/tmp）
    timeout_minutes: int = 30,   # 超时时间（可选，默认 30 分钟）
    user_models: List[Dict] = None  # 自定义模型（可选）
)
```

### 自定义模型

```python
user_models = [
    {'id': 'bailian/glm-5', 'tags': ['engineering']},
    {'id': 'bailian/kimi-k2.5', 'tags': ['design']},
]
```

---

## 📊 安全评分

**安全评分**: 97/100 ⭐⭐⭐⭐⭐

- ✅ 输入验证
- ✅ 命令注入防护
- ✅ 文件安全
- ✅ 数据安全
- ✅ 并发安全
- ✅ 资源管理

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-03-14 | 初始版本 |
| v1.0.1 | 2026-03-19 | P0 修复（并发安全） |
| v1.0.2 | 2026-03-19 | P1 修复（导入/日志） |
| v1.0.3 | 2026-03-19 | P1 修复（超时/死锁） |
| v1.0.4 | 2026-03-19 | 依赖管理器集成 |
| v1.0.5 | 2026-03-19 | 完整版（模型+Soul+Sessions_Spawn） |
| **v1.0.6** | **2026-03-19** | **八步流程版（设计→分解→编码→测试→反思→优化→验证→输出）** |

---

## 📞 技术支持

- **作者**: Krislu <krislu666@foxmail.com>
- **文档**: 参见 README-FULL.md
- **安全报告**: 参见 SECURITY-AUDIT.md
- **部署说明**: 参见 DEPLOYMENT.md

---

*Auto-Coding Skill - Krislu <krislu666@foxmail.com>*
