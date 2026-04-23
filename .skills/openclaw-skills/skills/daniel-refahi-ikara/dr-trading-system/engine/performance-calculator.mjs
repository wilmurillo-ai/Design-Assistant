function safeNumber(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

export function calculatePerformanceSummary({ state }) {
  const openPositions = state.openPositions.positions ?? [];
  const closedRows = (state.closedRows ?? []).map((row) => ({
    realized_pnl: safeNumber(row.realized_pnl),
    realized_return: safeNumber(row.realized_return)
  }));

  const wins = closedRows.filter((r) => r.realized_pnl > 0);
  const losses = closedRows.filter((r) => r.realized_pnl < 0);
  const sinceStartPnl = closedRows.reduce((sum, r) => sum + r.realized_pnl, 0);
  const sinceStartReturn = safeNumber(state.runtimeConfig?.job?.risk?.paper_account_size) > 0
    ? sinceStartPnl / safeNumber(state.runtimeConfig.job.risk.paper_account_size)
    : 0;

  return {
    job_id: state.jobState.job_id,
    today_pnl: 0,
    since_start_pnl: sinceStartPnl,
    since_start_return: sinceStartReturn,
    win_rate: closedRows.length ? wins.length / closedRows.length : null,
    avg_winning_trade_return: wins.length ? wins.reduce((s, r) => s + r.realized_return, 0) / wins.length : null,
    avg_losing_trade_return: losses.length ? losses.reduce((s, r) => s + r.realized_return, 0) / losses.length : null,
    max_drawdown: null,
    open_positions_count: openPositions.length,
    closed_today_count: 0
  };
}
