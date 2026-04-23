# 滑雪教程索引

本文件定义滑雪教程的级别体系、适配规则和元数据索引。技能元数据按级别拆分在 `levels/` 目录中，训练/FAQ/装备框架在独立文件中。

> **架构说明**：v3.0 动态教程生成 — 规则控质量 + Agent 生成内容。Agent 基于本文件索引 + `curriculum-skeleton.md` 协议 + 对应级别技能包动态组装教程。

---

## 元数据

```yaml
_meta:
  created: 2026-04-11
  updated: 2026-04-11
  next_review: 2026-10-11
  version: 3.0
  framework: "PSIA-AASI 级别框架（主）+ CASI/CSIA 术语对照（辅）"
  scoring: "coaching-rubric.md"
  gear: "gear-guide.md"
  disclaimer: "AI 生成内容，不能替代专业教练指导"
  architecture: "动态教程生成 — 规则控质量 + Agent 生成内容"
```

---

## 级别定义

每个级别按板型分为两个独立技能包，用户只读取自己板型的教程。

| 级别 | 名称 | 单板技能包 | 双板技能包 | 定义 | 目标分数 | 预计掌握时间 |
|------|------|-----------|-----------|------|---------|------------|
| 0 | First Time | `levels/sb-0.md` | `levels/ski-0.md` | 从未滑过或只滑过 1-2 次 | posture 3-5, turning 2-4, overall 3-5 | 1-2 个雪日 |
| 1 | Novice | `levels/sb-1.md` | `levels/ski-1.md` | 能在绿道/缓坡滑行，但转弯不流畅 | posture 5-6.5, turning 4-6, overall 5-6.5 | 3-5 个雪日 |
| 2 | Intermediate | `levels/sb-2.md` | `levels/ski-2.md` | 能流畅滑行蓝道，开始尝试黑道 | posture 6.5-7.5, turning 6-7.5, overall 6.5-7.5 | 5-10 个雪日 |
| 3 | Advanced | `levels/sb-3.md` | `levels/ski-3.md` | 黑道流畅滑行，追求技术和风格 | posture 7.5-9, turning 7.5-9, overall 7.5-9 | 持续精进 |

---

## coaching-rubric 维度映射

| coaching-rubric 维度 | 子项 | Level 0 目标 | Level 1 目标 | Level 2 目标 | Level 3 目标 |
|---------------------|------|------------|------------|------------|------------|
| 基础姿态 posture | 重心位置、膝盖弯曲、上半身姿态、手臂位置、髋部对齐、踝关节屈曲 | 3-5 | 5-6.5 | 6.5-7.5 | 7.5-9 |
| 转弯技术 turning | 平行站姿、立刃角度、换刃时机、卡宾质量、弯型控制、点杖技术 | 2-4 | 4-6 | 6-7.5 | 7.5-9 |
| 综合滑行 overall | 速度控制、路线选择、地形适应、节奏感、自信度、安全意识 | 3-5 | 5-6.5 | 6.5-7.5 | 7.5-9 |
| 自由式 freestyle | 起跳、空中控制、落地、技巧完成度、风格表现（仅 Level 3 公园/地形公园场景） | — | — | — | 7.5-9 |

**评分标准**：所有分数 1-10 分，精确到 0.5。达到目标分数下限视为该级别达标。

---

## 板型适配规则

| 维度 | 单板（snowboard） | 双板（ski） |
|------|------------------|------------|
| 入门技能 | 后刃滑行、前刃滑行、落叶飘 | 犁式制动、犁式转弯、平行滑行 |
| 核心差异 | 双脚固定在一块板上，换刃是核心 | 双脚独立，平行是核心 |
| 护具重点 | 护腕（必戴）、护臀、护膝 | 护膝（蘑菇/陡坡推荐） |
| 转弯技术 | 换刃时机、立刃角度、弯型控制 | 平行站姿、点杖技术、弯型控制 |

---

## 风格适配规则（Level 2+ 生效）

| 风格 | 核心技能 | 对应 coaching-rubric 子项 |
|------|---------|------------------------|
| 刻滑（carving） | 立刃角度、弯型控制、压力管理 | turning: edge_angle, turn_shape, carving_quality |
| 公园/平花（park） | 起跳、空中控制、落地、道具 | freestyle: 全部子项 |
| 野雪（freeride） | 地形适应、粉雪浮力、路线选择 | overall: terrain_adaptation, line_choice |
| 蘑菇（mogul） | 点杖技术、节奏感、膝盖缓冲 | turning: pole_plant, overall: rhythm |

