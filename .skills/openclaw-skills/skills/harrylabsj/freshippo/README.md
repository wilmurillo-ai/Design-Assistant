# Freshippo Skill v2.0

Freshippo Shopping Assistant Skill, supports browser automation for search, fresh produce selection, add to cart operations, with payment left to user control.

## Features

### v2.0 - Browser Automation Added

- 🔍 **Product Search**: Keyword search with fresh produce filtering
- 🥬 **Fresh Produce Selection**: Read origin, traceability codes, freshness indicators
- 💰 **Price Comparison**: Regular price vs X Member price comparison
- 🛒 **Cart Operations**: Add products under logged-in state
- 🎫 **X Member Benefits**: Auto-check member discounts
- 🚚 **Delivery Slots**: View 30-minute delivery slots
- 📋 **Order Preview**: Generate complete order information (excluding payment)

### v1.0 - Decision Support

- ✅ Fresh produce selection guide
- ✅ Delivery slot optimization
- ✅ X Member benefits explanation
- ✅ Weekly grocery planning

## Safety Boundary

| Operation | Agent | User |
|------|-------|------|
| Search/Browse | ✅ | - |
| View Freshness | ✅ | - |
| Add to Cart/Apply Coupons | ✅ | - |
| **Payment/Submit Order** | ❌ | ✅ |

## Workflow

```
Discovery → Comparison → Selection → Add to Cart → Select Delivery Slot → Preview → [User Pays]
```

## Version History

- v2.0.0 - Added browser automation support
- v1.0.0 - Basic shopping guide

## Installation

```bash
clawhub install freshippo
```

## Usage Example

```
User: Help me buy salmon from Freshippo
Agent: Search → Compare freshness → Add to cart → Select delivery slot → Generate order preview
User: 👤 Completes payment
```

## License

MIT