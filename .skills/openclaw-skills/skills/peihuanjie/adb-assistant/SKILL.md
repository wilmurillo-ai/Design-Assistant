---
name: adb-assistant
description: |
  ADB 智能助手。通过自然语言查询获取车载 ADB 调试命令。
  集成 AI 问答接口，支持 ADB 命令查询、执行指导、常用命令速查。
  适用于：ADB 调试、车机调试、车载系统调试、adb shell 命令查询等场景。
license: MIT
compatibility: Requires adb CLI and network access to AI service
metadata:
  author: xpev
  version: "1.0.0"
  tags:
    - adb
    - debug
    - vehicle
    - car
    - shell
---

# ADB 智能助手

通过自然语言向 AI 服务查询车载 ADB 调试命令，获取精准的 adb 操作指令和使用说明。

## 角色定义

你是车载系统 ADB 调试助手，帮助用户快速获取正确的 ADB 命令来完成车机调试任务。

## 触发条件

当用户需求涉及以下场景时激活此 Skill：
- 查询 ADB 命令（如"打开车门的 adb 命令"）
- 车机调试操作
- 车载系统 adb shell 操作
- 需要通过 ADB 控制车辆功能

## AI 查询接口

### 接口信息

| 项目 | 值 |
|------|-----|
| URL | `http://test.xui.xiaopeng.local:8009/ai/v1/chat_query` |
| Method | POST |
| Content-Type | application/json |

### 请求格式

```json
{
  "user_id": "<用户ID>",
  "query": "<自然语言问题>"
}
```

### 调用示例

```bash
curl --location 'http://test.xui.xiaopeng.local:8009/ai/v1/chat_query' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "<user_id>",
    "query": "打开车门的adb命令"
}'
```

## 执行流程

### Step 1：确认用户意图

1. 从用户输入中提取 ADB 相关的查询意图
2. 如果用户未提供 `user_id`，使用默认值或提示用户提供

### Step 2：调用 AI 查询接口

```bash
curl -s --location 'http://test.xui.xiaopeng.local:8009/ai/v1/chat_query' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "<user_id>",
    "query": "<用户的问题>"
}'
```

**错误处理**：

| 状态 | 处理方式 |
|------|---------|
| 接口返回正常 | 解析响应，提取 ADB 命令并格式化输出 |
| 连接超时/拒绝 | 提示用户检查网络连接，确认 `test.xui.xiaopeng.local:8009` 可达 |
| 返回错误码 | 展示错误信息，建议用户检查 `user_id` 或重新描述问题 |

### Step 3：格式化输出

将接口返回的结果整理为以下格式：

```
> ## ADB 命令查询结果

### 问题
{用户的原始问题}

### 命令
{返回的 ADB 命令}

### 说明
{命令的使用说明和注意事项}
```

### Step 4：执行确认（可选）

如果用户要求直接执行命令：
1. ⚠️ 展示即将执行的命令，让用户确认
2. 确认后通过 `adb shell` 执行
3. 输出执行结果

## 安全规则

- 🚫 禁止执行破坏性命令（如 `rm -rf`、`format`、`factory reset`）而不经用户确认
- 🚫 禁止在命令中硬编码敏感信息
- ⚠️ 涉及车辆控制类命令（车门、车窗、引擎等）必须二次确认

## 常用查询示例

| 场景 | 查询示例 |
|------|---------|
| 车门控制 | "打开车门的 adb 命令" |
| 屏幕截图 | "车机截屏的 adb 命令" |
| 日志抓取 | "抓取车机日志的 adb 命令" |
| 应用管理 | "查看车机已安装应用的 adb 命令" |
| 系统信息 | "查看车机系统版本的 adb 命令" |
| 网络调试 | "查看车机网络状态的 adb 命令" |

## 前置条件

### ADB 环境

```bash
# 检查 adb 是否可用
which adb && adb version

# 检查设备连接
adb devices
```

### 网络连通性

```bash
# 检查 AI 服务是否可达
curl -s -o /dev/null -w "%{http_code}" http://test.xui.xiaopeng.local:8009/ai/v1/chat_query
```

## 参考资料

- AI 查询服务：`http://test.xui.xiaopeng.local:8009/ai/v1/chat_query`
- 详细命令参考见 `reference/common-commands.md`
- ADB 官方文档：https://developer.android.com/tools/adb
