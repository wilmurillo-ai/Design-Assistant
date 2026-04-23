---
name: china-summarizer
description: 中文内容智能总结工具。Use when the user wants to summarize local files (TXT/MD/PDF/Word), web pages, news articles, or WeChat public account articles. No login, no API key, no VPN required. Extracts content via local file reading or curl, then summarizes using the current OpenClaw model. Domestic-friendly.
version: 1.0.0
license: MIT-0
metadata: {"openclaw": {"emoji": "📝", "requires": {"bins": ["curl", "python3"]}}}
---

# 中文内容智能总结 China Summarizer

支持本地文件和网页内容的智能总结。
使用 OpenClaw 当前加载的模型进行总结，无需任何额外配置。

内容提取技术细节 → `references/extract.md`
总结提示词模板 → `references/prompts.md`

## 触发时机

- "帮我总结这篇文章：[URL]"
- "这篇公众号讲了什么：[URL]"
- "总结一下这个文件：/path/to/file.pdf"
- "提炼这份文档的核心内容：/path/to/file.docx"
- 用户粘贴一段文字，要求提炼要点

---

## Step 1：识别内容源

```
包含 http:// 或 https:// → 网页/公众号 → [网页流程]
路径包含 .pdf            → 本地 PDF   → [PDF流程]
路径包含 .docx           → 本地 Word  → [Word流程]
路径包含 .txt / .md      → 本地文本   → [文本流程]
用户直接粘贴文字          → 直接进入   → [总结流程]
```

---

## [网页/公众号流程]

### Step W1：curl 抓取

```bash
curl -s "{URL}" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" \
  -H "Accept: text/html,application/xhtml+xml;q=0.9,*/*;q=0.8" \
  -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
  -L --max-time 15
```

### Step W2：提取正文

从 HTML 提取纯文本，处理规则：

```
去除：<script> <style> <nav> <header> <footer> <aside> 及其内部内容
去除：HTML 注释、HTML 标签（保留标签内文字）
去除：连续空行（多个空行合并为一个）
保留：<p> <h1>~<h6> <li> <article> <main> <section> 中的文本

微信公众号特殊处理：
  正文集中在 <div id="js_content"> 内
  优先提取该区域内容
```

### Step W3：质量检查

```
提取文本 < 200 字：
  → 页面为 JS 动态渲染，curl 无法获取正文
  → 告知用户：该页面需要 JavaScript，无法直接抓取
  → 建议：将文章内容复制粘贴后再请求总结

提取文本 ≥ 200 字：
  → 进入 [总结流程]
```

### 支持情况说明

```
✅ 通常可以直接抓取：
  微信公众号（mp.weixin.qq.com）
  知乎专栏（zhuanlan.zhihu.com）
  博客园（cnblogs.com）
  CSDN 博客（blog.csdn.net）
  简书（jianshu.com）
  少数派（sspai.com）
  36氪、虎嗅、澎湃等新闻网站
  政府/机构官网静态页面

⚠️ 可能失败（JS渲染）：
  今日头条、微博、部分知乎回答
  → 遇到时引导用户手动复制文本
```

---

## [本地 PDF 流程]

按顺序尝试，成功即停止：

```bash
# 方法1：pdftotext（最推荐）
pdftotext /path/to/file.pdf -

# 方法2：Python pypdf
python3 -c "
import pypdf
r = pypdf.PdfReader('/path/to/file.pdf')
print('\n'.join([p.extract_text() or '' for p in r.pages]))
"

# 方法3：Python pdfminer
python3 -m pdfminer.high_level /path/to/file.pdf
```

全部失败时提示：
```
请安装 PDF 解析工具（选择其中一种）：
  macOS:   brew install poppler
  Ubuntu:  sudo apt install poppler-utils
  Python:  pip install pypdf
```

提取结果为空或乱码时：
```
该 PDF 可能是扫描版（图片型），文本提取工具无法处理。
建议：使用 OCR 工具处理，或手动复制文字后粘贴总结。
```

---

## [本地 Word 流程]

```bash
python3 -c "
import docx
doc = docx.Document('/path/to/file.docx')
paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
print('\n'.join(paragraphs))
"
```

失败时提示：
```
pip install python-docx
```

---

## [本地文本流程]

```bash
cat /path/to/file.txt
# 或
cat /path/to/file.md
```

---

## [总结流程]

获取到纯文本后，根据内容类型从 `references/prompts.md` 选择对应模板进行总结。

**内容类型判断：**
```
包含大量代码/命令/配置   → 技术文章模板
包含时间/地点/人名/事件  → 新闻简报模板
包含研究方法/数据/结论   → 学术报告模板
其他                     → 通用总结模板
```

**输出格式（通用）：**

```
📝 内容总结
━━━━━━━━━━━━━━━━━━━━
来源：[文件名 / URL]
提取字数：约 X 字

【核心观点】
（1-3句话，概括最重要的结论）

【主要内容】
• 要点1
• 要点2
• 要点3
（3-7条，视内容长度而定）

【关键信息】
（具体数字、时间、人名、结论等值得记录的细节）

【一句话总结】
（用一句话概括全文精髓）
```

**内容过长（> 8000字）时：**
```
1. 将内容分为若干段（每段约2000字）
2. 对每段先生成段落摘要
3. 再对所有段落摘要做最终汇总
```

---

## 总结质量要求

```
✅ 保留原文所有具体数字、时间、人名
✅ 忠实原文，不添加原文没有的内容
✅ 用中文输出（无论原文是何语言）
✅ 长文总结控制在 500 字以内
✅ 逻辑清晰，层次分明

❌ 不用"本文介绍了..."等废话开头
❌ 不泛泛而谈，要有实质信息
❌ 不遗漏核心数据和结论
```
