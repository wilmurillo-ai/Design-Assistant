# BMad Agent / Trigger Cheatsheet

基于项目内 `_bmad/_config/bmad-help.csv` 动态映射出来的官方角色与触发器。

## BMM

### Analyst (Mary)
- `BP` → Brainstorm Project
- `MR` → Market Research
- `DR` → Domain Research
- `TR` → Technical Research
- `CB` → Create Brief
- `DP` → Document Project
- `GPC` → Generate Project Context

### PM (John)
- `CP` → Create PRD
- `VP` → Validate PRD
- `EP` → Edit PRD
- `CE` → Create Epics and Stories

### Architect (Winston)
- `CA` → Create Architecture
- `IR` → Check Implementation Readiness

### Scrum Master (Bob)
- `SP` → Sprint Planning
- `SS` → Sprint Status
- `CS` → Create Story
- `VS` → Validate Story
- `ER` → Retrospective
- `CC` → Correct Course

### Developer (Amelia)
- `DS` → Dev Story
- `CR` → Code Review

### QA (Quinn)
- `QA` → QA Automation Test

### UX Designer (Sally)
- `CU` → Create UX

### Quick Flow Solo Dev (Barry)
- `QS` → Quick Spec
- `QD` → Quick Dev

### Tech Writer (Paige)
- `WD` → Write Document
- `US` → Update Standards
- `MG` → Mermaid Generate
- `VD` → Validate Document
- `EC` → Explain Concept

## TEA

### TEA (Murat)
- `TMT` → Teach Me Testing
- `TD` → Test Design
- `TF` → Test Framework
- `CI` → CI Setup
- `AT` → ATDD
- `TA` → Test Automation
- `RV` → Test Review
- `NR` → NFR Assessment
- `TR` → Traceability

## BMB

### Agent Builder (Bond)
- `CA` → Create Agent
- `EA` → Edit Agent
- `VA` → Validate Agent

### Module Builder (Morgan)
- `PB` → Create Module Brief
- `CM` → Create Module
- `EM` → Edit Module
- `VM` → Validate Module

### Workflow Builder (Wendy)
- `CW` → Create Workflow
- `EW` → Edit Workflow
- `VW` → Validate Workflow
- `MV` → Max Parallel Validate
- `RW` → Rework Workflow

## 用法建议

优先使用：

```bash
scripts/run_bmad_persona.py --cwd <repo> --persona sm --trigger CS ...
```

而不是手工去猜 agent 命令和 workflow 映射。
