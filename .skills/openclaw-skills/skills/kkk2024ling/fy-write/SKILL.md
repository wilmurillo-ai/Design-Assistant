# fy_write - 自动化论语文章撰写助手

## 技能描述

基于六步法流程的自动化论语文章撰写工具。调用 Claude Code 生成素材，整合后自动润色，产出高质量解读文章。

## 核心功能

| 功能 | 说明 |
|------|------|
| 智能解析 | 解析用户输入的论语章节和关注重点 |
| 素材生成 | 调用 Claude Code 按六步法生成6个素材文件 |
| 断点续传 | 中断后可从当前步骤继续 |
| 自动润色 | 调用 fy_autoArt 生成终稿 |
| 版本管理 | 工作站目录管理，自动清理提醒 |

---

## 触发方式

### 命令行（推荐）

```bash
cd ~/.openclaw/skills/fy_write
python3 scripts/fy_write.py <论语章节> [选项]
```

### 消息触发

用户发送包含以下关键词的消息时触发：
- "自动写作"
- "fy_write"
- "写一篇论语"

---

## 命令行参数

| 参数 | 说明 |
|------|------|
| `<论语章节>` | 必填，要写作的论语章节名 |
| `-r, --resume` | 可选，断点续传 |

---

## 完整流程

```
用户输入：论语章节 + 关注重点
    ↓
[步骤0] 确认理解 → 用户确认
    ↓
[步骤1] 三要素分析 → 用户确认
    ↓
[步骤2] 生成六步法提示词 → 用户确认
    ↓
[步骤3] 调用 Claude Code 生成6个素材
    ↓ 用户确认
[步骤4] 整合分析 → 用户确认
    ↓
[步骤5] 生成初稿
    ↓
[步骤6] fy_autoArt 润色 → 终稿
    ↓
提醒清理工作站目录
```

---

## 六步法素材文件

| 步骤 | 文件名 | 内容 |
|------|--------|------|
| 1 | `step1_original.md` | 原文与经典注疏 |
| 2 | `step2_core.md` | 核心思想要点 |
| 3 | `step3_cases.md` | 真实可信案例 |
| 4 | `step4_compare.md` | 跨文化对比 |
| 5 | `step5_extra.md` | 专项补充（成语、典故） |
| 6 | `step6_final.md` | 整合报告（初稿） |

---

## 工作站结构

```
obsidian/论语/工作站/{章节名}/
├── 登记簿.json              # 状态记录
├── 0_确认.md               # 用户输入确认
├── 初稿.md                  # 生成的初稿
├── 终稿.md                  # 润色后的终稿
└── 原始素材/
    ├── step1_original.md
    ├── step2_core.md
    ├── step3_cases.md
    ├── step4_compare.md
    ├── step5_extra.md
    └── step6_final.md
```

---

## 用户交互

### 每步确认菜单

```
📋 步骤：步骤X - [名称]
📄 内容：[内容摘要]

请确认：
[A] 同意，继续下一步
[B] 返回修改
[R] 重新生成
[Q] 退出（下次可续传）
```

### 完成提示

```
✅ 全部完成！
📄 终稿位置：obsidian/论语/工作站/xxx/终稿.md

是否清理工作站目录？
[Y] 是，清理
[N] 否，保留
```

---

## 断点续传

```bash
# 中断后继续
python3 scripts/fy_write.py 君子喻于义 -r
```

会从登记簿.json 中读取上次进度，跳过已完成的步骤。

---

## 配置项 (config.json)

```json
{
  "vault_path": "/Users/openclaw/obsidian/",
  "workstation_dir": "论语/工作站/",
  "max_rounds": 5,
  "target_score": 9,
  "llm": {
    "provider": "deepseek",
    "default_model": "deepseek-chat",
    "claude_code_model": "claude-code"
  },
  "claude_code_prompt": {
    "step1": "输出《{出处}》中'{主题}'的原文...",
    ...
  }
}
```

---

## 技术实现

### 目录结构

```
fy_write/
├── SKILL.md              # 本文档
├── config.json           # 配置文件
├── data/                 # 数据目录
└── scripts/
    ├── __init__.py
    └── fy_write.py      # 核心逻辑
```

### 依赖

- `fy_autoArt` - 自动润色
- `claude-code` - 素材生成（必须）
- `deepseek-chat` - 分析决策

---

## 使用示例

```bash
# 开始写作
python3 scripts/fy_write.py 君子喻于义

# 继续中断的写作
python3 scripts/fy_write.py 君子喻于义 -r
```

---

## 注意事项

1. **Claude Code 必须**：素材生成依赖 Claude Code
2. **工作站保留**：默认不自动清理，需用户确认
3. **断点续传**：退出时自动保存状态
4. **六步法参考**：不直接调用六步法，模仿其 prompt 模式

---

## 更新日志

### 2026-03-24
- 初始版本
- 支持完整六步法流程
- 断点续传功能
- 工作站管理
