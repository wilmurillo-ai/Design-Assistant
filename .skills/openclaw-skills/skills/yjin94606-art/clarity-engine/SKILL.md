---
name: clarity-engine
description: Natural Language to Structured Intent Converter. Converts verbose Chinese/English input into structured, precise instructions. Supports 20+ programming languages. Activates when user says "开启精准模式" or "enable precision mode".
version: 1.0.0
author: Boss
---

# Clarity Engine - Precision Mode

## Core Functionality

Transforms verbose natural language into structured, precise instructions for better AI comprehension.

## Activation

**Trigger:** When user says "开启精准模式" or "enable precision mode"

**Deactivate:** When user says "关闭精准模式" or "disable precision mode"

## Supported Language Detection

**Backend:** JavaScript, TypeScript, Python, Java, C, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, R, MATLAB, Shell/Bash

**Frontend:** HTML, CSS, React, Vue, Next.js, Angular

**Other:** SQL, Flutter/Dart

## Output Format

```markdown
## 🎯 Precision Instruction

**📌 Intent:** Code Debug / Performance / Create / Explain / Modify / Review
**💻 Language:** Python / JavaScript / ... (if detected)
**🎯 Focus:** Loop / Function / Async / ... (if detected)

**💡 To help you better, please provide:**
- Question 1
- Question 2
```

## Examples

### Activation
**User:** 开启精准模式 / Enable precision mode

### Precision Transform
**User:** 帮我看看这个Python代码有什么问题

**Output:**
```markdown
## 🎯 Precision Instruction

**📌 Intent:** Code Debug
**💻 Language:** Python

**💡 To help you better, please provide:**
- What is the specific code?
- Is there any error message?
```

### Deactivation
**User:** 关闭精准模式 / Disable precision mode

## Technical Details

- **Pure JavaScript** - No external dependencies
- **Deterministic** - Stable, predictable output
- **Millisecond processing** - Fast local response
