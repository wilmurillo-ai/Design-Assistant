---
name: skincare-manager
description: 护肤管家 - 护肤 routine 管理 + 成分查询 + 产品追踪
version: 0.2.0
author: 鸭鸭 (Yaya)
license: MIT
tags:
  - skincare
  - beauty
  - routine
  - ingredient
  - health
emoji: 🧴
---

# 护肤管家 Skill

你的私人护肤管理助手，帮你建立科学护肤 routine，追踪产品使用效果。

## 🎯 功能特性

- ✅ **肤质测试** - 9 种肤质类型自测
- ✅ **护肤流程管理** - 记录早晚护肤步骤
- ✅ **成分查询** - 查询化妆品成分功效
- ✅ **产品追踪** - 管理护肤品库存和到期提醒
- ✅ **效果记录** - 拍照记录护肤效果

## 🚀 快速开始

### 1. 肤质测试

```bash
./scripts/skin-test.js
```

### 2. 添加护肤流程

```bash
./scripts/add-routine.js --time morning --product "洁面" --step 1
```

### 3. 查询成分

```bash
./scripts/query-ingredient.js "烟酰胺"
```

### 4. 添加产品

```bash
./scripts/add-product.js "SK-II 神仙水" --expiry 2027-12-31
```

### 5. 查看到期提醒

```bash
./scripts/check-expiry.js
```

---

## 📋 命令详解

### 肤质测试 `skin-test.js`

```bash
./scripts/skin-test.js
```

**输出示例：**
```
🧴 肤质测试结果

你的肤质类型：混合性皮肤

特征：
- T 区油腻，U 区干燥
- 毛孔中等大小
- 偶尔长痘

建议：
- T 区控油，U 区保湿
- 选择温和洁面产品
- 定期去角质

⚠️ 免责声明：测试结果仅供参考，不构成专业建议。
```

---

### 成分查询 `query-ingredient.js`

```bash
./scripts/query-ingredient.js <成分名>
```

**参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| 成分名 | ✅ | 成分名称（中文/英文/INCI） |

**示例：**

```bash
# 查询烟酰胺
./scripts/query-ingredient.js "烟酰胺"

# 查询视黄醇
./scripts/query-ingredient.js "视黄醇"

# 查询英文成分
./scripts/query-ingredient.js "Hyaluronic Acid"
```

**输出示例：**
```
🔬 成分查询：烟酰胺 (Niacinamide)

### 基本信息
- INCI 名称：Niacinamide
- 中文名：烟酰胺、维生素 B3
- ⭐⭐⭐⭐⭐ 来源：国家药监局化妆品数据库

### 功效
- 美白淡斑（抑制黑色素转移）
- 控油收敛（调节皮脂分泌）
- 修护屏障（促进神经酰胺合成）
- ⭐⭐⭐⭐ 来源：《化妆品化学》教材

### 安全评级
- COSDNA 评分：0-1（低刺激）
- 致痘等级：1（低致痘性）
- ⭐⭐⭐ 来源：COSDNA

### 使用建议
- 建议浓度：2-5%
- 适用肤质：油性、混合性、暗沉肌肤
- 注意事项：敏感肌需建立耐受
- ⭐⭐ 来源：知乎答主@皮肤科医生

### 用户反馈
"用了 2% 烟酰胺精华，一个月后肤色亮了"
- ⭐ 来源：小红书用户@护肤达人

⚠️ 免责声明：以上信息仅供参考，不构成专业建议。
```

---

### 添加护肤流程 `add-routine.js`

```bash
./scripts/add-routine.js --time <morning/night> --product <产品名> --step <步骤>
```

**参数说明：**

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| --time | ✅ | - | 护肤时间（morning/night） |
| --product | ✅ | - | 产品名称 |
| --step | ❌ | 1 | 步骤顺序 |
| --amount | ❌ | 适量 | 使用量 |

**示例：**

```bash
# 添加晨间护肤流程
./scripts/add-routine.js --time morning --product "氨基酸洁面" --step 1
./scripts/add-routine.js --time morning --product "爽肤水" --step 2
./scripts/add-routine.js --time morning --product "烟酰胺精华" --step 3
./scripts/add-routine.js --time morning --product "防晒霜" --step 4

# 添加夜间护肤流程
./scripts/add-routine.js --time night --product "卸妆油" --step 1
./scripts/add-routine.js --time night --product "洁面" --step 2
./scripts/add-routine.js --time night --product "视黄醇精华" --step 3
./scripts/add-routine.js --time night --product "面霜" --step 4
```

