import fs from 'node:fs/promises';
import path from 'node:path';
import { loadRuntimeConfig } from './config-loader.mjs';
import { loadJobState, saveJobState, getJobStatePaths } from './state-manager.mjs';
import { buildIndicatorMap } from './indicator-engine.mjs';
import { evaluateTrendBreakoutEntry } from './entry-evaluator.mjs';
import { evaluateTrendBreakoutExit } from './exit-evaluator.mjs';
import { calculatePositionSizing } from './position-sizing-engine.mjs';
import { buildBuyProposal, buildSellProposal } from './proposal-builder.mjs';
import { calculatePerformanceSummary } from './performance-calculator.mjs';
import { analyzeWatchlist } from './watchlist-analyzer.mjs';
import { generateStrategyReport } from './report-generator.mjs';
import { fetchMoomooOpenDData } from './providers/moomoo-opend.mjs';
import { providerRowsMap, providerSymbolsMap, isFreshSymbol } from './provider-utils.mjs';

function isoNow() {
  return new Date().toISOString();
}

function currentDateUtc() {
  return new Date().toISOString().slice(0, 10);
}

function daysBetween(dateA, dateB) {
  const a = new Date(`${dateA}T00:00:00Z`);
  const b = new Date(`${dateB}T00:00:00Z`);
  return Math.floor((a - b) / 86400000);
}

function hasPendingProposal(state, symbol, actionType) {
  return (state.pendingProposals.proposals ?? []).some((p) => p.symbol === symbol && p.action_type === actionType && p.approval_status === 'pending');
}

function deriveStopPrice(entryPrice, recentSupport) {
  const pctStop = entryPrice * 0.95;
  if (Number.isFinite(recentSupport) && recentSupport > 0) {
    return recentSupport > pctStop ? recentSupport : pctStop;
  }
  return pctStop;
}

async function readClosedRows(csvPath) {
  try {
    const raw = await fs.readFile(csvPath, 'utf8');
    const lines = raw.split(/\r?\n/).filter(Boolean);
    if (lines.length <= 1) return [];
    const headers = lines[0].split(',');
    return lines.slice(1).map((line) => {
      const cols = line.split(',');
      return Object.fromEntries(headers.map((h, i) => [h, cols[i] ?? '']));
    });
  } catch {
    return [];
  }
}

function indicatorInputFromProviderSymbols(symbolStates) {
  return Object.fromEntries(
    Object.entries(symbolStates).map(([symbol, item]) => [
      symbol,
      {
        ok: item.status !== 'provider_error' && item.status !== 'symbol_invalid' && item.status !== 'permission_denied' && item.status !== 'empty',
        rows: item.bars ?? []
      }
    ])
  );
}

function watchlistInputFromProviderSymbols(symbolStates) {
  return Object.fromEntries(
    Object.entries(symbolStates).map(([symbol, item]) => [
      symbol,
      {
        ok: item.status === 'ok' || item.status === 'stale',
        rows: item.bars ?? []
      }
    ])
  );
}

export async function runJob({ rootDir, jobId, marketDataOverride = null }) {
  const runtimeConfig = await loadRuntimeConfig({ rootDir, jobId });
  const state = await loadJobState(rootDir, jobId);
  state.runtimeConfig = runtimeConfig;

  const asOfDate = currentDateUtc();
  const providerResult = marketDataOverride ?? await fetchMoomooOpenDData({
    market: runtimeConfig.job.market,
    symbols: runtimeConfig.watchlist.symbols,
    lookbackDays: 80,
    asOfDate,
    maxStaleDays: 7
  });

  const symbolStates = providerSymbolsMap(providerResult);
  const marketData = providerRowsMap(providerResult);
  const indicators = buildIndicatorMap(indicatorInputFromProviderSymbols(symbolStates), runtimeConfig.strategy);

  for (const position of [...state.openPositions.positions]) {
    const symbol = position.symbol;
    const rows = marketData[symbol] ?? [];
    const latest = rows.at(-1);
    if (!isFreshSymbol(symbolStates[symbol]) || !latest || daysBetween(asOfDate, latest.date) > 7) continue;
    if (hasPendingProposal(state, symbol, 'sell')) continue;

    const exitEvaluation = evaluateTrendBreakoutExit({
      position,
      rows,
      indicators: indicators[symbol]
    });

    if (exitEvaluation.ok) {
      state.pendingProposals.proposals.push(buildSellProposal({
        job: runtimeConfig.job,
        strategy: runtimeConfig.strategy,
        position,
        signalTime: exitEvaluation.latestDate ?? isoNow(),
        exitReferencePrice: exitEvaluation.referencePrice,
        exitEvaluation
      }));
    }
  }

  const openSymbols = new Set(state.openPositions.positions.map((p) => p.symbol));
  for (const symbol of runtimeConfig.watchlist.symbols) {
    if (openSymbols.has(symbol)) continue;
    if (hasPendingProposal(state, symbol, 'buy')) continue;
    if ((state.openPositions.positions?.length ?? 0) >= Number(runtimeConfig.job.risk.max_open_positions ?? 0)) break;

    const rows = marketData[symbol] ?? [];
    const latest = rows.at(-1);
    if (!isFreshSymbol(symbolStates[symbol]) || !latest || daysBetween(asOfDate, latest.date) > 7) continue;

    const entryEvaluation = evaluateTrendBreakoutEntry({
      symbol,
      rows,
      indicators: indicators[symbol],
      strategy: runtimeConfig.strategy
    });

    if (!entryEvaluation.ok) continue;

    const stopPrice = deriveStopPrice(entryEvaluation.referencePrice, entryEvaluation.indicators?.recentSupport);
    const sizing = calculatePositionSizing({
      entryPrice: entryEvaluation.referencePrice,
      stopPrice,
      risk: runtimeConfig.job.risk
    });

    if (!sizing.ok) continue;

    state.pendingProposals.proposals.push(buildBuyProposal({
      job: runtimeConfig.job,
      strategy: runtimeConfig.strategy,
      symbol,
      signalTime: entryEvaluation.latestDate ?? isoNow(),
      entryReferencePrice: entryEvaluation.referencePrice,
      stopPrice,
      sizing,
      entryEvaluation
    }));
  }

  const { closedPositions } = getJobStatePaths(rootDir, jobId);
  state.closedRows = await readClosedRows(closedPositions);

  const performanceSummary = calculatePerformanceSummary({ state });
  const watchlistSummary = analyzeWatchlist({
    watchlist: runtimeConfig.watchlist,
    marketData: watchlistInputFromProviderSymbols(symbolStates),
    indicators,
    asOfDate,
    maxStaleDays: 7
  });
  watchlistSummary.provider_status = providerResult.provider_summary;

  state.performanceSummary = performanceSummary;
  state.watchlistSummary = { job_id: jobId, ...watchlistSummary };
  state.jobState.last_run_at = isoNow();

  const report = generateStrategyReport({
    runtimeConfig,
    state,
    performanceSummary,
    watchlistSummary
  });

  const reportDir = path.join(rootDir, 'reports', jobId);
  await fs.mkdir(reportDir, { recursive: true });
  const reportPath = path.join(reportDir, `${new Date().toISOString().slice(0, 10)}.md`);
  await fs.writeFile(reportPath, `${report}\n`, 'utf8');
  state.jobState.last_report_at = isoNow();
  state.jobState.last_report_path = reportPath;

  await saveJobState(rootDir, jobId, state);

  return {
    jobId,
    reportPath,
    pendingProposals: state.pendingProposals.proposals.length,
    openPositions: state.openPositions.positions.length,
    providerStatus: providerResult.provider_summary.overall_status
  };
}
