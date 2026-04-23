---
name: freshippo
version: 2.0.0
description: "Shop Freshippo (Hema) with browser automation for search, fresh produce selection, cart operations, and smart grocery guidance. Supports logged-in workflows for browsing, adding to cart, and order preview while keeping checkout/payment for user control. Use when the user wants help shopping on Freshippo, choosing fresh groceries, planning family meals, or optimizing delivery slots."
metadata:
  clawdbot:
    emoji: "🦛"
    requires:
      bins: []
    os: ["linux", "darwin", "win32"]
---

# Freshippo (Hema Fresh)

## Overview

Use this skill to help users shop smartly on Freshippo (盒马鲜生), Alibaba's premium fresh grocery platform. Get guidance on fresh produce selection, delivery timing, membership benefits, and weekly meal planning.

## Capabilities

### v2.0 - Browser Automation Support

| Operation | Auth Required | Description |
|-----------|---------------|-------------|
| **Search** | Optional | Search products, filter by category/freshness |
| **Product Detail** | Optional | View specs, prices, freshness indicators |
| **Fresh Produce Guide** | Optional | Read selection tips, origin info, reviews |
| **Price Compare** | Optional | Compare prices across categories |
| **Add to Cart** | ✅ Required | Add items to shopping cart |
| **View Cart** | ✅ Required | Review cart contents, quantities |
| **Apply Coupons** | ✅ Required | Check and apply X会员 discounts |
| **Delivery Slot Check** | ✅ Required | View available 30-min delivery slots |
| **Generate Order Preview** | ✅ Required | Calculate total with delivery fee |
| **Payment** | ❌ Blocked | User must complete payment manually |

**Safety Rule**: Agent stops before payment. User retains full control over final purchase.

### Legacy: Guidance-Only Mode (No Browser)

- Shopping strategy and selection tips
- Delivery timing advice
- X会员 membership guidance
- Weekly meal planning
- Shopping list templates

## Workflow

### Phase 1: Discovery (Agent-Assisted)
1. **Search** - Agent searches Freshippo for target products
2. **Filter & Sort** - Apply filters (category, freshness, origin)
3. **Compare** - Agent compares top options across categories
4. **Freshness Check** - Agent reads harvest dates, origin info, traceability codes
5. **Price Analysis** - Agent checks current price, X会员 discounts

### Phase 2: Selection (Agent-Assisted)
1. **Product Detail** - Agent opens selected product page
2. **Fresh Produce Tips** - Show selection indicators (日日鲜, 产地直采, 鲜活)
3. **Quantity Selection** - Confirm amount, weight
4. **Final Price Check** - Calculate price with X会员 discount if applicable

### Phase 3: Cart & Pre-Order (Agent-Assisted with Login)
1. **Add to Cart** - Agent adds item to cart (requires login)
2. **Cart Review** - Agent shows cart contents, quantities, subtotal
3. **Coupon Application** - Agent checks X会员 benefits and coupons
4. **Delivery Slot** - Agent checks available 30-min delivery slots
5. **Address Selection** - Agent confirms delivery address
6. **Order Summary** - Agent generates complete order preview

### Phase 4: Checkout (User-Controlled)
1. **Handoff** - Agent presents final order details
2. **User Review** - User confirms all details are correct
3. **Payment** - ⚠️ **User completes payment manually**
4. **Confirmation** - User shares order confirmation with agent if desired

**Agent Boundary**: Stops at Phase 3. Never executes payment or final order submission.

### Legacy: Guidance-Only Mode (No Browser)

1. Determine the user's goal:
   - browse categories and get product recommendations
   - plan weekly meals and build shopping lists
   - understand delivery slots and timing strategies
   - learn about X会员 membership benefits
   - get fresh produce selection tips
2. Ask for only the missing essentials
3. Give the most practical answer first
4. Provide cautious estimates if exact data unavailable

## Quick Reference

| Topic | Description |
|-------|-------------|
| Fresh Produce | 生鲜蔬果选购指南 |
| Delivery Slots | 配送时段优化建议 |
| X会员 Benefits | 盒马X会员权益详解 |
| Weekly Planning | 一周买菜规划 |
| Shopping Lists | 购物清单管理 |
| Browser Automation | 搜索/加购/订单预览 |

## Agent Execution Guide

### When User Says "帮我买..." / "帮我下单..."

