# search-marriott-package ref

## Marriott Hotel Package Search (search-marriott-package)

### Parameters

- **--keyword** (required): Search keyword
  - Supported dimensions: province (e.g., `江苏`), city (e.g., `三亚`), brand (e.g., `喜来登`), hotel name (e.g., `西溪喜来登度假大酒店`), selling point (e.g., `通兑套餐`, `儿童娱乐`, `藏地文化`)
  - Note: Only one dimension can be searched at a time, different dimensions cannot be combined
- **--sort-type** (optional): Sorting method
  - Values: `price_asc` (price low to high) · `price_desc` (price high to low)

### Examples

```bash
flyai search-marriott-package --keyword "三亚" --sort-type "price_asc"
```

### Output Example

```
{
  "data": {
    "itemList": [
      {
        "picUrl": "https://...jpg", // Package image
        "itemId": "...", // Package unique identifier
        "sellPoint": "...", // Selling point
        "price": "...", // Reference price, guide users to booking page for actual price with possible discounts
        "detailUrl": "https://...", // Booking link
        "title": "...", // Package name
        "benefit": "..." // Member benefits
      }
    ]
  },
  "message": "success",
  "status": 0
}
```