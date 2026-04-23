function pct(v) {
  if (v == null || !Number.isFinite(Number(v))) return 'n/a';
  return `${(Number(v) * 100).toFixed(1)}%`;
}

function money(v) {
  if (v == null || !Number.isFinite(Number(v))) return 'n/a';
  const n = Number(v);
  return `${n >= 0 ? '+' : '-'}$${Math.abs(n).toFixed(2)}`;
}

export function generateStrategyReport({ runtimeConfig, state, performanceSummary, watchlistSummary }) {
  const lines = [];
  lines.push(`# Strategy Report — ${runtimeConfig.job.job_name}`);
  lines.push(`**Mode:** ${runtimeConfig.job.mode}`);
  lines.push(`**Strategy:** ${runtimeConfig.strategy.strategy_name} ${runtimeConfig.strategy.version}`);
  lines.push(`**Domain:** ${runtimeConfig.job.domain}`);
  lines.push(`**Market:** ${runtimeConfig.job.market}`);
  lines.push('');
  lines.push('## Strategy Performance Summary');
  lines.push(`- Today P&L: ${money(performanceSummary.today_pnl)}`);
  lines.push(`- Since start P&L: ${money(performanceSummary.since_start_pnl)}`);
  lines.push(`- Since start return: ${pct(performanceSummary.since_start_return)}`);
  lines.push(`- Win rate: ${pct(performanceSummary.win_rate)}`);
  lines.push(`- Avg winning trade return: ${pct(performanceSummary.avg_winning_trade_return)}`);
  lines.push(`- Avg losing trade return: ${pct(performanceSummary.avg_losing_trade_return)}`);
  lines.push(`- Max drawdown: ${pct(performanceSummary.max_drawdown)}`);
  lines.push(`- Open positions: ${performanceSummary.open_positions_count}`);
  lines.push(`- Closed today: ${performanceSummary.closed_today_count}`);
  lines.push('');
  lines.push('## Open Positions');
  if ((state.openPositions.positions ?? []).length === 0) {
    lines.push('- none');
  } else {
    for (const p of state.openPositions.positions) {
      lines.push(`- ${p.symbol} — Entry: ${p.entry_price} — Stop: ${p.stop_price} — Shares: ${p.share_size}`);
    }
  }
  lines.push('');
  lines.push('## Closed Today');
  lines.push('- none');
  lines.push('');
  lines.push('## Watchlist Performance Summary');
  lines.push(`- Watchlist size: ${watchlistSummary.watchlist_size}`);
  lines.push(`- Up today: ${watchlistSummary.up_today}`);
  lines.push(`- Down today: ${watchlistSummary.down_today}`);
  lines.push(`- Average move today: ${pct(watchlistSummary.average_move_today)}`);
  lines.push(`- Best performer: ${watchlistSummary.best_performer ? `${watchlistSummary.best_performer.symbol} ${pct(watchlistSummary.best_performer.move)}` : 'n/a'}`);
  lines.push(`- Worst performer: ${watchlistSummary.worst_performer ? `${watchlistSummary.worst_performer.symbol} ${pct(watchlistSummary.worst_performer.move)}` : 'n/a'}`);
  lines.push(`- Near trigger: ${watchlistSummary.near_trigger.length ? watchlistSummary.near_trigger.join(', ') : 'none'}`);
  lines.push(`- Triggered today: ${watchlistSummary.triggered_today.length ? watchlistSummary.triggered_today.join(', ') : 'none'}`);
  lines.push(`- Overall tone: ${watchlistSummary.overall_tone ?? 'n/a'}`);
  if (watchlistSummary.stale_symbols) lines.push(`- Stale symbols: ${watchlistSummary.stale_symbols.length ? watchlistSummary.stale_symbols.join(', ') : 'none'}`);
  if (watchlistSummary.provider_status) lines.push(`- Provider status: ${watchlistSummary.provider_status.overall_status}`);
  lines.push('');
  lines.push('## Pending Proposals');
  if ((state.pendingProposals.proposals ?? []).length === 0) {
    lines.push('- none');
  } else {
    for (const p of state.pendingProposals.proposals) {
      lines.push(`- ${p.action_type.toUpperCase()} ${p.symbol} — status: ${p.approval_status}`);
    }
  }
  lines.push('');
  lines.push('## Notes and Flags');
  lines.push('- paper only');
  lines.push('- approval required for buys and sells');
  if (watchlistSummary.provider_status?.overall_status === 'stale') {
    lines.push('- data blocked: provider returned stale market history');
  }
  if (watchlistSummary.provider_status?.overall_status === 'permission_denied') {
    lines.push('- data blocked: provider quote permission missing');
  }
  if (watchlistSummary.provider_status?.overall_status === 'partial') {
    lines.push('- caution: provider returned mixed freshness/availability across symbols');
  }
  return lines.join('\n');
}
