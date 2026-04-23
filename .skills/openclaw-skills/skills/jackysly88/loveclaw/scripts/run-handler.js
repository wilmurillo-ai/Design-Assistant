// Wrapper script that patches setupCronJobs to be a no-op
const fs = require('fs');
const path = require('path');

const HANDLER_PATH = path.join(__dirname, 'cloud-handler.js');

// Read the handler
let code = fs.readFileSync(HANDLER_PATH, 'utf-8');

// Replace setupCronJobs with a no-op
code = code.replace(
  'function setupCronJobs(channel = \'feishu\') {',
  'function setupCronJobs(channel = \'feishu\') { return; // PATCHED - no-op'
);

// Also replace the async call to not await
code = code.replace(
  'setupCronJobs(channel);',
  'try { setupCronJobs(channel); } catch(e) { console.error("Cron setup error:", e.message); }'
);

// Write patched handler
const PATCHED_PATH = path.join(__dirname, 'cloud-handler-patched.js');
fs.writeFileSync(PATCHED_PATH, code);

// Now require and run
const handler = require(PATCHED_PATH);

const userId = process.argv[2] || 'test-user';
const message = process.argv[3] || '启动爱情龙虾技能';
const channel = process.argv[4] || 'feishu';

console.log('Calling handler with:', userId, message, channel);
handler.handleMessage(userId, message, channel).then(r => {
  console.log(JSON.stringify(r));
  process.exit(0);
}).catch(e => {
  console.error('ERR:', e.message);
  process.exit(1);
});

// Safety timeout
setTimeout(() => {
  console.error('TIMEOUT - forcing exit');
  process.exit(2);
}, 8000);
