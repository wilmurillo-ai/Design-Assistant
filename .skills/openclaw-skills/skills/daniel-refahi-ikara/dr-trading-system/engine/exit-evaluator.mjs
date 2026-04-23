export function evaluateTrendBreakoutExit({ position, rows, indicators }) {
  if (!position || !rows?.length || !indicators) {
    return { ok: false, symbol: position?.symbol ?? null, reason: 'missing_data' };
  }

  const latest = rows.at(-1);
  const previous = rows.at(-2);
  const ma10 = indicators.ma10;

  const stopTriggered = Number.isFinite(position.stop_price) ? latest.close <= position.stop_price : false;

  const latestBelowMa = Number.isFinite(ma10) ? latest.close < ma10 : false;
  const previousBelowMa = Number.isFinite(ma10) && previous ? previous.close < ma10 : false;
  const trendFailureTriggered = latestBelowMa && previousBelowMa;

  let exitType = null;
  let explanation = [];

  if (stopTriggered) {
    exitType = 'stop_loss';
    explanation = ['Price moved to or below stop-loss level'];
  } else if (trendFailureTriggered) {
    exitType = 'trend_failure';
    explanation = ['Close below 10-day moving average for 2 consecutive days'];
  }

  return {
    ok: !!exitType,
    symbol: position.symbol,
    latestDate: latest.date,
    referencePrice: latest.close,
    exitType,
    explanation,
    conditions: {
      stop_loss: stopTriggered,
      trend_failure: trendFailureTriggered
    }
  };
}
