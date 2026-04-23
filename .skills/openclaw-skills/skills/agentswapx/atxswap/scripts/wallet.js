#!/usr/bin/env node
import {
  createClient,
  exportKey,
  getDefaultKeystorePath,
  parseArgs,
  fmt,
  exitError,
  runMain,
  resolveNewPassword,
} from "./_helpers.js";

await runMain(async () => {
  const client = await createClient();
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];

  switch (command) {
    case "create": {
      const existing = client.wallet.list();
      if (existing.length > 0) {
        exitError(`Wallet already exists (${existing[0].address}). Only one wallet is allowed per skill instance.`);
      }
      const password = await resolveNewPassword(args);
      const name = args._[1];
      const result = await client.wallet.create(password, name);
      console.log(JSON.stringify({
        action: "create",
        address: result.address,
        keystoreFile: result.keystoreFile,
        keystoreDir: getDefaultKeystorePath(),
        name: name || null,
      }, null, 2));
      break;
    }

    case "list": {
      const wallets = client.wallet.list();
      if (wallets.length === 0) {
        console.log(JSON.stringify({ wallets: [] }, null, 2));
        break;
      }
      const results = [];
      for (const w of wallets) {
        const entry = { address: w.address, name: w.name || null };
        try {
          const bal = await client.query.getBalance(w.address);
          entry.bnb = fmt(bal.bnb);
          entry.atx = fmt(bal.atx);
          entry.usdt = fmt(bal.usdt);
        } catch {}
        results.push(entry);
      }
      console.log(JSON.stringify({ wallets: results }, null, 2));
      break;
    }

    case "import": {
      const existing = client.wallet.list();
      if (existing.length > 0) {
        exitError(`Wallet already exists (${existing[0].address}). Only one wallet is allowed per skill instance.`);
      }
      const privateKey = args._[1];
      if (!privateKey) exitError("Usage: wallet.js import <privateKey> [name] [--password <pwd>]");
      const password = await resolveNewPassword(args);
      const name = args._[2];
      const result = await client.wallet.importPrivateKey(privateKey, password, name);
      console.log(JSON.stringify({
        action: "import",
        address: result.address,
        keystoreFile: result.keystoreFile,
        keystoreDir: getDefaultKeystorePath(),
      }, null, 2));
      break;
    }

    case "export": {
      const address = args._[1];
      if (!address) exitError("Usage: wallet.js export <address> [--password <pwd>]");
      const pk = await exportKey(client, address, args);
      console.log(pk);
      break;
    }

    case "forget-password": {
      const address = args._[1];
      if (!address) exitError("Usage: wallet.js forget-password <address>");
      await client.wallet.forgetPassword(address);
      console.log(JSON.stringify({ action: "forget-password", address, success: true }, null, 2));
      break;
    }

    case "has-password": {
      const address = args._[1];
      if (!address) exitError("Usage: wallet.js has-password <address>");
      const saved = await client.wallet.hasSavedPassword(address);
      console.log(JSON.stringify({ address, hasSavedPassword: saved }, null, 2));
      break;
    }

    default:
      exitError("Usage: wallet.js <create|list|import|export|forget-password|has-password> [args] [--password <pwd>]");
  }
});
