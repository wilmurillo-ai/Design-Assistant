interface ClientConfig {
    serverUrl: string;
    apiKey: string;
    tlsSkipVerify?: boolean;
}
declare class UnraidClient {
    private configResolver;
    private insecureAgent;
    constructor(configResolver: () => ClientConfig);
    private getConfig;
    get<T>(path: string, query?: Record<string, string>): Promise<T>;
    post<T>(path: string, body?: unknown): Promise<T>;
    patch<T>(path: string, body?: unknown): Promise<T>;
    delete<T>(path: string): Promise<T>;
    private doRequest;
}

type ClientResolver = (serverName?: string) => UnraidClient;
declare function register(api: any): void;

export { type ClientResolver, register as default };