---

## 技能包索引

| 级别 | 单板文件 | 双板文件 | 技能数 | 约行数 |
|------|---------|---------|-------|-------|
| 0 | `levels/sb-0.md` | `levels/ski-0.md` | 5 + 5 | ~150 |
| 1 | `levels/sb-1.md` | `levels/ski-1.md` | 6 + 6 | ~180 |
| 2 | `levels/sb-2.md` | `levels/ski-2.md` | 9 + 10 | ~250-280 |
| 3 | `levels/sb-3.md` | `levels/ski-3.md` | 14 + 13 | ~350 |

## 框架文件索引

| 框架 | 文件 | 内容 | 约行数 |
|------|------|------|-------|
| 训练计划 | `training.md` | 各级别天数、时长、技能顺序（含权重）、休息规则 | ~200 |
| FAQ | `faq.md` | 各级别常见问题及回答要点 | ~200 |
| 装备决策 | `gear.md` | 按级别和板型定义 must_have / recommended / consider_buy | ~150 |

---

## 国际术语对照规则（方案 C：PSIA 为主，CASI/CSIA 为补充）

### 显示规则

- **Level 0-1**：不显示术语对照，只用中文 + 英文主术语
- **Level 2+**：在核心技能（转弯技术、姿态进阶）末尾添加一行术语对照
- 术语对照不超过 2 行，不展开讲解差异
- 差异讲解放在"国际术语速查表"，用户主动询问时输出

### 术语对照格式示例

```markdown
**术语对照**：
- PSIA-AASI：Short Radius Turn / Slalom
- CASI：Short Radius Pivoted Turn
- CSIA：Short Radius Steering Turn
```

### 核心术语对照表（Level 2+ 参考）

| 技术概念 | PSIA-AASI 术语 | CASI 术语（单板） | CSIA 术语（双板） |
|---------|--------------|-----------------|-----------------|
| 基础站姿 | Athletic Stance | Neutral Stance | Balanced Stance |
| 旋转引导 | Rotary Movement | Pivoting | Steering |
| 立刃 | Edging | Edging / Inclination vs Angulation | Edging |
| 压力管理 | Pressure Control | Fore/Aft + Lateral Pressure | Fore/Aft Balance |
| 节奏 | Rhythm | Timing | Coordination & Timing |
| 反弓 | Angulation | Angulation | Angulation |
| 卡宾 | Carving | Carving | Carving |
| 搓雪转弯 | Skidded Turns | Pivoted Turns | Steering Turns |
| 综合滑行 | Overall | Coordination & Timing | Coordination |

---

## 水平校准验证问题

### 单板验证问题

| 编号 | 问题 | Level 0 期望 | Level 1 期望 | Level 2 期望 |
|------|------|------------|------------|------------|
| Q1 | 你能在绿道上完成落叶飘（左右移动方向）吗？ | 不能/刚开始练 | 能 | 能，且流畅 |
| Q2 | 你能独立完成 S 弯转弯吗？转弯之间不停顿 | 不能 | 能，但不够流畅 | 能，且流畅 |
| Q3 | 上缆车时能自己穿脱雪板吗？ | 不能/需要帮助 | 能 | 能 |
| Q4 | 你能在蓝道上控制速度吗？ | 不能 | 基本能 | 能，且轻松 |

### 双板验证问题

| 编号 | 问题 | Level 0 期望 | Level 1 期望 | Level 2 期望 |
|------|------|------------|------------|------------|
| Q1 | 你能在绿道上完成犁式转弯吗？ | 不能/刚开始练 | 能 | 已过渡到平行 |
| Q2 | 你能在蓝道上完成平行转弯吗？双板保持平行 | 不能 | 能，但不够流畅 | 能，且流畅 |
| Q3 | 上缆车时能自己穿脱雪板吗？ | 不能/需要帮助 | 能 | 能 |
| Q4 | 你能控制转弯大小（大弯和小弯）吗？ | 不能 | 基本能 | 能，且切换自如 |

---

## 文件结构

