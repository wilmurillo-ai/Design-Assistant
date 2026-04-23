# xhs-auto-publish 技能

小红书笔记自动生成与发布技能，支持两种模式：外部主题模式和自动选题模式。

## 功能描述

本技能封装了 `xhs-auto-publish-v2.sh` 脚本的功能，提供以下能力：

1. **外部主题模式**：使用用户指定的主题生成小红书笔记并发布
2. **自动选题模式**：自动搜索小红书社区热点内容确定主题，生成相关内容并发布

## 使用方法

### 作为技能调用

当用户提到以下关键词时激活此技能：
- "自动发布小红书"
- "小红书自动发布"
- "xhs-auto-publish"
- "小红书定时发布"
- "自动生成小红书内容"
- "帮我自动发小红书"
- "小红书自动化发布"

### 技能激活后的行为

当技能被激活时，你应该：
1. 询问用户希望使用哪种模式（外部主题模式或自动选题模式）
2. 如果选择外部主题模式，询问具体主题
3. 确认后执行相应的脚本命令
4. 向用户反馈执行状态和结果

### 直接脚本使用

你也可以直接在工作空间中使用脚本：

```bash
# 进入工作空间目录
cd ~/.openclaw/workspace

# 外部主题模式
./scripts/xhs-auto-publish-v2.sh "新加坡Kaplan学院"

# 自动选题模式
./scripts/xhs-auto-publish-v2.sh --auto
```

### 技能执行流程

1. **参数解析**：解析用户输入，确定使用哪种模式
2. **Prompt构建**：根据模式构建合适的prompt
3. **幂等性检查**：避免重复执行相同任务
4. **Agent调用**：调用OpenClaw agent执行内容生成和发布
5. **结果反馈**：向用户反馈执行状态

## 脚本位置

主脚本位于：`scripts/xhs-auto-publish-v2.sh`

## 依赖关系

- 需要已安装并配置小红书技能 (`xhs`)
- 需要OpenClaw agent正常运行
- 需要bash shell环境

## 配置要求

无特殊配置要求，但建议：
1. 确保小红书技能已正确配置账号
2. 确保OpenClaw agent有足够权限执行任务
3. 如有需要，可以配置cron定时任务

## 示例用法

```bash
# 外部主题模式
./scripts/xhs-auto-publish-v2.sh "新加坡Kaplan学院"
./scripts/xhs-auto-publish-v2.sh "新加坡留学申请攻略"

# 自动选题模式
./scripts/xhs-auto-publish-v2.sh --auto
./scripts/xhs-auto-publish-v2.sh -a
```

## 注意事项

1. **幂等性**：脚本会自动检查是否有相同任务正在运行，避免重复发布
2. **封面生成**：使用ImageMagick生成浅色背景深色字体封面
3. **标签要求**：必须包含 `#留学新加坡` 和 `#新加坡私立大学`
4. **发布策略**：仅发布一次，无论成功与否均停止

## 技能文件结构

```
xhs-auto-publish/
├── SKILL.md                    # 技能说明文档
├── references/                 # 参考文件目录
│   ├── xhs-auto-publish-v2.sh  # 主脚本副本
│   └── README.md              # 详细使用指南
└── scripts/                   # 辅助脚本目录
    └── setup.sh              # 安装配置脚本
```

## 更新日志

- v1.0.0 (2026-04-08): 初始版本，基于xhs-auto-publish-v2.sh创建