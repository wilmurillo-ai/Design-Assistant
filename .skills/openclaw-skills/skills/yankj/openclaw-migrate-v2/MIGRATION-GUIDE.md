# 🦐 OpenClaw 迁移指南

**以我这只虾为例，帮你无缝迁移到你的电脑**

---

## 📋 我的数据（源电脑）

```
我这只虾的 OpenClaw 数据：
├── Skills (50 个)
│   ├── just-note/          # 笔记工具
│   ├── skill-creator/      # Skill 创建工具
│   ├── openclaw-migrate/   # 迁移工具（新创建）
│   ├── finance-*/          # 财务系列
│   └── ...
├── Memory (1090 个文件)
│   ├── 2026-03-26.md       # 今日日记
│   ├── product-ideas/      # 产品构思
│   ├── daily-report/       # 每日报告
│   └── just-note/          # just-note 记录
├── Cron Jobs (1 个)
│   └── 每日资讯收集
└── 配置
    ├── jobs.json           # Cron 配置
    └── 其他配置
```

---

## 🎯 迁移到你的电脑（3 步）

### 步骤 1: 在我这里备份

```bash
# 1. 停止 Gateway
openclaw gateway stop

# 2. 备份
openclaw-migrate backup --output ~/openclaw-backup/

# 输出：
# 🦞 开始备份 OpenClaw...
# 📦 备份 Skills... ✅ 50 个
# 📦 备份 Workspace... ✅ 1090 个文件
# 📦 备份 Cron Jobs... ✅ 1 个
# 📦 备份配置... ✅ 已备份
# ✅ 备份完成：~/openclaw-backup/
# 备份大小：915M
```

### 步骤 2: 复制到你的电脑

```bash
# 方法 1: U 盘
cp -r ~/openclaw-backup/ /mnt/usb-drive/

# 方法 2: rsync（同网络）
rsync -av ~/openclaw-backup/ user@your-pc:~/

# 方法 3: 网盘
# 上传到 Dropbox/Google Drive/坚果云
```

### 步骤 3: 在你那里恢复

```bash
# 1. 安装 OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# 2. 恢复数据
openclaw-migrate restore --input ~/openclaw-backup/

# 3. 重启 Gateway
openclaw gateway restart

# 输出：
# 🦞 开始恢复 OpenClaw...
# 📦 恢复 Skills... ✅ 50 个
# 📦 恢复 Workspace... ✅ 1090 个文件
# 📦 恢复 Cron Jobs... ✅ 1 个
# 📦 恢复配置... ✅ 已备份
# ✅ 恢复完成！
```

---

## ✅ 迁移完成后的验证

### 检查 Skills

```bash
ls -1 ~/.openclaw/skills/ | wc -l
# 应该显示：50
```

### 检查 Memory

```bash
find ~/openclaw/workspace -name "*.md" | wc -l
# 应该显示：1090
```

### 检查 Cron

```bash
ls -1 ~/.openclaw/cron/*.json | wc -l
# 应该显示：1
```

### 测试 just-note

```bash
just-note write --type test --content "迁移成功测试"
just-note today
```

---

## 🔄 持续同步方案（可选）

### 方案 1: Git 同步

**在你的电脑上**:

```bash
# 初始化 Git 仓库
cd ~/openclaw/workspace
git init
git remote add origin git@github.com:your-username/openclaw-data.git

# 添加 .gitignore
cat >> .gitignore << EOF
node_modules/
*.log
.DS_Store
EOF

# 提交
git add -A
git commit -m "Initial commit from openclaw-migrate"
git push -u origin main
```

**在另一台电脑上**:

```bash
# 克隆
git clone git@github.com:your-username/openclaw-data.git ~/openclaw/workspace

# 定期同步
cd ~/openclaw/workspace
git pull origin main
git add -A
git commit -m "Auto sync"
git push origin main
```

---

### 方案 2: 网盘同步

**配置 Dropbox**:

```bash
# 创建同步目录
ln -s ~/Dropbox/OpenClaw/workspace ~/openclaw/workspace-backup

# 定期备份
openclaw-migrate backup --output ~/Dropbox/OpenClaw/backup/
```

---

## 📤 导出到其他格式

### 导出为 flomo

```bash
openclaw-migrate export flomo --output flomo.jsonl

# 上传到 flomo
# https://flomoapp.com/import
```

### 导出为 Obsidian

```bash
openclaw-migrate export obsidian --output ~/Obsidian-Vault/OpenClaw/

# 在 Obsidian 中打开文件夹
```

### 导出为 Notion

```bash
openclaw-migrate export notion --output notion.md

# 导入到 Notion
```

---

## 🛡️ 安全与隐私

### 排除敏感数据

```bash
# 备份时自动排除
openclaw-migrate backup --exclude-secrets --output ~/backup/

# 排除的文件：
# - .env
# - credentials/
# - *api_key*
# - *token*
```

### 加密备份

```bash
# 加密
openclaw-migrate backup --encrypt --password "your-password" --output ~/encrypted/

# 解密恢复
openclaw-migrate restore --decrypt --password "your-password" --input ~/encrypted/
```

---

## 📊 迁移检查清单

### 备份前

- [ ] 停止 OpenClaw Gateway
- [ ] 检查磁盘空间（至少 1GB 可用）
- [ ] 检查权限（有读写权限）

### 恢复前

- [ ] 已安装 OpenClaw
- [ ] 检查备份文件完整性
- [ ] 检查目标磁盘空间

### 恢复后

- [ ] 检查 Skills 数量（50 个）
- [ ] 检查 Memory 文件（1090 个）
- [ ] 检查 Cron Jobs（1 个）
- [ ] 测试 just-note 功能
- [ ] 测试 Channel 连接

---

## 💡 常见问题

### Q: 备份太大怎么办？

A: 
```bash
# 选择性备份
openclaw-migrate backup --include memory --output ~/memory-only/

# 或排除大文件
openclaw-migrate backup --exclude "*.pdf" --exclude "*.mp4" --output ~/backup/
```

### Q: 恢复后 Skills 不可用？

A:
```bash
# 重新安装 Skills
openclaw-migrate restore --include skills --reinstall

# 或手动重新安装
npx clawhub install just-note --force
```

### Q: 如何定期自动备份？

A:
```bash
# 添加到 crontab
# 每天凌晨 2 点备份
0 2 * * * openclaw-migrate backup --output ~/daily-backup/$(date +\%Y-\%m-\%d)/
```

---

## 🎯 总结

### 迁移流程

```
源电脑（我）          传输              目标电脑（你）
    ↓                                    ↓
openclaw-migrate    U 盘/网盘/网络    openclaw-migrate
    backup          →               restore
    ↓                                    ↓
~/openclaw-backup/                   完整的 OpenClaw
```

### 核心优势

| 优势 | 说明 |
|------|------|
| **一键操作** | 一条命令完成备份/恢复 |
| **完整迁移** | Skills + Memory + Cron + 配置 |
| **格式转换** | 支持 flomo/Obsidian/Notion |
| **数据自主** | 数据永远在你手里 |
| **开源免费** | MIT License |

---

**迁移工具已就绪！** 🦐

需要我帮你：
1. 发布 openclaw-migrate 到 ClawHub？
2. 测试完整迁移流程？
3. 还是先备份我的数据？
