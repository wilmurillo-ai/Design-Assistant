#!/usr/bin/env node

const { AppError, EXIT_CODES } = require('./lib/errors');
const {
  ensureNoPositionals,
  parseCli,
  parseDate,
  parseEnum,
  parseInteger,
  resolvePath,
} = require('./lib/cli/helpers');
const { writeHelp, writeJsonError, writeJsonSuccess } = require('./lib/output');
const { formatLocalDate, isValidDate } = require('./lib/core/fsrs-scheduler');
const { ensureSafeWord, normalizeWord } = require('./lib/core/input-guard');
const { DEFAULT_WORKSPACE_DIR } = require('./lib/core/vocab-db');
const { ALL_QUESTION_TYPES, buildQuestionPlan } = require('./lib/services/question-plan');

const HELP_TEXT = `
WordPal 题型规划脚本

用法:
  node question-plan.js --mode <learn|review> --word <word> --item-type <pending|due> [--status <0-7>] [--difficulty-level <I|II|III|IV|V>] [--last-type <N1..N7|R1..R11>] [--today YYYY-MM-DD] [--compact] [--workspace-dir <path>]

输出:
  默认输出完整题型规划 JSON；使用 --compact 时仅输出热路径需要的最小字段。
`;

function parseInput(argv = process.argv.slice(2)) {
  const { values, positionals } = parseCli({
    argv,
    options: {
      help: { type: 'boolean', short: 'h' },
      mode: { type: 'string' },
      word: { type: 'string' },
      'item-type': { type: 'string' },
      status: { type: 'string' },
      'difficulty-level': { type: 'string' },
      'last-type': { type: 'string' },
      today: { type: 'string' },
      compact: { type: 'boolean' },
      'workspace-dir': { type: 'string' },
    },
  });
  ensureNoPositionals(positionals);

  if (values.help) {
    return { help: true };
  }

  const word = normalizeWord(values.word);
  try {
    ensureSafeWord(word);
  } catch (error) {
    throw new AppError('INVALID_WORD', error.message, EXIT_CODES.INVALID_INPUT);
  }

  return {
    help: false,
    mode: parseEnum(values.mode, '--mode', ['learn', 'review']),
    word,
    itemType: parseEnum(values['item-type'], '--item-type', ['pending', 'due']),
    status: typeof values.status === 'string'
      ? parseInteger(values.status, '--status', 0, 7)
      : null,
    difficultyLevel: typeof values['difficulty-level'] === 'string'
      ? parseEnum(values['difficulty-level'], '--difficulty-level', ['I', 'II', 'III', 'IV', 'V'])
      : null,
    lastType: typeof values['last-type'] === 'string'
      ? parseEnum(values['last-type'], '--last-type', ALL_QUESTION_TYPES)
      : null,
    today: values.today ? parseDate(values.today, '--today', isValidDate) : formatLocalDate(),
    compact: !!values.compact,
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

    const data = buildQuestionPlan(input);
    writeJsonSuccess({
      script: 'question-plan',
      meta: {
        mode: input.mode,
        item_type: input.itemType,
        today: input.today,
        compact: input.compact,
        workspace_dir: input.workspaceDir,
      },
      data,
    });
  } catch (error) {
    writeJsonError(error);
  }
}

main();
