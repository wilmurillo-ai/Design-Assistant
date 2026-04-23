# Module 6: Ski Tutorial — 滑雪教程

**触发词**：新手教程、怎么学滑雪、进阶指南、刻滑怎么练、公园怎么练、ski tutorial, beginner guide, learn to ski, how to snowboard

**加载知识**：
- 必须读取 `references/tutorial-curriculum/_index.md`（级别定义、适配规则、技能包索引、coaching-rubric 维度映射表、**动态生成规则摘要**）
- 首次生成教程时可按需读取 `references/tutorial-curriculum/curriculum-skeleton.md`（完整动态生成协议，含质量检查清单、个性化适配），常规请求 _index.md 中的规则摘要已足够
- 按需读取 `references/tutorial-curriculum/levels/sb-{X}.md`（单板）或 `levels/ski-{X}.md`（双板）（对应级别技能包）
- 按需读取 `references/tutorial-curriculum/training.md`（167 行，文件短可直接读取，或按 `training_framework_snowboard.level_X` / `training_framework_ski.level_X` 定位）
- 按需读取 `references/tutorial-curriculum/faq.md`（119 行，文件短可直接读取，或按 `faq_snowboard.level_X` / `faq_ski.level_X` 定位）
- 按需读取 `references/tutorial-curriculum/gear.md`（57 行，文件短可直接读取，或按 `gear_framework.level_X` 定位）
- 按需读取 `references/tutorial-curriculum/level-common.md`（通用内容：安全须知、雪场礼仪）
- 引用 `references/gear-guide.md`（装备推荐，作为 gear.md 的补充）
- **不读取** `references/coaching-rubric.md`（评分维度映射已内嵌到 _index.md）
- 旧版 level 文件（`legacy-backup/`）已在 v3.0 重构中清理，git 历史已保存

> **读取策略**：`_index.md` 和 `levels/{board}-{level}.md` 无依赖关系，**必须并行读取**。training.md / faq.md / gear.md 文件较短（<200 行），可直接读取。常规教程请求不需要读 curriculum-skeleton.md（规则摘要已在 _index.md 中）。

---

## MUST 步骤（不可跳过，跳过须告知用户原因）

### 场景 A：主动请求教程（"给我一份新手教程"、"怎么学滑雪"）

1. **确认板型**：询问用户是单板（snowboard）还是双板（ski）。如 `~/.ski-assistant/user_profile.json` 中有 `board_type` 字段可直接使用
2. **确认水平**：从 `~/.ski-assistant/user_profile.json` 读取 `level`。如无记录或用户表述模糊，执行场景 C 水平校准
3. **读取教程索引**：读取 `references/tutorial-curriculum/_index.md` 获取级别定义、技能骨架、训练框架、FAQ 框架、装备框架、**动态生成规则摘要**
4. **读取对应级别技能包**：并行读取 `levels/sb-{X}.md`（单板）或 `levels/ski-{X}.md`（双板）
5. **读取通用内容**：读取 `references/tutorial-curriculum/level-common.md`（安全须知、雪场礼仪等通用内容）
6. **动态生成教程**：按 `_index.md` 中的动态生成规则摘要，从技能包元数据动态生成教程内容
   - 从技能元数据读取 why_important / action_guide_template / common_mistakes_template / practice_template / success_signal
   - 从 training.md 读取训练计划，从 faq.md 读取 FAQ 要点，从 gear.md 读取装备决策规则
   - **仅当需要质量检查清单或个性化适配时**，才读取 `curriculum-skeleton.md` 获取完整协议
7. **个性化调整**：根据 `~/.ski-assistant/user_profile.json` 的 `style/freestyle` 偏好和 `~/.ski-assistant/records.json` 的历史评分，调整技能顺序和重点
8. **输出教程**：按下方"输出格式 - 场景 A"输出
9. **引导闭环**：末尾引导用户"完成后发视频给 AI 教练打分验证"

> **备用方案**：如动态生成失败（如 `_index.md` 技能元数据不完整），回退到读取 `levels/sb-{X}.md`（单板）或 `levels/ski-{X}.md`（双板），并告知用户"教程正在更新中，当前显示旧版内容"。

