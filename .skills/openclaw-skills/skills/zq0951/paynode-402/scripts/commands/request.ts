import { PayNodeAgentClient, RequestOptions, ethers } from '@paynodelabs/sdk-js';
import { join, parse } from 'path';
import { tmpdir } from 'os';
import fs from 'fs';
import { spawn } from 'child_process';
import {
    getPrivateKey,
    resolveNetwork,
    requireMainnetConfirmation,
    reportError,
    jsonEnvelope,
    withRetry,
    generateTaskId,
    isInlineContent,
    cleanupOldTasks,
    DEFAULT_TASK_DIR,
    DEFAULT_MAX_AGE_SECONDS,
    EXIT_CODES,
    SKILL_VERSION,
    GLOBAL_CONFIG,
    BaseCliOptions,
    maskAddress
} from '../utils.ts';

interface UnifiedRequestOptions extends BaseCliOptions {
    method?: string;
    data?: string;
    header?: string | string[];
    background?: boolean;
    output?: string;
    maxAge?: number;
    taskDir?: string;
    taskId?: string;
}

interface CoreResult {
    result: {
        url: string;
        method: string;
        http_status: number;
        content_type: string;
        body_type: 'json' | 'text' | 'binary';
        network: string;
        data: any;
        duration_ms: number;
        dry_run?: boolean;
        wallet?: string;
        message?: string;
        data_binary?: string;
        data_size?: number;
    };
    binaryBuffer?: Uint8Array;
    contentType: string;
}

// --- Background Launcher ---
function spawnBackground(url: string, args: string[], options: UnifiedRequestOptions) {
    const taskId = options.taskId || generateTaskId(); // Use existing if re-spawning (though unlikely)
    const taskDir = options.taskDir || DEFAULT_TASK_DIR;
    const maxAge = options.maxAge || DEFAULT_MAX_AGE_SECONDS;
    const outputPath = options.output || join(taskDir, `${taskId}.json`);
    const logPath = join(taskDir, `${taskId}.log`);

    fs.mkdirSync(taskDir, { recursive: true });
    cleanupOldTasks(taskDir, maxAge);

    const originalArgs = process.argv.slice(2);
    const flagsToRemove = ['--background', '--json', '--task-id', '--output', '--dry-run', '--max-age', '--task-dir'];
    const childArgs: string[] = [];

    for (let i = 0; i < originalArgs.length; i++) {
        const arg = originalArgs[i];
        if (flagsToRemove.includes(arg)) {
            // If flag takes an argument, skip both flag and value
            if (['--output', '--task-id', '--max-age', '--task-dir'].includes(arg) && i + 1 < originalArgs.length) {
                i++;
            }
            continue;
        }
        childArgs.push(arg);
    }
    childArgs.push('--task-id', taskId, '--output', outputPath);

    // [SECURITY & LOGIC] 
    // This is a self-re-execution for background processing.
    // 1. We spawn the same script (process.argv[1]) with filtered arguments.
    // 2. We add '--task-id' which signals the next execution to use 'executeAndWrite' path.
    // 3. This avoids infinite recursion because the sub-process will NOT have '--background' in its args.
    // 4. Stderr is piped to a .log file to allow debugging of background failures.
    
    const logFd = fs.openSync(logPath, 'a');
    // The child command is pinned to 'process.execPath' (the current runtime) and 'process.argv[1]' (the current script).
    // Arguments are filtered to prevent recursive loops.
    // [SECURITY] Filter environment variables passed to background child process.
    // Minimizes exposure of non-essential credentials.
    const whitelist = [
        'CLIENT_PRIVATE_KEY',
        'CUSTOM_ROUTER_ADDRESS',
        'CUSTOM_USDC_ADDRESS',
        'RPC_URL',
        'ALCHEMY_API_KEY',
        'INFURA_API_KEY',
        'ETHERSCAN_API_KEY',
        'HTTP_PROXY',
        'HTTPS_PROXY',
        'NODE_PATH',
        'NVM_DIR',
        'BUN_INSTALL'
    ];
    // Essential OS-level vars
    const baseEnv = Object.fromEntries(
        Object.entries({
            PATH: process.env.PATH,
            HOME: process.env.HOME,
            TMPDIR: process.env.TMPDIR,
            USER: process.env.USER,
            SHELL: process.env.SHELL
        }).filter(([, v]) => v !== undefined)
    ) as Record<string, string>;
    const childEnv: Record<string, string | undefined> = { ...baseEnv };
    for (const key of whitelist) {
        if (process.env[key]) childEnv[key] = process.env[key];
    }

    const child = spawn(process.execPath, [process.argv[1], ...childArgs], {
        detached: true,
        stdio: ['ignore', 'ignore', logFd],
        env: childEnv
    });
    child.unref();

    // After unref. the parent no longer needs logFd. The child has its own copy.
    fs.closeSync(logFd);

    const pendingInfo = {
        status: 'pending',
        task_id: taskId,
        output_file: outputPath,
        task_dir: taskDir,
        max_age_seconds: maxAge,
        command: `cat ${outputPath}`,
        message: '🕒 x402 background request started. The wallet will automatically handle payments.'
    };

    if (options.json) {
        console.log(jsonEnvelope(pendingInfo));
    } else {
        console.log(`\n🚀 **Background Task Started**`);
        console.log(`- **Task ID**: \`${taskId}\``);
        console.log(`- **Output**: \`${outputPath}\``);
        console.log(`- **Log**:    \`${logPath}\``);
        console.log(`\nUse \`cat ${outputPath}\` to check progress or \`tail -f ${logPath}\` for logs.`);
    }
    process.exit(0);
}

