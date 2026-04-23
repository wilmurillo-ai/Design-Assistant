# AppKey 登录接口

## 接口信息

| 项 | 值 |
|---|---|
| 请求方式 | GET |
| URL | `https://sg-cwork-web.mediportal.com.cn/user/login/appkey` |
| 需要 token | 否（本接口是获取 token） |

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| appCode | string | 是 | 应用编码，固定为 `cms_gpt` |
| appKey | string | 是 | CWork AppKey |

## 请求示例

```
GET /user/login/appkey?appCode=cms_gpt&appKey=your-app-key
```

## 响应示例

```json
{
  "resultCode": 1,
  "data": {
    "xgToken": "xxxx",
    "userId": "123456",
    "userName": "张三",
    "avatar": "https://...",
    "corpId": "789",
    "personId": "456"
  }
}
```

## 字段映射

| 响应字段 | 用途 |
|---------|------|
| `data.xgToken` | 作为后续请求的 `access-token` Header |
| `data.userId` | 用户 ID |
| `data.userName` | 用户名 |
| `data.corpId` | 企业 ID |

## 对应脚本

`scripts/auth/login.py`
