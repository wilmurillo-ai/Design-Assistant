---
name: jiuwu-message
description: 调用久吾消息网关HTTP接口给企业内部联系人发送消息。使用场景：(1) 需要向企业内部同事发送通知或提醒时，(2) 调用时传入接收人工号(code)、消息内容(text)和标题(title)
---

# 久吾消息网关

调用久吾消息网关HTTP接口发送消息。

## 环境配置

消息网关服务器地址从环境变量 `JIUWU_MESSAGE_GATEWAY_URL` 读取，默认为 `http://192.168.1.213:5000`。

如需自定义，请配置环境变量，优先使用workspace/.env，其次使用OpenClaw根目录的.env

## 使用方式

### 直接调用

使用 `scripts/send_message.py` 脚本发送消息：

```bash
python scripts/send_message.py --code "1112" --text "测试消息" --title "测试标题"
```

参数说明：
- `--code` 或 `-c`: 接收人工号，多个工号用英文逗号分隔（必填）
- `--text` 或 `-t`: 消息内容（必填）
- `--title` 或 `-tt`: 消息标题（可选）

### 在代码中调用

```python
from scripts.send_message import send_message

result = send_message(
    code="1112,1113",  # 多个工号用英文逗号分隔
    text="消息内容",
    title="消息标题"   # 可选
)

if result["success"]:
    print("发送成功")
else:
    print(f"发送失败: {result['message']}")
```

## 接口规范

- **URL**: `{JIUWU_MESSAGE_GATEWAY_URL}/api/MessageGateway/SendMessagePost`
- **方法**: POST
- **Headers**:
  - `accept: text/plain`
  - `Content-Type: application/json-patch+json`
- **请求体**:
  ```json
  {
    "code": "工号，多个用英文逗号分隔",
    "text": "消息内容",
    "title": "消息标题（可选）"
  }
  ```
- **成功响应**:
  ```json
  {
    "success": true,
    "data": true,
    "message": "请求成功"
  }
  ```
- **失败响应**:
  ```json
  {
    "success": false,
    "data": null,
    "message": "错误信息"
  }
  ```
