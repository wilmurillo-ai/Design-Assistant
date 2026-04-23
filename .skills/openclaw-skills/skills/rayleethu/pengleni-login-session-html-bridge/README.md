# ClawHub Skill Bundle

## 文件说明

- `skill_manifest.clawhub.yaml`
  - Skill 元数据
- `openapi.yaml`
  - 接口定义
- `.env.example`
  - 运行参数模板
- `skill_client.py`
  - 单文件 Python 客户端

## 快速使用

1. 复制环境变量模板并填值

```bash
cp .env.example .env
```

2. 发送验证码

```bash
python skill_client.py send-code --phone 13800138000
```

3. 登录并建会话

```bash
python skill_client.py login --phone 13800138000 --verify-code 123456
```

4. 发送 HTML 消息

```bash
python skill_client.py message --user-id u_xxx --session-id s_xxx --html '<p>你好</p>'
```

## 接口路径

- 站点级（验证码）：`POST {SITE_BASE_URL}/chainlit/send-verification-code`
- Skill API（登录）：`POST {API_BASE_URL}/session/login`
- Skill API（消息）：`POST {API_BASE_URL}/session/message`

## 注意事项

- 客户端默认使用 Bearer Token：`CLAWHUB_SKILL_TOKEN`
- API_BASE_URL 建议形如：`https://your-domain/api/v1/clawhub`
- 默认非流式调用，适合 ClawHub 直接接入
