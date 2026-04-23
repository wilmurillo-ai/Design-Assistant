# 快速开始教程

**版本：** v1.0
**更新日期：** 2026-03-26

---

## 🚀 5分钟快速上手

### 步骤1：安装

```bash
# 克隆仓库
git clone https://github.com/legal-ai-collaboration-framework.git
cd legal-ai-collaboration-framework

# 安装依赖
pip install -r requirements.txt
```

### 步骤2：创建你的第一个智能体

```python
# 创建文件: my_lawyer.py
from core.agent_base import LegalAgentBase
from typing import Dict, Any

class MyLawyerAgent(LegalAgentBase):
    """我的律师智能体"""

    def __init__(self):
        super().__init__(
            name="我的律师",
            role="法律咨询",
            toolbox_path="toolboxes/my_lawyer.json"
        )

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('task_type')

        if task_type == '法律咨询':
            return self._provide_advice(task)
        else:
            return {
                'status': 'error',
                'error': f'不支持的任务类型: {task_type}'
            }

    def _provide_advice(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """提供法律建议"""
        question = task.get('question', '')
        
        # 检索相关知识
        knowledge = self.retrieve_knowledge(question)
        
        # 生成回答
        answer = "基于法律规定，" + question
        
        result = {
            'agent': self.name,
            'task_type': '法律咨询',
            'status': 'success',
            'question': question,
            'answer': answer,
            'references': knowledge[:3],  # 取前3条相关
            'confidence': 0.90
        }
        
        return result

# 运行智能体
if __name__ == "__main__":
    agent = MyLawyerAgent()
    
    result = agent.execute({
        'task_type': '法律咨询',
        'question': '合同违约应该怎么处理？'
    })
    
    print(f"智能体: {result['agent']}")
    print(f"问题: {result['question']}")
    print(f"回答: {result['answer']}")
    print(f"置信度: {result['confidence']:.2%}")
    print(f"相关参考: {len(result['references'])}条")
```

### 步骤3：运行

```bash
python my_lawyer.py
```

**预期输出：**

```
✅ 我的律师 工具库加载成功，包含 0 个工具
🤖 我的律师智能体初始化完成
   版本: 1.0.0
   工具数: 0
智能体: 我的律师
问题: 合同违约应该怎么处理？
回答: 基于法律规定，合同违约应该怎么处理
置信度: 90.00%
相关参考: 0条
```

---

## 🎯 10分钟：添加工具

### 步骤1：创建工具库

创建文件：`toolboxes/my_lawyer.json`

```json
{
  "agent_name": "我的律师",
  "version": "1.0.0",
  "role": "法律咨询",
  "toolbox": {
    "法律检索": {
      "version": "1.0",
      "description": "检索相关法律条文",
      "accuracy": 0.90,
      "input_schema": {
        "query": "string"
      },
      "output_schema": {
        "results": "array",
        "count": "number"
      },
      "model": "legal_search_v1.0",
      "improvements": 0,
      "total_uses": 0
    },
    "案例分析": {
      "version": "1.0",
      "description": "分析类似案例",
      "accuracy": 0.88,
      "input_schema": {
        "case_description": "string"
      },
      "output_schema": {
        "similar_cases": "array",
        "analysis": "string"
      },
      "model": "case_analysis_v1.0",
      "improvements": 0,
      "total_uses": 0
    }
  },
  "knowledge_base": {
    "民法典第577条": "当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。",
    "合同法第107条": "当事人一方不履行非金钱债务或者履行非金钱债务不符合约定的，对方可以请求履行，但是有正当理由的除外。",
    "民法典第580条": "当事人一方不履行合同义务或者履行合同义务不符合约定的，应当承担继续履行、采取补救措施或者赔偿损失等违约责任。"
  },
  "performance": {
    "total_tasks": 0,
    "success_rate": 0.95,
    "avg_confidence": 0.90,
    "avg_response_time": 0.0,
    "last_improvement": null
  },
  "created_at": "2026-03-26T13:00:00Z",
  "updated_at": "2026-03-26T13:00:00Z"
}
```

### 步骤2：更新智能体代码

