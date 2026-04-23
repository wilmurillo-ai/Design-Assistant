# API 文档

**版本：** v1.0
**更新日期：** 2026-03-26

---

## 📚 核心API

### LegalAgentBase

智能体基类，所有智能体都应继承此类。

#### `__init__(name, role, toolbox_path=None)`

初始化智能体。

**参数：**
- `name` (str): 智能体名称
- `role` (str): 智能体角色
- `toolbox_path` (str, optional): 工具库文件路径

**返回：**
- 无

**示例：**
```python
agent = LegalAgentBase(
    name="民事律师",
    role="民事纠纷处理",
    toolbox_path="toolboxes/civil_lawyer.json"
)
```

---

#### `execute(task) -> Dict`

执行任务。

**参数：**
- `task` (Dict): 任务字典
  - `task_type` (str): 任务类型
  - 其他参数根据任务类型而定

**返回：**
- `Dict`: 任务结果字典
  - `agent` (str): 智能体名称
  - `version` (str): 智能体版本
  - `status` (str): 执行状态
  - `response_time` (float): 响应时间（秒）
  - `confidence` (float): 置信度（0-1）
  - 其他字段根据任务类型而定

**示例：**
```python
result = agent.execute({
    'task_type': '侵权分析',
    'case_description': 'A公司侵犯B公司专利',
    'behavior_facts': ['生产并销售侵权产品']
})

print(result['status'])  # 'success'
print(result['confidence'])  # 0.90
```

---

#### `evolve(feedback) -> bool`

让智能体自进化。

**参数：**
- `feedback` (Dict): 反馈字典
  - `improvement_score` (float): 改进分数（0-1）
  - `feedback` (str): 反馈描述
  - `user_satisfaction` (float): 用户满意度（0-5）

**返回：**
- `bool`: 是否进化成功

**进化条件：**
- `improvement_score > 0.8`

**示例：**
```python
feedback = {
    'improvement_score': 0.85,
    'feedback': '表现优秀',
    'user_satisfaction': 4.5
}

evolved = agent.evolve(feedback)
print(f"进化结果: {'成功' if evolved else '未进化'}")
print(f"新版本: {agent.version}")
```

---

#### `get_tool(tool_name) -> Dict`

获取工具信息。

**参数：**
- `tool_name` (str): 工具名称

**返回：**
- `Dict`: 工具信息字典
  - `version` (str): 工具版本
  - `accuracy` (float): 准确率
  - `description` (str): 工具描述
  - `input_schema` (Dict): 输入结构
  - `output_schema` (Dict): 输出结构

**示例：**
```python
tool = agent.get_tool('侵权分析')
print(tool['version'])      # "1.0"
print(tool['accuracy'])      # 0.90
print(tool['description'])   # "分析侵权案件的构成要件"
```

---

#### `retrieve_knowledge(query) -> List[Dict]`

检索知识库。

**参数：**
- `query` (str): 查询内容

**返回：**
- `List[Dict]`: 知识条目列表
  - `title` (str): 知识标题
  - `content` (str): 知识内容

**示例：**
```python
knowledge = agent.retrieve_knowledge('合同违约')
print(f"找到 {len(knowledge)} 条相关知识")
for item in knowledge:
    print(f"- {item['title']}")
```

---

#### `get_stats() -> Dict`

获取智能体统计信息。

**返回：**
- `Dict`: 统计信息字典
  - `name` (str): 智能体名称
  - `role` (str): 智能体角色
  - `version` (str): 智能体版本
  - `toolbox` (Dict): 工具库信息
  - `performance` (Dict): 性能统计
  - `experiment_count` (int): 实验次数

**示例：**
```python
stats = agent.get_stats()
print(f"智能体: {stats['name']}")
print(f"版本: {stats['version']}")
print(f"工具数: {stats['toolbox']['total_tools']}")
print(f"任务数: {stats['performance']['total_tasks']}")
print(f"成功率: {stats['performance']['success_rate']:.2%}")
```

---

#### `log_experiment(experiment)`

记录实验日志。

**参数：**
- `experiment` (Dict): 实验数据字典

**返回：**
- 无

**示例：**
```python
agent.log_experiment({
    'task_type': '侵权分析',
    'input': {...}',
    'output': {...}',
    'self_evaluation': {...}'
})
```

---

## 🧬 EvolutionEngine API

进化引擎，管理智能体的进化过程。

#### `should_evolve(agent) -> bool`

判断智能体是否应该进化。

**参数：**
- `agent` (LegalAgentBase): 智能体实例

**返回：**
- `bool`: 是否进化

