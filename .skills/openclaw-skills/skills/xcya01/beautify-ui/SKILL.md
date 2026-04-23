# beautify-ui - 智能 UI 美化技能 v3.0.1

🎨 一键应用 16 种知名设计风格（Notion/Figma/Linear/Apple 等），自动检测项目类型并生成实时预览页

## 功能特性

- **16 种设计风格**：Notion、Figma、Linear、Vercel、Stripe、Apple、Tesla、Spotify 等
- **智能项目检测**：自动识别 Vite/Next.js/Tailwind/CRA 等项目类型
- **自动风格推荐**：根据内容类型（教育/文档/电商）推荐最佳风格
- **实时预览**：生成对比页，一键查看修改前后效果
- **智能 CSS 注入**：支持多种框架，自动处理构建项目
- **Tailwind 支持**：生成 tailwind.config.js 配置建议

## 使用方法

### 基础用法
```bash
# 指定风格
py skills/beautify-ui/scripts/beautify.py <项目路径> linear

# 智能推荐（自动检测并推荐最佳风格）
py skills/beautify-ui/scripts/beautify.py <项目路径> --auto

# 生成实时预览页（不修改原项目）
py skills/beautify-ui/scripts/beautify.py <项目路径> apple --preview

# 查看帮助
py skills/beautify-ui/scripts/beautify.py --help
```

### 使用示例
```bash
# 示例 1：教育网站美化（自动推荐 Notion 风格）
py skills/beautify-ui/scripts/beautify.py C:\projects\edu-site --auto

# 示例 2：技术文档美化（指定 Vercel 风格）
py skills/beautify-ui/scripts/beautify.py C:\projects\docs vercel

# 示例 3：生成 Apple 风格预览页
py skills/beautify-ui/scripts/beautify.py C:\projects\my-site apple --preview

# 示例 4：批量处理多个项目
for project in project1 project2 project3; do
  py skills/beautify-ui/scripts/beautify.py C:\projects\$project linear
done
```

## 支持的 16 种风格

### 教育文档类（4 种）
- `notion` - 温暖简约，适合教育/文学/阅读
- `vercel` - 黑白科技感，适合技术文档/API
- `claude` - 温暖陶土色，适合阅读写作
- `cursor` - 暗黑编辑器风，适合开发工具

### 创意设计类（4 种）
- `figma` - 活泼多彩，适合互动/创意/年轻
- `elevenlabs` - 暗黑电影感，适合音频/媒体
- `spotify` - 绿黑音乐风，适合娱乐媒体
- `airbnb` - 珊瑚旅行风，适合生活摄影

### 工具效率类（4 种）
- `linear` - 极简精准，适合工具/逻辑/效率
- `raycast` - 暗铬渐变，适合效率工具
- `superhuman` - 高级键盘流，适合邮件效率
- `ollama` - 终端单色，适合极客开发者

### 商务金融类（4 种）
- `stripe` - 专业紫色，适合商务/金融/企业
- `tesla` - 未来科技感，适合汽车/科技
- `apple` - 高级留白电影感，适合高端零售

## 输出内容

执行后生成：

1. **DESIGN.md** - 完整设计规范文档
   - 色彩系统
   - 字体规范
   - 组件样式
   - 布局原则

2. **styles/theme-override.css** - CSS 变量覆盖文件
   - 全局样式覆盖
   - 组件样式优化
   - 使用 `!important` 确保优先级

3. **assets/theme-override.css** - 构建项目专用（如适用）
   - 自动复制到 assets 目录
   - 支持 Vite/Next.js/CRA 项目

4. **preview-{style}.html** - 实时预览页（使用 --preview 时）
   - 完整 HTML 页面
   - 交互式色彩系统展示
   - 按钮/卡片效果演示
   - 对比区域（修改前后）

## 智能检测能力

自动识别：
- **项目类型**：Static HTML / Vite / Next.js / Create React App
- **样式系统**：Tailwind CSS / CSS Modules
- **内容类型**：教育/文档/电商/通用

根据检测结果：
- 推荐最适合的风格
- 选择正确的 CSS 注入策略
- 处理构建项目的特殊需求

## 适用场景

- ✅ 快速美化教育网站/学习平台
- ✅ 为技术文档应用专业风格
- ✅ 电商网站风格统一
- ✅ 企业官网视觉升级
- ✅ 个人博客美化
- ✅ 原型设计快速出效果
- ✅ A/B 测试不同风格效果

## 注意事项

⚠️ **重要提示**：
1. 本技能会修改项目文件，建议先备份或使用 Git
2. 构建项目（Vite/Next.js）需要手动添加 CSS 引用
3. 预览页会生成在项目目录中，可手动删除
4. 使用 `--preview` 参数不会修改原项目

💡 **最佳实践**：
- 首次使用建议先用 `--auto` 让技能推荐风格
- 使用 `--preview` 查看效果后再应用
- 生产环境使用前先在开发环境测试
- 保留 DESIGN.md 作为项目文档

## 技术细节

### 项目类型检测
- 读取 `package.json` 判断框架（Vite/Next.js/CRA）
- 扫描依赖检测 Tailwind CSS
- 分析文件结构识别 CSS Modules

### CSS 注入策略
1. 生成 CSS 变量（`:root`）
2. 全局覆盖（使用 `!important`）
3. 针对组件选择器优化
4. 构建项目自动复制到 `assets/`

### 预览页生成
- 完整 HTML 页面（含样式）
- 交互式色彩系统展示
- 按钮/卡片效果演示
- 对比区域（修改前后）

## 更新日志

### v3.0.1 (2026-04-14)
- 📝 完善 SKILL.md 文档
- 📝 添加详细使用示例
- 📝 补充风格列表说明
- 📝 添加注意事项和最佳实践

### v3.0.0 (2026-04-14)
- ✨ 新增实时预览功能（--preview）
- ✨ 风格库扩展至 16 种
- ✨ 智能项目检测（Vite/Next.js/Tailwind）
- ✨ 自动风格推荐
- 🐛 修复构建项目 CSS 注入问题
- 🐛 优化 Windows 编码兼容性

### v2.0.0
- ✨ 智能项目检测
- ✨ 自动风格推荐
- ✨ Tailwind 配置支持

### v1.0.0
- 🎉 初始版本发布
- 5 种基础风格

## 文件结构

```
beautify-ui/
├── SKILL.md              # 技能说明（本文件）
├── README.md             # 使用文档
├── scripts/
│   └── beautify.py       # 核心脚本（v3.0）
```

## 致谢

灵感来自 [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 项目，感谢 VoltAgent 团队的出色工作！

## 许可证

MIT License

## 支持与贡献

- **问题反馈**：欢迎提交 Issue
- **风格建议**：欢迎 PR 新风格
- **功能建议**：欢迎讨论改进方案

---

**作者**：OpenClaw Community  
**版本**：3.0.1  
**最后更新**：2026-04-14
