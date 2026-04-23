#!/usr/bin/env node

const { AppError, EXIT_CODES } = require('./lib/errors');
const {
  ensureNoPositionals,
  parseCli,
  parseDate,
  parseEnum,
  parseInteger,
  requireString,
  resolvePath,
} = require('./lib/cli/helpers');
const { writeHelp, writeJsonError, writeJsonSuccess, writeText } = require('./lib/output');
const { isValidDate } = require('./lib/core/fsrs-scheduler');
const {
  ensureSafeWord,
  ensureValidEvent,
  ensureValidOpId,
  normalizeWord,
} = require('./lib/core/input-guard');
const { createRepository, DEFAULT_WORKSPACE_DIR } = require('./lib/core/vocab-db');
const { formatUpdateText, updateWord } = require('./lib/services/update-word');

const HELP_TEXT = `
WordPal 词汇管理脚本

用法:
  node updater.js --word <word> --event <correct|wrong|remembered_after_hint|skip|unreviewed> --last-reviewed <YYYY-MM-DD> [--first-learned <YYYY-MM-DD>] [--status <0-8>] [--op-id <id>] [--format json|text] [--workspace-dir <path>]

输出:
  默认输出 { meta, data } JSON；脚本会根据 event 自动计算新状态。若使用 --format text，则输出兼容的文本结果。
`;

function parseInput(argv = process.argv.slice(2)) {
  const { values, positionals } = parseCli({
    argv,
    options: {
      help: { type: 'boolean', short: 'h' },
      word: { type: 'string' },
      status: { type: 'string' },
      'first-learned': { type: 'string' },
      'last-reviewed': { type: 'string' },
      event: { type: 'string' },
      'op-id': { type: 'string' },
      format: { type: 'string' },
      'workspace-dir': { type: 'string' },
    },
  });
  ensureNoPositionals(positionals);

  if (values.help) {
    return { help: true };
  }

  const rawWord = normalizeWord(values.word);
  try {
    ensureSafeWord(rawWord);
  } catch (error) {
    throw new AppError('INVALID_WORD', error.message, EXIT_CODES.INVALID_INPUT);
  }

  let eventArg = null;
  try {
    eventArg = requireString(values.event, '--event').toLowerCase();
    ensureValidEvent(eventArg);
  } catch (error) {
    if (error instanceof AppError) {
      throw error;
    }
    throw new AppError('INVALID_EVENT', error.message, EXIT_CODES.INVALID_INPUT);
  }

  let opIdArg = null;
  if (typeof values['op-id'] === 'string') {
    opIdArg = values['op-id'].trim();
    try {
      ensureValidOpId(opIdArg);
    } catch (error) {
      throw new AppError('INVALID_OP_ID', error.message, EXIT_CODES.INVALID_INPUT);
    }
  }

  let firstLearnedArg = null;
  if (typeof values['first-learned'] === 'string') {
    firstLearnedArg = parseDate(values['first-learned'], '--first-learned', isValidDate);
  }

  return {
    help: false,
    format: values.format ? parseEnum(values.format, '--format', ['json', 'text']) : 'json',
    word: rawWord,
    statusArg: typeof values.status === 'string'
      ? parseInteger(values.status, '--status', 0, 8)
      : null,
    firstLearnedArg,
    lastReviewed: parseDate(values['last-reviewed'], '--last-reviewed', isValidDate),
    eventArg,
    opIdArg,
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
      const data = updateWord({
        repo,
        input,
      });

      if (input.format === 'text') {
        writeText(formatUpdateText(data));
        return;
      }

      writeJsonSuccess({
        script: 'updater',
        meta: {
          format: input.format,
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
