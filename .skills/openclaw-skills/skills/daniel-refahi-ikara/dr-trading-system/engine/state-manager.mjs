import fs from 'node:fs/promises';
import path from 'node:path';

async function readJson(filePath) {
  const raw = await fs.readFile(filePath, 'utf8');
  return JSON.parse(raw);
}

async function writeJson(filePath, value) {
  await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

export function getJobStatePaths(rootDir, jobId) {
  const base = path.join(rootDir, 'state', jobId);
  return {
    base,
    jobState: path.join(base, 'job_state.json'),
    pendingProposals: path.join(base, 'pending_proposals.json'),
    openPositions: path.join(base, 'open_positions.json'),
    closedPositions: path.join(base, 'closed_positions.csv'),
    performanceSummary: path.join(base, 'performance_summary.json'),
    watchlistSummary: path.join(base, 'watchlist_summary.json'),
    approvalsLog: path.join(base, 'approvals.log.jsonl')
  };
}

export async function loadJobState(rootDir, jobId) {
  const paths = getJobStatePaths(rootDir, jobId);
  return {
    paths,
    jobState: await readJson(paths.jobState),
    pendingProposals: await readJson(paths.pendingProposals),
    openPositions: await readJson(paths.openPositions),
    performanceSummary: await readJson(paths.performanceSummary),
    watchlistSummary: await readJson(paths.watchlistSummary)
  };
}

export async function saveJobState(rootDir, jobId, state) {
  const paths = getJobStatePaths(rootDir, jobId);
  await writeJson(paths.jobState, state.jobState);
  await writeJson(paths.pendingProposals, state.pendingProposals);
  await writeJson(paths.openPositions, state.openPositions);
  await writeJson(paths.performanceSummary, state.performanceSummary);
  await writeJson(paths.watchlistSummary, state.watchlistSummary);
}

export async function appendApprovalLog(rootDir, jobId, event) {
  const { approvalsLog } = getJobStatePaths(rootDir, jobId);
  await fs.appendFile(approvalsLog, `${JSON.stringify(event)}\n`, 'utf8');
}