// --- Core x402 Execution ---
async function executeCore(url: string, args: string[], options: UnifiedRequestOptions): Promise<CoreResult> {
    const isJson = !!options.json || !!options.taskId;
    const startTs = Date.now();

    const { rpcUrls, networkName, isSandbox } = await resolveNetwork(options.rpc, options.network, options.rpcTimeout);
    requireMainnetConfirmation(isSandbox, !!options.confirmMainnet, isJson);

    // Handle params (k=v)
    const kvParams: Record<string, string> = {};
    for (const p of args) {
        if (!p.includes('=')) continue;
        const [k, ...v] = p.split('=');
        kvParams[k.trim()] = v.join('=').trim();
    }

    const method = options.method?.toUpperCase() || (options.data || Object.keys(kvParams).length > 0 ? 'POST' : 'GET');

    // Headers parsing
    const headers: Record<string, string> = {};
    if (options.header) {
        const headerArray = Array.isArray(options.header) ? options.header : [options.header];
        for (const h of headerArray) {
            if (!h || !h.includes(':')) continue;
            const [k, ...v] = h.split(':');
            headers[k.trim()] = v.join(':').trim();
        }
    }
    // [P1] Inject network header for Proxy validation
    const paynodeNetwork = isSandbox ? 'testnet' : 'mainnet';
    if (!headers['X-PayNode-Network']) {
        headers['X-PayNode-Network'] = paynodeNetwork;
    }

    // Auto-sniff JSON body for manual data
    if (options.data && !headers['Content-Type'] && !headers['content-type']) {
        try {
            JSON.parse(options.data);
            headers['Content-Type'] = 'application/json';
        } catch { /* ignore */ }
    }

    const requestOptions: RequestOptions = { method, headers };
    let targetUrl = url;

    if (method === 'GET') {
        const urlObj = new URL(url);
        for (const [k, v] of Object.entries(kvParams)) {
            urlObj.searchParams.set(k, v);
        }
        targetUrl = urlObj.toString();
    } else {
        if (options.data) {
            requestOptions.body = options.data;
        } else {
            // [Smart Promotion] For POST/PUT, if no explicit body data is given but 
            // query parameters exist (either in URL or as args), put them into JSON body.
            const urlObj = new URL(url);
            const combinedParams = { ...kvParams };

            // If the user only passed the URL with query params (no extra args)
            if (Object.keys(combinedParams).length === 0 && urlObj.searchParams.size > 0) {
                for (const [k, v] of urlObj.searchParams.entries()) {
                    combinedParams[k] = v;
                }
            }

            if (Object.keys(combinedParams).length > 0) {
                requestOptions.json = combinedParams;
            }
        }
    }

    // Dry-run
    if (options.dryRun) {
        const pkForAddress = GLOBAL_CONFIG.PRIVATE_KEY;
        let walletAddr: string | undefined;
        try {
            if (pkForAddress && isJson) {
                walletAddr = maskAddress((new ethers.Wallet(pkForAddress)).address);
            }
        } catch { /* skip if PK invalid */ }

        return {
            result: {
                url: targetUrl,
                method,
                http_status: 0,
                content_type: 'application/json',
                body_type: 'json',
                network: networkName,
                data: null,
                duration_ms: 0,
                dry_run: true,
                wallet: walletAddr,
                message: 'Dry-run: request prepared but not sent.'
            },
            contentType: 'application/json'
        };
    }

    const pk = getPrivateKey(isJson);

    const client = new PayNodeAgentClient(pk, rpcUrls);
    const response = await withRetry(
        () => client.requestGate(targetUrl, requestOptions),
        'x402:requestGate'
    );

    const contentType = response.headers.get('content-type') || 'application/octet-stream';
    const httpStatus = response.status;
    let resultBody: any;
    let bodyType: 'json' | 'text' | 'binary' = 'text';
    let binaryBuffer: Uint8Array | undefined;

    if (isInlineContent(contentType)) {
        if (contentType.toLowerCase().includes('application/json')) {
            resultBody = await response.json();
            bodyType = 'json';
        } else {
            resultBody = await response.text();
            bodyType = 'text';
        }
    } else {
        const arrayBuf = await response.arrayBuffer();
        binaryBuffer = new Uint8Array(arrayBuf);
        bodyType = 'binary';
        resultBody = null;
    }

    return {
        result: {
            url: targetUrl,
            method,
            http_status: httpStatus,
            content_type: contentType,
            body_type: bodyType,
            network: networkName,
            data: resultBody,
            duration_ms: Date.now() - startTs
        },
        binaryBuffer,
        contentType
    };
}

