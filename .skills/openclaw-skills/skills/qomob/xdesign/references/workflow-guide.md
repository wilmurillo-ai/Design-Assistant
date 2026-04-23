# Advanced Workflow Guide / 高手玩法 / 上級ワークフローガイド

## Table of Contents

1. [Master Prompt Template](#master-prompt-template)
2. [Reference Input Strategy](#reference-input-strategy)
3. [Iteration Techniques](#iteration-techniques)
4. [Design-to-Code Handoff](#design-to-code-handoff)

## Master Prompt Template

Use this template when starting a new project. Fill in all fields for best results / 新项目启动时使用此模板，填入所有字段获得最佳效果:

```
做一个 [产品类型]
目标用户：[用户画像]
使用场景：[使用情境]
核心功能：
- [功能1]
- [功能2]
页面结构：
- [页面1]
- [页面2]
设计风格：[风格描述]
参考：
- [参考1，如 Stripe]
- [参考2，如 Notion]
输出：
1. 低保真结构
2. 3种布局方案
```

**Example / 示例:**
```
做一个 B2B SaaS 后台
目标用户：运营人员，非技术背景
使用场景：日常数据监控 + 客户管理
核心功能：
- 数据看板（实时指标）
- 客户列表（筛选+操作）
- 任务分配
页面结构：
- Dashboard（首页）
- Customer List
- Customer Detail
设计风格：简洁冷静，专业可信
参考：
- Stripe Dashboard
- Linear
输出：
1. Wireframe（低保真）
2. 3种 Dashboard 布局方案（信息优先 / 操作优先 / 极简）
```

## Reference Input Strategy

XDesign is strongest when fed reference material. Always encourage users to provide input / XDesign 在有参考输入时最强。始终鼓励用户提供输入:

**Accepted inputs / 接受的输入:**
- Website URLs → extract layout patterns, color systems, typography
- Screenshots → inherit visual style, component language
- Figma exports → pixel-accurate recreation
- PPT files → extract slide layouts, brand colors
- Code repositories → lift exact design tokens, component patterns
- Hand-drawn sketches / napkin files → interpret structure and intent
- Brand assets (logos, style guides) → auto-extract design system

**Pro tip / 高手技巧:**
Give it screenshots of Stripe / Notion / Linear → get same-tier UI quality without building from scratch.

给它 Stripe / Notion / Linear 的截图 → 直接生成同级别 UI。

## Iteration Techniques

Three iteration modes / 三种迭代模式:

### 1. Conversational / 对话修改
Best for directional changes / 方向性调整:
- "按钮太重了，轻一点"
- "整体风格偏冷，加暖色"
- "信息层级不对，数据应该是主角"

### 2. Canvas Annotation / 画布批注
Best for specific element changes / 具体元素修改:
- Click element → "这里改成卡片布局"
- Drag element → adjust spacing/position
- Select text → change copy

### 3. Slider/Tweak Adjustment / 滑杆调整
Best for parameter tuning / 参数微调:
- Spacing scale
- Color palette
- Font size/weight
- Layout density

## Design-to-Code Handoff

When user says "把这个转成 React 组件" or "hand off to development":

1. Invoke **Handoff to Claude Code** sub-skill
2. Output structured component code with:
   - Props interface
   - Style tokens extracted from design
   - Responsive breakpoints
   - Accessibility attributes
3. This bridges design → development in one flow

**设计 → 开发一体化。** 一句话从设计稿转成可开发代码。