### 场景 B：教练推荐教程（从 coaching 场景 A 流转）

1. AI 教练打分后，对比当前级别目标分数（从 `_index.md` 的 coaching-rubric 维度映射表读取）
2. 找出低于目标分的维度
3. 从 `_index.md` 的技能骨架中定位对应 `rubric_mapping` 的技能
4. 推荐对应教程章节（"你的转弯技术 5.0/10，Level 1 目标 6.0，建议参考 Level 1 教程 — 转弯技术章节"）
5. 用户同意后，按 `curriculum-skeleton.md` 规则动态生成对应技能讲解

### 场景 C：水平校准

当用户自评水平与实际情况可能不符时，执行 2-3 个验证问题：

**单板验证问题**：
1. "你能在绿道上完成落叶飘（左右移动方向）吗？"
2. "你能独立完成 S 弯转弯吗？转弯之间不停顿"
3. "上缆车时能自己穿脱雪板吗？"

**双板验证问题**：
1. "你能在绿道上完成平行转弯吗？双板保持平行"
2. "你能控制转弯大小（大弯和小弯）吗？"
3. "上缆车时能自己穿脱雪板吗？"

根据回答判断真实水平：
- 3 个都"能" → 确认用户自评
- 2 个"能" → 可能是用户自评，建议从该级别开始
- 1 个或 0 个"能" → 温和建议降低级别

### 场景 D：查看教程目录（"教程都有哪些级别？"）

1. 读取 `_index.md` 获取级别列表
2. 按下方"输出格式 - 场景 D"输出
3. 根据用户档案标记当前建议级别

---

## 输出格式

### 场景 A：教程内容输出

> 以下格式定义教程的最终输出结构。具体内容由 `curriculum-skeleton.md` 协议驱动，从 `_index.md` 的技能骨架动态生成。

必须包含以下九部分，顺序不可变：

**1. 免责声明**（必须放在最开头）

> ⚠️ 本教程由 AI 生成，基于 PSIA-AASI 教学框架和 AI 电子教练评分标准生成，不能替代专业滑雪教练的现场指导。滑雪有风险，请在安全环境下学习，佩戴头盔，购买滑雪专项保险。

**2. 版本标注**

格式：`版本：v3.0 | 架构：动态教程生成`

**3. 级别标题**

格式：`## [板型] Level [X] — [级别名称]教程`

**4. 本级别适合你吗**

基于 `_index.md` 中级别定义的"定义"列，生成 3-4 句自我评估引导。

**5. 训练计划**

基于 `_index.md` 的 `training_framework` 生成天数、时长、技能顺序表格。

必须包含以下列：

| 阶段 | 技能 | 时长 | 权重 | 关键目标 |
|------|------|------|------|---------|

**6. 核心技能详解**

每个技能必须包含以下 5 个子章节（按 `curriculum-skeleton.md` 规则 1）：

- **为什么重要**：基于 `why_important` 展开为 2-3 句自然语言
- **怎么做**：基于 `action_guide_template` 展开为分步指导（至少 3 步）
- **常见错误**：基于 `common_mistakes_template` 展开为「错误 + 后果 + 纠正」三段式
- **练习方法**：基于 `practice_template` 展开为具体步骤，保留数量和组数
- **成功信号**：基于 `success_signal` 展开为可自检的描述

Level 2+ 核心技能在末尾附加术语对照（从技能的 `terms` 字段读取）。

**7. 装备清单**

基于 `_index.md` 的 `gear_framework` 按优先级分类生成。

**8. 常见问题**

基于 `_index.md` 的 `faq_framework` 生成 5-8 个自然语言问答。

**9. 下一步**

基于级别递进关系生成进阶指引。如有 `~/.ski-assistant/records.json` 历史记录，提及上次进度。

如任一项因信息不足无法提供，写明原因，不可省略不告知。

### 场景 B：教练推荐教程

输出格式：

| 维度 | 得分 | 目标 | 状态 |
|------|------|------|------|
| 基础姿态 | X/10 | ≥ X | ✅/⚠️ |
| 转弯技术 | X/10 | ≥ X | ✅/⚠️ |
| 综合滑行 | X/10 | ≥ X | ✅/⚠️ |
| 自由式 | X/10 | ≥ X | ✅/⚠️/— |

