# 配置说明

## 配置文件位置

用户需要在 `~/.config/wendao-yun/config.json` 创建配置文件，或者在工作空间根目录创建 `wendao-yun-config.json`。

## 配置格式

只需要配置 API Key 即可，接口信息已经固化在技能中：

```json
{
  "api_key": "your-api-key-here"
}
```

或者通过环境变量配置：
```bash
export WENDAOYUN_API_KEY=your-api-key-here
```

## 获取 API Key

1. 打开 https://open.wintaocloud.com/home
2. 登录你的账号
3. 在个人中心或开发者中心获取 API Key
4. 一个用户可以拥有多个 API Key
5. **每个用户每日调用额度限制为 200 次**

## 注意事项

- API Key 属于敏感信息，请妥善保管，不要泄露给他人
- 如果发现 API Key 泄露，请及时在问道云开放平台作废
