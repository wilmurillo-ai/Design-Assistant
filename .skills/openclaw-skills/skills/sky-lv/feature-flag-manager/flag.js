// feature-flag-manager engine
const fs = require('fs');
const path = require('path');

const CONFIG_DIR = '.featureflags';
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

function ensureConfig() {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  if (!fs.existsSync(CONFIG_FILE)) {
    fs.writeFileSync(CONFIG_FILE, JSON.stringify({ flags: {} }, null, 2));
  }
  return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

const args = process.argv.slice(2);
const cmd = args[0];

if (cmd === 'create') {
  const name = args[1];
  const config = ensureConfig();
  const flag = { enabled: true, percentage: 100, description: '' };
  
  for (let i = 2; i < args.length; i++) {
    if (args[i].startsWith('--percentage')) {
      flag.percentage = parseInt(args[i].split('=')[1] || args[++i]);
    } else if (args[i].startsWith('--description')) {
      flag.description = args[i].split('=')[1] || args[++i];
    } else if (args[i].startsWith('--variants')) {
      const variants = (args[i].split('=')[1] || args[++i]).split(',');
      flag.variants = variants;
      flag.weights = variants.map(() => Math.floor(100 / variants.length));
    }
  }
  
  config.flags[name] = flag;
  saveConfig(config);
  console.log(`✅ Created flag: ${name}`);
} 
else if (cmd === 'enabled') {
  const name = args[1];
  const config = ensureConfig();
  const flag = config.flags[name];
  console.log(flag ? flag.enabled : false);
}
else if (cmd === 'toggle') {
  const name = args[1];
  const config = ensureConfig();
  if (config.flags[name]) {
    config.flags[name].enabled = !config.flags[name].enabled;
    saveConfig(config);
    console.log(`✅ Toggled ${name}: ${config.flags[name].enabled}`);
  }
}
else if (cmd === 'list') {
  const config = ensureConfig();
  console.log(JSON.stringify(config.flags, null, 2));
}
else {
  console.log('Usage: node flag.js <command> [args]');
  console.log('Commands:');
  console.log('  create <name> [--percentage=N] [--description="..."] [--variants=a,b,c]');
  console.log('  enabled <name>');
  console.log('  toggle <name>');
  console.log('  list');
}
