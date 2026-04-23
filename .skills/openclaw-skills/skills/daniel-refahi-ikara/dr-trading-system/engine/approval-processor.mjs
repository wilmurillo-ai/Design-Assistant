import fs from 'node:fs/promises';
import { appendApprovalLog, getJobStatePaths } from './state-manager.mjs';
import { executePaperBuy, executePaperSell } from './paper-execution-engine.mjs';

function toCsvRow(record) {
  return [
    record.position_id,
    record.symbol,
    record.entry_time,
    record.exit_time,
    record.entry_price,
    record.exit_price,
    record.share_size,
    record.realized_pnl,
    record.realized_return,
    record.exit_reason,
    record.approval_trail
  ].join(',');
}

export async function applyApproval({ rootDir, jobId, proposalId, decision, state }) {
  const proposal = state.pendingProposals.proposals.find((p) => p.proposal_id === proposalId);
  if (!proposal) throw new Error(`Proposal not found: ${proposalId}`);
  if (proposal.approval_status !== 'pending') throw new Error(`Proposal is not pending: ${proposalId}`);

  proposal.approval_status = decision;
  await appendApprovalLog(rootDir, jobId, {
    proposal_id: proposalId,
    decision,
    at: new Date().toISOString()
  });

  if (decision === 'rejected') return { proposal, executed: false };

  if (proposal.action_type === 'buy') {
    const position = executePaperBuy({ proposal, state });
    return { proposal, executed: true, position };
  }

  if (proposal.action_type === 'sell') {
    const closed = executePaperSell({ proposal, state });
    if (closed) {
      const { closedPositions } = getJobStatePaths(rootDir, jobId);
      await fs.appendFile(closedPositions, `${toCsvRow(closed)}\n`, 'utf8');
    }
    return { proposal, executed: true, closed };
  }

  throw new Error(`Unsupported action_type: ${proposal.action_type}`);
}
