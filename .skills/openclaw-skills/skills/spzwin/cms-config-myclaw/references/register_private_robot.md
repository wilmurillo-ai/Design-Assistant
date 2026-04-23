# 注册私有 AI 机器人接口参考

## 登录换 token

- 本 skill 不再自行实现登录换 token；统一依赖 `cms-auth-skills` 获取 `access-token`。
- 这里的 `appKey` 指的是登录鉴权用的工作协同 key，不是机器人创建成功后返回的 `robot appKey`。
- 地址：`GET https://sg-cwork-web.mediportal.com.cn/user/login/appkey`
- Query：
  - `appCode=cms_gpt`
  - `appKey=<登录用工作协同 key>`
- 目标：由 `cms-auth-skills` 从返回体 `data.xgToken / data.token / data.access-token` 中拿到 `access-token`

## 创建机器人

- 地址：`POST https://sg-al-cwork-api.mediportal.com.cn/im/robot/private/register`
- Header：
  - `access-token: <token>`
- Body：
  - `agentId` 必填
  - `name` 可选
  - `avatar` 可选
  - `groupLabel` 可选
  - `remark` 可选

## 关键返回字段

- `data.agentId`
- `data.appKey`：机器人自己的 `robot appKey`
- `data.baseUrl`
- `data.wsBaseUrl`
- `data.name`
- `data.userId`

## 本 skill 的落地约定

- 向用户索要的是登录 `appKey`，只用于换取 `access-token`
- 实际写入 `channels.xg_cwork_im.accounts` 的 `appKey`，必须使用创建机器人接口返回的 `data.appKey`
- `channels.xg_cwork_im.accounts` 的 key 固定等于用户选择的 `agentId`
- 写入 account 结构：

```json
{
  "appKey": "<robot appKey>",
  "agentId": "<agentId>",
  "name": "<robotName>"
}
```

- `bindings` 中只保留当前 agent 的一条规范 route：

```json
{
  "type": "route",
  "agentId": "<agentId>",
  "match": {
    "channel": "xg_cwork_im",
    "accountId": "<agentId>"
  }
}
```

- `channels.xg_cwork_im.baseUrl / wsBaseUrl` 优先使用接口返回值；缺失时回退到：
  - `https://sg-al-cwork-api.mediportal.com.cn`
  - `wss://sg-al-cwork-api.mediportal.com.cn`
