# daxiapi-cli

大虾皮(daxiapi.com)金融数据API命令行工具。需要注册 daxiapi.com 网站，并且获取API Token之后才能使用。

## 安装

```bash
# 全局安装
npm install -g daxiapi-cli

# 或使用 pnpm
pnpm add -g daxiapi-cli
```

## 配置

首次使用需要配置 API Token（在 daxiapi.com 用户中心申请）：

```bash
# 方式一：配置文件
daxiapi config set token YOUR_API_TOKEN

# 方式二：环境变量
export DAXIAPI_TOKEN=YOUR_API_TOKEN
```

## 使用

### 配置管理

```bash
# 设置Token
daxiapi config set token YOUR_API_TOKEN

# 设置API地址（可选）
daxiapi config set baseUrl https://daxiapi.com

# 查看所有配置
daxiapi config get

# 删除配置
daxiapi config delete token
```

### 市场数据

```bash
# 市场概览（默认）
daxiapi market

# 市场温度
daxiapi market -d

# 大小盘风格
daxiapi market -s

# 指数估值
daxiapi market -v

# 收盘新闻
daxiapi market -n

# 涨跌停股票池
daxiapi market -z
```

### 指数K线

```bash
# 获取上证指数K线
daxiapi index
```

### 板块数据

```bash
# 板块热力图
daxiapi sector

# 指定排序字段和天数
daxiapi sector -o zdf -l 10

# 获取板块内个股排名
daxiapi sector -c BK0477 -o cs

# 获取概念内个股
daxiapi sector -g GN1234
```

### 个股查询

```bash
# 查询单个股票
daxiapi stock 000001

# 查询多个股票
daxiapi stock 000001 600031 300750

# JSON格式输出
daxiapi stock 000001 --json
```

### 搜索

```bash
# 搜索股票
daxiapi search 三一重工

# 搜索行业
daxiapi search 机械 -t hy
```

> 💡 提示：`daxiapi` 命令也可以使用简写 `dxp`

## 输出示例

### 市场概览

```
📈 市场概览

主要指数:
┌─────────┬────────┬───────────┬───────┬─────────┬─────────┐
│ (index) │  名称  │  涨跌幅   │  CS   │   5日   │   20日  │
├─────────┼────────┼───────────┼───────┼─────────┼─────────┤
│    0    │ '上证' │ '0.50%'   │  5.23 │ '2.10%' │ '3.50%' │
│    1    │ '深证' │ '0.80%'   │  6.45 │ '2.50%' │ '4.20%' │
│    2    │ '创业' │ '1.20%'   │  8.12 │ '3.00%' │ '5.10%' │
└─────────┴────────┴───────────┴───────┴─────────┴─────────┘
```

### 个股详情

```
📊 个股详情

三一重工 (600031)
────────────────────────────────────────
价格: 18.50  涨跌幅: 2.50%

动量指标:
  CS(短期): 8.25  SM(中期): 5.30  ML(长期): 3.20
  RPS: 85  SCTR: 72

形态标签: Good, LPS
技术形态: VCP, SOS
```

## 核心指标说明

| 指标 | 说明 |
|------|------|
| CS | 短期动量，股价与20日均线乖离率。>0在均线上方，>30可能反转 |
| SM | 中期动量，短期与中期均线乖离率。>0多头排列 |
| ML | 长期动量，中期与长期均线乖离率 |
| RPS | 欧奈尔相对强度，>80为强势股 |
| SCTR | 技术排名百分比，如60代表强于市场60%股票 |
| VCP | 马克米勒维尼波动收缩模式 |
| SOS | Wyckoff强势走势行为 |
| LPS | Wyckoff最后支撑点 |

## 限流规则

- 每日上限：1000次
- 每分钟上限：10次
- 超限返回 429 错误

## License

MIT