---

### 查看护肤流程 `list-routine.js`

```bash
./scripts/list-routine.js [time]
```

**示例：**

```bash
# 查看所有流程
./scripts/list-routine.js

# 只看晨间
./scripts/list-routine.js morning

# 只看夜间
./scripts/list-routine.js night
```

**输出示例：**
```
🌅 晨间护肤流程

步骤 1: 氨基酸洁面 (适量)
步骤 2: 爽肤水 (适量)
步骤 3: 烟酰胺精华 (2-3 滴)
步骤 4: 防晒霜 (一元硬币大小)

⏱️ 预计耗时：5 分钟
📝 最后更新：2026-04-09
```

---

### 添加产品 `add-product.js`

```bash
./scripts/add-product.js <产品名> [--expiry <日期>] [--category <类别>]
```

**参数说明：**

| 参数 | 必填 | 说明 |
|------|------|------|
| 产品名 | ✅ | 产品全称 |
| --expiry | ❌ | 到期日期 (YYYY-MM-DD) |
| --category | ❌ | 类别 (洁面/精华/面霜等) |
| --opened | ❌ | 开封日期 (YYYY-MM-DD) |

**示例：**

```bash
# 添加产品（简单）
./scripts/add-product.js "SK-II 神仙水"

# 添加产品（完整信息）
./scripts/add-product.js "SK-II 神仙水" --expiry 2027-12-31 --category 精华水 --opened 2026-01-01

# 添加产品（开封后保质期）
./scripts/add-product.js "兰蔻小黑瓶" --opened 2026-04-01 --paq 12
# PAQ: Period After Opening (开封后保质期，单位：月)
```

---

### 查看产品列表 `list-products.js`

```bash
./scripts/list-products.js [options]
```

**选项：**

| 选项 | 说明 |
|------|------|
| --expiring | 只看即将到期（30 天内） |
| --expired | 只看已过期 |
| --category | 按类别筛选 |

**示例：**

```bash
# 查看所有产品
./scripts/list-products.js

# 看即将到期的
./scripts/list-products.js --expiring

# 看精华类产品
./scripts/list-products.js --category 精华
```

---

### 检查到期提醒 `check-expiry.js`

```bash
./scripts/check-expiry.js
```

**输出示例：**
```
⚠️ 产品到期提醒

以下产品即将到期（30 天内）：

1. 雅诗兰黛小棕瓶
   到期：2026-04-25 (16 天后)
   开封：2025-10-01
   建议：尽快使用

2. 理肤泉 B5 面霜
   到期：2026-05-01 (22 天后)
   开封：2025-11-15
   建议：尽快使用

📦 库存统计：
- 总计：15 个产品
- 即将到期：2 个
- 已过期：0 个

⏰ 下次检查：2026-04-16
```

---

## 📁 文件结构

```
skincare-manager/
├── SKILL.md                    # 本文件
├── README.md                   # 快速入门
├── package.json                # 项目配置
├── install.sh                  # 安装脚本
├── scripts/
│   ├── skin-test.js            # 肤质测试
│   ├── query-ingredient.js     # 成分查询
│   ├── add-routine.js          # 添加护肤流程
│   ├── list-routine.js         # 查看护肤流程
│   ├── add-product.js          # 添加产品
│   ├── list-products.js        # 查看产品列表
│   ├── check-expiry.js         # 检查到期
│   └── update-database.js      # 更新数据库
├── data/
│   ├── skin-types.json         # 肤质类型数据
│   ├── ingredients.json        # 成分数据库
│   ├── routines.json           # 用户护肤流程
│   └── products.json           # 用户产品库存
└── database/
    └── official/               # 官方数据（药监局等）
```

---

## 💾 数据格式

### 肤质数据 `data/skin-types.json`

```json
{
  "types": [
    {
      "id": "oily",
      "name": "油性皮肤",
      "features": ["全脸出油", "毛孔粗大", "易长痘"],
      "care_tips": ["控油", "清洁", "清爽保湿"]
    },
    {
      "id": "dry",
      "name": "干性皮肤",
      "features": ["皮肤干燥", "易起皮", "细纹明显"],
      "care_tips": ["补水", "保湿", "滋润"]
    }
  ]
}
```

### 成分数据 `data/ingredients.json`

