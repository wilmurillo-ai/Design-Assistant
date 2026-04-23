#!/usr/bin/env python3
"""
进化内核 - 技能自进化引擎的核心

类比Linux内核，提供技能进化的基础能力
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .tracker import SkillTracker
from .analyzer import PerformanceAnalyzer
from .planner import EvolutionPlanner
from .executor import EvolutionExecutor
from .sync import CrossSkillSync


@dataclass
class KernelConfig:
    """内核配置"""
    data_dir: Path = field(default_factory=lambda: Path.home() / ".ssee")
    auto_evolve: bool = False
    sync_enabled: bool = True
    log_level: str = "INFO"
    max_backup_count: int = 10


class EvolutionKernel:
    """
    技能进化内核 - 全球技能自进化的技术底座
    
    核心职责：
    1. 提供技能进化的基础能力（追踪、分析、规划、执行、同步）
    2. 管理技能生命周期
    3. 协调技能间协同进化
    4. 提供插件化扩展机制
    """
    
    def __init__(self, config: Optional[KernelConfig] = None):
        self.config = config or KernelConfig()
        self.logger = self._setup_logging()
        
        # 初始化核心组件
        self.tracker = SkillTracker(self.config.data_dir / "tracking")
        self.analyzer = PerformanceAnalyzer(self.config.data_dir / "analysis")
        self.planner = EvolutionPlanner(self.config.data_dir / "plans")
        self.executor = EvolutionExecutor(self.config.data_dir / "backups")
        self.sync = CrossSkillSync(self.config.data_dir / "sync")
        
        # 插件注册表
        self._plugins: Dict[str, Any] = {}
        self._hooks: Dict[str, List[Callable]] = {
            "pre_track": [],
            "post_track": [],
            "pre_analyze": [],
            "post_analyze": [],
            "pre_evolve": [],
            "post_evolve": [],
        }
        
        # 内核状态
        self._initialized = False
        self._skill_registry: Dict[str, Dict] = {}
        
        self.logger.info("🚀 EvolutionKernel v2.0.0 初始化完成")
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger("SSEE.Kernel")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def initialize(self) -> bool:
        """
        初始化内核
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            # 创建数据目录
            self.config.data_dir.mkdir(parents=True, exist_ok=True)
            
            # 初始化各组件
            self.tracker.initialize()
            self.analyzer.initialize()
            self.planner.initialize()
            self.executor.initialize()
            self.sync.initialize()
            
            # 加载已注册技能
            self._load_skill_registry()
            
            self._initialized = True
            self.logger.info("✅ 内核初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 内核初始化失败: {e}")
            return False
    
    # ==================== 核心API ====================
    
    def register_skill(self, skill_id: str, skill_config: Dict) -> bool:
        """
        注册技能到进化引擎
        
        Args:
            skill_id: 技能唯一标识
            skill_config: 技能配置
            
        Returns:
            bool: 注册是否成功
        """
        if skill_id in self._skill_registry:
            self.logger.warning(f"技能 {skill_id} 已注册，更新配置")
        
        self._skill_registry[skill_id] = {
            "id": skill_id,
            "config": skill_config,
            "registered_at": datetime.now().isoformat(),
            "status": "active",
            "version": skill_config.get("version", "1.0.0"),
        }
        
        self._save_skill_registry()
        self.logger.info(f"✅ 技能 {skill_id} 注册成功")
        return True
    
    def track(self, skill_id: str, metrics: Dict[str, Any]) -> Dict:
        """
        追踪技能使用 - 系统调用
        
        Args:
            skill_id: 技能ID
            metrics: 性能指标
            
        Returns:
            Dict: 追踪结果
        """
        self._check_initialized()
        
        # 执行前置钩子
        for hook in self._hooks["pre_track"]:
            hook(skill_id, metrics)
        
        # 执行追踪
        result = self.tracker.track(skill_id, metrics)
        
        # 执行后置钩子
        for hook in self._hooks["post_track"]:
            hook(skill_id, metrics, result)
        
        return result
    
    def analyze(self, skill_id: str) -> Dict:
        """
        分析技能性能 - 系统调用
        
        Args:
            skill_id: 技能ID
            
        Returns:
            Dict: 分析结果
        """
        self._check_initialized()
        
        for hook in self._hooks["pre_analyze"]:
            hook(skill_id)
        
        # 获取追踪数据
        tracking_data = self.tracker.get_data(skill_id)
        
        # 执行分析
        result = self.analyzer.analyze(skill_id, tracking_data)
        
        for hook in self._hooks["post_analyze"]:
            hook(skill_id, result)
        
        return result
    
    def plan(self, skill_id: str, analysis_result: Optional[Dict] = None) -> Dict:
        """
        生成进化计划 - 系统调用
        
        Args:
            skill_id: 技能ID
            analysis_result: 分析结果（可选，不传则自动分析）
            
        Returns:
            Dict: 进化计划
        """
        self._check_initialized()
        
        if analysis_result is None:
            analysis_result = self.analyze(skill_id)
        
        plan = self.planner.generate(skill_id, analysis_result)
        
        return plan
    
    def evolve(self, skill_id: str, plan: Optional[Dict] = None) -> Dict:
        """
        执行技能进化 - 系统调用
        
        Args:
            skill_id: 技能ID
            plan: 进化计划（可选，不传则自动生成）
            
        Returns:
            Dict: 进化结果
        """
        self._check_initialized()
        
        for hook in self._hooks["pre_evolve"]:
            hook(skill_id, plan)
        
        if plan is None:
            plan = self.plan(skill_id)
        
        result = self.executor.execute(skill_id, plan)
        
        for hook in self._hooks["post_evolve"]:
            hook(skill_id, plan, result)
        
        return result
    
    def sync_skills(self, skill_ids: List[str]) -> Dict:
        """
        技能间同步进化 - 核心飞轮机制
        
        实现技能间的知识迁移和协同进化
        
        Args:
            skill_ids: 技能ID列表
            
        Returns:
            Dict: 同步结果
        """
        self._check_initialized()
        
        if not self.config.sync_enabled:
            self.logger.info("技能同步已禁用")
            return {"status": "disabled"}
        
        return self.sync.synchronize(skill_ids)
    
    # ==================== 插件系统 ====================
    
    def register_plugin(self, name: str, plugin: Any) -> bool:
        """注册插件"""
        self._plugins[name] = plugin
        self.logger.info(f"🔌 插件 {name} 注册成功")
        return True
    
    def add_hook(self, event: str, callback: Callable) -> bool:
        """添加钩子"""
        if event not in self._hooks:
            self.logger.error(f"未知事件类型: {event}")
            return False
        
        self._hooks[event].append(callback)
        return True
    
    # ==================== 辅助方法 ====================
    
    def _check_initialized(self):
        """检查内核是否已初始化"""
        if not self._initialized:
            raise RuntimeError("内核未初始化，请先调用 initialize()")
    
    def _load_skill_registry(self):
        """加载技能注册表"""
        registry_file = self.config.data_dir / "skill_registry.json"
        if registry_file.exists():
            with open(registry_file, 'r') as f:
                self._skill_registry = json.load(f)
    
    def _save_skill_registry(self):
        """保存技能注册表"""
        registry_file = self.config.data_dir / "skill_registry.json"
        with open(registry_file, 'w') as f:
            json.dump(self._skill_registry, f, indent=2)
    
    def get_status(self) -> Dict:
        """获取内核状态"""
        return {
            "version": "2.0.0",
            "initialized": self._initialized,
            "registered_skills": len(self._skill_registry),
            "plugins": list(self._plugins.keys()),
            "config": {
                "data_dir": str(self.config.data_dir),
                "auto_evolve": self.config.auto_evolve,
                "sync_enabled": self.config.sync_enabled,
            }
        }
