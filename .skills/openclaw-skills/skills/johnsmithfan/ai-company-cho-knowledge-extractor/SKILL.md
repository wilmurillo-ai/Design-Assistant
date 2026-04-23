---
name: "AI Company CHO Knowledge Extractor"
slug: ai-company-cho-knowledge-extractor
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-cho-knowledge-extractor
description: |
  AI Company CHO知识提取模块。分析skill结构、提取核心知识、建立能力映射、managementknowledge base。
  触发关键词：知识提取、能力分析、skill解析
license: MIT-0
tags: [ai-company, cho, knowledge, extraction, capability-mapping]
triggers:
  - 知识提取
  - 能力分析
  - skill解析
  - 知识management
  - knowledge extraction
  - capability analysis
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        skill_path:
          type: string
          description: 待分析skill路径
        extraction_depth:
          type: string
          enum: [shallow, standard, deep]
          default: standard
          description: 提取深度
        include_capabilities:
          type: boolean
          default: true
          description: 是否包含能力映射
      required: [skill_path]
  outputs:
    type: object
    schema:
      type: object
      properties:
        skill_name:
          type: string
        knowledge_summary:
          type: object
          properties:
            domain:
              type: string
              description: skill领域
            core_functions:
              type: array
              items:
                type: string
            knowledge_types:
              type: array
              items:
                type: string
            complexity_score:
              type: number
        capability_map:
          type: array
          items:
            type: object
            properties:
              capability:
                type: string
              level:
                type: string
                enum: [basic, intermediate, advanced, expert]
              prerequisites:
                type: array
              related_skills:
                type: array
        learning_path:
          type: array
          items:
            type: object
            properties:
              step:
                type: integer
              topic:
                type: string
              duration:
                type: string
              resources:
                type: array
        knowledge_graph:
          type: object
          description: 知识图谱结构
      required: [skill_name, knowledge_summary]
  errors:
    - code: KNOWLEDGE_001
      message: "Skill path not found"
    - code: KNOWLEDGE_002
      message: "Invalid skill structure"
    - code: KNOWLEDGE_003
      message: "Knowledge extraction failed"
permissions:
  files: [read]
  network: []
  commands: []
  mcp: []
dependencies:
  skills:
    - ai-company-hq
    - ai-company-kb
    - ai-company-cho
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  tags: [ai-company, cho, knowledge, extraction]
---

# AI Company CHO Knowledge Extractor v1.0

> CHO主导的知识提取模块。分析skill结构、提取核心知识、建立能力映射。

---

## 概述

**ai-company-cho-knowledge-extractor** 是AIskilllearning流程的知识management模块，负责：

1. **skill解析**: 分析skill结构和功能
2. **知识提取**: 识别核心知识类型
3. **能力映射**: 建立能力雷达图
4. **learning路径**: 生成learning建议

---

## Module 1: skill解析

### 分析维度

```yaml
analysis_dimensions:
  structure:
    - 目录组织
    - 文件关系
    - 依赖结构
    - 接口契约
  
  functionality:
    - 核心功能
    - 输入输出
    - 错误处理
    - 配置参数
  
  technology:
    - 技术栈
    - API设计
    - 数据格式
    - 第三方依赖
  
  documentation:
    - 描述质量
    - 示例完整性
    - 注释覆盖率
```

### 解析算法

```python
def analyze_skill_structure(skill_path: str) -> SkillStructure:
    structure = {
        'directories': [],
        'files': [],
        'relationships': [],
        'entry_points': [],
    }
    
    # 遍历目录
    for root, dirs, files in os.walk(skill_path):
        for file in files:
            file_path = os.path.join(root, file)
            structure['files'].append({
                'path': file_path,
                'type': infer_file_type(file),
                'size': os.path.getsize(file_path),
            })
    
    # 分析依赖关系
    structure['relationships'] = analyze_dependencies(structure['files'])
    
    # 识别入口点
    structure['entry_points'] = find_entry_points(structure['files'])
    
    return structure
```

---

## Module 2: 知识提取

### 知识类型分类

| 类型 | 说明 | 提取方法 |
|------|------|----------|
| **Declarative** | 事实性知识 | 模式匹配 |
| **Procedural** | 过程性知识 | 代码分析 |
| **Structural** | 结构性知识 | 图谱build |
| **Heuristic** | 经验性知识 | 示例learning |