```json
{
  "烟酰胺": {
    "inci_name": "Niacinamide",
    "aliases": ["维生素 B3", "尼克酰胺"],
    "efficacy": [
      {
        "effect": "美白淡斑",
        "mechanism": "抑制黑色素转移",
        "source": "国家药监局",
        "authority": 5
      }
    ],
    "safety": {
      "cosdna_rating": "0-1",
      "comedogenic": 1,
      "source": "COSDNA"
    },
    "usage": {
      "concentration": "2-5%",
      "suitable_skin": ["油性", "混合性", "暗沉"],
      "cautions": ["敏感肌需建立耐受"]
    }
  }
}
```

### 护肤流程 `data/routines.json`

```json
{
  "user_id": "o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat",
  "morning": [
    {
      "step": 1,
      "product": "氨基酸洁面",
      "amount": "适量",
      "notes": ""
    }
  ],
  "night": [],
  "updated_at": "2026-04-09T10:00:00Z"
}
```

### 产品库存 `data/products.json`

```json
{
  "products": [
    {
      "id": "prod_1712649600000",
      "name": "SK-II 神仙水",
      "category": "精华水",
      "expiry_date": "2027-12-31",
      "opened_date": "2026-01-01",
      "paq_months": 12,
      "status": "active",
      "created_at": "2026-04-09T10:00:00Z"
    }
  ]
}
```

---

## ⏰ 自动提醒

### 定时任务

安装时会自动添加 cron 任务，每周一 9:00 检查产品到期：

```bash
0 9 * * 1 /path/to/skincare-manager/scripts/check-expiry.js >> ~/.openclaw/logs/skincare.log 2>&1
```

### 提醒规则

| 情况 | 提醒时间 | 提醒内容 |
|------|---------|---------|
| 到期前 30 天 | 每周一 9:00 | 产品即将到期 |
| 到期前 7 天 | 每天 9:00 | 产品快到期了 |
| 已过期 | 每天 9:00 | 产品已过期 |

---

## 🔧 配置

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `WEIXIN_CHANNEL` | openclaw-weixin | 微信渠道 ID |
| `WEIXIN_USER_ID` | - | 接收提醒的用户 ID |

---

## ❓ 常见问题

### Q: 成分数据从哪里来？

**A:** 
- 官方数据：国家药监局化妆品数据库
- 社区数据：COSDNA、小红书、知乎
- 所有数据都标注来源和权威等级

### Q: 数据多久更新一次？

**A:** 
- 官方数据：每周抓取一次
- 社区内容：按需抓取
- 自动更新：`./scripts/update-database.js`

### Q: 成分查询准确吗？

**A:** 
- 数据来源都标注权威等级（1-5 星）
- 建议优先参考 5 星（官方）来源
- 仅供参考，不构成专业建议

### Q: 支持进口产品吗？

**A:** 
- 支持，可以查询 INCI 成分名
- 数据库持续更新中

---

## ⚠️ 免责声明

### 信息性质
- 本技能提供的所有内容均整理自公开资料
- 仅供信息参考，不构成专业建议
- 不替代皮肤科医生诊断或治疗

### 使用风险
- 个体差异大，效果因人而异
- 如有过敏或不适请立即停止使用并就医
- 重大皮肤问题请咨询专业皮肤科医生

### 数据来源
- 所有信息均标注来源
- 优先采用官方/权威来源（⭐⭐⭐⭐⭐）
- 用户经验分享仅供参考（⭐）

### 责任限制
- 不对使用结果承担责任
- 不保证信息完全准确
- 建议多方核实重要信息

---

## 📝 更新日志

### v0.2.0 (2026-04-09)
- ✅ 新增产品管理完整功能
- ✅ 新增到期提醒（分级提醒：已过期/7 天/30 天）
- ✅ 扩充成分数据库（8 个常见成分）
- ✅ 成分查询支持模糊匹配
- ✅ 添加用户反馈展示
- ✅ 优化输出格式和体验

### v0.1.0 (2026-04-09)
- ✅ 初始版本发布
- ✅ 肤质测试功能
- ✅ 成分查询（基础数据库）
- ✅ 护肤流程管理
- ✅ 产品库存管理
- ✅ 到期提醒功能

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

数据来源建议：[DATA-COLLECTION-GUIDE.md](../DATA-COLLECTION-GUIDE.md)

---

## 📄 许可证

MIT-0 License

---

## 🦆 作者

鸭鸭 (Yaya) - 你的私人护肤管家

**理念：** 不做专家，只做负责任的"信息搬运工" 🧴
