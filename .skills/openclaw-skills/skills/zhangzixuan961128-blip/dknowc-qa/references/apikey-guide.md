# 深知可信问答 - API Key 获取指南

## 注册与获取

### 第 1 步：注册账号

访问 [深知 MAAS 平台](https://platform.dknowc.cn) → 点击「注册」

- 支持手机号注册
- 注册后需要完成**实名认证**

### 第 2 步：实名认证（送 100 元额度）

完成实名认证后，平台自动赠送 100 元免费额度。

- 可信问答：¥0.5/次
- 安全识别：¥0.05/次
- 100 元 ≈ 可问答 200 次

### 第 3 步：创建应用

1. 登录后进入 [应用管理](https://platform.dknowc.cn/#/app/list)（控制台首页左侧菜单）
2. 点击「创建应用」
3. 选择「**统一应用**」
4. 创建成功后获得 **AppID** 和 **API Key**

### 第 4 步：记录信息

你需要记录两个值，告诉 OpenClaw 即可：

- **API Key**：形如 `sk-xxxxxxxxxxxxxxxx`
- **调用地址**：`https://open.dknowc.cn/chat/trusted/unification/{你的AppID}`

### 第 5 步：配置到 OpenClaw

在对话中直接告诉 AI：

> 我的深知可信问答 API Key 是 sk-xxxxx，调用地址是 https://open.dknowc.cn/chat/trusted/unification/xxxxx

AI 会自动完成配置，无需手动操作。

---

## 常见问题

### 余额不足怎么办？
登录 [MAAS 平台](https://platform.dknowc.cn) → 充值页面进行充值。

### API Key 无效？
检查是否复制完整，确认是「统一应用」的 Key。

### 权限不足（403）？
确认创建的是「统一应用」而非其他类型应用。

### 调用地址格式？
格式为：`https://open.dknowc.cn/chat/trusted/unification/` + 你的 AppID
