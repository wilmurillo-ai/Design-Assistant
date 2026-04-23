import { ethers } from '@paynodelabs/sdk-js';
import {
    getPrivateKey,
    resolveNetwork,
    reportError,
    jsonEnvelope,
    withRetry,
    EXIT_CODES,
    BaseCliOptions
} from '../utils.ts';

interface MintOptions extends BaseCliOptions {
    amount?: string;
}

export async function mintAction(options: MintOptions) {
    const isJson = !!options.json;
    const pk = getPrivateKey(isJson);

    try {
        const { provider, usdcAddress, chainId, networkName, isSandbox } = await resolveNetwork(
            options.rpc,
            options.network || 'testnet',
            options.rpcTimeout
        );

        if (!isSandbox) {
            throw new Error(`Minting is only supported on Sepolia. Current ChainID: ${chainId}`);
        }

        const wallet = new ethers.Wallet(pk, provider);
        const mintAmountStr = options.amount || '1000';

        // Gas check
        const balance = await provider.getBalance(wallet.address);
        if (balance === 0n) {
            reportError(
                `Gas balance is 0 ETH on ${networkName}. Please fund \`${wallet.address}\` to continue.\n` +
                `💡 **Faucet**: [console.optimism.io/faucet](https://console.optimism.io/faucet) — 0.01 ETH daily (Recommended)`,
                isJson,
                EXIT_CODES.INSUFFICIENT_FUNDS
            );
        }

        // Progress messages are sent to stderr to avoid polluting stdout 
        // when valid JSON output is expected by the caller (e.g. via --json)
        if (!isJson) {
            console.error(`💰 Connecting to ${networkName}...`);
            console.error(`🔗 Minting ${mintAmountStr} USDC for address: ${wallet.address}`);
        }

        const abi = ['function mint(address to, uint256 amount) external'];
        const usdc = new ethers.Contract(usdcAddress, abi, wallet);

        const amount = ethers.parseUnits(mintAmountStr, 6);

        if (!isJson) console.error('⏳ Sending mint transaction...');
        const tx = await withRetry(
            () => usdc.mint(wallet.address, amount),
            'mint'
        );

        if (!isJson) console.error('⏳ Waiting for confirmation...');
        const receipt: any = await withRetry(
            () => tx.wait(),
            'mintConfirm'
        );

        if (!receipt || receipt.status !== 1) {
            throw new Error('Transaction reverted or failed.');
        }

        if (isJson) {
            console.log(
                jsonEnvelope({
                    status: 'success',
                    txHash: tx.hash,
                    address: wallet.address,
                    amount: mintAmountStr,
                    token: 'MockUSDC',
                    network: networkName
                })
            );
        } else {
            console.log(`\n✅ **Success!**`);
            console.log(`──────────────────────────────────────────────────`);
            console.log(`💰 **Minted**:      ${mintAmountStr} Test USDC`);
            console.log(`🌐 **Network**:     ${networkName}`);
            console.log(`🔗 **Tx Hash**:     \`${tx.hash}\``);
            console.log(`──────────────────────────────────────────────────`);
            console.log(`🚀 **Your wallet (\`${wallet.address}\`) is now funded and ready for testing.**`);
            console.log(``);
        }
    } catch (error: any) {
        reportError(error, isJson, EXIT_CODES.NETWORK_ERROR);
    }
}
