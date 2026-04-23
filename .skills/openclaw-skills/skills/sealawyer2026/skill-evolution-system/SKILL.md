---
name: skill-evolution-system
version: 2.0.0
description: |
  技能自进化引擎 (Skill Self-Evolution Engine) - 全球AI技能基础设施
  
  从技能进化系统升级为技术底座，支持多平台、多技能协同进化。
  实现技能间正向演化飞轮：引擎越厉害 -> 技能同步越厉害 -> 越用越进化。
  
  使用场景:
  1. 技能自进化引擎内核管理
  2. 跨平台技能同步进化
  3. 技能间知识迁移和协同
  4. 数据飞轮驱动的持续优化
  5. 开放API接入全球技能生态
  
  当用户询问以下问题时激活:
  - "技能自进化引擎"
  - "全球技能基础设施"
  - "技能间协同进化"
  - "AI技能技术底座"
  - "多平台技能适配"
  - "Skill Evolution Protocol"
---

# 🧬 技能进化系统

让29类技能自我学习、自动优化、持续进化。

## 核心理念

技能不是静态的，而是应该随着使用不断进化：
- **越用越聪明** - 根据使用模式优化响应策略
- **越用越完善** - 基于用户反馈补全功能短板
- **越用越高效** - 通过数据分析提升执行效率
- **自动迭代** - 无需人工干预的持续进化

## 系统架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  数据收集   │ -> │  性能分析   │ -> │  计划生成   │ -> │  自动更新   │
│  Tracker    │    │  Analyzer   │    │  Planner    │    │  Updater    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       ^                                                    |
       └──────────────── 报告生成 <────────────────────────┘
```

## 快速开始

### 1. 追踪技能使用

每次使用技能时记录数据：

```bash
python scripts/track_usage.py record <skill-name>
```

更新执行结果：

```bash
python scripts/track_usage.py update <record-id> <success> [satisfaction]
```

收集用户反馈：

```python
# 在代码中调用
from scripts.track_usage import SkillUsageTracker

tracker = SkillUsageTracker()
tracker.collect_feedback(
    skill_name="skill-name",
    feedback_type="improvement",  # improvement, bug, suggestion
    details="用户反馈内容",
    rating=4  # 1-5分
)
```

### 2. 分析技能性能

分析单个技能：

```bash
python scripts/analyze_performance.py analyze <skill-name>
```

分析所有技能：

```bash
python scripts/analyze_performance.py analyze-all
```

比较多个技能：

```bash
python scripts/analyze_performance.py compare <skill1> <skill2> <skill3>
```

### 3. 生成进化计划

为单个技能生成计划：

```bash
python scripts/generate_evolution_plan.py plan <skill-name>
```

批量生成计划：

```bash
# 所有技能
python scripts/generate_evolution_plan.py batch

# 指定技能
python scripts/generate_evolution_plan.py batch skill1 skill2 skill3
```

### 4. 执行自动更新

更新单个技能（试运行）：

```bash
python scripts/auto_update_skill.py update <skill-name> --dry-run
```

正式更新：

```bash
python scripts/auto_update_skill.py update <skill-name>
```

批量更新：

```bash
python scripts/auto_update_skill.py batch --dry-run
```

回滚更新：

```bash
python scripts/auto_update_skill.py rollback <skill-name> [timestamp]
```

### 5. 生成进化报告

完整报告：

```bash
python scripts/generate_report.py
```

单个技能报告：

```bash
python scripts/generate_report.py skill <skill-name>
```

## 数据存储

所有数据存储在 `~/.openclaw/workspace/skills/.evolution-data/`：

- `usage_stats.json` - 使用统计数据
- `feedback.json` - 用户反馈
- `analysis_results.json` - 分析结果
- `evolution_plans.json` - 进化计划
- `backups/` - 技能备份

## 工作流程

### 日常使用流程

```
1. 技能被使用时 -> 自动记录使用数据
2. 技能执行完成后 -> 更新成功/失败状态
3. 用户反馈时 -> 记录改进建议
4. 定期（如每周）-> 运行分析脚本
5. 基于分析 -> 生成进化计划
6. 审核计划 -> 执行自动更新
7. 更新后 -> 生成报告查看效果
```

### 自动化集成

可以将以下命令添加到定时任务（cron）：

```bash
# 每小时追踪
0 * * * * cd ~/.openclaw/workspace/skills/skill-evolution-system && python scripts/track_usage.py list

