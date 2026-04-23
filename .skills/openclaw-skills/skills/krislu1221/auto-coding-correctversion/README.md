# Auto-Coding Skill 完整文档

**版本**: v1.1.0  
**更新日期**: 2026-03-19  
**作者**: Krislu <krislu666@foxmail.com>

---

## 📖 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [核心功能](#核心功能)
4. [使用指南](#使用指南)
5. [配置说明](#配置说明)
6. [API 参考](#api 参考)
7. [最佳实践](#最佳实践)
8. [故障排除](#故障排除)
9. [安全说明](#安全说明)
10. [更新日志](#更新日志)

---

## 概述

### 什么是 Auto-Coding？

**Auto-Coding** 是一个智能自主编码系统，通过多 Agent 协作完成从需求到代码的完整开发流程。

**核心理念**: 不是任务分发器，而是自我完善的智能编程系统。它利用 OpenClaw 的多子 Agent 进程，进行设计→分解→编码→测试→反思→优化→验证→输出，分不同角色的 Prompt 实现多维度的自我审查和自我优化，提升代码可执行率。适合复杂项目，但会消耗更多的 Token，应谨慎使用。

**推荐使用**: Claw RoundTable 先进行多 Agent 项目研讨和方案完善，然后将结论送入 Auto-Coding 进行编码，效果更好。

### 致谢

**Agent 人格**: 借鉴了 [Agency-Agent](https://github.com/zhayujie/agency-agent) 关于程序员的部分，特此致敬。

### 核心特性

| 特性 | 说明 |
|------|------|
| 🤖 **多 Agent 协作** | 工程/设计/测试专家协同工作 |
| 🔄 **八步循环** | 设计→分解→编码→测试→反思→优化→验证→输出 |
| 🔗 **任务依赖管理** | 智能依赖图构建和拓扑排序 |
| 🎯 **模型可选** | 支持多模型配置和自动匹配 |
| ⏱️ **超时保护** | 可配置超时和死锁检测 |
| 📊 **进度追踪** | 实时任务进度和状态报告 |

### 适用场景

✅ **推荐使用**:
- 复杂项目开发（多任务依赖）
- 技术方案设计和实现
- 代码审查和优化
- 测试用例生成
- RoundTable 研讨后的编码实现

❌ **不推荐**:
- 简单单文件修改
- 需要立即回答的问题
- 纯咨询类问题
- Token 预算有限的场景

---

## 快速开始

### 1. 安装

Auto-Coding 已集成到 OpenClaw Skills，无需单独安装。

```bash
# 验证安装
cd ~/.openclaw/workspace/skills/auto-coding
python3 -c "from auto_coding_workflow import AutoCodingWorkflow; print('✅ 安装成功')"
```

### 2. 基本使用

```python
from auto_coding_workflow import AutoCodingWorkflow

# 定义需求
requirements = """
创建一个简单的待办应用 (Todo App)

功能需求:
1. 创建、编辑、删除待办事项
2. 标记完成状态
3. 按优先级排序（高/中/低）
4. LocalStorage 持久化存储

技术栈:
- HTML + CSS + JavaScript
- 无需后端
"""

# 创建工作流
workflow = AutoCodingWorkflow(
    requirements=requirements,
    timeout_minutes=30
)

# 运行工作流
result = await workflow.run()
```

### 3. 带任务列表使用

```python
# 定义任务（带依赖关系）
tasks = [
    {'id': 1, 'name': '创建项目结构', 'depends_on': []},
    {'id': 2, 'name': '实现 HTML 框架', 'depends_on': [1]},
    {'id': 3, 'name': '实现 CSS 样式', 'depends_on': [2]},
    {'id': 4, 'name': '实现 JS 功能', 'depends_on': [2]},
    {'id': 5, 'name': '测试功能', 'depends_on': [3, 4]},
]

workflow = AutoCodingWorkflow(
    requirements=requirements,
    tasks=tasks,
    project_dir="/tmp/todo-app",
    timeout_minutes=30
)

result = await workflow.run()
```

---

## 核心功能

### 1. 八步循环工作流

```
设计 (Design)
  ↓ 技术方案设计和架构
分解 (Decomposition)
  ↓ 任务拆解和依赖管理
编码 (Coding)
  ↓ 代码实现
测试 (Testing)
  ↓ 功能测试
反思 (Reflection)
  ↓ 代码审查和反思
优化 (Optimization)
  ↓ 改进和修复
验证 (Verification)
  ↓ 最终验证
输出 (Output)
  ↓ 交付物生成
```

**迭代逻辑**: 测试→反思→优化 形成迭代循环（最多 3 次）

### 2. 任务依赖管理

**依赖图构建**:
```python
tasks = [
    {'id': 1, 'depends_on': []},      # 无依赖
    {'id': 2, 'depends_on': [1]},     # 依赖任务 1
    {'id': 3, 'depends_on': [1, 2]},  # 依赖任务 1 和 2
]
```

**执行顺序**: [1, 2, 3]（拓扑排序）

**并行任务**: 任务 1 完成后，任务 2 可执行；任务 1 和 2 完成后，任务 3 可执行

### 3. 模型选择

**自动匹配**:
```python
# 根据 Agent 角色自动匹配模型
model = model_selector.select_model_for_role("engineering")
# 返回：qwen3.5-plus（或用户配置的首选模型）
```

**自定义配置**:
```python
user_models = [
    {'id': 'bailian/glm-5', 'tags': ['engineering'], 'priority': 1},
    {'id': 'bailian/kimi-k2.5', 'tags': ['design'], 'priority': 1},
]

workflow = AutoCodingWorkflow(
    requirements=...,
    user_models=user_models
)
```

### 4. Agent Soul 加载

**已加载 Agent (8 个)**:

| 类别 | Agent | 用途 |
|------|-------|------|
| Engineering | engineering-frontend-developer | 前端开发 |
| Engineering | engineering-backend-architect | 后端架构 |
| Engineering | engineering-software-architect | 软件架构 |
| Engineering | engineering-code-reviewer | 代码审查 |
| Engineering | engineering-senior-developer | 高级开发 |
| Design | design-ui-designer | UI 设计 |
| Design | design-ux-architect | UX 架构 |
| Testing | testing-api-tester | API 测试 |

---

## 使用指南

### 场景 1: 简单项目开发

```python
workflow = AutoCodingWorkflow(
    requirements="创建一个天气查询 Web 应用",
    timeout_minutes=30
)
result = await workflow.run()
```

### 场景 2: 复杂项目（多任务依赖）

```python
tasks = [
    {'id': 1, 'name': '需求分析', 'depends_on': []},
    {'id': 2, 'name': '架构设计', 'depends_on': [1]},
    {'id': 3, 'name': '前端开发', 'depends_on': [2]},
    {'id': 4, 'name': '后端开发', 'depends_on': [2]},
    {'id': 5, 'name': '集成测试', 'depends_on': [3, 4]},
]

workflow = AutoCodingWorkflow(
    requirements="企业级 CRM 系统",
    tasks=tasks,
    timeout_minutes=60
)
result = await workflow.run()
```

### 场景 3: 代码审查和优化

```python
workflow = AutoCodingWorkflow(
    requirements="审查以下代码并提出优化建议：[代码内容]",
    timeout_minutes=15
)
result = await workflow.run()
```

---

## 配置说明

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

### 高级配置

#### 自定义模型配置

```python
user_models = [
    {
        'id': 'bailian/glm-5',
        'tags': ['engineering', 'architecture'],
        'priority': 1
    },
    {
        'id': 'bailian/kimi-k2.5',
        'tags': ['design', 'ux'],
        'priority': 2
    }
]
```

#### 任务依赖配置

```python
tasks = [
    {
        'id': 1,
        'name': '任务名称',
        'description': '任务描述',
        'depends_on': [],           # 依赖的任务 ID 列表
        'priority': 'high'          # 优先级：high/medium/low
    }
]
```

---

## API 参考

### AutoCodingWorkflow

#### 构造函数

```python
def __init__(
    self,
    requirements: str,
    tasks: List[Dict] = None,
    project_dir: str = None,
    timeout_minutes: int = 30,
    user_models: List[Dict] = None
)
```

#### 方法

```python
async def run() -> Dict:
    """运行完整的八步循环工作流"""
    
async def step_production():
    """步骤 1: 生产 - 分析需求并生成代码"""
    
async def step_testing():
    """步骤 2: 测试 - 运行测试并报告覆盖率"""
    
async def step_reflection():
    """步骤 3: 反思 - 反思代码质量"""
    
async def step_improvement():
    """步骤 4: 改进 - 修复代码"""
    
async def step_verification():
    """步骤 5: 验证 - 最终验证"""
```

### DependencyManager

```python
def build_dependency_graph(tasks: List[Dict]) -> Dict:
    """构建任务依赖图"""

def topological_sort() -> Optional[List[int]]:
    """拓扑排序，返回执行顺序"""

def detect_cycle() -> bool:
    """检测是否有循环依赖"""

def get_parallel_tasks(completed_tasks: Set[int]) -> List[int]:
    """获取可并行执行的任务"""
```

### AgentSoulLoader

```python
def get_agent_soul(agent_id: str) -> Optional[Dict]:
    """获取 Agent Soul"""

def list_available_agents() -> List[str]:
    """列出所有可用 Agent"""

def get_agents_by_category(category: str) -> List[Dict]:
    """按类别获取 Agent"""
```

---

## 最佳实践

### 1. 需求描述最佳实践

✅ **好的需求描述**:
```python
requirements = """
创建一个待办应用 (Todo App)

功能需求:
1. 创建、编辑、删除待办事项
2. 标记完成状态
3. 按优先级排序（高/中/低）
4. LocalStorage 持久化存储

技术栈:
- HTML + CSS + JavaScript
- 无需后端
- 单页面应用

验收标准:
- 所有功能正常工作
- 界面简洁美观
- 代码有注释
"""
```

❌ **不好的需求描述**:
```python
requirements = "做个 todo"  # 太模糊
```

### 2. 任务分解最佳实践

✅ **好的任务分解**:
```python
tasks = [
    {'id': 1, 'name': '创建项目结构', 'depends_on': [], 'description': '创建 HTML/CSS/JS 文件'},
    {'id': 2, 'name': '实现 HTML 框架', 'depends_on': [1], 'description': '创建页面结构'},
    {'id': 3, 'name': '实现 CSS 样式', 'depends_on': [2], 'description': '美化界面'},
]
```

❌ **不好的任务分解**:
```python
tasks = [
    {'id': 1, 'name': '做所有事情'},  # 任务太大
]
```

### 3. 超时配置最佳实践

| 项目规模 | 建议超时 | 说明 |
|---------|---------|------|
| 简单项目 | 15 分钟 | 单文件或小功能 |
| 中等项目 | 30 分钟 | 多文件功能模块 |
| 复杂项目 | 60 分钟 | 完整应用开发 |

### 4. 模型配置最佳实践

```python
# 推荐：为不同角色配置不同模型
user_models = [
    {'id': 'bailian/glm-5', 'tags': ['engineering'], 'priority': 1},
    {'id': 'bailian/kimi-k2.5', 'tags': ['design'], 'priority': 1},
]

# 不推荐：所有角色用同一个模型
user_models = [
    {'id': 'bailian/qwen3.5-plus', 'tags': ['engineering', 'design'], 'priority': 1},
]
```

---

## 故障排除

### 问题 1: 依赖图构建失败

**错误**: `依赖图验证失败：检测到循环依赖`

**原因**: 任务依赖关系形成环路

**解决方法**:
```python
# 错误：A→B→C→A
tasks = [
    {'id': 1, 'depends_on': [3]},
    {'id': 2, 'depends_on': [1]},
    {'id': 3, 'depends_on': [2]},
]

# 正确：A→B→C
tasks = [
    {'id': 1, 'depends_on': []},
    {'id': 2, 'depends_on': [1]},
    {'id': 3, 'depends_on': [2]},
]
```

### 问题 2: 超时错误

**错误**: `超时！已达到 30 分钟限制`

**原因**: 项目复杂度过高或迭代次数过多

**解决方法**:
```python
# 增加超时时间
workflow = AutoCodingWorkflow(
    requirements=...,
    timeout_minutes=60  # 增加到 60 分钟
)

# 或减少迭代次数（修改源码）
max_iterations = 2  # 从 3 减少到 2
```

### 问题 3: Agent Soul 加载失败

**错误**: `未找到 Agent Soul`

**原因**: agency-agents-zh 目录不存在或路径错误

**解决方法**:
```python
# 检查路径
from agent_soul_loader import AgentSoulLoader
loader = AgentSoulLoader()
print(f"Agency 路径：{loader.agency_path}")
print(f"路径存在：{loader.agency_path.exists()}")

# 如果路径不存在，使用默认 Soul
# （代码会自动降级到默认 Soul）
```

### 问题 4: sessions_spawn 不可用

**错误**: `sessions_spawn 不可用，使用模拟结果`

**原因**: OpenClaw 环境未正确配置

**解决方法**:
```python
# 验证 OpenClaw 安装
python3 -c "from openclaw.tools import sessions_spawn; print('✅ 已安装')"

# 如果未安装，使用模拟模式（自动降级）
# 代码会自动处理，不会崩溃
```

---

## 安全说明

### 数据安全

- ✅ **不存储敏感信息**: 不存储 API Key、密码等
- ✅ **本地执行**: 所有代码在本地执行
- ✅ **文件锁保护**: 并发安全的文件操作

### 资源安全

- ✅ **超时保护**: 防止无限执行
- ✅ **死锁检测**: 10 分钟无进展自动终止
- ✅ **迭代限制**: 最多 3 次迭代

### 代码安全

- ✅ **沙箱执行**: 通过 sessions_spawn 沙箱执行
- ✅ **无 shell 注入**: 不直接执行 shell 命令
- ✅ **路径验证**: 限制在项目目录内

**详细安全报告**: 参见 `SECURITY-AUDIT.md`

---

## 更新日志

### v1.1.0 (2026-03-20)

**新增**:
- ✅ 八步循环流程（设计→分解→编码→测试→反思→优化→验证→输出）
- ✅ 迭代逻辑优化（测试→反思→优化循环）
- ✅ 独立输出步骤（交付物生成）

**改进**:
- ✅ 设计独立，专注技术方案
- ✅ 分解独立，明确任务依赖
- ✅ 编码独立，按依赖顺序执行
- ✅ 减少不必要迭代，提高效率

**测试**:
- ✅ 测试覆盖率 100% (12/12)
- ✅ 安全评分 97/100

### v1.0.5 (2026-03-19)

**新增**:
- ✅ 复用 RoundTable 的 ModelSelector
- ✅ 集成 Agency Agent 人格 Prompt（8 个）
- ✅ 实现完整的 sessions_spawn 调用
- ✅ 任务依赖管理（DependencyManager）
- ✅ Agent Soul 加载器

**修复**:
- ✅ P0: TaskManager 并发安全
- ✅ P1: 统一导入策略
- ✅ P1: 动态导入冗余
- ✅ P1: 改进错误处理
- ✅ P1: 任务取消机制
- ✅ P1: 死锁检测优化

**测试**:
- ✅ 测试覆盖率 100% (20/20)
- ✅ 安全评分 97/100

### v1.0.0 (2026-03-14)

- ✅ 初始版本发布

---

## 📞 技术支持

- **问题反馈**: GitHub Issues
- **文档**: 本文件 + `COMPLETE-IMPLEMENTATION-REPORT.md`
- **安全报告**: `SECURITY-AUDIT.md`

---

**文档版本**: v1.1.0  
**最后更新**: 2026-03-19  
**作者**: Krislu <krislu666@foxmail.com>  
**文档工程师**: AI Technical Writer

---

*Auto-Coding Skill - Krislu <krislu666@foxmail.com>*
