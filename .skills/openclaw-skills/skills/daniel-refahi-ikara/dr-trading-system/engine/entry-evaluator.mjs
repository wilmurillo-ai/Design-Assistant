export function evaluateTrendBreakoutEntry({ symbol, rows, indicators, strategy }) {
  if (!rows?.length || !indicators) {
    return { ok: false, symbol, reason: 'missing_data', conditions: {} };
  }

  const latest = rows.at(-1);
  const volumeMultiplier = strategy.inputs?.volume_multiplier ?? 1.2;

  const conditions = {
    close_above_prior_20_day_high: indicators.prior20DayHigh != null ? latest.close > indicators.prior20DayHigh : false,
    volume_at_least_required: indicators.avg20DayVolume != null ? latest.volume >= indicators.avg20DayVolume * volumeMultiplier : false,
    close_above_50_day_moving_average: indicators.ma50 != null ? latest.close > indicators.ma50 : false
  };

  const ok = Object.values(conditions).every(Boolean);

  const explanation = [];
  if (conditions.close_above_prior_20_day_high) explanation.push('Close above prior 20-day high');
  if (conditions.volume_at_least_required) explanation.push(`Volume at least ${volumeMultiplier}x 20-day average`);
  if (conditions.close_above_50_day_moving_average) explanation.push('Close above 50-day moving average');

  return {
    ok,
    symbol,
    latestDate: latest.date,
    referencePrice: latest.close,
    conditions,
    explanation,
    indicators
  };
}
