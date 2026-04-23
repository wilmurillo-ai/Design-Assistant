# 3Q 质量体系 - 手动安装指南

**版本**: v4.0.1  
**最后更新**: 2026-03-31

---

## ⚠️ 重要提示

**安装前请阅读**：

本技能包将修改以下文件：
- `$WORKSPACE/HEARTBEAT.md` - 添加 QualityOS 配置
- `$WORKSPACE/quality-metrics.json` - 创建质量指标文件（如不存在）

**备份建议**：
```bash
# 备份 HEARTBEAT.md
cp ~/.openclaw/workspace-main/HEARTBEAT.md ~/.openclaw/workspace-main/HEARTBEAT.md.backup.$(date +%Y%m%d-%H%M%S)
```

---

## 🚀 安装步骤

### 步骤 1：检查环境

```bash
# 确认 OpenClaw workspace 存在
ls -d ~/.openclaw/workspace-main
```

如果目录不存在，请先安装 OpenClaw。

---

### 步骤 2：复制技能文件

```bash
# 进入安装包目录
cd 3Q-Installation-Pack

# 复制 6 个核心技能
cp -r skills/self-challenge-3q-v3.1 ~/.openclaw/workspace-main/skills/
cp -r skills/3Q-Plus-v3 ~/.openclaw/workspace-main/skills/
cp -r skills/quality-os-trigger ~/.openclaw/workspace-main/skills/
cp -r skills/task-breakdown-v3 ~/.openclaw/workspace-main/skills/
cp -r skills/decision-checklist-v2 ~/.openclaw/workspace-main/skills/
cp -r skills/subagent-brief-template-v3 ~/.openclaw/workspace-main/skills/

# 复制 2 个辅助技能（可选）
cp -r skills/quality-prevention-milestone ~/.openclaw/workspace-main/skills/
cp -r skills/quality-os ~/.openclaw/workspace-main/skills/
```

---

### 步骤 3：配置 HEARTBEAT.md

**检查是否已存在 QualityOS 配置**：
```bash
grep "QualityOS 统一触发器" ~/.openclaw/workspace-main/HEARTBEAT.md
```

- 如果有输出 → 已配置，跳过此步骤
- 如果无输出 → 继续追加配置

**追加配置**：
```bash
cat >> ~/.openclaw/workspace-main/HEARTBEAT.md << 'EOF'

---

## 🚀 QualityOS 统一触发器 v4.0（3Q 质量体系）

**触发入口**: `skills/quality-os-trigger/SKILL.md`

**手动触发规则**：
| 场景 | 触发方式 | 技能 |
|------|---------|------|
| 文档发布前 | 手动触发 | 对 AI 说"3Q 检查 v3.1" |
| 代码提交前 | 手动触发 | 对 AI 说"代码质量检查" |
| 决策开始前 | 手动触发 | 对 AI 说"重大决策检查" |
| 子代理任务 | 手动触发 | 使用 subagent-brief-template |
| 子代理交付 | 手动触发 | 对 AI 说"3Q 验收" |
| 内容发布前 | 手动触发 | 对 AI 说"3Q Plus 检查" |

**HEARTBEAT 自动检查**（推荐）：
- 心跳检查时自动提醒未完成的 3Q 检查
- 每周生成质量仪表板报告

**质量指标**：
- 手动触发率：≥90%
- 平均评分：≥14/15
- S 级比例：≥50%
- 返工率：≤10%
EOF
```

---

### 步骤 4：创建质量指标文件

```bash
# 检查是否已存在
ls ~/.openclaw/workspace-main/quality-metrics.json

# 如不存在则创建
cat > ~/.openclaw/workspace-main/quality-metrics.json << 'EOF'
{
  "manualTriggerRate": 0.90,
  "avgScore": 14.0,
  "sGradeRatio": 0.50,
  "reworkRate": 0.10,
  "lastUpdate": "2026-03-31",
  "taskDistribution": {
    "mechanical": 0.40,
    "creative": 0.40,
    "decision": 0.10,
    "integration": 0.10
  }
}
EOF
```

---

### 步骤 5：验证安装

```bash
# 验证 6 个核心技能
ls ~/.openclaw/workspace-main/skills/self-challenge-3q-v3.1/SKILL.md
ls ~/.openclaw/workspace-main/skills/3Q-Plus-v3/SKILL.md
ls ~/.openclaw/workspace-main/skills/quality-os-trigger/SKILL.md
ls ~/.openclaw/workspace-main/skills/task-breakdown-v3/SKILL.md
ls ~/.openclaw/workspace-main/skills/decision-checklist-v2/SKILL.md
ls ~/.openclaw/workspace-main/skills/subagent-brief-template-v3/SKILL.md

# 验证 HEARTBEAT 配置
grep "QualityOS" ~/.openclaw/workspace-main/HEARTBEAT.md

# 验证质量指标文件
cat ~/.openclaw/workspace-main/quality-metrics.json
```

**全部通过** → ✅ 安装成功！

---

## 🎯 快速测试

**测试第一个 3Q 检查**：

1. 打开任意文档（或新建一个）
2. 对 AI 说：`3Q 检查 v3.1`
3. 等待 20-30 分钟，获取 13 问检查报告
4. 查看质量评分（15 分制）

---

## ❓ 常见问题

### Q: 安装失败怎么办？

**A**: 检查以下几点：
1. OpenClaw 是否正确安装
2. skills 目录是否有写权限
3. HEARTBEAT.md 是否存在

### Q: 如何卸载？

**A**: 手动删除即可：
```bash
# 删除技能
rm -rf ~/.openclaw/workspace-main/skills/self-challenge-3q-v3.1
rm -rf ~/.openclaw/workspace-main/skills/3Q-Plus-v3
# ... 其他技能

# 删除配置（可选）
# 手动编辑 HEARTBEAT.md，删除 QualityOS 部分
rm ~/.openclaw/workspace-main/quality-metrics.json
```

### Q: 如何更新？

**A**: 重新运行安装步骤即可（配置会保留）

---

## 📞 需要帮助？

- **GitHub**: https://github.com/qh582/3Q-quality-system
- **问题反馈**: GitHub Issues
- **文档**: README.md

---

**维护者**: 小鑫 🔮 & 小 O 🤖  
**版本**: v4.0.1
