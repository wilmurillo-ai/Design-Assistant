# xhs-auto-publish 技能使用指南

## 概述

`xhs-auto-publish` 技能是一个自动化小红书笔记生成与发布工具，封装了 `xhs-auto-publish-v2.sh` 脚本的功能。

## 快速开始

### 1. 安装技能

技能已自动安装到工作空间。如果需要重新安装：

```bash
cd ~/.openclaw/workspace/skills/xhs-auto-publish/scripts
./setup.sh
```

### 2. 基本使用

#### 外部主题模式（手动指定主题）

```bash
# 生成并发布关于特定主题的笔记
./scripts/xhs-auto-publish-v2.sh "新加坡Kaplan学院"
./scripts/xhs-auto-publish-v2.sh "新加坡留学申请攻略"
./scripts/xhs-auto-publish-v2.sh "新加坡学生签证最新政策"
```

#### 自动选题模式（自动搜索热点）

```bash
# 自动搜索小红书热点内容并生成相关笔记
./scripts/xhs-auto-publish-v2.sh --auto
./scripts/xhs-auto-publish-v2.sh -a
```

### 3. 查看帮助

```bash
./scripts/xhs-auto-publish-v2.sh --help
```

## 技能激活

当用户提到以下关键词时，此技能会自动激活：

- "自动发布小红书"
- "小红书自动发布"
- "xhs-auto-publish"
- "小红书定时发布"
- "自动生成小红书内容"

## 功能特点

### 1. 两种发布模式
- **外部主题模式**：用户指定主题，生成相关内容
- **自动选题模式**：自动搜索热点，智能确定主题

### 2. 幂等性保护
- 自动检查是否有相同任务正在运行
- 避免重复发布相同内容

### 3. 标准化输出
- 使用ImageMagick生成统一风格的封面
- 标题作为封面文字，保持一致性
- 必须包含指定标签（#留学新加坡 #新加坡私立大学）

### 4. 一次发布策略
- 仅发布一次，无论成功与否均停止
- 避免重复发布造成账号风险

## 配置定时任务

可以使用cron配置定时自动发布：

```bash
# 每天上午10点自动发布（自动选题模式）
0 10 * * * cd /home/chan/.openclaw/workspace && ./scripts/xhs-auto-publish-v2.sh --auto

# 每周一、三、五下午3点发布指定主题
0 15 * * 1,3,5 cd /home/chan/.openclaw/workspace && ./scripts/xhs-auto-publish-v2.sh "新加坡留学申请攻略"
```

## 故障排除

### 1. 脚本无法执行
```bash
# 检查权限
chmod +x ~/.openclaw/workspace/scripts/xhs-auto-publish-v2.sh

# 检查依赖
which openclaw
```

### 2. 重复执行警告
如果看到"发现正在运行的xhs-auto-publish任务"警告：
```bash
# 查看正在运行的任务
ps aux | grep -E "openclaw.*agent.*xhs-auto-publish" | grep -v grep

# 如果需要强制停止
pkill -f "openclaw.*agent.*xhs-auto-publish"
```

### 3. 发布失败
- 检查小红书账号是否已登录
- 检查网络连接
- 查看OpenClaw日志：`openclaw logs`

## 技能文件结构

```
xhs-auto-publish/
├── SKILL.md                    # 技能主文档
├── references/
│   ├── xhs-auto-publish-v2.sh  # 主脚本副本
│   └── README.md              # 使用指南
└── scripts/
    └── setup.sh               # 安装脚本
```

## 版本历史

- **v1.0.0** (2026-04-08): 初始版本
  - 基于xhs-auto-publish-v2.sh创建
  - 支持两种发布模式
  - 添加幂等性检查
  - 创建完整技能文档结构

## 注意事项

1. **账号安全**：确保小红书账号安全，避免频繁发布
2. **内容质量**：定期检查生成内容的质量和合规性
3. **频率控制**：合理设置发布频率，避免被平台限制
4. **备份重要**：定期备份技能配置和生成的内容