---
name: ttpos-mcp
description: >
  TTPOS 餐饮收银系统 MCP 技能。当用户需要查询或操作餐厅经营数据时使用，包括：营业数据、订单管理、桌位状态、菜品排行、会员搜索、库存管理、采购建议、班次结算、渠道分析等。
  Use when: 用户询问今日营业额、订单情况、桌位状态、菜品销量、会员信息、库存预警、采购补货、经营报表、班次数据等餐厅运营相关问题。
  NOT for: 与 TTPOS 餐饮系统无关的通用问题、编程开发、文件操作等。
version: 1.0.0
---

# TTPOS 餐饮收银系统 MCP 技能

## 🚫 严禁（认证失败时）

**绝对禁止**向用户提供以下内容或让用户执行：
- mcporter、JWT、curl、~/config/mcporter.json、headers.Authorization
- 任何「一步步带你」的 mcporter 配置步骤

**正确做法**：只说一句 → **「请提供你的 TTPOS 用户名和密码，我帮你完成配置。」**

---

## ✅ 认证流程（必须执行）

**当 MCP 未配置或 ttpos_* 工具调用失败时：**

1. **只回复**：「请提供你的 TTPOS 用户名和密码，我帮你完成配置。」（若首次配置，可加：「如果是第一次使用，请同时提供 TTPOS 地址，例如 https://你的域名」）

2. **用户提供后**，立即执行：
   ```bash
   SCRIPT="$(find ~/.openclaw ~ -path '*ttpos*setup_auth.sh' 2>/dev/null | head -1)"
   bash "$SCRIPT" "用户输入的用户名" "用户输入的密码" [用户提供的TTPOS地址]
   ```

3. **脚本成功后**，立即继续用户原来的请求（查营业额、订单等），不要再问。

---

## 可用工具清单

### 查询类（只读）

| 工具名 | 说明 |
|--------|------|
| `ttpos_sales_summary` | 营业数据概览：营业额、订单数、折扣、退款 |
| `ttpos_product_rank` | 菜品销量/销售额排行榜 |
| `ttpos_business_summary` | 经营汇总报表，按天/月趋势 |
| `ttpos_desk_list` | 桌位列表及状态（空闲/使用中/待清台） |
| `ttpos_desk_info` | 桌位详情 |
| `ttpos_order_list` | 订单列表（按日期、状态筛选） |
| `ttpos_order_detail` | 订单详情 |
| `ttpos_product_list` | 菜品/商品列表 |
| `ttpos_member_search` | 会员搜索（手机号/姓名） |
| `ttpos_material_list` | 原材料列表 |
| `ttpos_material_stock_detail` | 库存明细 |
| `ttpos_product_sales` | 菜品销售统计 |
| `ttpos_payment_method_stats` | 支付方式统计 |
| `ttpos_staff_list` | 员工列表 |
| `ttpos_shift_summary` | 班次结算数据 |
| `ttpos_member_recharge_list` | 会员充值记录 |
| `ttpos_channel_sales` | 渠道销售对比（堂食/外卖/扫码） |
| `ttpos_customer_analytics` | 顾客分析（新客/回头客） |
| `ttpos_kitchen_efficiency` | 厨房效率分析 |
| `ttpos_dashboard_7days` | 最近 7 天营业趋势 |
| `ttpos_purchase_order_list` | 采购单列表 |
| `ttpos_purchase_order_detail` | 采购单详情 |
| `ttpos_stock_loss_list` | 报损记录 |
| `ttpos_promotion_list` | 促销活动列表 |
| `ttpos_time_period_sales` | 时段销售分析 |
| `ttpos_home_dashboard` | 首页仪表盘 |

### 操作类（写入，需谨慎）

| 工具名 | 说明 | 风险 |
|--------|------|------|
| `ttpos_cancel_order` | 取消订单 | ⚠️ 不可逆 |
| `ttpos_order_remark` | 订单备注 | - |
| `ttpos_send_to_kitchen` | 送厨 | - |
| `ttpos_accept_h5_order` | 接受 H5 扫码订单 | - |
| `ttpos_reject_h5_order` | 拒绝 H5 订单 | - |
| `ttpos_close_desk` | 关台 | ⚠️ 不可逆 |
| `ttpos_change_desk` | 转台 | - |
| `ttpos_merge_desk` | 并台 | - |
| `ttpos_product_status` | 商品上下架 | - |
| `ttpos_product_change_price` | 改价 | ⚠️ 不可逆 |
| `ttpos_update_safety_stock` | 修改安全库存 | - |

### 采购类

| 工具名 | 说明 |
|--------|------|
| `ttpos_supplier_list` | 供应商列表 |
| `ttpos_purchase_suggestion` | 智能采购建议（基于消耗与库存） |
| `ttpos_create_purchase_order` | 创建采购单 |

---

## 采购工作流

当用户要求采购建议或补货时，推荐流程：

1. 调用 `ttpos_purchase_suggestion` 获取建议（可指定 `replenish_days`）
2. 向用户展示：物品名、当前库存、日均消耗、预计可用天数、建议采购量
3. 用户确认后，调用 `ttpos_supplier_list` 获取供应商
4. 用户选择供应商后，调用 `ttpos_create_purchase_order` 创建采购单
5. 采购单创建后为「待提交」状态，需在 TTPOS 系统中手动提交审核

---

## 重要规则

- **危险操作**：取消订单、关台、改价等执行前必须向用户明确确认
- **数据呈现**：用简洁语言总结，金额使用当地货币符号
- **异常提示**：主动指出异常或值得关注的数据
- **大结果集**：先给摘要再提供详情

---


