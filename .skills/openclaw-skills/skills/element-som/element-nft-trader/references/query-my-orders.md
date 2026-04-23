# Query My Orders

Use this when the user asks:

- "Show my orders"
- "What listings do I have?"
- "What has this wallet listed on Element?"

Ask for the required `chain` first before executing this query. Do not iterate over multiple chains to find the user's orders.

This is account-specific and uses the unified `entry.ts` executor. It uses `chain`, not `network`.

If `wallet_address` is omitted, the query defaults to the account associated with the configured API key.

```json
{
  "operationType": "queryMyOrders",
  "queryMyOrders": {
    "chain": "base",
    "wallet_address": "0x...",
    "limit": 20
  }
}
```

Run with `npx ts-node scripts/entry.ts "$INPUT"`.

Returns:

- `chain`
- `usingDefaultAccount`
- `walletAddress`
- `count`
- normalized order summaries
- `orders[].expirationTime` as a readable UTC time string