```
references/tutorial-curriculum/
├── _index.md                    # 本文件（~100 行）：级别定义、适配规则、索引
├── curriculum-skeleton.md       # 动态生成协议
├── level-common.md              # 通用内容：安全须知、雪场礼仪
├── levels/                      # 技能包（按级别+板型拆分）
│   ├── sb-0.md                  # 单板 Level 0（5 技能）
│   ├── sb-1.md                  # 单板 Level 1（6 技能）
│   ├── sb-2.md                  # 单板 Level 2（9 技能）
│   ├── sb-3.md                  # 单板 Level 3（14 技能）
│   ├── ski-0.md                 # 双板 Level 0（5 技能）
│   ├── ski-1.md                 # 双板 Level 1（6 技能）
│   ├── ski-2.md                 # 双板 Level 2（10 技能）
│   └── ski-3.md                 # 双板 Level 3（13 技能）
├── training.md                  # 训练计划框架
├── faq.md                       # FAQ 框架
└── gear.md                      # 装备决策框架
```

**读取规则**：根据用户 `board_type` 和 `level` 读取对应技能包。单板用户读 `levels/sb-{X}.md`，双板用户读 `levels/ski-{X}.md`。

---

## 维护规则

1. **复核周期**：180 天（每年雪季前复核）
2. **触发条件**：coaching-rubric.md 更新时，自动触发教程复核
3. **用户反馈**：收集"这个教程对你有帮助吗？"的反馈，低分章节标记为需要复核
4. **术语同步**：PSIA-AASI 或 CASI/CSIA 官方更新术语时，同步更新对照表
5. **技能元数据更新**：新增或删除技能时，更新对应 `levels/*.md` 文件，并同步更新 `training.md`、`faq.md`、`gear.md`
6. **动态生成质量**：每次修改技能包或生成协议后，对比旧版教程内容确保质量不低于旧版本

---

## 动态生成规则摘要（来自 curriculum-skeleton.md）

> 以下为 curriculum-skeleton.md 核心规则摘要，足够覆盖常规教程生成。完整协议（含质量检查清单、个性化适配、维护说明）见 `curriculum-skeleton.md`。

### 教程结构（按顺序，不可变）

1. **免责声明** → `⚠️ 本教程由 AI 生成...不能替代专业滑雪教练的现场指导`
2. **版本标注** → `版本：v3.0 | 架构：动态教程生成`
3. **级别标题** → `## [板型] Level [X] — [级别名称]教程`
4. **本级别适合你吗** → 基于级别定义表的"定义"列生成 3-4 句自我评估
5. **训练计划** → 表格：| 阶段 | 技能 | 时长 | 权重 | 关键目标 |
6. **核心技能详解** → 每个技能必须含 5 子章节（见下）
7. **装备清单** → 按 must_have / recommended / consider_buy / 风格专精 分类
8. **常见问题** → 基于 faq.md 的 answer_key_points 展开为 3-5 句自然语言
9. **下一步** → 级别递进指引 + 历史记录提及

### 技能讲解 5 子章节（每个技能必须完整覆盖）

| 子章节 | 数据来源 | 要求 |
|--------|---------|------|
| **为什么重要** | `why_important` | 2-3 句自然语言，说明与整体滑行的关系 |
| **怎么做** | `action_guide_template` | 分步指导至少 3 步，含身体部位具体动作 |
| **常见错误** | `common_mistakes_template` | 每个错误：错误描述 + 后果 + 纠正方法 |
| **练习方法** | `practice_template` | 具体步骤，保留数量和组数 |
| **成功信号** | `success_signal` | 1-2 句可自检描述 |

### 语言风格

- 第二人称（你），友好专业鼓励性
- 技术术语首次出现标注英文（如：反弓 Angulation）
- Level 0-1 不显示术语对照，Level 2+ 核心技能末尾附加术语对照（从 `terms` 字段读取，不超过 2 行）

### Level 3 风格路线选择

按用户 `freestyle` 偏好选择：
- `carving` → 刻滑路线（单板 L3-SB-04/05/06，双板 L3-SK-05/06/07）
- `park` / `freestyle` → 公园路线（L3-SB-07/08/09，仅单板）
- `freeride` / `powder` → 野雪路线（单板 L3-SB-10/11/12，双板 L3-SK-11/12/13）
- `mogul` → 蘑菇路线（L3-SK-08/09/10，仅双板）
- 未指定 → 全部生成但标注优先级