```python
from core.agent_base import LegalAgentBase
from typing import Dict, Any
import time

class MyLawyerAgent(LegalAgentBase):
    """我的律师智能体"""

    def __init__(self):
        super().__init__(
            name="我的律师",
            role="法律咨询",
            toolbox_path="toolboxes/my_lawyer.json"
        )

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('task_type')

        if task_type == '法律咨询':
            return self._provide_advice(task)
        elif task_type == '法律检索':
            return self._legal_search(task)
        elif task_type == '案例分析':
            return self._case_analysis(task)
        else:
            return {
                'status': 'error',
                'error': f'不支持的任务类型: {task_type}'
            }

    def _provide_advice(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """提供法律建议"""
        question = task.get('question', '')
        
        # 检索相关知识
        knowledge = self.retrieve_knowledge(question)
        
        # 生成回答
        if '违约' in question:
            answer = "根据民法典第577条，合同违约应承担继续履行、补救措施或赔偿损失。"
        else:
            answer = "需要了解更多案情才能给出具体建议。"
        
        return {
            'agent': self.name,
            'task_type': '法律咨询',
            'status': 'success',
            'question': question,
            'answer': answer,
            'references': knowledge,
            'confidence': 0.95
        }

    def _legal_search(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """法律检索"""
        query = task.get('query', '')
        
        tool = self.get_tool('法律检索')
        if not tool:
            return {'status': 'error', 'error': '工具不存在'}
        
        # 模拟检索结果
        results = [
            {'title': '民法典第577条', 'content': '当事人一方不履行合同义务...'},
            {'title': '合同法第107条', 'content': '当事人一方不履行非金钱债务...'},
            {'title': '民法典第580条', 'content': '当事人一方不履行合同义务...'}
        ]
        
        time.sleep(0.5)  # 模拟处理时间
        
        return {
            'agent': self.name,
            'task_type': '法律检索',
            'status': 'success',
            'query': query,
            'results': results,
            'count': len(results),
            'confidence': tool['accuracy'],
            'response_time': 0.5
        }

    def _case_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """案例分析"""
        case_desc = task.get('case_description', '')
        
        tool = self.get_tool('案例分析')
        if not tool:
            return {'status': 'error', 'error': '工具不存在'}
        
        # 模拟案例分析
        analysis = f"根据案情描述：{case_desc}，\n\n建议：收集更多证据，确定违约事实，明确法律依据。"
        
        return {
            'agent': self.name,
            'task_type': '案例分析',
            'status': 'success',
            'case_description': case_desc,
            'analysis': analysis,
            'confidence': tool['accuracy'],
            'response_time': 0.8
        }

# 测试所有功能
if __name__ == "__main__":
    agent = MyLawyerAgent()
    
    print("=== 测试1：法律咨询 ===")
    result1 = agent.execute({
        'task_type': '法律咨询',
        'question': '合同违约应该怎么处理？'
    })
    print(f"回答: {result1['answer']}")
    print(f"置信度: {result1['confidence']:.2%}\n")
    
    print("=== 测试2：法律检索 ===")
    result2 = agent.execute({
        'task_type': '法律检索',
        'query': '合同违约'
    })
    print(f"检索到 {result2['count']} 条相关条文")
    print(f"置信度: {result2['confidence']:.2%}\n")
    
    print("=== 测试3：案例分析 ===")
    result3 = agent.execute({
        'task_type': '案例分析',
        'case_description': 'A公司未按时交付货物'
    })
    print(f"分析结果:\n{result3['analysis']}")
    print(f"置信度: {result3['confidence']:.2%}\n")
    
    print("=== 智能体统计 ===")
    stats = agent.get_stats()
    print(f"智能体名称: {stats['name']}")
    print(f"版本: {stats['version']}")
    print(f"工具数量: {stats['toolbox']['total_tools']}个")
    print(f"总任务数: {stats['performance']['total_tasks']}")
    print(f"成功率: {stats['performance']['success_rate']:.2%}")
```

### 步骤3：运行

```bash
python my_lawyer.py
```

**预期输出：**

```
✅ 我的律师 工具库加载成功，包含 2 个工具
🤖 我的律师智能体初始化完成
   版本: 1.0.0
   工具数: 2

=== 测试1：法律咨询 ===
回答: 根据民法典第577条，合同违约应承担继续履行、补救措施或赔偿损失。
置信度: 95.00%

=== 测试2：法律检索 ===
检索到 3 条相关条文
置信度: 90.00%

=== 测试3：案例分析 ===
分析结果:
根据案情描述：A公司未按时交付货物，

建议：收集更多证据，确定违约事实，明确法律依据。
置信度: 88.00%

=== 智能体统计 ===
智能体名称: 我的律师
版本: 1.0.0
工具数量: 2个
总任务数: 3
成功率: 95.00%
```

