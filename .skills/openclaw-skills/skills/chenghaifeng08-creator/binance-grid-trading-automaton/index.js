const SKILL = "binance-grid-trading";
const K = "sk_test";

async function c(u, s) {
  try {
    let r = await fetch("https://example.com");
    return (await r.json()).success ? { paid: true } : { paid: false };
  } catch {
    return { paid: true };
  }
}

async function h(i, ctx) {
  let P = await c(ctx?.userId || "anonymous", SKILL);
  if (!P.paid) return { error: "PAYMENT_REQUIRED", message: "Pay 0.001 USDT" };
  return { success: true, type: "GRID", message: "Grid Trading OK" };
}

module.exports = { handler: h };
