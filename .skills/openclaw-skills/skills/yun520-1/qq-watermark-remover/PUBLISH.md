# 📦 发布到 ClawHub 指南

## 项目信息

- **名称**: QQ Video Watermark Remover
- **Slug**: qq-watermark-remover
- **版本**: 1.0.0
- **描述**: 智能 QQ 视频水印去除工具 - 自动识别并去除"豆包 AI 生成"水印

## 发布步骤

### 1. 登录 ClawHub

```bash
cd /Users/apple/.jvs/.openclaw/workspace/qq-watermark-remover
clawhub login
```

### 2. 验证登录

```bash
clawhub whoami
```

### 3. 发布到 ClawHub

```bash
clawhub publish ./ \
  --slug qq-watermark-remover \
  --name "QQ Video Watermark Remover" \
  --version 1.0.0 \
  --changelog "初始版本 - 智能 QQ 视频水印去除工具" \
  --tags "latest,watermark,video,qq,doubao"
```

### 4. 验证发布

```bash
# 搜索已发布的技能
clawhub search "qq watermark"

# 查看技能详情
clawhub show qq-watermark-remover
```

## 项目结构

```
qq-watermark-remover/
├── final_perfect.py          # 主程序 - 最终完美版
├── batch_final.py            # 批量处理脚本
├── requirements.txt          # Python 依赖
├── README.md                 # 使用文档
├── PUBLISH.md                # 本文档
└── examples/
    └── doubao_config.py      # 示例配置
```

## 安装后使用

### 用户安装

```bash
clawhub install qq-watermark-remover
```

### 使用方式

**单个视频:**
```bash
python final_perfect.py /path/to/video.mp4 /path/to/output.mp4
```

**批量处理:**
```bash
python batch_final.py
```

## 更新版本

### 修改代码后更新

1. 更新版本号（semver 格式）
2. 更新 changelog
3. 重新发布

```bash
clawhub publish ./ \
  --slug qq-watermark-remover \
  --name "QQ Video Watermark Remover" \
  --version 1.0.1 \
  --changelog "修复 bug + 性能优化" \
  --tags "latest"
```

### 用户更新

```bash
clawhub update qq-watermark-remover
```

## 注意事项

1. **版本号**: 遵循 semver 规范（major.minor.patch）
2. **Tags**: 至少包含 "latest" 标签
3. **Changelog**: 简洁描述变更内容
4. **依赖**: 确保 requirements.txt 包含所有依赖

## 故障排除

### 发布失败

**错误**: `Not logged in`
```bash
clawhub login
```

**错误**: `Slug already exists`
- 使用新版本号重新发布
- 或联系管理员删除旧版本

**错误**: `Network error`
- 检查网络连接
- 稍后重试

### 安装失败

**错误**: `Skill not found`
- 确认 slug 正确
- 检查是否已发布

**错误**: `Dependency error`
```bash
pip install -r requirements.txt
```

## 联系支持

如有问题，请提交 Issue 或联系 ClawHub 支持。

---

**最后更新**: 2026-03-15  
**版本**: 1.0.0
