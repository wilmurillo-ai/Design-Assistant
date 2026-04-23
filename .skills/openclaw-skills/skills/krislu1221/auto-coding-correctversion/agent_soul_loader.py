#!/usr/bin/env python3
"""
Auto-Coding Agent 人格 Prompt 加载器

功能：
1. 从 agency-agents-zh 加载编程、UI 设计、提示词相关的人格 Prompt
2. 提供 Agent Soul 查询接口
3. 支持自定义 Agent Prompt
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class AgentSoulLoader:
    """Agent 人格 Prompt 加载器"""
    
    # 需要的 Agent 类别
    REQUIRED_CATEGORIES = [
        "engineering",      # 编程相关
        "design",          # UI 设计相关
        "testing",         # 测试相关
        "product",         # 产品相关
    ]
    
    # 需要的具体 Agent（从每个类别中筛选）
    # 注意：Agent 文件名已经包含类别前缀，如 engineering-frontend-developer.md
    REQUIRED_AGENTS = {
        "engineering": [
            "engineering/engineering-frontend-developer",
            "engineering/engineering-backend-architect",
            "engineering/engineering-software-architect",
            "engineering/engineering-code-reviewer",
            "engineering/engineering-senior-developer",
        ],
        "design": [
            "design/design-ui-designer",
            "design/design-ux-architect",
        ],
        "testing": [
            "testing/testing-qa-engineer",
            "testing/testing-api-tester",
        ],
        "product": [
            "product/product-manager",
        ]
    }
    
    def __init__(self, agency_path: str = None):
        """
        初始化加载器
        
        Args:
            agency_path: agency-agents-zh 路径（可选，默认自动查找）
        """
        self.agency_path = Path(agency_path) if agency_path else self._find_agency_path()
        self.loaded_souls: Dict[str, Dict] = {}
        
        # 自动加载
        self._load_required_agents()
    
    def _find_agency_path(self) -> Path:
        """自动查找 agency-agents 路径
        
        只读取编程相关的 Agent 人格（engineering/design/testing/product）
        不读取其他技能的 prompt 文件
        """
        # 支持通过环境变量指定路径
        env_path = Path.home() / ".auto-coding" / "agency-agents"
        if env_path.exists():
            print(f"✅ 找到 agency-agents (环境变量): {env_path}")
            return env_path
        
        possible_paths = [
            # 其他可能路径（使用 Path.home() 避免硬编码）
            Path.home() / ".enhance-claw" / "instances" / "虾软" / "workspace" / "skills" / "agency-agents",
            Path.home() / ".enhance-claw" / "instances" / "虾总" / "workspace" / "skills" / "agency-agents-zh",
            Path.home() / ".openclaw" / "workspace" / "skills" / "agency-agents-zh",
            Path.home() / ".agents" / "skills" / "agency-agents-zh",
            Path(__file__).parent.parent / "agency-agents-zh",
            Path(__file__).parent / "agency-agents-zh",
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"✅ 找到 agency-agents: {path}")
                return path
        
        # 如果都找不到，返回第一个（会触发降级）
        print(f"⚠️  未找到 agency-agents，使用默认路径")
        return possible_paths[0]
    
    def _load_required_agents(self):
        """加载需要的 Agent"""
        for category in self.REQUIRED_CATEGORIES:
            category_path = self.agency_path / category
            
            if not category_path.exists():
                print(f"⚠️  类别目录不存在：{category_path}")
                continue
            
            # 加载该类别下需要的 Agent
            required_agents = self.REQUIRED_AGENTS.get(category, [])
            
            # 扫描目录下所有 .md 文件
            for agent_file in category_path.glob("*.md"):
                agent_id = f"{category}/{agent_file.stem}"
                
                # 只加载需要的 Agent
                if agent_id in required_agents:
                    soul = self._load_agent_soul(agent_file)
                    if soul:
                        self.loaded_souls[agent_id] = soul
                        print(f"✅ 加载 Agent: {agent_id}")
        
        print(f"✅ 已加载 {len(self.loaded_souls)} 个 Agent Soul")
    
    def _load_agent_soul(self, agent_file: Path) -> Optional[Dict]:
        """
        从文件加载 Agent Soul
        
        Args:
            agent_file: Agent Markdown 文件路径
        
        Returns:
            Agent Soul 字典
        """
        try:
            content = agent_file.read_text(encoding='utf-8')
            
            # 解析 Markdown frontmatter
            soul = self._parse_frontmatter(content)
            
            if soul:
                soul['id'] = agent_file.stem
                soul['file'] = str(agent_file)
                return soul
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  加载 Agent Soul 失败：{agent_file} - {e}")
            return None
    
    def _parse_frontmatter(self, content: str) -> Optional[Dict]:
        """
        解析 Markdown frontmatter
        
        格式:
        ---
        name: DevAgent
        role: Developer
        expertise: ["architecture", "implementation"]
        ---
        """
        if not content.startswith('---'):
            return None
        
        try:
            # 提取 frontmatter 部分
            end_index = content.find('---', 3)
            if end_index == -1:
                return None
            
            frontmatter = content[4:end_index].strip()
            
            # 简单解析 YAML（不使用 yaml 库避免依赖）
            soul = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 解析数组
                    if value.startswith('[') and value.endswith(']'):
                        value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]
                    
                    soul[key] = value
            
            # 提取 system prompt（frontmatter 之后的内容）
            soul['system'] = content[end_index+3:].strip()
            
            return soul
            
        except Exception as e:
            print(f"⚠️  解析 frontmatter 失败：{e}")
            return None
    
    def get_agent_soul(self, agent_id: str) -> Optional[Dict]:
        """
        获取 Agent Soul
        
        Args:
            agent_id: Agent ID（如 "engineering/engineering-frontend-developer"）
        
        Returns:
            Agent Soul 字典
        """
        # 尝试精确匹配
        if agent_id in self.loaded_souls:
            return self.loaded_souls[agent_id]
        
        # 尝试模糊匹配（去掉前缀）
        for soul_id, soul in self.loaded_souls.items():
            if agent_id in soul_id or soul_id.endswith(agent_id):
                return soul
        
        # 未找到
        return None
    
    def list_available_agents(self) -> List[str]:
        """列出所有可用的 Agent ID"""
        return list(self.loaded_souls.keys())
    
    def get_agents_by_category(self, category: str) -> List[Dict]:
        """
        按类别获取 Agent
        
        Args:
            category: 类别名称（engineering/design/scripts）
        
        Returns:
            Agent Soul 列表
        """
        return [
            soul for soul_id, soul in self.loaded_souls.items()
            if soul_id.startswith(category)
        ]


# 快捷函数
def load_agent_soul(agent_id: str, agency_path: str = None) -> Optional[Dict]:
    """快捷加载 Agent Soul"""
    loader = AgentSoulLoader(agency_path)
    return loader.get_agent_soul(agent_id)


def list_agents(agency_path: str = None) -> List[str]:
    """快捷列出所有 Agent"""
    loader = AgentSoulLoader(agency_path)
    return loader.list_available_agents()


# 测试
if __name__ == "__main__":
    print("🧪 Agent Soul Loader 测试")
    print("="*60)
    
    loader = AgentSoulLoader()
    
    print(f"\n📂 Agency 路径：{loader.agency_path}")
    print(f"✅ 已加载 Agent 数：{len(loader.loaded_souls)}")
    
    print(f"\n📋 可用 Agent 列表:")
    for agent_id in loader.list_available_agents():
        print(f"  - {agent_id}")
    
    print(f"\n🔍 测试获取 Agent Soul:")
    test_agent = "engineering/engineering-frontend-developer"
    soul = loader.get_agent_soul(test_agent)
    
    if soul:
        print(f"  ✅ 找到：{soul.get('name', 'Unknown')}")
        print(f"  角色：{soul.get('role', 'Unknown')}")
        print(f"  专长：{soul.get('expertise', [])}")
    else:
        print(f"  ❌ 未找到：{test_agent}")
    
    print("\n" + "="*60)
