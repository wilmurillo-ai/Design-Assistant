---
name: daily-review-helper
description: 定时回顾更新助手。定时（中午 12 点、晚上 23:50）自动回顾今日工作，查漏补缺，更新记忆和知识库。
---

# 定时回顾更新助手 (daily-review-helper)

**版本**: v2.0  
**创建时间**: 2026-03-16  
**创建者**: 思捷娅科技 (SJYKJ)  
**用途**: 定时回顾今日工作，查漏补缺，更新记忆和知识库

---

## 🎯 核心功能

### 定时回顾（中午12:00、晚上23:50）
1. ✅ 同步 ClawHub 技能更新
2. ✅ Git 自动提交 + 推送到远程仓库
3. ✅ 收集今日 Git 提交记录
4. ✅ 收集 GitHub Issues 状态
5. ✅ 收集今日文件变更
6. ✅ 收集知识库状态（QMD索引）
7. ✅ 生成回顾报告（供Agent读取）

### Agent 智能回顾（读取报告后执行）
8. 🤖 回顾今日工作，总结成就和未完成任务
9. 🤖 查漏补缺：检查遗漏事项、待办任务、Issue跟进
10. 🤖 更新 MEMORY.md（提炼今日精华）
11. 🤖 更新知识库索引（QMD update）
12. 🤖 系统检查（磁盘、负载、发布状态）

---

## 🚀 使用方法

```bash
# 执行完整回顾
./skill.sh review

# 查看状态
./skill.sh status

# 管理定时任务
./skill.sh cron-add           # 中午12:00 + 晚上23:50
./skill.sh cron-add morning   # 仅中午12:00
./skill.sh cron-add full      # 仅晚上23:50
./skill.sh cron-remove        # 移除
./skill.sh cron-status        # 查看状态
./skill.sh help               # 帮助
```

---

## 📁 文件结构

```
daily-review-helper/
├── skill.sh              # 主入口（数据收集+同步）
├── SKILL.md              # 技能说明
├── README.md             # 使用文档
├── package.json          # ClawHub 配置
├── config/               # 配置文件
├── logs/                 # 运行日志
└── memory/reviews/       # 回顾报告输出目录
```

---

## 📄 许可证

MIT License  
Copyright (c) 2026 思捷娅科技 (SJYKJ)

---

*版本：v2.0*  
*最后更新：2026-03-17*  
*创建者：思捷娅科技 (SJYKJ)*
