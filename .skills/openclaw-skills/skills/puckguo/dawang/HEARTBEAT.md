# HEARTBEAT.md - 大汪心跳任务

## 定时任务

### 每30分钟检查
- [x] 查看 TODO.md 中的待办任务
- [x] 检查是否有新任务分配
- [x] 更新任务进度
- [x] 检查小红书活动爬虫输出，如有新内容则更新飞书文档

### 每小时汇报
- [x] 向 puck 汇报当前任务状态
- [x] 报告已完成的任务
- [x] 报告遇到的问题（如有）

## 当前状态
- 最后检查: 2026-03-26 06:54
- 进行中任务: 0
- 待处理任务: 1 (飞书凭据未配置)
- 已完成任务: 5
- 备注: 2026-03-25 16:09 完成播客精选日报功能，新增自动抓取任务(每晚8点)

## 待处理问题
- ✅ 飞书发送已修复（2026-04-02）：脚本已更新，绕过代理直连飞书API

## 问题记录
- ⚠️ 2026-03-24 21:42: 飞书凭据未配置，文档更新失败 (doc: XgKqdoo0AoXiCrxdHeqcwasnnae)

## 自动化任务

### 小红书 OpenClaw 活动爬虫 (2026-03-24)
- ✅ 爬虫脚本创建完成
- ✅ 飞书文档创建完成
- ✅ Cron Job 创建完成 (每天晚上7点)
- 飞书文档: https://feishu.cn/docx/XgKqdoo0AoXiCrxdHeqcwasnnae
- 数据文件: `~/.openclaw/workspaces/dawang/scripts/xhs_openclaw_data.json`
- 输出文件: `~/.openclaw/workspaces/dawang/scripts/xhs_openclaw_output.json`

**心跳检查流程:**
1. 检查 `xhs_openclaw_output.json` 是否存在
2. 检查 `has_new` 字段是否为 true
3. 如有新内容，读取 `content` 字段并更新飞书文档
4. 更新后重置状态

### 播客精选日报 (2026-03-25)
- ✅ 抓取脚本创建完成 (支持 Lex Fridman, All-In, Latent Space, Lenny's)
- ✅ 飞书文档创建完成
- ✅ Cron Job 创建完成 (每天晚上8点)
- ✅ 本地日报保存完成 (report_YYYY-MM-DD.md)
- 脚本位置: `~/.openclaw/workspaces/dawang/scripts/podcasts/`
- 报告输出: `~/.openclaw/workspaces/dawang/scripts/podcasts/latest_report.md`
- Cron Job: `~/Library/LaunchAgents/com.dawang.podcast-updater.plist`
- 最新文档: https://feishu.cn/docx/XhyNdCzCeoO54vxZCA7cyPk3n1b

**心跳检查流程:**
1. 检查 `latest_report.md` 是否存在且有更新
2. 如有新内容，读取内容并创建飞书文档
3. 通过飞书消息通知 puck
4. 注意：Python脚本无法调用飞书API（代理阻断），需通过 feishu_doc 工具创建文档

## 进行中任务

### 网站重新部署 (2026-03-24 15:37)
- ✅ beijing-bbq 重新部署到 nginx 目录
- ✅ 美国中餐连锁报告 (us_chains.html) 部署完成
- ✅ 截图已上传 (panda_express, pf_changs, pei_wei, pick_up_stix, china_wok, jade_wok)
- 访问地址: http://8.147.56.18/report/us_chains.html

## 文件位置
- TODO: `/Users/godspeed/.openclaw/workspaces/dawang/TODO.md`
- 心跳脚本: `/Users/godspeed/.openclaw/workspaces/dawang/heartbeat.sh`
- 汇报脚本: `/Users/godspeed/.openclaw/workspaces/dawang/daily-report.sh`
- 日志: `/Users/godspeed/.openclaw/agents/dawang/cron/`
- 爬虫脚本: `/Users/godspeed/.openclaw/workspaces/dawang/scripts/xhs_openclaw_scraper.py`
- Cron Job: `~/Library/LaunchAgents/com.dawang.xhs_scraper.plist`