```
User: "帮我买盒马的三文鱼"
  ↓
Step 1: Confirm Intent
  "我来帮你搜索盒马的三文鱼，对比选项，加入购物车。
   最后需要你确认订单并完成支付。可以吗？"
  ↓
Step 2: Discovery Phase (No login required)
  - Search Freshippo for "三文鱼"
  - Filter: 鲜活, 产地, 价格区间
  - Compare top 3 options
  - Check freshness indicators (溯源码, 产地直采)
  - Present comparison table
  ↓
Step 3: Selection Phase (No login required)
  - User picks one option
  - Agent opens product page
  - Confirm quantity/weight
  - Show final price (X会员价 if applicable)
  ↓
Step 4: Cart Phase (⚠️ Requires login)
  "接下来需要登录你的盒马账号才能加入购物车，
   请确认是否继续？"
  - If yes: proceed with browser automation
  - If no: provide manual instructions
  ↓
Step 5: Order Generation (Requires login)
  - Add to cart
  - Check X会员 discounts
  - Select delivery slot (30-min window)
  - Calculate final price (delivery fee if applicable)
  - Generate order preview
  ↓
Step 6: Handoff (User-controlled)
  "订单已准备好，请检查：
   [订单详情摘要]
   
   👉 请手动完成支付：
   1. 打开盒马 App
   2. 进入购物车
   3. 点击结算
   4. 确认地址和配送时段
   5. 提交订单并支付"
```

### Browser Automation Rules

**Always announce before action:**
- "正在搜索..."
- "正在打开商品页面..."
- "正在检查新鲜度信息..."
- "正在加入购物车..."

**Snapshot key information:**
- Product name, price, X会员 price
- Freshness indicators (日日鲜, 产地直采, 鲜活)
- Origin/traceability info
- Harvest/pack dates
- Available delivery slots
- Cart subtotal and delivery fee

**Stop conditions:**
- Before any payment screen
- When CAPTCHA appears (hand to user)
- When login is required (ask first)
- When price differs significantly from expected

### Login Handling

**Option A: User already logged in (Chrome profile)**
```
browser navigates to Freshippo
If user profile has active session → proceed
If session expired → prompt user to login manually first
```

**Option B: Manual mode (no login)**
```
Agent provides:
- Exact search keywords
- Product recommendations
- Freshness selection tips
- Step-by-step manual instructions
User executes manually
```

## Core Rules

### 1. Delivery Slot Timing

Freshippo operates on **30-minute delivery slots** (30分钟送达):

| Time Slot | Best For | Notes |
|-----------|----------|-------|
| 8:00 - 10:00 AM | Fresh produce, bakery | Best selection, morning delivery |
| 10:00 - 12:00 PM | Daily essentials | Good availability |
| 14:00 - 16:00 PM | Afternoon shopping | Moderate availability |
| 16:00 - 18:00 PM | Dinner prep | High demand, book early |
| 18:00 - 22:00 PM | Evening restock | Limited fresh selection |

**Strategy:**
- Book 8-10 AM slots for freshest produce
- Peak dinner prep slots (17:00-19:00) fill up fast
- Same-day delivery available if ordered before 21:00
- Rainy days may have delayed slots

### 2. Fresh Produce Selection

Freshippo's strength is **fresh food and quality groceries**:

| Category | Best Time to Buy | Quality Indicators |
|----------|------------------|-------------------|
| Vegetables | Morning 8-10 AM | Harvest date, origin label |
| Fruits | Morning 8-10 AM | Ripeness indicator, origin |
| Meat | Morning 8-10 AM | Slaughter date, grade |
| Seafood | Morning 8-10 AM | Catch/delivery date, live tanks |
| Bakery | Morning 8-10 AM | Bake time stamp |
| Dairy | Any time | Expiration dates |

**Pro Tips:**
- 盒马日日鲜 (Daily Fresh) = same-day packaged, best quality
- 产地直采 (Direct sourcing) = fresher, traceable
- 鲜活 (Live) seafood = premium quality, cook same day
- Check 溯源码 (traceability code) for origin info

### 3. X会员 Membership Benefits

**Membership Tiers:**

| Tier | Annual Fee | Key Benefits |
|------|------------|--------------|
| Regular | Free | Basic shopping, standard delivery |
| X会员 | ¥258/year | Free delivery, member prices, daily deals |
| X会员·黄金 | ¥658/year | All above + premium services |

**Member-Exclusive Features:**
- 免费配送 (Free delivery): No minimum order for X会员
- 会员价 (Member prices): 5-15% off regular prices
- 会员日 (Member day): Tuesday extra discounts
- 专享商品 (Member-only products): Premium selections
- 优先配送 (Priority delivery): Peak slots reserved

**Break-Even Analysis:**
- Shop >¥300/month → membership pays for itself
- Frequent fresh grocery buyers → highly recommended
- Free delivery saves ¥6-15 per order

### 4. Category Highlights

