function nowIso() {
  return new Date().toISOString();
}

export function executePaperBuy({ proposal, state }) {
  const position = {
    position_id: proposal.proposal_id,
    symbol: proposal.symbol,
    job_id: proposal.job_id,
    strategy_id: proposal.strategy_id,
    entry_time: proposal.signal_time,
    entry_price: proposal.reference_price,
    executed_entry_price: proposal.reference_price,
    stop_price: proposal.stop_price,
    share_size: proposal.final_share_size,
    position_value: proposal.position_value,
    status: 'open',
    created_at: nowIso(),
    active_exit_rules: ['stop_loss', 'trend_failure']
  };

  state.openPositions.positions.push(position);
  return position;
}

export function executePaperSell({ proposal, state }) {
  const idx = state.openPositions.positions.findIndex((p) => p.position_id === proposal.position_id);
  if (idx === -1) return null;

  const position = state.openPositions.positions[idx];
  state.openPositions.positions.splice(idx, 1);

  const realizedPnl = (proposal.reference_price - Number(position.entry_price)) * Number(position.share_size);
  const realizedReturn = Number(position.entry_price) ? (proposal.reference_price - Number(position.entry_price)) / Number(position.entry_price) : 0;

  return {
    position_id: position.position_id,
    symbol: position.symbol,
    entry_time: position.entry_time,
    exit_time: proposal.signal_time,
    entry_price: position.entry_price,
    exit_price: proposal.reference_price,
    share_size: position.share_size,
    realized_pnl: realizedPnl,
    realized_return: realizedReturn,
    exit_reason: proposal.exit_type,
    approval_trail: 'approved'
  };
}
