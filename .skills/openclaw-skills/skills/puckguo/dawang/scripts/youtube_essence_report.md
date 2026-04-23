# YouTube 频道精华内容整理

> 生成时间: 2026-04-06  
> 数据来源: Jeff Su, Andrej Karpathy, Tina Huang, Dave Ebbelaar, IBM Technology, Google Cloud Tech

---

## 🎬 Jeff Su - NotebookLM 2026 完全指南

### 视频信息
- **标题**: NotebookLM Changed Completely: Here's What Matters (in 2026)
- **时长**: 20分30秒 | **观看**: 246K | **2周前**
- **链接**: https://www.youtube.com/watch?v=_uXnyhrqmsU
- **转录状态**: ✅ 已完成（本地 Whisper 转录）

---

### 📝 完整字幕（已提取）

 Notebook LM, after receiving a massive amount of updates recently, is now more popular than even Gemini in terms of usage and interest. Which is pretty wild. So, if you're still using Notebook LM, like you were a few weeks ago, you're missing out on some incredible capabilities. In this video, I cover what Notebook LM is still the best at, then go through the features and the workflows that actually matter. Let's get started.

 Even with all the updates, Notebook LM's core advantage has not changed. Here's a simple illustration. The first one gives you a PDF brochure, the second gives you a spreadsheet and the third recorded a video walkthrough. Instead of digging through all that dense material, you'll throw them into Notebook LM and ask something like, "Which provider offers the best dental coverage?" And Notebook LM parses through everything to give you a grounded answer.

 **Notebook LM 适用场景（三个条件）：**
 1. 你已经知道哪些文档包含答案，只需要帮助提取
 2. 不同格式（PDF/表格/幻灯片）或不同媒介（文本/音频/视频），没有单一来源能提供完整信息
 3. 需要 AI 严格基于文档回答，不能胡编——因为出错代价太高

 **三栏布局：**
 - 左侧：Sources Panel（来源面板）—— 添加所有需要处理的文档
 - 中间：Chat Panel（聊天面板）—— 提问、总结、提取细节
 - 右侧：Studio Panel（工作室面板）—— 生成实际可用的交付物

 **来源面板使用技巧：**
 - Web + Fast Research = Google 搜索，但不离线
 - Drive + Fast Research = Google Drive 搜索
 - Web + Deep Research = 搜索 + 综合成研究报告
 - Pro tip: Google Docs/Slides/Sheets 是"活文档"，会自动同步更新；PDF 是静态上传
 - Pro tip: 无法直接添加的网站 → 右键 → 阅读模式 → 全选文本 → 粘贴到 Notebook LM

 **聊天面板核心功能：**
 - Configure Chat Window（配置聊天窗口）：为高风险任务添加自定义指令
 - 删除聊天历史前检查是否有值得保留的内容
 - Source Guide 功能：自动分析来源并给出后续问题建议

 **Studio Panel - Tier 1 必备工具：**

 **1. Reports（报告）**
 - 从原始来源生成完整的简报或竞争分析
 - Suggested Formats 是动态的，会根据来源自动推荐最有用方向
 - 可以自定义格式或用 Gemini 的提示模板

 **2. Slide Decks（幻灯片）**
 - 从来源直接生成完整演示文稿
 - 注意：下载的 PPT 中所有幻灯片都是图片，不可编辑
 - 妙用：用它来生成演示叙事的初稿，减少头脑风暴时间
 - 还可生成社交媒体用的竖屏轮播图（1916 portrait format）

 **3. Infographics（信息图）**
 - 将来源转化为单个精美视觉图
 - 适合发 LinkedIn/Instagram
 - Pro tip: 上传品牌指南作为来源，确保风格一致

 **4. Mind Maps（思维导图）**
 - 一目了然展示所有来源内容
 - 点击任意节点可直接进入该主题的聊天
 - 非常适合准备内容创作前快速浏览素材

 **Studio Panel - Tier 2 场景工具：**

 **5. Data Tables（数据表）**
 - 从分散的来源中提取信息到可排序/筛选的表格
 - 可直接导出到 Google Sheets

 **6. Video Overviews（视频概览）**
 - 将来源转化为带解说的幻灯片
 - 适合不想阅读长文的情况
 - 新功能：Cinematic Mode 可生成动画序列（Ultra 订阅限定）

 **7. Quiz（测验）**
 - 基于来源生成多项选择题
 - 适合培训和会议互动

 **8. Flashcards（闪卡）**
 - 帮助记忆关键术语、概念或事实
 - 适合备考

 **9. Audio Overviews（音频概览）**
 - Jeff 直言这个对他来说主要是噱头
 - 真正有用的场景：通勤时听长文通讯

 **实用场景举例：**
 - 健康报告：上传年度体检报告，追踪变化趋势
 - 会议记录知识库：自动生成的会议记录存入笔记本
 - 税务：上传财务报表+税法，询问可抵扣项目

 **核心限制：**
 - Notebook LM 最大优势（高准确性）也是最大局限（缺乏创造力）
 - 需要创造力时用 Gemini、ChatGPT、Claude 或 Grok

---

## 📊 其他频道精华

### Andrej Karpathy
- **最新视频**: How I use LLMs (2小时11分钟, 2.3M观看)
- **特色**: OpenAI 创始成员，最受欢迎的 LLM 教育者

### Tina Huang
- **最新视频**: Every Way To Run Open Source AI Models (17分钟, 66K观看)
- **特色**: 前 Meta 数据工程师，AI Agent 入门专家

### Dave Ebbelaar  
- **最新视频**: I Stopped Writing Code - These 5 Skills Are All That Matter (10分钟, 16K观看)
- **特色**: Datalumina 创始人，AI 工程师视角

### IBM Technology
- **最新视频**: Agentic Trust: Securing AI Interactions with Tokens & Delegation (5分钟)
- **特色**: AI Agent 安全系列专家

### Google Cloud Tech
- **最新视频**: Vibe coding to production: AI agents, testing & CI/CD with Gemini CLI
- **特色**: Gemini CLI 实战，Multi-Agent 系统

---

## 🔧 转录工具链

**成功验证的工作流：**
```
YouTube URL → yt-dlp (下载音频) → whisper.cpp (本地 ASR) → .txt 字幕文件
```

**所需工具：**
- yt-dlp (`brew install yt-dlp`)
- whisper-cpp (`brew install whisper-cpp`)
- whisper 模型（ggml-tiny.bin，74MB）

**使用命令：**
```bash
./transcribe.sh "YouTube链接" "输出文件.txt"
```

**性能参考（Jeff Su 20分30秒视频）：**
- 转录时间：约 4.4 分钟
- 使用模型：tiny（最快，精度较低）
- 如需更高精度可换 base/small 模型

---

*字幕文件位置：`~/.openclaw/workspaces/dawang/scripts/transcripts/jeffsu_notebooklm.txt`*
