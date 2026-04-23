"""
技能自进化引擎核心 (Skill Self-Evolution Engine Core)

全球AI技能基础设施 - 技术底座
"""

from .kernel import EvolutionKernel, KernelConfig
from .tracker import SkillTracker
from .analyzer import PerformanceAnalyzer
from .planner import EvolutionPlanner
from .executor import EvolutionExecutor
from .sync import CrossSkillSync

__version__ = "2.0.0"
__all__ = [
    "EvolutionKernel",
    "KernelConfig",
    "SkillTracker", 
    "PerformanceAnalyzer",
    "EvolutionPlanner",
    "EvolutionExecutor",
    "CrossSkillSync",
]