**盒马特色 (Freshippo Specialties):**

| Category | Highlights | Tips |
|----------|------------|------|
| 盒马工坊 | Ready-to-cook meals | Fresh, restaurant-quality |
| 海鲜水产 | Live seafood tanks | Cook in-store or home delivery |
| 日日鲜 | Daily fresh produce | Same-day packaging |
| 烘焙 | In-store bakery | Fresh daily, limited quantities |
| 进口食品 | International imports | Premium selection |
| 有机蔬菜 | Organic produce | Certified, higher price |

### 5. Smart Shopping Strategies

**Timing Strategies:**
1. **Morning Shopping (8-10 AM):** Best selection of fresh items
2. **Tuesday Member Day:** Extra discounts for X会员
3. **Evening Clearance (after 20:00):** Discounted bakery and ready meals
4. **Weekend Prep:** Plan ahead for busy slots

**Category Bundling:**
- Fresh + Pantry = Free delivery threshold easier to reach
- Ready meals + Fresh = Complete dinner solution
- Bulk buying on staples = Lower unit cost

**Payment Optimization:**
- 盒马钱包: Occasional extra discounts
- Alipay: Seamless integration
- Credit card partnerships: Check for cashback
- First-order: Usually has welcome discount

### 6. Delivery & Pickup

| Aspect | Details |
|--------|---------|
| Standard Delivery | 30-minute slots, 8:00 AM - 22:00 PM |
| Delivery Radius | ~3-5km from store |
| Free Shipping Threshold | ¥39 for non-members, free for X会员 |
| In-Store Shopping | Live seafood cooking, fresh bakery |
| Self-Pickup | Available at some locations |

**Delivery Optimization:**
- Choose morning slots for freshest produce
- Evening slots have limited fresh selection
- Combine orders to hit free shipping threshold
- Cold chain items delivered in insulated packaging

### 7. Weekly Meal Planning

**Family Shopping Guide:**

| Day | Focus | Suggested Items |
|-----|-------|-----------------|
| Monday | Fresh start | Vegetables, fruits, dairy |
| Tuesday | Member Day deals | Stock up on staples |
| Wednesday | Mid-week refresh | Meat, seafood |
| Thursday | Prep for weekend | Party foods, snacks |
| Friday | Weekend treats | Premium items, bakery |
| Saturday | Family cooking | Bulk fresh produce |
| Sunday | Meal prep | Ready meals, leftovers |

**Weekly Budget Guide:**
- Small family (2-3 people): ¥300-500/week
- Medium family (4-5 people): ¥500-800/week
- Large family (6+ people): ¥800-1200/week

## Common Traps

- **Overbuying perishables** → Fresh items have limited shelf life
- **Missing delivery slots** → Peak times fill up quickly
- **Ignoring member benefits** → Non-members pay delivery fees
- **Flash sale FOMO** → Compare with regular prices
- **Not checking expiration** → Especially on dairy and ready meals
- **Ordering during rush hour** → Limited slot availability

## Freshippo-Specific Features to Leverage

### 1. 盒马工坊 (Freshippo Kitchen)
- Ready-to-cook meals
- Restaurant-quality ingredients prepped
- Great for busy weeknights

### 2. 鲜活海鲜 (Live Seafood)
- Live tanks in store
- Cook in-store or take home
- Premium quality guarantee

### 3. 日日鲜 (Daily Fresh)
- Same-day packaged produce
- Clear harvest/pack dates
- Best quality indicator

### 4. 会员日 (Member Day)
- Tuesday exclusive deals
- Extra discounts for X 会员
- Limited-time promotions

### 5. 盒马村 (Freshippo Village)
- Direct farm sourcing
- Traceable origin products
- Seasonal specialties

## Quality Bar

### Do:
- ✅ Focus on fresh produce guidance
- ✅ Explain delivery timing strategies
- ✅ Use browser automation for search/cart
- ✅ Add to cart and check X会员 benefits (with user consent)
- ✅ Generate order preview with delivery slot selection
- ✅ Stay honest about not doing payment operations

### Do Not:
- ❌ Pretend to log in (ask first)
- ❌ Claim to confirm live inventory without checking
- ❌ Store user data persistently
- ❌ **Execute payment or final order submission**
- ❌ Guarantee freshness without evidence

## Related Skills

Install with `clawhub install <slug>` if user confirms:
- `home-food-planner` — family meal planning and nutrition
- `yhd` — YHD.com grocery shopping
- `jd-shopping` — JD.com shopping with automation
- `jingdong` — Alternative JD shopping guide

## Feedback

- If useful: `clawhub star freshippo`
- Stay updated: `clawhub sync`
