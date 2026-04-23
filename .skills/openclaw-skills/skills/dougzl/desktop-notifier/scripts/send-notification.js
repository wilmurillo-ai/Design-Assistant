const { spawnSync } = require('node:child_process');
const path = require('node:path');

function getArg(name, fallback = '') {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx !== -1 && idx + 1 < process.argv.length) {
    return process.argv[idx + 1];
  }
  return fallback;
}

function runNpmInstall(skillDir) {
  const result = spawnSync('cmd.exe', ['/d', '/s', '/c', 'npm install'], {
    cwd: skillDir,
    stdio: 'inherit',
    windowsHide: true
  });
  if (result.error) {
    console.error('AUTO_INSTALL_ERROR');
    console.error(result.error.message || String(result.error));
    process.exit(1);
  }
  if (result.status !== 0) {
    console.error('AUTO_INSTALL_ERROR');
    console.error(`npm install exited with code ${result.status}`);
    process.exit(result.status || 1);
  }
}

function loadNotifier(skillDir) {
  try {
    return require('node-notifier');
  } catch (err) {
    const missingModule = err && (err.code === 'MODULE_NOT_FOUND' || String(err.message || err).includes("Cannot find module 'node-notifier'"));
    if (!missingModule) throw err;
    console.log('DEPENDENCY_MISSING: node-notifier');
    console.log('AUTO_INSTALL_START');
    runNpmInstall(skillDir);
    console.log('AUTO_INSTALL_DONE');
    return require('node-notifier');
  }
}

const skillDir = path.resolve(__dirname, '..');
const notifier = loadNotifier(skillDir);

const title = getArg('title', '学习提醒');
const message = getArg('message', '现在开始今天的学习时段。');
const wait = getArg('wait', 'false') === 'true';
const timeout = Number(getArg('timeout', '10'));

notifier.notify(
  {
    title,
    message,
    wait,
    timeout,
    appID: 'OpenClaw Windows Notifier'
  },
  (err, response, metadata) => {
    if (err) {
      console.error('NOTIFY_ERROR');
      console.error(err && err.message ? err.message : String(err));
      process.exit(1);
    }
    console.log('NOTIFY_SENT');
    if (response) console.log(`RESPONSE:${response}`);
    if (metadata) console.log(`METADATA:${JSON.stringify(metadata)}`);
  }
);