### 知识提取流程

```
skill源码 → 知识识别 → 知识分类 → 知识抽取 → 知识存储
     ↓
  解析AST    模式匹配   规则判断   结构化   知识图谱
```

---

## Module 3: 能力映射

### 能力维度

```yaml
capability_dimensions:
  technical:
    - "编程能力"
    - "算法设计"
    - "系统架构"
    - "性能优化"
  
  domain:
    - "领域理解"
    - "业务建模"
    - "行业知识"
  
  process:
    - "流程设计"
    - "质量控制"
    - "项目management"
  
  collaboration:
    - "团队协作"
    - "文档编写"
    - "沟通表达"
```

### 能力雷达图

```
能力评分: 0-100

         编程能力
            85
             ▲
            ╱ ╲
   系统架构 ╱   ╲ 领域理解
     78  ╱─────╲  72
        ╱   81   ╲
   ─────╱────────╲─────
  文档  ╲        ╱  协作
   75   ╲      ╱   80
         ╲    ╱
          ╲  ╱
           ╲╱
         算法
          82
```

---

## Module 4: learning路径

### 路径生成

```python
def generate_learning_path(skill: Skill, depth: str) -> LearningPath:
    """
    基于skill复杂度生成learning路径
    """
    steps = []
    
    if depth == "shallow":
        # 基础入门
        steps.append({"step": 1, "topic": "核心概念", "duration": "30min"})
        steps.append({"step": 2, "topic": "快速上手", "duration": "1h"})
        
    elif depth == "standard":
        # 标准learning路径
        steps.append({"step": 1, "topic": "背景知识", "duration": "1h"})
        steps.append({"step": 2, "topic": "核心概念", "duration": "2h"})
        steps.append({"step": 3, "topic": "基础实践", "duration": "3h"})
        steps.append({"step": 4, "topic": "进阶特性", "duration": "4h"})
        steps.append({"step": 5, "topic": "项目实战", "duration": "6h"})
        
    elif depth == "deep":
        # 深度learning路径
        steps.append({"step": 1, "topic": "理论基础", "duration": "4h"})
        steps.append({"step": 2, "topic": "源码分析", "duration": "8h"})
        steps.append({"step": 3, "topic": "扩展开发", "duration": "8h"})
        steps.append({"step": 4, "topic": "性能调优", "duration": "4h"})
        steps.append({"step": 5, "topic": "生产部署", "duration": "4h"})
        steps.append({"step": 6, "topic": "最佳实践", "duration": "6h"})
    
    return LearningPath(steps=steps, total_duration=sum(s.duration))
```

---

## 接口定义

### `extract`

执行知识提取。

**Input:**
```yaml
skill_path: "~/.qclaw/skills/pdf-processor"
extraction_depth: standard
include_capabilities: true
```

**Output:**
```yaml
skill_name: "pdf-processor"
knowledge_summary:
  domain: "文档处理"
  core_functions:
    - "PDF合并"
    - "PDF拆分"
    - "页面旋转"
    - "文本提取"
  knowledge_types:
    - "Procedural"
    - "Structural"
  complexity_score: 72
capability_map:
  - capability: "编程能力"
    level: advanced
    prerequisites: []
    related_skills: ["file-processor"]
  - capability: "领域理解"
    level: intermediate
    prerequisites: ["文件处理基础"]
    related_skills: []
learning_path:
  - step: 1
    topic: "PDF格式基础"
    duration: "1h"
    resources: []
  - step: 2
    topic: "PyPDF2/PyMuPDF入门"
    duration: "2h"
    resources: ["官方文档"]
  - step: 3
    topic: "核心功能开发"
    duration: "4h"
    resources: []
  - step: 4
    topic: "异常处理与优化"
    duration: "2h"
    resources: []
knowledge_graph:
  nodes: []
  edges: []
```

---

## KPI 仪表板

| 维度 | KPI | 目标值 |
|------|-----|--------|
| 准确性 | 知识提取准确率 | ≥ 85% |
| 完整性 | 能力覆盖度 | ≥ 90% |
| 效率 | 平均提取时间 | ≤ 30秒 |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-04-15 | 初始版本：skill解析+知识提取+能力映射+learning路径 |

---

*本Skill由AI Company CHO开发*  
*作为ai-company-skill-learner的模块组件*
