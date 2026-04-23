/** Format USD value with $ prefix and 2 decimal places */
export function formatUSD(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

/** Format percentage with sign and % suffix */
export function formatPct(value: number, decimals = 2): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}%`;
}

/** Format rate as basis points or percentage */
export function formatRate(value: number): string {
  const pct = (value * 100).toFixed(4);
  return `${Number(pct) >= 0 ? "+" : ""}${pct}%`;
}

/** Format a number with appropriate decimal places */
export function formatNum(value: number, decimals = 2): string {
  return value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/** Format timestamp to human-readable relative time or datetime */
export function formatTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

/** Calculate duration string from entry time to now */
export function formatDuration(entryIso: string): string {
  const ms = Date.now() - new Date(entryIso).getTime();
  const hours = Math.floor(ms / 3_600_000);
  const days = Math.floor(hours / 24);
  const remainHours = hours % 24;

  if (days > 0) return `${days}d ${remainHours}h`;
  return `${hours}h`;
}

/** Exchange name display mapping */
export function exchangeName(exchange: string): string {
  const map: Record<string, string> = {
    hyperliquid: "Hyperliquid",
    binance: "Binance",
  };
  return map[exchange] ?? exchange;
}
