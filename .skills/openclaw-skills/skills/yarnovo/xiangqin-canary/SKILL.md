---
name: xiangqin
description: 相亲平台（付费置顶曝光商业模式）的使用入口。TRIGGER when 用户说"相亲"、"找对象"、"xiangqin"、"注册相亲"、"填资料"、"查匹配"、"买曝光"、"买置顶"、"让更多人看到我"、"付费相亲"。DO NOT TRIGGER when 用户要聊天/推荐/匹配算法（本项目不做）、用户想的是 matchmaker（已废弃）、服务端不可达时先 curl health。
model: haiku
---

# xiangqin — 相亲平台 skill

付费置顶曝光。人人进池免费查，唯一收费点 = 买曝光次数让自己更可见。

## 心智模型

- **数据层**：sqlite in epsilon (112.124.27.213)。`users` / `profiles` / `exposure_orders` / `exposure_usage` 4 张表
- **查询**：受限 WHERE DSL + `ORDER BY exposure_weight DESC`。付费用户自然排前
- **计费**：买 N 次曝光 → 被 query 命中一次扣 1 → 扣到 0 回普通池
- **客户端**：`xq` CLI（本 skill 触发装 + 用）
- **隐私红线**：手机号永不出 stdout / stderr / vault；ULID request_id 代理

## 典型流程

### 首次注册
```
用户：帮我在 xiangqin 注册，手机 138xxxx1111
Claude: [跑] xq register 13800001111
        → 验证码已发 138****1111，60s 有效，request_id=01K...
Claude: 请把手机收到的 6 位验证码告诉我
用户：123456
Claude: [跑] xq verify 123456 --request-id 01K...
        → session 写 vault 成功
```

### 填 profile
```
用户：我是男的，28 岁，杭州，喜欢程序 / 登山 / 做饭，bio 写"程序员，想找能一起爬山的人"
Claude: [逐条跑] xq profile set gender m
         xq profile set age 28
         xq profile set city hangzhou
         xq profile set tags '程序,登山,做饭'
         xq profile set bio '程序员，想找能一起爬山的人'
        xq profile show
```

### 查匹配
```
用户：帮我查杭州 25-30 岁的女生
Claude: [跑] xq query 'gender=f AND city=hangzhou AND age>=25 AND age<=30' --limit 20
        → 返回列表。带 🔥 的是付费置顶用户
```

### 买曝光
```
用户：我想让更多女生看到我，买 100 次曝光
Claude: [跑] xq expose buy --count 100 --mock
        → 0.1 期 mock 扣款，账户 exposure_remaining = 100
        → 从此起到被 query 命中 100 次前，在所有 query 里置顶 + 带 🔥
```

## 不变量

- 服务端零推荐 / 零排序算法，只按 `exposure_weight DESC`
- 查询结果只返回白名单字段（手机号永不出）
- WHERE 不能为空；LIMIT 默认 50 最大 100
- 余额不足的付费用户降级到普通池，不退款
- 删号 7 天物理清理，期间可撤销
- 0.1 期支付走 mock（--mock 必填）；0.2 起对接真支付

## 和其它 skill / CLI 关系

- **唯一外部依赖**：`vault`（读 session_token / phone ↔ request_id 映射）
- **不用**：host / oss / backup / cashier / membership / hitch（本项目自治单体实验；shipyard 因 2026-04-22 判定保留改 Python 栈，暂不强制自治）
- **不收跨项目邮件**：`.mailbox/` 不设；跨项目协作走直接 ping

## 安装（未来）

```bash
skills install xiangqin
pip install xiangqin-cli  # 或 uv tool install xiangqin
```

## Gotchas

（初始为空，由实践中踩坑后 skill-evolve 补充。）
