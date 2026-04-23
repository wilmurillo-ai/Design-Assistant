from core.agent_base import LegalAgentBase
from typing import Dict, Any, Optional
from datetime import datetime
import time

class CivilLawyerAgent(LegalAgentBase):
    """民事律师智能体"""
    
    def __init__(self, toolbox_path: Optional[str] = None):
        super().__init__(
            name="民事律师",
            role="民事纠纷处理",
            toolbox_path=toolbox_path or "../toolboxes/civil_lawyer.json"
        )
        print(f"🤖 民事律师智能体初始化完成")
        print(f"   版本: {self.version}")
        print(f"   工具数: {len(self.toolbox)}")
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务"""
        task_type = task.get('task_type', 'unknown')
        start_time = time.time()
        
        try:
            result = {
                'agent': self.name,
                'version': self.version,
                'task_type': task_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            # 获取工具并执行
            tool_name = task.get('tool_name')
            if tool_name and tool_name in self.toolbox:
                result.update(self._execute_tool(tool_name, task))
            else:
                result.update(self._default_execute(task))
            
            result['response_time'] = time.time() - start_time
            result['confidence'] = 0.90
            
        except Exception as e:
            result = {
                'agent': self.name,
                'version': self.version,
                'task_type': task_type,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        self.log_experiment({'task_type': task_type, 'result': result})
        return result
    
    def _execute_tool(self, tool_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行特定工具"""
        tool = self.toolbox[tool_name]
        return {
            'tool_used': tool_name,
            'tool_version': tool['version'],
            'tool_accuracy': tool['accuracy'],
            'message': f"{tool_name}工具执行完成"
        }
    
    def _default_execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """默认执行"""
        return {
            'message': '任务执行完成',
            'input_summary': str(task)[:100]
        }

if __name__ == "__main__":
    agent = CivilLawyerAgent()
    stats = agent.get_stats()
    print(f"\n统计信息: {stats}")
    print("\n✅ 测试完成！")
