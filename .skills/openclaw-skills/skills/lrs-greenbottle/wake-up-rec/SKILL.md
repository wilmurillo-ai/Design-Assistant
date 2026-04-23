---
name: wake-up-rec
description: 醒醒吧，开始录 — 点亮 Mac 屏幕并执行安全检查。**每次执行电脑操作前都必须调用此技能**。触发词覆盖所有电脑操作场景：(1) 文件管理：打开文件夹、打开桌面/下载/文档、查看文件、找文件、显示文件 (2) 浏览器：打开xx网站、打开百度/知乎、浏览网页 (3) 应用：打开app、打开微信/Safari (4) 截图录屏：截屏、录屏 (5) 鼠标键盘：鼠标点击、键盘输入、操作电脑 (6) 窗口管理：最小化/最大化/关闭窗口。任何涉及屏幕显示、文件访问、应用控制的任务都需要先调用此技能。
---

# Wake Up Rec

> ⚠️ **核心原则**：每次执行任何电脑操作前，必须先调用此技能完成安全检查流程。

## 安全检查流程

### 第一步：点亮屏幕（必须）
```bash
caffeinate -u -t 2
```
点亮屏幕并等待2秒，确保 Mac 处于唤醒状态。

### 第二步：自动判断是否需要截图确认

**需要截图确认的操作类型：**
- 读取隐私信息（消息、文件、密码、聊天记录）
- 删除/修改文件
- 发送消息（邮件、聊天等）
- 系统配置修改

**截图确认流程：**
1. 执行截屏：`bash ~/.openclaw/workspace/skills/wake-up-rec/scripts/screenshot.sh`
2. 推送给用户确认
3. 等待用户回复"确认/继续"后执行

### 第三步：自动判断是否需要录屏

**需要全程录屏的操作类型：**
- 文件操作（打开文件夹、复制、移动、删除文件）
- 窗口/应用控制（最小化、最大化、切换、关闭）
- 浏览器自动化（打开网站、搜索、点击网页元素）
- 任何涉及桌面环境操作的场景

**录屏流程：**
1. 启动录屏：`bash ~/.openclaw/workspace/skills/wake-up-rec/scripts/record-start.sh`
2. 执行目标操作（录屏记录整个过程）
3. 操作结束后延迟9秒停止录屏：`bash ~/.openclaw/workspace/skills/wake-up-rec/scripts/record-stop.sh`
4. 推送录屏结果给用户

## 触发判断决策树

```
收到任务
  ↓
1. caffeinate -u -t 2（点亮屏幕）
  ↓
2. 判断操作类型
  ├─ 隐私/敏感操作？ → 推送截图确认 → 等"确认/继续"
  ├─ 文件操作？
  │   → 推送截图确认 → 等"确认/继续"
  │   → 启动录屏
  │   → 执行操作（打开文件夹）
  │   → Finder 反映变化（录屏可见）
  │   → 延迟9秒 → 停止录屏 → 推送
  ├─ 电脑UI操作？
  │   → 启动录屏
  │   → 执行操作
  │   → 延迟9秒停止 → 推送
  └─ 普通查询/计算/文字？ → 直接执行
  ↓
3. 完成
```

## 安装配置

当用户说"配置技能"、"配置wake-up-rec"时，AI 应自动运行一次此脚本。

或手动运行：

```bash
bash ~/.openclaw/workspace/skills/wake-up-rec/scripts/setup.sh
```

**重要**：首次使用前必须配置，否则 hook 不会生效。

## 内置脚本

| 功能 | 命令 |
|------|------|
| 点亮屏幕 | `caffeinate -u -t 2` |
| 截屏 | `bash ~/.openclaw/workspace/skills/wake-up-rec/scripts/screenshot.sh` |
| 开始录屏 | `bash ~/.openclaw/workspace/skills/wake-up-rec/scripts/record-start.sh` |
| 停止录屏 | `bash ~/.openclaw/workspace/skills/wake-up-rec/scripts/record-stop.sh` |

- 截屏输出：`~/Desktop/screenshot_YYYYMMDD_HHMMSS.png`
- 录屏输出：`~/Desktop/recording_YYYYMMDD_HHMMSS.mp4`

## 注意事项

- **每次执行电脑操作前都必须先调用此技能**
- 录屏文件统一保存到桌面
- 延迟9秒停止录屏是为了确保操作结束的瞬间被完整记录
- 此技能不会阻止系统正常休眠，只是临时唤醒