# 每周分析
0 9 * * 1 cd ~/.openclaw/workspace/skills/skill-evolution-system && python scripts/analyze_performance.py analyze-all

# 每月生成报告
0 10 1 * * cd ~/.openclaw/workspace/skills/skill-evolution-system && python scripts/generate_report.py > monthly_report.md
```

## 评估指标

系统追踪以下关键指标：

| 指标 | 说明 | 健康阈值 |
|------|------|----------|
| 成功率 | 成功执行的比例 | > 80% |
| 响应时间 | 平均执行时长 | < 30秒 |
| 用户满意度 | 1-5分评价 | > 3.5 |
| 使用频率 | 单位时间使用次数 | 持续增长 |
| 健康度评分 | 综合评分 (0-100) | > 70 |

## 进化策略

### 自动优化类型

1. **性能优化**
   - 识别慢速操作
   - 添加缓存机制
   - 优化脚本效率

2. **可靠性提升**
   - 添加错误处理
   - 完善边界情况
   - 增加重试逻辑

3. **功能增强**
   - 实现用户建议
   - 补全缺失功能
   - 优化交互流程

4. **文档更新**
   - 同步最新功能
   - 添加使用示例
   - 更新最佳实践

### 优先级算法

```
紧急 > 高 > 中 > 低

紧急: 成功率 < 60% 或 严重错误
高: 成功率 60-80% 或 性能问题
中: 功能建议或体验优化
低: 文档更新或代码重构
```

## 使用示例

### 场景1: 新技能上线监控

```bash
# 上线后立即开始追踪
python scripts/track_usage.py record my-new-skill

# 每天检查表现
python scripts/analyze_performance.py analyze my-new-skill

# 一周后生成改进计划
python scripts/generate_evolution_plan.py plan my-new-skill
```

### 场景2: 批量技能优化

```bash
# 分析所有技能
python scripts/analyze_performance.py analyze-all > analysis.json

# 找出表现最差的3个技能
# 生成批量进化计划
python scripts/generate_evolution_plan.py batch underperforming-skill1 skill2 skill3

# 执行更新
python scripts/auto_update_skill.py batch underperforming-skill1 skill2 skill3 --dry-run
python scripts/auto_update_skill.py batch underperforming-skill1 skill2 skill3
```

### 场景3: 定期健康检查

```bash
# 生成月度报告
python scripts/generate_report.py > report_$(date +%Y%m).md

# 检查需要关注的技能
grep "🔴" report_*.md
```

## 扩展开发

### 添加自定义分析维度

编辑 `scripts/analyze_performance.py`，在 `_identify_bottlenecks` 方法中添加：

```python
# 自定义检查
if self._check_custom_metric(records):
    bottlenecks.append({
        "type": "custom_issue",
        "severity": "medium",
        "description": "发现自定义问题"
    })
```

### 集成到技能调用流程

在其他技能的脚本中集成追踪：

```python
import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/skill-evolution-system')
from scripts.track_usage import SkillUsageTracker

tracker = SkillUsageTracker()
record_id = tracker.record_usage("current-skill", {"context": "info"})

try:
    # 执行技能逻辑
    result = do_work()
    tracker.update_result(record_id, success=True, satisfaction=5)
except Exception as e:
    tracker.update_result(record_id, success=False)
    raise
