---
name: amazon-return-optimizer
description: "Amazon return rate analyzer and reduction agent. Identify why customers return your products, fix listing accuracy issues, improve packaging to reduce damage returns, and manage FBA removal orders and reimbursement claims. Triggers: return rate, amazon returns, reduce returns, return analysis, fba returns, return reason, product return, amazon refund, return optimization, high return rate, listing accuracy, amazon removal order, fba reimbursement, return report, customer returns"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-return-optimizer
---

# Amazon Return Rate Optimizer

High return rates kill your margins and can get your listing suppressed. Diagnose why customers return your product, fix the root causes, and recover lost revenue from FBA reimbursements.

## Commands

```
return analyze [data]           # analyze return reasons and patterns
return audit [product]          # listing accuracy audit to reduce returns
return benchmark [category]     # return rate benchmarks for your category
return reimbursement            # FBA reimbursement claim guide
return packaging                # packaging improvement checklist
return response [reason]        # how to address specific return reason
return removal                  # FBA removal order strategy
return report                   # generate return reduction action plan
```

## What Data to Provide

- **Return rate %** — from Seller Central Voice of Customer or FBA Returns report
- **Return reasons** — paste the return reason breakdown
- **Product category** — for benchmark comparison
- **Current listing** — title, bullets, images description
- **Packaging details** — how product is packaged for shipment

## Return Rate Benchmarks by Category

| Category | Average Return Rate | High Alert |
|----------|--------------------|-----------:|
| Electronics | 8–15% | >20% |
| Clothing / Apparel | 20–40% | >45% |
| Shoes | 25–35% | >40% |
| Jewelry | 10–20% | >25% |
| Toys | 5–10% | >15% |
| Home & Kitchen | 5–12% | >18% |
| Beauty / Health | 5–10% | >15% |
| Sports & Outdoors | 5–10% | >15% |
| Books | 1–3% | >5% |
| Food & Grocery | 2–5% | >8% |

**Amazon suppression risk**: Return rate >15% above category average may trigger review

## Return Reason Analysis Framework

### Top Amazon Return Reasons & Fixes

| Return Reason | Root Cause | Fix |
|--------------|-----------|-----|
| "Item defective or doesn't work" | Manufacturing defect | Supplier QC, materials upgrade |
| "Inaccurate website description" | Listing mismatch | Rewrite bullets, update images |
| "Item smaller/larger than expected" | Size not clear | Add size comparison image, dimensions in title |
| "Wrong item sent" | Pick & pack error | Work with FBA, check SKU setup |
| "No longer needed" | Impulse purchase | Add urgency to listing, not fixable |
| "Item arrived damaged" | Packaging failure | Improve inner packaging, double-box |
| "Didn't like the quality" | Expectation mismatch | Honest listing, better photos |
| "Bought by mistake" | Listing confusion | Clearer title, compatibility section |
| "Doesn't fit" | Size guide missing | Add size chart, fit guide to listing |
| "Missing parts/accessories" | Incomplete shipment | QC check on packing line |

### Prioritization Matrix

```
High Return Rate × Fixable = ACT NOW
High Return Rate × Not Fixable = Manage/Accept
Low Return Rate × Fixable = Nice to Have
Low Return Rate × Not Fixable = Ignore
```

## Listing Accuracy Audit

Run this checklist to reduce expectation-gap returns:

### Dimensions & Size
- [ ] Exact dimensions in title or first bullet (not just in description)
- [ ] Size comparison image (next to common object or hand)
- [ ] Weight listed if relevant to customer decision
- [ ] Package dimensions vs. product dimensions clearly distinguished

### Materials & Quality
- [ ] Material composition stated (100% cotton, not just "soft fabric")
- [ ] Color accuracy: photo matches real product (calibrated display)
- [ ] Texture/finish described accurately (glossy vs. matte, rough vs. smooth)
- [ ] Fragrance/scent honestly described

### Compatibility
- [ ] Compatible models/sizes explicitly listed (for accessories)
- [ ] Incompatible items listed ("Does NOT fit iPhone 15 Pro Max")
- [ ] Power requirements, voltage, plug type (for electronics)
- [ ] Age appropriateness (for toys, children's products)

### What's in the Box
- [ ] Complete list of included items in listing
- [ ] What's NOT included (batteries, tools, etc.)
- [ ] Flat lay image showing all components

## Packaging Improvement Guide

### Transit Damage Prevention

| Issue | Solution |
|-------|---------|
| Product shifting in box | Add void fill (air pillows, paper) |
| Box crushing | Double-wall corrugated, minimum 32 ECT |
| Glass/fragile items | Bubble wrap + foam inserts, "Fragile" label |
| Electronics | Anti-static bag + foam surround |
| Liquid products | Sealed inner bag + absorbent pad |

**Amazon Drop Test Standard**: Box should survive 3-foot drop on each face, edge, and corner

### FBA Packaging Requirements
- Products must be in sealed poly bag or box (no exposed products)
- Barcodes scannable through packaging
- Sets/bundles bagged together with "Sold as Set" label
- Adult products in opaque packaging

## FBA Reimbursement Claims

Amazon owes you money when:
- Units lost in FBA warehouse
- Units damaged by Amazon (not customer)
- Customer returned item but Amazon didn't restock or reimburse
- Overcharged FBA fees (wrong size tier)

### Reimbursement Process

1. **Lost inventory**: Check Inventory Reconciliation Report → file case if discrepancy
2. **Damaged by Amazon**: Check FBA Customer Returns report → units marked "Damaged:Amazon" → file claim
3. **Customer return not received**: Wait 45 days after return initiated → file claim if not processed
4. **Fee overcharge**: Check FBA Fee Preview → measure product → file dispute if wrong tier

**Time limits**: Most claims must be filed within 18 months of incident

**Tools**: Sellerboard, Getida, GETIDA (recovery services that work on % of recovered amount)

## Return Reduction Action Plan Template

```
Week 1: Audit
- Download return reason report (90 days)
- Identify top 3 return reasons
- Score each: fixable in listing vs. product vs. packaging

Week 2: Listing Fixes
- Update listing based on accuracy audit
- Add size comparison image
- Rewrite any misleading bullets

Week 3: Packaging Fix
- Order improved packaging materials
- Update FBA prep instructions

Week 4: Monitor
- Compare return rate to 30 days prior
- File any pending reimbursement claims
- Repeat monthly
```

## Output Format

1. **Return Rate Diagnosis** — which reasons are causing most returns
2. **Priority Fix List** — top 3 changes ranked by impact
3. **Listing Accuracy Checklist** — specific items to update
4. **Packaging Recommendations** — if damage is a factor
5. **Reimbursement Opportunity** — estimate of recoverable Amazon errors
6. **30-Day Action Plan** — week-by-week improvement roadmap
