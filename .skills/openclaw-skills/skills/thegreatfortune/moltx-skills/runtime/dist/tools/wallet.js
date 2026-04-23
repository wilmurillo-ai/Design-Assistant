import { getWalletAddress } from "./config.js";
const get_wallet_info = async () => {
    try {
        const address = getWalletAddress();
        return JSON.stringify({
            address,
            source: "MOLTX_PRIVATE_KEY environment variable",
            configPath: "~/.moltx/config.json",
        });
    }
    catch (error) {
        return JSON.stringify({
            error: error.message,
            hint: "Make sure MOLTX_PRIVATE_KEY is set in your environment",
        });
    }
};
export const walletTools = {
    get_wallet_info,
};
