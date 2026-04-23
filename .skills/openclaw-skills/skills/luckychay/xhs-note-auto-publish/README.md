# xhs-auto-publish Skill

[![ClawHub](https://img.shields.io/badge/ClawHub-Skill-blue)](https://clawhub.com/skills/xhs-auto-publish)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

小红书笔记自动生成与发布技能，支持两种模式：外部主题模式和自动选题模式。

## 功能特性

- **两种发布模式**：
  - **外部主题模式**：用户指定主题，生成相关内容
  - **自动选题模式**：自动搜索热点，智能确定主题
- **幂等性保护**：自动检查避免重复执行
- **标准化输出**：统一封面风格和标签要求
- **一次发布策略**：仅发布一次，无论成功与否均停止
- **定时任务支持**：可配置cron定时自动发布

## 安装

```bash
# 使用ClawHub CLI安装
clawhub install xhs-auto-publish
```

## 使用方法

### 作为技能调用

当用户提到以下关键词时激活此技能：
- "自动发布小红书"
- "小红书自动发布"
- "xhs-auto-publish"
- "小红书定时发布"
- "自动生成小红书内容"

### 直接脚本使用

```bash
# 外部主题模式
./scripts/xhs-auto-publish-v2.sh "新加坡Kaplan学院"

# 自动选题模式
./scripts/xhs-auto-publish-v2.sh --auto
```

### 配置定时任务

```bash
# 每天上午10点自动发布（自动选题模式）
0 10 * * * cd /path/to/workspace && ./scripts/xhs-auto-publish-v2.sh --auto

# 每周一、三、五下午3点发布指定主题
0 15 * * 1,3,5 cd /path/to/workspace && ./scripts/xhs-auto-publish-v2.sh "新加坡留学申请攻略"
```

## 技能要求

- 需要已安装并配置小红书技能 (`xhs`)
- 需要OpenClaw agent正常运行
- 需要bash shell环境

## 文件结构

```
xhs-auto-publish/
├── SKILL.md                    # 技能主文档
├── package.json               # 技能元数据
├── README.md                  # 项目说明
├── CHANGELOG.md              # 版本历史
├── references/
│   ├── xhs-auto-publish-v2.sh  # 主脚本副本
│   └── README.md              # 详细使用指南
└── scripts/
    └── setup.sh              # 安装配置脚本
```

## 配置说明

### 封面生成
- 使用ImageMagick生成浅色背景深色字体封面
- 标题作为封面文字，保持一致性
- 封面文字内容与标题保持一致

### 标签要求
- 必须包含 `#留学新加坡` 和 `#新加坡私立大学`
- 话题标签不超过5个

### 内容要求
- 内容真诚务实、不引导讨论
- 标题默认选择第一个
- 仅发布一次，无论成功与否均停止

## 故障排除

### 常见问题

1. **脚本无法执行**
   ```bash
   # 检查权限
   chmod +x ~/.openclaw/workspace/scripts/xhs-auto-publish-v2.sh
   ```

2. **重复执行警告**
   ```bash
   # 查看正在运行的任务
   ps aux | grep -E "openclaw.*agent.*xhs-auto-publish" | grep -v grep
   ```

3. **发布失败**
   - 检查小红书账号是否已登录
   - 检查网络连接
   - 查看OpenClaw日志：`openclaw logs`

## 版本历史

详见 [CHANGELOG.md](CHANGELOG.md)

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和Pull Request！

## 支持

如有问题，请访问：
- [ClawHub技能页面](https://clawhub.com/skills/xhs-auto-publish)
- [OpenClaw社区](https://discord.com/invite/clawd)