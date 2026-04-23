#!/usr/bin/env node

const { ensureNoPositionals, parseCli, requireString, resolvePath } = require('./lib/cli/helpers');
const { writeHelp, writeJsonError, writeJsonSuccess } = require('./lib/output');
const { createRepository, DEFAULT_WORKSPACE_DIR } = require('./lib/core/vocab-db');
const { validateNewWords } = require('./lib/services/validate-new-words');

const HELP_TEXT = `
WordPal 新词候选校验脚本

用法:
  node validate-new-words.js --words "word1,word2,word3" [--workspace-dir <path>]

输出:
  成功时输出 { meta, data } JSON，其中 data.available / data.rejected 为校验结果。
`;

function parseInput(argv = process.argv.slice(2)) {
  const { values, positionals } = parseCli({
    argv,
    options: {
      help: { type: 'boolean', short: 'h' },
      words: { type: 'string' },
      'workspace-dir': { type: 'string' },
    },
  });
  ensureNoPositionals(positionals);

  if (values.help) {
    return { help: true };
  }

  return {
    help: false,
    wordsRaw: requireString(values.words, '--words'),
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
      const data = validateNewWords({
        repo,
        wordsRaw: input.wordsRaw,
      });
      writeJsonSuccess({
        script: 'validate-new-words',
        meta: {
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
