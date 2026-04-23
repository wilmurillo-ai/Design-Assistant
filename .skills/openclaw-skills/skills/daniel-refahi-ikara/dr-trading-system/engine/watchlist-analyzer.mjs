function daysBetween(dateA, dateB) {
  const a = new Date(`${dateA}T00:00:00Z`);
  const b = new Date(`${dateB}T00:00:00Z`);
  return Math.floor((a - b) / 86400000);
}

export function analyzeWatchlist({ watchlist, marketData, indicators, asOfDate = null, maxStaleDays = 7 }) {
  const symbols = watchlist.symbols ?? [];
  const moves = [];
  const nearTrigger = [];
  const triggeredToday = [];
  const staleSymbols = [];

  for (const symbol of symbols) {
    const item = marketData[symbol];
    const ind = indicators[symbol];
    if (!item?.ok || !item.rows?.length || !ind) continue;

    const rows = item.rows;
    const latest = rows.at(-1);
    const previous = rows.at(-2);
    if (!latest || !previous) continue;

    if (asOfDate && daysBetween(asOfDate, latest.date) > maxStaleDays) {
      staleSymbols.push(symbol);
      continue;
    }

    const move = previous.close ? (latest.close - previous.close) / previous.close : 0;
    moves.push({ symbol, move });

    if (ind.prior20DayHigh && latest.close >= ind.prior20DayHigh * 0.98 && latest.close <= ind.prior20DayHigh) {
      nearTrigger.push(symbol);
    }
    if (ind.prior20DayHigh && latest.close > ind.prior20DayHigh) {
      triggeredToday.push(symbol);
    }
  }

  const upToday = moves.filter((m) => m.move > 0).length;
  const downToday = moves.filter((m) => m.move < 0).length;
  const avgMove = moves.length ? moves.reduce((s, m) => s + m.move, 0) / moves.length : 0;
  const sorted = [...moves].sort((a, b) => b.move - a.move);

  return {
    watchlist_size: symbols.length,
    up_today: upToday,
    down_today: downToday,
    average_move_today: avgMove,
    best_performer: sorted[0] ?? null,
    worst_performer: sorted.at(-1) ?? null,
    near_trigger: nearTrigger,
    triggered_today: triggeredToday,
    stale_symbols: staleSymbols,
    overall_tone: moves.length === 0 ? 'stale_or_unavailable' : avgMove > 0.005 ? 'bullish' : avgMove < -0.005 ? 'bearish' : 'mixed'
  };
}