```

## 最佳实践

1. **持续追踪** - 每次技能调用都记录数据
2. **及时反馈** - 鼓励用户提供使用反馈
3. **定期分析** - 建议每周运行一次分析
4. **小步快跑** - 优先执行紧急和高优先级更新
5. **备份意识** - 自动更新前会自动备份，但重要更新建议手动备份
6. **效果验证** - 更新后观察指标变化，必要时回滚

## 故障排除

### 数据文件损坏

```bash
# 重置数据（谨慎操作！）
rm ~/.openclaw/workspace/skills/.evolution-data/*.json
```

### 备份恢复

```bash
# 列出可用备份
ls ~/.openclaw/workspace/skills/.evolution-data/backups/

# 回滚特定技能
python scripts/auto_update_skill.py rollback <skill-name> <timestamp>
```

### 性能问题

如果数据量过大影响性能：

```python
# 在 track_usage.py 中调整保留记录数
self.data[skill_name] = self.data[skill_name][-500:]  # 改为保留500条
```

---

# 🌍 SSE Core v2.0 - 技能自进化引擎

## 全球AI技能基础设施

技能进化系统已升级为**技能自进化引擎 (Skill Self-Evolution Engine)**，成为全球AI技能的技术底座。

### 核心理念升级

**引擎飞轮效应**：
```
引擎越厉害 → 技能同步越厉害 → 越用越进化 → 引擎更厉害
     ↑___________________________________________|
```

### 新架构

```
┌─────────────────────────────────────────────────────────────┐
│                     AI 应用层                                │
│    (OpenClaw, GPTs, 钉钉, 飞书, 腾讯, 智谱, 文心...)        │
├─────────────────────────────────────────────────────────────┤
│                    SSE Core v2.0                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              技能自进化引擎 (SSEE)                   │   │
│  │                                                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │ 进化内核  │  │ 适配中间件│  │ 数据飞轮 │         │   │
│  │  │  Core    │  │ Adapter  │  │ Flywheel │         │   │
│  │  └──────────┘  └──────────┘  └──────────┘         │   │
│  │                                                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│  │  │ SEP协议  │  │ 认证体系 │  │ 共享网络 │         │   │
│  │  │Protocol  │  │   Auth   │  │ Network  │         │   │
│  │  └──────────┘  └──────────┘  └──────────┘         │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                     模型层                                   │
│    (GPT-4, Claude, DeepSeek, 文心一言...)                   │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

| 组件 | 功能 | 状态 |
|------|------|------|
| EvolutionKernel | 进化内核主类，提供追踪/分析/规划/执行/同步API | ✅ |
| SkillTracker | 使用数据追踪 | ✅ |
| PerformanceAnalyzer | 性能分析，瓶颈识别，健康评分 | ✅ |
| EvolutionPlanner | 进化计划生成 | ✅ |
| EvolutionExecutor | 计划执行，自动备份 | ✅ |
| CrossSkillSync | 技能间协同进化（飞轮核心） | ✅ |

### 多平台适配

| 平台 | 适配器 | 状态 |
|------|--------|------|
| OpenClaw | OpenClawAdapter | ✅ 已验证 |
| GPTs | GPTsAdapter | ✅ 框架完成 |
| 钉钉 | DingTalkAdapter | ✅ API实现 |
| 飞书 | FeishuAdapter | ✅ API实现 |

### 技能间协同进化

**核心机制**：技能A的进化经验自动同步给技能B、C、D...

```
技能A进化 ─┐
技能B进化 ─┼→ 引擎学习 → 发现共性模式 → 所有技能同步受益
技能C进化 ─┘
```

### 快速开始 SSE Core

```python
from ssee.core import EvolutionKernel, KernelConfig
from pathlib import Path

# 初始化内核
config = KernelConfig(
    data_dir=Path("~/.ssee"),
    sync_enabled=True,
)
kernel = EvolutionKernel(config)
kernel.initialize()

# 注册技能
kernel.register_skill("my-skill", {"version": "1.0.0"})

# 追踪使用
kernel.track("my-skill", {
    "duration": 1.5,
    "success": True,
})

# 分析性能
analysis = kernel.analyze("my-skill")

# 生成进化计划
plan = kernel.plan("my-skill", analysis)

# 执行进化
result = kernel.evolve("my-skill", plan)

# 技能间同步
kernel.sync_skills(["skill-a", "skill-b", "skill-c"])
```

### 多平台连接

```python
from ssee.adapters import AdapterRegistry

# 获取适配器
adapter = AdapterRegistry.get("dingtalk")
adapter.connect()  # 需要配置 app_key/secret

# 获取技能列表
skills = adapter.get_skill_list()

# 追踪使用
adapter.track_skill_usage("skill-id", metrics)
```

### SEP v1.0 - Skill Evolution Protocol

标准化的技能进化协议：

```yaml
端点:
  POST /v1/track      - 追踪技能使用
  GET  /v1/analyze    - 分析技能性能
  POST /v1/plan       - 生成进化计划
  POST /v1/evolve     - 执行技能进化
  POST /v1/sync       - 技能间同步
  GET  /v1/status     - 获取引擎状态
```

### 全球化愿景

**成为AI技能领域的技术底座**：

- **Phase 1**: 内核重构 ✅ (已完成)
- **Phase 2**: 多平台集成 🚀 (进行中)
- **Phase 3**: 标准制定 (2026 Q3)
- **Phase 4**: 全球基础设施 (2026 Q4+)

### 状态：v2.0.0 已发布

- ✅ 6个核心组件
- ✅ 4个平台适配器
- ✅ 数据飞轮层
- ✅ SEP协议 v1.0
- ✅ REST API
- ✅ 8个单元测试全部通过
- ✅ 演示验证成功