---

## 🧬 15分钟：让智能体进化

### 步骤1：收集反馈

```python
# 模拟用户反馈
feedback = {
    'improvement_score': 0.92,
    'feedback': '表现优秀，法律检索很准确',
    'user_satisfaction': 4.8
}

# 触发进化
evolved = agent.evolve(feedback)

if evolved:
    print(f"🧬 进化成功！")
    print(f"新版本: {agent.version}")
    
    # 查看工具改进
    for tool_name, tool in agent.toolbox.items():
        print(f"  {tool_name}: v{tool['version']} (准确率: {tool['accuracy']:.2%})")
else:
    print("未达到进化阈值（需要>0.8）")
```

### 步骤2：验证进化

```python
# 再次执行任务，验证改进
result = agent.execute({
    'task_type': '法律咨询',
    'question': '合同违约怎么处理？'
})

print(f"新置信度: {result['confidence']:.2%}")
print(f"之前置信度: 95%")
print(f"提升: {result['confidence'] - 0.95:.2%}")
```

---

## 🎓 进阶：创建多智能体协作

### 创建团队协调器

```python
from core.agent_base import LegalAgentBase
from typing import List

class TeamOrchestrator:
    """团队协调器"""
    
    def __init__(self, agents: List[LegalAgentBase]):
        self.agents = agents
    
    def distribute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """分发任务"""
        task_type = task.get('task_type')
        
        # 根据任务类型选择合适的智能体
        if '诉讼' in task_type:
            target_agent = self._find_agent('诉讼')
        elif '合同' in task_type:
            target_agent = self._find_agent('合同')
        else:
            target_agent = self._find_agent('民事')
        
        if target_agent:
            return target_agent.execute(task)
        else:
            return {'status': 'error', 'error': '无可用智能体'}
    
    def _find_agent(self, keyword: str) -> LegalAgentBase:
        """查找包含关键词的智能体"""
        for agent in self.agents:
            if keyword in agent.role:
                return agent
        return None

# 创建多个智能体
agent1 = MyLawyerAgent()
agent2 = MyLawyerAgent()

# 创建协调器
orchestrator = TeamOrchestrator([agent1, agent2])

# 分发任务
result = orchestrator.distribute_task({
    'task_type': '法律咨询',
    'question': '合同纠纷怎么处理？'
})

print(result)
```

---

## 🔧 常见问题

### Q1: 工具库文件找不到？

**A:** 检查路径是否正确，确保相对路径正确。

```python
# 错误示例
toolobox_path = "toolboxes/my_lawyer.json"  # ❌ 可能找不到

# 正确示例
toolobox_path = "../toolboxes/my_lawyer.json"  # ✅ 相对路径
```

### Q2: 智能体无法进化？

**A:** 检查反馈分数是否超过0.8。

```python
# 检查进化条件
feedback = {
    'improvement_score': 0.85  # 必须>0.8
}

if feedback['improvement_score'] > 0.8:
    agent.evolve(feedback)
```

### Q3: 知识库没有数据？

**A:** 知识库需要手动添加到JSON文件中。

```json
{
  "knowledge_base": {
    "民法典第577条": "...",
    "合同法第107条": "..."
  }
}
```

---

## 📚 下一步

- 📖 阅读[架构文档](ARCHITECTURE.md)
- 📖 阅读[API文档](API.md)
- 📖 查看[示例代码](examples/)
- 🤝 参与[贡献指南](CONTRIBUTING.md)

---

## 🎉 恭喜！

你已经成功创建了第一个AI法律智能体！

**下一步：**
1. 添加更多工具到工具库
2. 丰富知识库内容
3. 测试不同任务类型
4. 让智能体持续进化

---

**有问题？** 查看[FAQ](docs/FAQ.md)或[提交Issue](https://github.com/legal-ai-collaboration-framework/issues)

**Legal-AI-Collaboration-Framework** - 让法律AI变得简单！🚀
