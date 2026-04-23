---
name: cn-expense-tracker
description: |
  中文个人记账助手。随手记、查统计、设预算、看趋势。
  本地存储，无账户、无云端、隐私安全。
  当用户说"记账"、"花了多少钱"、"本月支出"、"预算提醒"时触发。
  Keywords: 记账, 支出, 预算, 花费, expense, 收支, 月统计.
metadata: {"openclaw": {"emoji": "💰"}}
---

# 💰 CN Expense Tracker — 中文个人记账助手

本地记账，无账户、无云端、隐私安全。

## 核心功能

| 功能 | 说明 |
|------|------|
| 随手记 | 一句话记账：金额 + 类别 + 备注 |
| 月统计 | 本月花了多少、各类占比 |
| 预算管理 | 设置月度预算，超支提醒 |
| 趋势分析 | 月度对比，涨了还是降了 |
| 导出CSV | 方便 Excel 分析 |

## 使用方式

```bash
# 记一笔
python3 scripts/expense.py --add "午餐" 25 --category 餐饮
python3 scripts/expense.py --add "打车" 38 --category 交通 --note "赶时间"
python3 scripts/expense.py --add "咖啡" 22 --category 饮品

# 本月统计
python3 scripts/expense.py --month

# 设置预算
python3 scripts/expense.py --budget 3000

# 月度对比
python3 scripts/expense.py --compare

# 查看所有记录
python3 scripts/expense.py --list

# 删除记录
python3 scripts/expense.py --delete 3

# 导出CSV
python3 scripts/expense.py --export

# 快速记账（交互）
python3 scripts/expense.py --interactive
```

## 类别预设

餐饮 | 交通 | 购物 | 娱乐 | 居住 | 医疗 | 教育 | 通讯 | 服饰 | 护肤 | 饮品 | 其他

## 数据存储

本地 JSON 文件：`~/.qclaw/workspace/expenses.json`
- 无需账户
- 无需联网
- 随时可导出

## 示例输出

```
💰 本月支出报告（2026年4月）
━━━━━━━━━━━━━━━━━━━━━━
总支出：2,847.5 元
预算：3,000 元（已用 94.9%）

📊 分类明细：
  🍽️ 餐饮    1,200 (42%)
  🚗 交通    580   (20%)
  🛒 购物    450   (16%)
  ☕ 饮品    280   (10%)
  🎬 娱乐    337.5 (12%)

📈 对比上月（3月）：
  餐饮  +15%（外卖增加）
  交通  -8%（少出差）

⚠️ 注意：饮品支出增长较快
```