// --- Persistence ---
async function executeAndWrite(url: string, args: string[], options: UnifiedRequestOptions) {
    const taskId = options.taskId || generateTaskId();
    const taskDir = options.taskDir || DEFAULT_TASK_DIR;
    const outputPath = options.output || join(taskDir, `${taskId}.json`);

    fs.mkdirSync(taskDir, { recursive: true });

    try {
        const { result, binaryBuffer, contentType } = await executeCore(url, args, options);

        if (binaryBuffer) {
            const { dir, name } = parse(outputPath);
            const binaryPath = join(dir, `${name}.bin`);
            fs.writeFileSync(binaryPath, binaryBuffer);
            result.data = `[binary: ${contentType}, ${binaryBuffer.length} bytes → ${binaryPath}]`;
            result.data_binary = binaryPath;
            result.data_size = binaryBuffer.length;
        }

        const finalOutput = {
            version: SKILL_VERSION,
            status: 'completed',
            task_id: taskId,
            ...result,
            completed_at: new Date().toISOString()
        };

        fs.writeFileSync(outputPath, JSON.stringify(finalOutput, null, 2));
    } catch (error: any) {
        const errorResult = {
            version: SKILL_VERSION,
            status: 'failed',
            task_id: taskId,
            error: error.message,
            errorCode: error?.code || 'internal_error',
            completed_at: new Date().toISOString()
        };
        fs.writeFileSync(outputPath, JSON.stringify(errorResult, null, 2));
    }
}

// --- Main Entry ---
export async function requestAction(url: string, args: string[], options: UnifiedRequestOptions) {
    if (options.background) {
        spawnBackground(url, args, options);
        return;
    }

    if (options.taskId) {
        await executeAndWrite(url, args, options);
        return;
    }

    const isJson = !!options.json;

    try {
        if (!isJson && !options.dryRun) {
            console.error(`🌐 x402 Request: ${url}...`);
        }

        const { result, binaryBuffer, contentType } = await executeCore(url, args, options);

        if (binaryBuffer) {
            const binPath = options.output
                ? join(parse(options.output).dir, `${parse(options.output).name}.bin`)
                : join(tmpdir(), `paynode-${Date.now().toString(36)}.bin`);

            fs.writeFileSync(binPath, binaryBuffer);
            result.data = `[binary: ${contentType}, ${binaryBuffer.length} bytes → ${binPath}]`;
            result.data_binary = binPath;
            result.data_size = binaryBuffer.length;
        }

        if (isJson) {
            console.log(jsonEnvelope({ status: 'success', ...result }));
        } else {
            if (result.dry_run) {
                console.log('🧪 DRY RUN PREPARED:');
                console.log(JSON.stringify(result, null, 2));
            } else {
                if (typeof result.data === 'object') {
                    console.log(JSON.stringify(result.data, null, 2));
                } else {
                    console.log(result.data);
                }
            }
        }
    } catch (error: any) {
        reportError(error, isJson, EXIT_CODES.NETWORK_ERROR);
    }
}

