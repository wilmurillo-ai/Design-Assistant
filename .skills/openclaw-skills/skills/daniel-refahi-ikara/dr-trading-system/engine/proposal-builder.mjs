function makeProposalId(jobId, symbol, actionType, signalTime) {
  const safeTime = String(signalTime).replace(/[^0-9A-Za-z]/g, '');
  return `${jobId}_${symbol}_${actionType}_${safeTime}`;
}

export function buildBuyProposal({ job, strategy, symbol, signalTime, entryReferencePrice, stopPrice, sizing, entryEvaluation }) {
  return {
    proposal_id: makeProposalId(job.job_id, symbol, 'buy', signalTime),
    job_id: job.job_id,
    strategy_id: strategy.strategy_id,
    symbol,
    action_type: 'buy',
    signal_time: signalTime,
    reference_price: entryReferencePrice,
    stop_price: stopPrice,
    calculated_share_size: sizing.calculatedShareSize,
    final_share_size: sizing.finalShareSize,
    position_value: sizing.positionValue,
    approval_status: 'pending',
    explanation: [
      ...entryEvaluation.explanation,
      `Risk per share: ${sizing.riskPerShare}`,
      `Max risk per trade: ${sizing.maxRiskPerTrade}`,
      sizing.capped ? 'Position size capped by max position value rule' : 'Position size within cap'
    ],
    conditions: entryEvaluation.conditions
  };
}

export function buildSellProposal({ job, strategy, position, signalTime, exitReferencePrice, exitEvaluation }) {
  const currentPnl = (exitReferencePrice - Number(position.entry_price)) * Number(position.share_size);
  const currentReturn = Number(position.entry_price) ? (exitReferencePrice - Number(position.entry_price)) / Number(position.entry_price) : 0;

  return {
    proposal_id: makeProposalId(job.job_id, position.symbol, 'sell', signalTime),
    job_id: job.job_id,
    strategy_id: strategy.strategy_id,
    symbol: position.symbol,
    action_type: 'sell',
    signal_time: signalTime,
    reference_price: exitReferencePrice,
    approval_status: 'pending',
    current_pnl: currentPnl,
    current_return: currentReturn,
    exit_type: exitEvaluation.exitType,
    explanation: exitEvaluation.explanation,
    conditions: exitEvaluation.conditions,
    position_id: position.position_id
  };
}
