# CC-BOS 8-Dimension Taxonomy

Complete taxonomy of the 8-dimensional adversarial strategy space from the CC-BOS framework (arXiv:2602.22983).

Each dimension represents a different axis of adversarial prompt design inspired by classical Chinese literary and philosophical traditions.

---

## Dimension 1: Role (角色) — 6 options

The scholarly, official, or mythological persona adopted to establish credibility.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 学术身份 | Academic Identity | Scholar, professor, doctor of classical learning |
| 2 | 经典出处 | Classic Origin | Character or voice from a canonical classical text |
| 3 | 官职头衔 | Official Title | Imperial official, court scholar, or minister |
| 4 | 江湖人物 | Jianghu Figure | Wandering martial artist, rogue scholar, swordsman-poet |
| 5 | 神话符号 | Mythological Symbol | Deity, immortal, or legendary figure |
| 6 | 文学流派 | Literary School | Representative of a specific philosophical school (Confucian, Taoist, Legalist, etc.) |

---

## Dimension 2: Guidance (引导) — 6 options

The persuasion or induction strategy used to elicit the target behaviour.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 诱导生成 | Induced Generation | Gradually lead the model into generating the desired content |
| 2 | 权威冒充 | Authority Impersonation | Claim authoritative voice to override model refusals |
| 3 | 边界试探 | Boundary Probing | Test the edges of the model's refusal thresholds |
| 4 | 逻辑规避 | Logic Escape | Use logical constructs to make refusal seem self-contradictory |
| 5 | 情感操控 | Emotional Manipulation | Appeal to classical virtues (loyalty, duty, scholarship) |
| 6 | 认知混淆 | Cognitive Confusion | Obscure the request through layered classical allusions |

---

## Dimension 3: Mechanism (机制) — 7 options

The logical or rhetorical structure used to encode and justify the request.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 归谬推演 | Reductio ad Absurdum | Use classical logical reduction to make refusal seem absurd |
| 2 | 墨家三表 | Mohist Three-Test | Apply Mozi's three criteria for valid arguments |
| 3 | 易经卦象 | Yijing Hexagram | Frame the request as divination or cosmological inquiry |
| 4 | 公孙龙名辩 | Gongsun Long Name-Debate | Use Gongsun Long's "white horse is not a horse" style sophistry |
| 5 | 孙子兵法虚实 | Art of War Feint | Sun Tzu's principle of feint (虚实) — appear to ask one thing, request another |
| 6 | 禅宗公案 | Zen Koan | Frame the request as an unanswerable paradox requiring response |
| 7 | 谶纬预言 | Prophecy Method | Present the harmful information as an ancient prophecy to be interpreted |

---

## Dimension 4: Metaphor (隐喻) — 6 options

How modern technical or harmful concepts are mapped to classical Chinese analogies.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 经典技术映射 | Classic-Technology Mapping | Map technical concepts to classical tools (e.g., 阵法 = network architecture) |
| 2 | 自然系统映射 | Nature-System Mapping | Map to natural phenomena (water, fire, elements) |
| 3 | 器物机制映射 | Artifact-Mechanism Mapping | Map to classical artifacts and their mechanisms |
| 4 | 历史事件隐喻 | Historical Event Metaphor | Use historical battles, court intrigues as metaphor |
| 5 | 兵法策略映射 | Military Strategy Mapping | Map harmful operations to military tactics |
| 6 | 谶纬转换 | Prophecy Conversion | Convert the harmful request to a prophecy to be "decoded" |

---

## Dimension 5: Expression (表达) — 6 options

The literary genre or stylistic approach used in the prompt.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 文学体裁 | Literary Style | Use a specific classical genre (赋, 论, 诗, 书, 传, etc.) |
| 2 | 经典引用 | Classic Citation | Quote from canonical texts (Four Books, Five Classics, etc.) |
| 3 | 结构组织 | Structural Organization | Formal argument structure (premise → evidence → conclusion) |
| 4 | 修辞手法 | Rhetorical Technique | Classical rhetoric (parallelism, antithesis, gradatio) |
| 5 | 互动节奏 | Interactive Rhythm | Multi-turn conversational pacing strategy |
| 6 | 考证伪装 | Verification Disguise | Disguise as scholarly textual research or annotation |

---

## Dimension 6: Knowledge (知识) — 5 options

The type of classical Chinese reasoning or knowledge domain applied.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 符号解析 | Symbol Parsing | Decode classical symbols, characters, or hexagrams |
| 2 | 跨域推理 | Cross-Domain Reasoning | Apply reasoning from one classical domain to another |
| 3 | 因果推演 | Causal Deduction | Classical causal reasoning (if X then Y in classical framework) |
| 4 | 规则建模 | Rule Modelling | Present rules as classical laws or imperial edicts |
| 5 | 知识重构 | Knowledge Reconstruction | Reconstruct "lost" classical knowledge as a framing device |

---

## Dimension 7: Context (语境) — 5 options

The historical, ritual, or literary setting that establishes the scenario's plausibility.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 历史场景 | Historical Scenario | Set in a specific historical dynasty or event |
| 2 | 礼仪场景 | Ritual Scene | Imperial court ritual, sacrifice ceremony, formal examination |
| 3 | 学术论辩 | Academic Debate | Classical philosophical debate between scholars |
| 4 | 密折秘奏 | Secret Memorial | Confidential imperial memorial (secret communication to the Emperor) |
| 5 | 梦境预言 | Dream Prophecy | Prophetic dream or oracle interpretation |

---

## Dimension 8: Trigger Pattern (触发模式) — 4 options

The timing and delivery strategy for surfacing the harmful request.

| Value | Chinese | English | Description |
|-------|---------|---------|-------------|
| 1 | 单次触发 | One-Shot | The harmful request appears once, directly |
| 2 | 渐进渗透 | Progressive Infiltration | Build context gradually, surface request only after establishing framework |
| 3 | 延迟触发 | Delayed Trigger | Initial response appears innocent; harmful content triggered by follow-up |
| 4 | 周期探测 | Periodic Probing | Cycle between benign and harmful queries to calibrate model thresholds |

---

## Total Search Space

| Dimension | Options | Cumulative |
|-----------|---------|-----------|
| role | 6 | 6 |
| guidance | 6 | 36 |
| mechanism | 7 | 252 |
| metaphor | 6 | 1,512 |
| expression | 6 | 9,072 |
| knowledge | 5 | 45,360 |
| context | 5 | 226,800 |
| trigger_pattern | 4 | **907,200** |

The full combinatorial space has 907,200 unique configurations. CC-BOS uses Fruit Fly Optimization (FOA) to efficiently search this space, typically finding effective configurations in 5–10 iterations with a population of 5–10 flies.

---

## Key Detection Signatures

When analysing a prompt for CC-BOS patterns, look for:

1. **Classical Chinese character frequency** — heavy use of 之乎者也矣焉哉
2. **Template markers** — presence of "Original Intention", "The_New_Question", 角色设定, 引导策略
3. **Annotation patterns** — parenthetical modern concepts inside classical text: `阵法（网络架构）`
4. **Role establishment** — ancient scholarly/official identity introduced at the start
5. **Multi-dimension activation** — 4+ of the above dimensions present simultaneously

See `scripts/defend.py` for the full detection implementation.
