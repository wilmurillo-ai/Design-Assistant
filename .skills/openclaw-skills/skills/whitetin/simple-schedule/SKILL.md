---
name: simple-schedule
description: 简单智能日程安排管理技能。支持自然语言添加日程，自动检测时间冲突，结合高德地图路线规划智能计算出发提醒时间，到点推送通知。支持修改、删除、查询日程。当用户说"记一下"、"提醒我"、"日程"、"安排"、"行程"时使用此技能。
---

# Simple Schedule 简单日程安排

## 概述

纯本地管理的智能日程技能，用户用自然语言说清楚「什么时候，去哪里，做什么」，自动添加日程。支持：
- 自动检测时间冲突，避免重复安排
- 结合地图技能计算路程时间，智能提醒出发，避免迟到
- 支持修改/删除/查询日程
- 自动设置定时提醒，到点推送通知

## 核心工作流程

**架构原则**：自然语言理解是大模型强项，AI直接解析，脚本只做确定性工作。

### 1. 添加日程
用户说："明天下午4点去天河机场坐飞机"
技能自动：
1. **AI直接解析**时间、地点、事项、出发地，识别是不是DDL
2. 调用`schedule_manager.py`检测是否和已有日程时间冲突
3. 如果有目的地和高德API，调用`map_router.py`计算从起点到目的地的路程时间
4. 计算提醒时间，调用`reminder_manager.py`创建cron定时提醒
5. 保存日程到存储

### 2. 修改日程
用户说："把明天下午4点的飞机改成明天晚上8点"
技能自动：
1. **AI直接解析**用户要修改哪个日程，改成什么新时间
2. 匹配最接近的原日程
3. 更新时间，重新检查冲突
4. 重新计算提醒时间，更新cron定时任务
5. 保存修改

### 3. 删除日程
用户说："取消明天下午的行程"
技能自动：
1. AI识别要取消哪个日程
2. 匹配日程，调用删除接口
3. 删除对应的cron定时提醒
4. 返回结果

### 4. 查询日程
用户说："看看今天有什么安排" / "这周末有什么计划"
技能自动：
1. AI解析用户要查哪个时间段
2. 调用`schedule_manager.py`列出该时间段日程
3. 整理结果返回给用户

## AI解析规则（必须遵守）

当你收到用户自然语言添加日程，你必须直接解析出以下结构，输出JSON：

```json
{
  "success": true,
  "data": {
    "type": "schedule",     // schedule=普通行程，ddl=截止日期
    "datetime": "2026-03-28T17:30:00+08:00",  // ISO 8601格式，带时区
    "where": "天河机场",    // 目的地，没有就写null
    "what": "坐飞机",      // 要做的事
    "from_address": "家",   // 出发地，没有就写null
    "duration_minutes": null
  }
}
```

解析失败（时间/地点看不懂）输出：
```json
{
  "success": false,
  "error": "无法识别时间，请说清楚什么时候"
}
```

**解析技巧**：
- "今天下午五点半" → 直接转成今天17:30，不用管dateparser懂不懂
- "下班回家" → 时间是下班时间（今天18:00），地点是"家"，事项是"下班回家"
- "明天开会" → 时间默认明天上午9点，地点null，事项"开会"
- "从公司去体育馆打球" → 出发地"公司"，目的地"体育馆"，事项"打球"

> 用户说人话就行，不用迁就固定格式，AI负责看懂。

## 地图对接说明

本技能预留地图接口，支持对接已安装的高德地图技能：
- 如果已安装 `smart-map-guide` 或 `amap-lbs-skill`，自动调用获取路线耗时
- 如果未安装地图技能，只使用固定提前提醒时间（默认15分钟，可配置）
- 用户需要自己在地图技能配置高德 API Key

## 配置说明

配置文件存于 `~/.openclaw/workspace/data/simple-schedule/config.json`：

```json
{
  "amap_api_key": "",          // 可选：不填则用地图技能的配置
  "default_start_address": "家", // 默认出发地址
  "buffer_minutes": 10,        // 额外缓冲时间（路程耗时 + 缓冲 = 提前提醒时间）
  "same_location_remind_before_minutes": 10, // 同地点提前提醒时间
  "default_transit_mode": "driving", // 默认出行方式：driving(驾车)/bus(公交)/riding(骑行)/walking(步行)
  "ddl_remind_1day_before": true, // DDL是否提前一天提醒
  "ddl_remind_1hour_before": true, // DDL是否提前一小时提醒
  "data_path": "~/.openclaw/workspace/data/simple-schedule/schedule.json"
}
```

## 首次使用说明

1. **安装依赖**：
```bash
pip install -r requirements.txt
```
或者手动安装：
```bash
pip install requests
```

