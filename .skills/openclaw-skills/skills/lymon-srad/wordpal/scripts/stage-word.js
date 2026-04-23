#!/usr/bin/env node

const { AppError, EXIT_CODES } = require('./lib/errors');
const { ensureNoPositionals, parseCli, parseEnum, resolvePath } = require('./lib/cli/helpers');
const { writeHelp, writeJsonError, writeJsonSuccess, writeText } = require('./lib/output');
const {
  ensureSafeWord,
  ensureValidOpId,
  normalizeWord,
} = require('./lib/core/input-guard');
const { createRepository, DEFAULT_WORKSPACE_DIR } = require('./lib/core/vocab-db');
const { formatStageText, stageWord } = require('./lib/services/stage-word');

const HELP_TEXT = `
WordPal 新词暂存脚本

用法:
  node stage-word.js --word <word> [--op-id <id>] [--format json|text] [--workspace-dir <path>]

输出:
  默认输出 { meta, data } JSON；若使用 --format text，则输出兼容的文本结果。
`;

function parseInput(argv = process.argv.slice(2)) {
  const { values, positionals } = parseCli({
    argv,
    options: {
      help: { type: 'boolean', short: 'h' },
      word: { type: 'string' },
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

  let opIdArg = null;
  if (typeof values['op-id'] === 'string') {
    opIdArg = values['op-id'].trim();
    try {
      ensureValidOpId(opIdArg);
    } catch (error) {
      throw new AppError('INVALID_OP_ID', error.message, EXIT_CODES.INVALID_INPUT);
    }
  }

  return {
    help: false,
    format: values.format ? parseEnum(values.format, '--format', ['json', 'text']) : 'json',
    word: rawWord,
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
      const data = stageWord({
        repo,
        input,
      });

      if (input.format === 'text') {
        writeText(formatStageText(data));
        return;
      }

      writeJsonSuccess({
        script: 'stage-word',
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
