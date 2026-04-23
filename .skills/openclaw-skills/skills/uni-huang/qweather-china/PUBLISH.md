# 发布指南

## 发布到 ClawHub

### 1. 确保已安装 ClawHub CLI
```bash
npm install -g clawhub
```

### 2. 登录 ClawHub
```bash
clawhub login
```

### 3. 发布技能
```bash
# 进入技能目录
cd ~/.openclaw/workspace/qweather-china-clean

# 发布到 ClawHub
clawhub publish . \
  --slug qweather-china \
  --name "国内天气预报 - 和风天气(QWeather)驱动" \
  --version 1.3.0 \
  --changelog "安全性增强：添加.gitignore、LICENSE、配置模板；完善权限声明；跨平台路径优化"
```

### 4. 验证发布
```bash
clawhub search qweather-china
clawhub info qweather-china
```

## 版本说明

### v1.3.0 改进点
1. **安全性**
   - 添加 `.gitignore` 防止敏感信息泄露
   - 添加 `config.json.template` 模板
   - 完全移除硬编码凭证

2. **合规性**
   - 添加 MIT LICENSE
   - 添加 CHANGELOG.md
   - 完善权限声明

3. **跨平台**
   - 自动处理缓存路径
   - 自动处理私钥路径
   - 支持 Windows/Linux/macOS

4. **文档**
   - 详细的安装说明
   - 网络访问声明
   - 配置文件模板

## 目录结构

```
qweather-china-clean/
├── .gitignore              # Git忽略文件
├── CHANGELOG.md            # 版本变更日志
├── LICENSE                 # MIT许可证
├── README.md               # 用户文档
├── SKILL.md                # OpenClaw技能文档
├── PUBLISH.md              # 本文件
├── config.json             # 配置文件（用户配置）
├── config.json.template    # 配置模板
├── skill.yaml              # ClawHub技能配置
├── qweather.py             # 核心天气服务
├── openclaw_integration.py # OpenClaw集成
├── encoding_utils.py       # 编码处理
├── location_handler.py     # 地点处理
└── simple_question_fix.py  # 简单问题处理
```

## 安全检查清单

- [x] 无硬编码敏感信息
- [x] 有 .gitignore 文件
- [x] 有 LICENSE 文件
- [x] 有 CHANGELOG.md
- [x] skill.yaml 完整
- [x] README.md 完整
- [x] SKILL.md 完整
- [x] 权限声明清晰
- [x] 网络访问声明清晰