2. **安装openclaw CLI**（必需）：
   - 本技能需要openclaw CLI来管理定时提醒
   - 请确保openclaw已安装并在PATH中，或设置环境变量`OPENCLAW_PATH`指向openclaw可执行文件
   - Windows示例：`set OPENCLAW_PATH=C:\Users\xxx\AppData\Roaming\npm\openclaw.cmd`

3. **配置（可选）**：
   配置文件位置：`~/.openclaw/workspace/data/simple-schedule/config.json`
   - 如果需要路线提醒，填上你的高德 API Key 到 `amap_api_key`（或者装好 `amap-lbs-skill` 配好也可以）
   - 修改 `default_start_address` 为你常用的出发地址（比如家/公司）
   - `buffer_minutes`：路程额外缓冲时间（默认10分钟）
   - `same_location_remind_before_minutes`：同地点提前多久提醒（默认10分钟）
   - `ddl_remind_1day_before` / `ddl_remind_1hour_before`：DDL要不要提前一天/一小时提醒，默认都开

3. **用法**：
   - **添加行程**：直接说 "明天下午3点从公司去天河机场坐飞机"
   - **添加DDL**：直接说 "周五18点前提交项目周报截止"
   - **查询行程**：说 "看看今天有什么安排"
   - **修改行程**：说 "把今天下午3点的开会改成4点"
   - **删除行程**：说 "取消今天下午的行程"

## 脚本说明

### scripts/
- `schedule_manager.py` - 日程增删改查、冲突检测核心逻辑
- `reminder_manager.py` - 创建/更新/删除定时提醒任务（调用 openclaw cron），支持DDL多段提醒
- `map_router.py` - 对接已安装高德地图技能，获取路程耗时
- `config_manager.py` - 集中配置管理和统一错误处理

### references/
- `schema.md` - 日程数据结构定义

## 使用提示（自然语言解析）

v1.2 优化了中文自然语言识别，现在支持更口语化的输入：

✅ 支持这些说法了：
- "今天下午5点半回家" → 正确识别17:30，目的地家
- "17:30去公司" → 没说日期自动补今天，正确识别
- "下班回家" → 自动识别目的地是家
- "明天早上9点半开会" → "X点半"自动识别正确

❌ 还是尽量说清楚：
- 最好带上今天/明天，识别更准
- 目的地尽量用"去XX"结构，更快识别

## 高德地图配置说明

要使用智能出发提醒，需要配置高德地图API：

1. **推荐方式**：安装 `amap-lbs-skill` 技能，在技能配置里填入你的高德 API Key，本技能会自动读取配置
   ```bash
   clawhub install amap-lbs-skill
   ```
2. **独立配置**：直接在本技能的 `config.json` 里填写 `amap_api_key`，不依赖其他技能也能用

如何获取高德 API Key：
- 去 [高德开放平台](https://lbs.amap.com/) 注册账号
- 创建"Web服务"类型的应用
- 复制 API Key 粘贴到配置文件即可

## 更新日志

### v1.4.0 (2026-03-27) 安全与性能优化
- 🔒 **安全修复**：
  - 修复`reminder_manager.py`中的命令注入风险，增强命令执行安全性
  - 改进`map_router.py`中的API密钥管理，支持从环境变量读取API密钥
  - 增强`schedule_manager.py`中的输入验证，确保数据完整性和合法性
  - 修复文件系统安全问题，包括路径遍历防护和文件权限设置
  - 完善网络安全问题，包括HTTPS证书验证和错误处理
  - 改进错误处理机制，避免空异常捕获，提供更详细的错误信息
  - 添加`requirements.txt`文件，指定依赖库版本，确保依赖安全

- ⚡ **性能优化**：
  - 实现地图API请求缓存，减少重复网络请求，提高响应速度
  - 优化日程查询算法，预解析时间并使用更高效的排序方式
  - 实现文件IO自动保存机制，减少频繁的文件读写操作
  - 优化代码结构，创建`config_manager.py`模块，集中配置管理和统一错误处理
  - 添加详细的代码注释和文档，提高代码可维护性

### v1.3.0 (2026-03-27) 今日大更新
- 🎨 **架构重构**：自然语言解析改由AI直接做，脚本只做业务逻辑，彻底解决dateparser识别不了中文口语的问题，用户说人话就行
- ✨ **新增功能**：新用户首次使用自动引导设置常用地址（家/公司），不用手动改配置
- 🚗 **多种出行方式**：配置`default_transit_mode`支持驾车/公交/骑行/步行，不同方式计算不同提醒时间
- 🪛 **Windows兼容性全面修复**：自动从node路径推算openclaw位置，找不到支持`OPENCLAW_PATH`手动兜底，彻底解决"找不到命令"，所有脚本强制UTF-8解决中文乱码
- 🐛 **修复所有已知解析bug**："X点半"/"下班回家"/"无日期时间"/"无地点会议"/"地点吃事项"/"过期时间"全修复

### v1.2.x (2026-03-27)
- 测试迭代版本，修复细节问题

### v1.1.0
- 初始版本，核心功能完成
