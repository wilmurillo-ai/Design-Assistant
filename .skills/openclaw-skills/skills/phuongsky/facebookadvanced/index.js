#!/usr/bin/env node
/**
 * Facebook Page Posting CLI
 * Usage: openclaw-facebook-posting <command> [args]
 */

const path = require('path');

const commands = {
  'fb-post-setup': './commands/setup.js',
  'fb-post': './commands/post.js',
  'fb-post-image': './commands/post-image.js',
  'fb-post-schedule': './commands/post-schedule.js',
  'fb-post-schedule-list': './commands/post-schedule-list.js',
  'fb-post-schedule-delete': './commands/post-schedule-delete.js',
  'fb-post-delete': './commands/delete-post.js',
  'fb-post-hide': './commands/hide-post.js',
  'fb-post-test': './commands/post-test.js',
  'fb-config-show': './commands/config-show.js',
  '--help': './commands/help.js',
  '-h': './commands/help.js',
  'help': './commands/help.js'
};

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command) {
    require('./commands/help.js')();
    process.exit(0);
  }

  const commandPath = commands[command];
  if (!commandPath) {
    console.error(`❌ Unknown command: ${command}`);
    console.error('\n📝 Run "openclaw-facebook-posting --help" for available commands.');
    process.exit(1);
  }

  try {
    const commandModule = require(path.resolve(__dirname, commandPath));
    await commandModule(...args.slice(1));
  } catch (error) {
    console.error('❌ Error executing command:', error.message);
    process.exit(1);
  }
}

main();
