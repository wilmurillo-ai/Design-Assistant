#!/usr/bin/env node

const { spawnSync } = require('node:child_process');

const command = process.argv[2];
const args = process.argv.slice(3);

if (!command) {
  console.error(JSON.stringify({ success: false, error: 'Missing command. Use: rewrite or check-quota' }));
  process.exit(1);
}

const run = (cmd, cmdArgs) => {
  const result = spawnSync(cmd, cmdArgs, { stdio: 'inherit' });
  if (result.error) {
    console.error(JSON.stringify({ success: false, error: result.error.message }));
    process.exit(1);
  }
  process.exit(result.status ?? 1);
};

switch (command) {
  case 'rewrite':
    run('npx', ['--yes', 'markdown-ai-rewrite', 'rewrite', ...args]);
    break;
  case 'check-quota':
    console.log(JSON.stringify({
      success: true,
      message: 'check-quota is not provided by markdown-ai-rewriter CLI in this version. Please monitor quota in your provider console.'
    }));
    break;
  default:
    console.error(JSON.stringify({ success: false, error: `Unknown command: ${command}` }));
    process.exit(1);
}
