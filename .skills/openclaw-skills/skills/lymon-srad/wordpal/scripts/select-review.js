#!/usr/bin/env node

const { ensureNoPositionals, parseCli, parseDate, resolvePath } = require('./lib/cli/helpers');
const { writeHelp, writeJsonError, writeJsonSuccess } = require('./lib/output');
const { formatLocalDate, isValidDate } = require('./lib/core/fsrs-scheduler');
const { createRepository, DEFAULT_WORKSPACE_DIR } = require('./lib/core/vocab-db');
const { buildSelectReview } = require('./lib/services/select-review');

const HELP_TEXT = `
WordPal 复习筛选脚本

用法:
  node select-review.js [--today YYYY-MM-DD] [--diagnostics] [--workspace-dir <path>]

输出:
  成功时输出 { meta, data } JSON，其中 data.items 为到期词列表。
`;

function parseInput(argv = process.argv.slice(2)) {
  const { values, positionals } = parseCli({
    argv,
    options: {
      help: { type: 'boolean', short: 'h' },
      today: { type: 'string' },
      diagnostics: { type: 'boolean' },
      diag: { type: 'boolean' },
      'workspace-dir': { type: 'string' },
    },
  });
  ensureNoPositionals(positionals);

  if (values.help) {
    return { help: true };
  }

  return {
    help: false,
    today: values.today ? parseDate(values.today, '--today', isValidDate) : formatLocalDate(),
    diagnostics: !!(values.diagnostics || values.diag),
    workspaceDir: values['workspace-dir']
      ? resolvePath(values['workspace-dir'], '--workspace-dir')
      : DEFAULT_WORKSPACE_DIR,
  };
}

function main() {
  try {
    const input = parseInput();
    if (input.help) {
      writeHelp(HELP_TEXT);
      return;
    }

    const repo = createRepository(input.workspaceDir);
    try {
      const data = buildSelectReview({
        repo,
        today: input.today,
        diagnostics: input.diagnostics,
      });
      writeJsonSuccess({
        script: 'select-review',
        meta: {
          today: input.today,
          diagnostics: input.diagnostics,
          workspace_dir: input.workspaceDir,
        },
        data,
      });
    } finally {
      repo.close();
    }
  } catch (error) {
    writeJsonError(error);
  }
}

main();
