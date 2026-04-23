function floorShares(value) {
  if (!Number.isFinite(value) || value <= 0) return 0;
  return Math.floor(value);
}

export function calculatePositionSizing({ entryPrice, stopPrice, risk }) {
  const maxRiskPerTrade = Number(risk?.max_risk_per_trade ?? 0);
  const maxPositionValue = Number(risk?.max_position_value ?? 0);
  const riskPerShare = entryPrice - stopPrice;

  if (!Number.isFinite(entryPrice) || !Number.isFinite(stopPrice) || !Number.isFinite(riskPerShare) || riskPerShare <= 0) {
    return {
      ok: false,
      reason: 'invalid_prices',
      riskPerShare: null,
      calculatedShareSize: 0,
      finalShareSize: 0,
      positionValue: 0,
      capped: false
    };
  }

  const calculatedShareSize = floorShares(maxRiskPerTrade / riskPerShare);
  const cappedShareSize = maxPositionValue > 0 ? floorShares(maxPositionValue / entryPrice) : calculatedShareSize;
  const finalShareSize = Math.max(0, Math.min(calculatedShareSize, cappedShareSize || calculatedShareSize));
  const positionValue = finalShareSize * entryPrice;
  const capped = finalShareSize < calculatedShareSize;

  return {
    ok: finalShareSize > 0,
    riskPerShare,
    calculatedShareSize,
    finalShareSize,
    positionValue,
    capped,
    maxRiskPerTrade,
    maxPositionValue
  };
}
