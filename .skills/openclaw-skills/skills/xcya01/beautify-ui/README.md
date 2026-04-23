# beautify-ui 技能

## 🎨 功能说明
基于 DESIGN.md 规范自动美化网站 UI，支持多种知名设计风格。

## 🚀 快速开始

### 方式 1：直接调用脚本
```bash
# Windows PowerShell
py C:\Users\sys\.openclaw\workspace\skills\beautify-ui\scripts\beautify.py <项目路径> <风格>

# 示例 - 语文网站用 Notion 风格
py C:\Users\sys\.openclaw\workspace\skills\beautify-ui\scripts\beautify.py C:\Users\sys\Desktop\jiangsu-grade3-poems notion
```

### 方式 2：用自然语言调用
直接对我说：
- "帮我把语文网站改成 Notion 风格"
- "用 Figma 风格美化英语网站"
- "把数学网站改成 Linear 风格"

## 🎭 支持的样式

| 风格 | 效果 | 适用场景 |
|------|------|----------|
| `notion` | 温暖简约 | 语文、文学、教育类 |
| `figma` | 活泼多彩 | 英语、互动、创意类 |
| `linear` | 极简精准 | 数学、工具、效率类 |
| `vercel` | 黑白科技感 | 技术文档、开发者工具 |
| `stripe` | 专业优雅 | 商务、金融、企业服务 |

## 📦 输出内容

执行后会生成：
1. **DESIGN.md** - 完整设计规范文档
2. **styles/theme-override.css** - 可直接引用的 CSS 变量覆盖
3. **控制台报告** - 修改建议和下一步操作

## 🔧 高级用法

### 查看可用风格
```bash
py skills/beautify-ui/scripts/beautify.py --help
```

### 自定义风格
编辑 `scripts/beautify.py` 中的 `DESIGN_TEMPLATES` 字典，添加自己的配色方案。

## 📝 示例输出

```
🎨 开始美化项目：jiangsu-grade3-poems
   风格：Notion - 温暖简约，适合文学、教育类

✅ 已生成：DESIGN.md
✅ 已生成：styles/theme-override.css

📋 下一步操作：
   1. 在 HTML 的 <head> 中添加：<link rel='stylesheet' href='styles/theme-override.css'>
   2. 或者将 CSS 变量合并到现有样式中
   3. 查看 DESIGN.md 了解完整设计规范

✨ 完成！
```

## 🛠️ 技术细节

- **零依赖**：仅需 Python 3.8+ 标准库
- **非侵入式**：生成独立 CSS 文件，不影响原代码
- **可逆**：删除生成的文件即可恢复原样
- **可扩展**：支持自定义风格模板

---

**创建时间**：2026-04-14  
**版本**：1.0.0