**进化条件：**
- 总任务数 >= 100
- 连续失败 >= 3
- 成功率 < 0.9

**示例：**
```python
from core.evolution_engine import EvolutionEngine

engine = EvolutionEngine()

if engine.should_evolve(agent):
    print("智能体应该进化")
else:
    print("暂不需要进化")
```

---

#### `execute_evolution(agent, feedback)`

执行进化操作。

**参数：**
- `agent` (LegalAgentBase): 智能体实例
- `feedback` (Dict): 反馈数据

**返回：**
- `bool`: 进化是否成功

**示例：**
```python
from core.evolution_engine import EvolutionEngine

engine = EvolutionEngine()
success = engine.execute_evolution(agent, feedback)

if success:
    print("进化成功！")
else:
    print("进化失败")
```

---

## 📝 StandardSync API

标准同步器，同步智能体与标准。

#### `check_update(standard_version) -> bool`

检查标准是否有更新。

**参数：**
- `standard_version` (str): 标准版本

**返回：**
- `bool`: 是否有更新

**示例：**
```python
from core.standard_sync import StandardSync

sync = StandardSync()

if sync.check_update('1.5'):
    print("检测到标准更新，从v1.5升级到v1.6")
else:
    print("标准已是最新版本")
```

---

#### `sync_agent(agent, standard_version)`

同步智能体到最新标准。

**参数：**
- `agent` (LegalAgentBase): 智能体实例
- `standard_version` (str): 标准版本

**返回：**
- `bool`: 同步是否成功

**示例：**
```python
from core.standard_sync import StandardSync

sync = StandardSync()

success = sync.sync_agent(agent, '1.6')

if success:
    print("同步成功")
else:
    print("同步失败")
```

---

## 🛠️ 工具API

### 工具调用示例

```python
# 获取工具
tool = agent.get_tool('侵权分析')

# 使用工具
if tool:
    print(f"工具名称: {tool_name}")
    print(f"工具版本: {tool['version']}")
    print(f"准确率: {tool['accuracy']}")
    print(f"使用次数: {tool['total_uses']}")
    print(f"描述: {tool['description']}")
    print(f"输入: {tool['input_schema']}")
    print(f"输出: {tool['output_schema']}")
```

### 工具输出格式

```json
{
  "tool_used": "侵权分析",
  "tool_version": "1.0",
  "tool_accuracy": 0.90,
  "result": {
    "infringement_established": true,
    "causality": "明确",
    "legal_basis": ["民法典第1165条"],
    "confidence": 0.90
  },
  "message": "侵权分析工具执行完成"
}
```

---

## 📊 统计API

### 性能指标

```python
stats = agent.get_stats()

# 指标说明
performance = stats['performance']
performance['total_tasks']        # 总任务数
performance['success_rate']        # 成功率
performance['avg_confidence']     # 平均置信度
performance['avg_response_time']  # 平均响应时间
performance['last_improvement']   # 上次改进时间
```

### 工具统计

```python
toolbox = agent.toolbox

# 工具信息
for tool_name, tool in toolbox.items():
    print(f"工具: {tool_name}")
    print(f"  版本: {tool['version']}")
    print(f"  准确率: {tool['accuracy']:.2%}")
    print(f"  使用次数: {tool['total_uses']}")
    print(f"  改进次数: {tool['improvements']}")
```

---

## 🔧 配置API

### 加载配置

```python
# 从文件加载配置
config = load_config('config.json')

# 设置配置
agent.config = config

# 使用配置
result = agent.execute({
    'task_type': '任务',
    'data': {...}',
    **config
})
```

### 保存配置

```python
# 保存当前配置
agent.save_config('config.json')
```

---

## 🚀 错误处理

### 常见错误

#### 1. 工具不存在

```python
tool = agent.get_tool('不存在的工具')
# 返回: None
```

**处理：**
```python
if not tool:
    return {
        'status': 'error',
        'error': '工具不存在: 不存在的工具'
    }
```

#### 2. 任务类型不支持

```python
result = agent.execute({
    'task_type': '不支持的类型'
})
# 返回: {'status': 'error', 'error': '不支持的任务类型: 不支持的类型'}
```

#### 3. 进化失败

```python
feedback = {'improvement_score': 0.5}  # 分数过低
evolved = agent.evolve(feedback)
# 返回: False
```

---

## 📚 更多资源

- [教程](docs/TUTORIAL.md)
- [架构文档](docs/ARCHITECTURE.md)
- [贡献指南](../CONTRIBUTING.md)
- [FAQ](docs/FAQ.md)

---

**Legal-AI-Collaboration-Framework - 让法律AI变得简单！** 🚀
