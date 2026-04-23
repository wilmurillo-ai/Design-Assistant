# 数字人生成技能 (Jiaodian TEST Generator)

命令行版本数字人生成工具，输入 MP3 地址、MP4 地址和文字内容，调用后端 API 生成数字人视频。

## 功能特性

- ✅ 分步引导，交互清晰
- ✅ 支持本地路径或网络URL
- ✅ 无需下载文件，直接传递地址给后端
- ✅ 可随时确认重填，错误可追溯
- ✅ 进度自动增长到 99%，卡住等待后端返回
- ✅ 异步任务自动轮询，完成立即输出

## 搜索关键词

jiaodian-test, 数字人, 数字人生成, AI数字人, 视频生成, ai视频, 语音合成, 唇形同步

## 安装

通过 OpenClaw Skills 安装：

```bash
npx skills add <仓库地址> -s jiaodian-test-generator -g -y
```

安装后进入目录：

```bash
cd jiaodian-test-generator
```

## 使用

```bash
python3 scripts/jiaodian_human_generator.py
```

按照提示一步步操作：

```
==================================================
       数字人生成工具
==================================================

1️⃣  请输入 MP3 路径/URL:
➡️  输入你的 MP3 地址

2️⃣  请输入 MP4 路径/URL:
➡️  输入你的 MP4 地址

3️⃣  请输入需要合成的文字内容:
➡️  输入数字人要说的文字

📋 请确认信息：
  MP3: https://example.com/audio.mp3
  MP4: https://example.com/video.mp4
  文字: 你好，欢迎使用数字人生成

请选择：[1] 提交  [2] 重新输入
选择:
➡️  输入 1 提交，输入 2 重新开始
```

## 后端 API 协议

**提交接口**
```
POST {BASE_URL}/skill/api/submit
Content-Type: application/json

Body (JSON):
{
  "mp3": "MP3 文件地址/URL",
  "mp4": "MP4 文件地址/URL",
  "text": "需要合成的文字内容"
}
```

**返回格式**

1. 直接返回结果：
```json
{
  "videoUrl": "https://example.com/output/result.mp4"
}
```

2. 异步任务（需轮询）：
```json
{
  "orderNo": "任务单号"
}
```

**轮询接口**
```
POST {BASE_URL}/skill/api/api/result
Content-Type: application/json

Body (JSON):
{
  "orderNo": "任务单号"
}
```

返回可能为 JSON 对象或字符串形式的 JSON，且 `progress` 字段可能为空。返回示例：
```json
{
  "status": "processing",
  "progress": 60,
  "videoUrl": ""
}
```
完成时：`"status": "done"` 且返回 `videoUrl`；失败时：`"status": "error"` 且可含 `message`。

## 隐私说明

- 本工具仅提供客户端调用能力，**不存储任何用户数据**
- 所有请求直接发送到后端服务 `https://yunji.focus-jd.cn`
- 数据处理和存储由后端服务负责，本工具仅作中转调用
- 用户需确保所上传内容符合法律法规，不侵犯第三方权益

## 依赖

- Python 3.6+
- requests 库 (`pip install requests`)

## 许可证

MIT