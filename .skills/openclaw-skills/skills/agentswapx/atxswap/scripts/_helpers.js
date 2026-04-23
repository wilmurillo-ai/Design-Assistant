import { AtxClient } from "atxswap-sdk";
import { homedir } from "node:os";
import { join } from "node:path";
import readline from "node:readline";

const DEFAULT_KEYSTORE_PATH = join(homedir(), ".config", "atxswap", "keystore");

export async function createClient() {
  const client = new AtxClient({
    rpcUrl: process.env.BSC_RPC_URL,
    keystorePath: DEFAULT_KEYSTORE_PATH,
  });
  await client.ready();
  return client;
}

export function getDefaultKeystorePath() {
  return DEFAULT_KEYSTORE_PATH;
}

export function parseArgs(args) {
  const parsed = { _: [] };
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      parsed[key] = args[i + 1] || true;
      i++;
    } else {
      parsed._.push(args[i]);
    }
  }
  return parsed;
}

export function fmt(wei, decimals = 18) {
  const n = Number(wei) / 10 ** decimals;
  if (n === 0) return "0";
  if (n < 0.000001) return n.toExponential(4);
  return n.toLocaleString("en-US", { maximumFractionDigits: 6 });
}

export function exitError(message, code = 1) {
  console.error(JSON.stringify({ error: message }));
  process.exit(code);
}

export function getErrorMessage(error) {
  if (typeof error === "string") return error;
  if (error?.shortMessage) return error.shortMessage;
  if (error?.reason) return error.reason;
  if (error?.message) return error.message.split("\n")[0];
  return "Unknown error";
}

export async function runMain(fn) {
  try {
    await fn();
  } catch (error) {
    exitError(getErrorMessage(error));
  }
}

async function promptHidden(promptText) {
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    return null;
  }

  return await new Promise((resolve, reject) => {
    let value = "";
    const wasRaw = process.stdin.isRaw;

    readline.emitKeypressEvents(process.stdin);
    process.stdin.setRawMode?.(true);
    process.stdin.resume();
    process.stdout.write(promptText);

    const onKeypress = (char, key) => {
      if (key?.ctrl && key.name === "c") {
        cleanup();
        process.stdout.write("\n");
        reject(new Error("Password input cancelled"));
        return;
      }

      if (key?.name === "return" || key?.name === "enter") {
        cleanup();
        process.stdout.write("\n");
        resolve(value);
        return;
      }

      if (key?.name === "backspace") {
        value = value.slice(0, -1);
        return;
      }

      if (char) {
        value += char;
      }
    };

    const cleanup = () => {
      process.stdin.off("keypress", onKeypress);
      process.stdin.setRawMode?.(Boolean(wasRaw));
      process.stdin.pause();
    };

    process.stdin.on("keypress", onKeypress);
  });
}

export async function resolvePassword(args, promptText = "Enter wallet password: ") {
  if (args.password) return args.password;

  const ttyPassword = await promptHidden(promptText);
  if (ttyPassword) return ttyPassword;

  exitError("Password required: use --password <pwd> or run in an interactive terminal");
}

export async function resolveNewPassword(args) {
  if (args.password) return args.password;

  if (process.stdin.isTTY && process.stdout.isTTY) {
    while (true) {
      const password = await promptHidden("Create wallet password: ");
      if (!password) exitError("Password cannot be empty");
      const confirm = await promptHidden("Confirm wallet password: ");
      if (password !== confirm) {
        console.error("Passwords do not match, please try again.");
        continue;
      }
      return password;
    }
  }

  exitError("Password required: use --password <pwd> or run in an interactive terminal");
}

export async function loadWallet(client, address, args) {
  try {
    return await client.wallet.load(address);
  } catch {
    if (args.password) {
      return await client.wallet.load(address, args.password);
    }

    const ttyPassword = await promptHidden(`Password for ${address}: `);
    if (ttyPassword) {
      return await client.wallet.load(address, ttyPassword);
    }

    exitError(`Password required for ${address}: use --password <pwd> or run in an interactive terminal`);
  }
}

export async function exportKey(client, address, args) {
  try {
    return await client.wallet.exportPrivateKey(address);
  } catch {
    if (args.password) {
      return await client.wallet.exportPrivateKey(address, args.password);
    }

    const ttyPassword = await promptHidden(`Password for ${address}: `);
    if (ttyPassword) {
      return await client.wallet.exportPrivateKey(address, ttyPassword);
    }

    exitError(`Password required for ${address}: use --password <pwd> or run in an interactive terminal`);
  }
}
