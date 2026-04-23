function sma(values, length) {
  if (values.length < length) return null;
  const slice = values.slice(values.length - length);
  return slice.reduce((a, b) => a + b, 0) / length;
}

function priorHighestHigh(rows, length) {
  if (rows.length < length + 1) return null;
  const prior = rows.slice(rows.length - 1 - length, rows.length - 1);
  return Math.max(...prior.map((r) => r.high));
}

function averageVolume(rows, length) {
  if (rows.length < length + 1) return null;
  const prior = rows.slice(rows.length - 1 - length, rows.length - 1);
  return prior.reduce((sum, r) => sum + r.volume, 0) / length;
}

function recentSupport(rows, lookback = 10) {
  if (rows.length < lookback + 1) return null;
  const prior = rows.slice(rows.length - 1 - lookback, rows.length - 1);
  return Math.min(...prior.map((r) => r.low));
}

export function buildIndicatorsForRows(rows, strategy) {
  const closes = rows.map((r) => r.close);
  const latest = rows.at(-1) ?? null;
  if (!latest) return null;

  const breakoutLookback = strategy.inputs?.breakout_lookback_days ?? 20;
  const volumeAvgDays = strategy.inputs?.volume_avg_days ?? 20;
  const trendMaDays = strategy.inputs?.trend_ma_days ?? 50;
  const exitMaDays = strategy.inputs?.exit_ma_days ?? 10;

  return {
    latestDate: latest.date,
    latestClose: latest.close,
    latestVolume: latest.volume,
    prior20DayHigh: priorHighestHigh(rows, breakoutLookback),
    avg20DayVolume: averageVolume(rows, volumeAvgDays),
    ma50: sma(closes, trendMaDays),
    ma10: sma(closes, exitMaDays),
    recentSupport: recentSupport(rows, 10)
  };
}

export function buildIndicatorMap(marketData, strategy) {
  const output = {};
  for (const [symbol, item] of Object.entries(marketData)) {
    output[symbol] = item.ok ? buildIndicatorsForRows(item.rows, strategy) : null;
  }
  return output;
}
