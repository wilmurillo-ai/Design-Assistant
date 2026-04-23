#!/usr/bin/env node
import { createClient, loadWallet, parseArgs, exitError, runMain } from "./_helpers.js";
import { parseEther } from "atxswap-sdk";

await runMain(async () => {
  const client = await createClient();
  const args = parseArgs(process.argv.slice(2));
  const command = args._[0];

  if (!command) {
    exitError("Usage: liquidity.js <add|remove|collect|burn> [args] [--from address] [--password <pwd>]");
  }

  const fromAddress = args.from || client.wallet.list()[0]?.address;
  if (!fromAddress) exitError("No wallet found. Create one first.");

  const wallet = await loadWallet(client, fromAddress, args);

  switch (command) {
    case "add": {
      const atxAmount = args._[1];
      const usdtAmount = args._[2];
      if (!atxAmount || !usdtAmount) {
        exitError("Usage: liquidity.js add <atxAmount> <usdtAmount> [--from address]");
      }
      const result = await client.liquidity.addLiquidity(
        wallet,
        parseEther(atxAmount),
        parseEther(usdtAmount),
        { fullRange: true },
      );
      console.log(JSON.stringify({ action: "add liquidity", txHash: result.txHash }, null, 2));
      break;
    }

    case "remove": {
      const tokenId = args._[1];
      const percent = args._[2];
      if (!tokenId || !percent) {
        exitError("Usage: liquidity.js remove <tokenId> <percent> [--from address]");
      }
      const result = await client.liquidity.removeLiquidity(wallet, BigInt(tokenId), parseInt(percent));
      console.log(JSON.stringify({ action: "remove liquidity", txHash: result.txHash }, null, 2));
      break;
    }

    case "collect": {
      const tokenId = args._[1];
      if (!tokenId) exitError("Usage: liquidity.js collect <tokenId> [--from address]");
      const result = await client.liquidity.collectFees(wallet, BigInt(tokenId));
      console.log(JSON.stringify({ action: "collect fees", txHash: result.txHash }, null, 2));
      break;
    }

    case "burn": {
      const tokenId = args._[1];
      if (!tokenId) exitError("Usage: liquidity.js burn <tokenId> [--from address]");
      const result = await client.liquidity.burnPosition(wallet, BigInt(tokenId));
      console.log(JSON.stringify({ action: "burn position", txHash: result.txHash }, null, 2));
      break;
    }

    default:
      exitError("Usage: liquidity.js <add|remove|collect|burn> [args]");
  }
});