注：自由式仅在公园/mogul/跳台场景评分，普通雪道显示"—"。

**重点关注**：[低于目标的维度]

📚 **建议参考教程**：[Level X 教程 — 具体章节]

核心练习：
1. ...
2. ...

练完后再发视频给我重新打分。

### 场景 C：水平校准

输出验证问题表格，根据回答判断水平，温和建议合适的起始级别。

### 场景 D：教程目录

| 级别 | 适合人群 | 核心能力 | 预计掌握时间 |
|------|---------|---------|------------|
| Level 0 — 零基础 | ... | ... | ... |

**当前状态**：你的用户档案显示 level=XXX，建议从 Level X 开始。

---

## 数据适配规则

从 `_index.md` 读取适配规则，根据以下维度动态调整教程内容：

| 维度 | 数据源 | 影响内容 |
|------|--------|---------|
| board_type | `~/.ski-assistant/user_profile.json` | 选择 `skills_snowboard_level_X` 或 `skills_ski_level_X` |
| style / freestyle | `~/.ski-assistant/user_profile.json` | Level 3 选择风格路线（carving / freestyle / powder / mogul） |
| level | `~/.ski-assistant/user_profile.json` | 决定读取哪个级别的技能骨架 |
| snow_hours / ski_days | `~/.ski-assistant/user_profile.json` / `~/.ski-assistant/records.json` | 跳过已掌握的阶段 |
| 最近评分 | `~/.ski-assistant/records.json` | 弱项强化：找出评分最低的子项，在对应技能讲解中增加针对性建议 |

---

## 输出规则

1. **免责声明不可省略**：每次输出教程必须在开头包含免责声明
2. **版本标注不可省略**：在免责声明后立即标注版本
3. **板型适配**：根据用户板型输出对应内容，不要同时输出单板和双板（除非用户明确要求对比）
4. **技能优先级**：按 `skill_sequence` 定义的顺序排列，建议用户按顺序练习
5. **成功信号可验证**：每个技能的成功信号必须是具体可验证的行为，不是模糊描述
6. **引导闭环**：每个级别末尾引导用户发视频给 AI 教练打分验证
7. **国际术语对照**：Level 0-1 不显示术语对照，Level 2+ 在核心技能末尾显示一行术语对照（从技能 `terms` 字段读取）
8. **动态生成优先**：优先使用 `_index.md` 技能骨架 + `curriculum-skeleton.md` 协议动态生成。旧版 level 文件仅作备用

---

## 国际术语对照显示规则（方案 C）

**Level 0-1**：不显示术语对照

**Level 2+**：在核心技能（转弯技术、姿态进阶）末尾添加术语对照，从技能的 `terms` 字段读取：

```markdown
**术语对照**：
- PSIA-AASI：[terms.psia]
- CASI：[terms.casi]
- CSIA：[terms.csi]
```

**规则**：
- 只在有 `terms` 字段的技能显示
- 不超过 2 行
- 不展开讲解差异
- 用户主动询问"这个在 CASI 里叫什么"时，输出 `_index.md` 中的完整对照表

---

## MAY（可选）

- **生成 DOCX 教程文件**（完整版排版，用户明确要求时）
  - 使用 docx skill 创建专业排版
  - 包含封面、目录、章节标题、表格、图片占位
  - 文件名：`Level[X]_[board_type]_Tutorial_v3.0.docx`
- 根据用户已有 `records.json` 记录，跳过已掌握的技能
- 推荐附近适合练习该级别技能的雪场

---

## DOCX 导出规范

当用户明确要求"生成 DOCX 教程"或"导出为 Word 文档"时：

1. 调用 docx skill
2. 创建以下结构：
   - 封面：级别标题 + 板型 + 版本
   - 目录：自动生成
   - 正文：按教程内容格式
   - 表格：级别目标、训练计划、里程碑
   - 页脚：页码 + 免责声明
3. 输出到工作目录的 `outputs/` 文件夹
4. 提供 file:// 链接给用户
