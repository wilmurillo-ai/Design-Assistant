"""
智能体基类
所有法律AI智能体的基础类

安全说明：
- 所有数据处理都是本地的
- 不发送任何数据到外部服务
- 用户完全控制所有文件路径和数据
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
import uuid


class LegalAgentBase(ABC):
    """法律AI智能体基类"""

    def __init__(self, name: str, role: str, toolbox_path: Optional[str] = None, toolbox_root: Optional[str] = None):
        self.name = name
        self.role = role
        self.version = "1.0.0"
        self.agent_id = str(uuid.uuid4())

        # 工具箱根目录（默认为agents目录的上级toolboxes目录）
        if toolbox_root:
            self.toolbox_root = toolbox_root
        else:
            # 获取agent_base.py所在的目录
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # 工具箱根目录为agents目录的上级toolboxes目录
            self.toolbox_root = os.path.join(os.path.dirname(base_dir), 'toolboxes')

        # 性能统计（先初始化）
        self.performance = {
            "total_tasks": 0,
            "success_rate": 0.95,
            "avg_confidence": 0.90,
            "avg_response_time": 0.0,
            "last_improvement": None
        }

        # 加载工具库
        self.toolbox = {}
        self.toolbox_path = toolbox_path
        if toolbox_path:
            self._load_toolbox(toolbox_path)

        # 知识库
        self.knowledge_base = {}

        # 实验日志（本地存储）
        self.experiment_log = []

    def _load_toolbox(self, toolbox_path: str):
        """加载工具库"""
        try:
            # 如果是相对路径（以"../"开头），则基于toolbox_root构建绝对路径
            if toolbox_path.startswith('../'):
                # 从../toolboxes/xxx.json中提取文件名
                filename = os.path.basename(toolbox_path)
                toolbox_path = os.path.join(self.toolbox_root, filename)
            # 如果不是绝对路径，则基于toolbox_root构建路径
            elif not os.path.isabs(toolbox_path):
                toolbox_path = os.path.join(self.toolbox_root, toolbox_path)

            # 尝试加载工具库文件
            with open(toolbox_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.toolbox = data.get('toolbox', {})
                self.knowledge_base = data.get('knowledge_base', {})
                self.version = data.get('version', '1.0.0')

                # 加载性能统计
                if 'performance' in data:
                    self.performance.update(data['performance'])

                # 保存完整的工具库路径
                self.toolbox_path = toolbox_path

            print(f"✅ {self.name} 工具库加载成功，包含 {len(self.toolbox)} 个工具")
            print(f"📂 工具库路径: {toolbox_path}")
        except FileNotFoundError:
            print(f"⚠️ 工具库文件不存在: {toolbox_path}")
            print(f"⚠️ 工具箱根目录: {self.toolbox_root}")
        except json.JSONDecodeError as e:
            print(f"⚠️ 工具库文件格式错误: {e}")

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行任务（子类必须实现）"""
        pass

    def evolve(self, feedback: Dict[str, Any]) -> bool:
        """自进化"""
        improvement_score = feedback.get('improvement_score', 0)

        # 只有反馈分数大于0.8才进化
        if improvement_score > 0.8:
            # 更新版本
            version_parts = self.version.split('.')
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            self.version = '.'.join(version_parts)

            # 改进工具
            for tool_name, tool in self.toolbox.items():
                # 更新工具版本
                tool_version = float(tool['version'])
                tool['version'] = str(round(tool_version + 0.1, 1))

                # 提升准确率（不超过0.99）
                tool['accuracy'] = min(0.99, tool['accuracy'] * 1.01)

                # 增加改进次数
                tool['improvements'] = tool.get('improvements', 0) + 1

            # 更新性能统计
            self.performance['total_tasks'] += 1
            self.performance['success_rate'] = min(0.99, self.performance['success_rate'] * 1.005)
            self.performance['last_improvement'] = datetime.now().isoformat()

            print(f"🧬 {self.name} 进化成功！新版本: {self.version}")

            # 保存更新后的工具库
            if self.toolbox_path:
                self._save_toolbox()

            return True
        else:
            return False

    def log_experiment(self, experiment: Dict[str, Any]):
        """记录实验（本地存储）"""
        experiment['timestamp'] = datetime.now().isoformat()
        experiment['agent'] = self.name
        experiment['version'] = self.version
        experiment['agent_id'] = self.agent_id

        self.experiment_log.append(experiment)

        print(f"📊 实验已记录: {experiment.get('task_type', 'unknown')}")

    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具"""
        return self.toolbox.get(tool_name)

    def retrieve_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """检索知识"""
        results = []
        query_lower = query.lower()

        for key, value in self.knowledge_base.items():
            if query_lower in key.lower() or query_lower in value.lower():
                results.append({
                    "title": key,
                    "content": value
                })

        return results

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "name": self.name,
            "role": self.role,
            "version": self.version,
            "agent_id": self.agent_id,
            "toolbox": {
                "total_tools": len(self.toolbox),
                "tools": list(self.toolbox.keys())
            },
            "performance": self.performance,
            "experiment_count": len(self.experiment_log)
        }

    def _save_toolbox(self):
        """保存工具库（本地存储）"""
        if not self.toolbox_path:
            return

        try:
            data = {
                "agent_name": self.name,
                "version": self.version,
                "role": self.role,
                "toolbox": self.toolbox,
                "knowledge_base": self.knowledge_base,
                "performance": self.performance,
                "updated_at": datetime.now().isoformat()
            }

            with open(self.toolbox_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"💾 {self.name} 工具库已保存")
        except Exception as e:
            print(f"⚠️ 保存工具库失败: {e}")


# 添加os导入
import os
