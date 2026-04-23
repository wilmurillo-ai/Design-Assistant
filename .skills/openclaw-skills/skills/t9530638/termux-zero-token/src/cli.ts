/**
 * Termux Zero Token CLI
 * 
 * 命令行工具：用於連接手機 Chrome 並管理 AI credentials
 */

import * as readline from "node:readline";
import { importProviderCredentials, listProviders, testCredentials, loadCredentials, PROVIDERS, type ProviderId } from "./index.js";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function prompt(question: string): Promise<string> {
  return new Promise(resolve => rl.question(question, resolve));
}

async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case "list":
      await listCommand();
      break;
    case "import":
      await importCommand(args[1]);
      break;
    case "test":
      await testCommand(args[1]);
      break;
    case "chat":
      await chatCommand(args[1], args.slice(2).join(" "));
      break;
    case "help":
    default:
      showHelp();
  }
  
  rl.close();
}

async function listCommand() {
  console.log("\n📋 Available Providers:\n");
  const providers = listProviders();
  
  for (const p of providers) {
    const info = PROVIDERS[p.provider];
    const status = p.configured ? "✅ Configured" : "❌ Not configured";
    console.log(`  ${p.provider}`);
    console.log(`    Name: ${info.name}`);
    console.log(`    Models: ${info.models.join(", ")}`);
    console.log(`    Status: ${status}`);
    console.log();
  }
}

async function importCommand(provider?: string) {
  if (!provider) {
    console.log("❌ Please specify provider: zero-token import <provider>");
    console.log("   Example: zero-token import deepseek-web");
    return;
  }
  
  if (!Object.keys(PROVIDERS).includes(provider)) {
    console.log(`❌ Unknown provider: ${provider}`);
    console.log(`   Available: ${Object.keys(PROVIDERS).join(", ")}`);
    return;
  }
  
  console.log(`\n📱 Importing credentials for ${provider}...`);
  console.log("Make sure:");
  console.log("  1. ADB port forward is set: adb forward tcp:9222 tcp:9222");
  console.log("  2. Chrome remote debugging is enabled");
  console.log("  3. You are logged into the AI website in Chrome");
  console.log();
  
  try {
    await importProviderCredentials(provider as ProviderId);
    console.log("\n✅ Import complete!");
  } catch (error) {
    console.error("❌ Import failed:", error);
  }
}

async function testCommand(provider?: string) {
  if (!provider) {
    console.log("❌ Please specify provider: zero-token test <provider>");
    return;
  }
  
  const success = await testCredentials(provider as ProviderId);
  if (success) {
    console.log("\n✅ Credentials valid!");
  } else {
    console.log("\n❌ Credentials invalid or missing");
  }
}

async function chatCommand(provider?: string, message?: string) {
  if (!provider || !message) {
    console.log("❌ Usage: zero-token chat <provider> <message>");
    return;
  }
  
  const creds = loadCredentials(provider as ProviderId);
  if (!creds) {
    console.log(`❌ No credentials for ${provider}. Run: zero-token import ${provider}`);
    return;
  }
  
  console.log(`\n🤖 Sending to ${provider}: ${message}`);
  console.log("(Chat functionality coming soon...)");
}

function showHelp() {
  console.log(`
🔧 Zero Token CLI

Usage: zero-token <command> [options]

Commands:
  list              List all available providers
  import <provider> Import credentials from phone Chrome
  test <provider>   Test credentials validity
  chat <provider>  Chat with AI (coming soon)
  help             Show this help

Examples:
  zero-token list
  zero-token import deepseek-web
  zero-token test deepseek-web
  zero-token chat deepseek-web "Hello!"

Setup:
  1. adb forward tcp:9222 tcp:9222  # 在電腦上執行
  2. zero-token import <provider>
  3. zero-token chat <provider> "Hi"
`);
}

main();