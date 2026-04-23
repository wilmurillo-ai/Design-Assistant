import { jsonEnvelope, reportError, withRetry, EXIT_CODES, GLOBAL_CONFIG } from '../utils.ts';
import type { CatalogApiItem, CatalogListResponse, InvokePreparation } from './types.ts';

export interface MarketplaceClientOptions {
  baseUrl?: string;
  json?: boolean;
}

export class MarketplaceError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code: string = 'unknown_error'
  ) {
    super(message);
    this.name = 'MarketplaceError';
  }
}

export interface ListCatalogOptions {
  network?: string;
  limit?: number;
  tag?: string[];
  seller?: string;
}

export interface PrepareInvokeOptions {
  network?: string;
  payload?: any;
}

function joinUrl(baseUrl: string, path: string): string {
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${normalizedBase}${normalizedPath}`;
}

export interface RawCatalogApiItem {
  id?: string;
  api_id?: string;
  name?: string;
  title?: string;
  api_name?: string;
  description?: string;
  tags?: string[];
  price_per_call?: string | number;
  price?: string | number;
  amount?: string | number;
  currency?: string;
  network?: string;
  seller?: any;
  seller_name?: string;
  wallet_address?: string;
  method?: string;
  http_method?: string;
  payable_url?: string;
  payment_url?: string;
  invoke_url?: string;
  input_schema?: any;
  sample_response?: any;
  headers_template?: any;
}

function normalizeCatalogItem(raw: RawCatalogApiItem): CatalogApiItem {
  return {
    id: raw.id || raw.api_id || '',
    name: raw.name || raw.title || raw.api_name || raw.api_id || 'unnamed',
    description: raw.description,
    tags: Array.isArray(raw.tags) ? raw.tags : [],
    price_per_call: String(raw.price_per_call || raw.price || raw.amount || '0'),
    currency: raw.currency || 'USDC',
    network: raw.network,
    seller: (raw.seller && typeof raw.seller === 'object' && Object.keys(raw.seller).length > 0) ? {
      name: raw.seller.name || raw.seller.seller_name,
      wallet_address: raw.seller.wallet_address || raw.seller.address
    } : {
      name: raw.seller_name,
      wallet_address: raw.wallet_address
    },
    method: raw.method || raw.http_method,
    payable_url: raw.payable_url || raw.payment_url,
    invoke_url: raw.invoke_url,
    input_schema: raw.input_schema,
    sample_response: raw.sample_response,
    headers_template: raw.headers_template
  };
}

export class MarketplaceClient {
  private readonly baseUrl: string;
  private readonly isJson: boolean;

  constructor(options: MarketplaceClientOptions = {}) {
    this.baseUrl = options.baseUrl || GLOBAL_CONFIG.MARKETPLACE_URL;
    this.isJson = !!options.json;
  }

  private async request<T>(path: string, init?: RequestInit): Promise<T> {
    const url = joinUrl(this.baseUrl, path);
    const response = await withRetry(
      () => fetch(url, init),
      `marketplace:${path}`
    );

    if (!response.ok) {
      const text = await response.text();
      let errorMessage = `Marketplace request failed (${response.status}) at ${path}: ${text || 'empty response'}`;
      let errorCode = 'unknown_error';
      try {
        const json = JSON.parse(text);
        if (json.message) errorMessage = json.message;
        errorCode = json.code || json.error || errorCode;
      } catch { /* use defaults if parse fails */ }

      throw new MarketplaceError(errorMessage, response.status, errorCode);
    }

    return await response.json() as T;
  }

  async listCatalog(options: ListCatalogOptions = {}): Promise<CatalogListResponse> {
    const params = new URLSearchParams();
    if (options.network) params.set('network', options.network);
    if (options.limit) params.set('limit', String(options.limit));
    if (options.seller) params.set('seller', options.seller);
    for (const tag of options.tag || []) {
      params.append('tag', tag);
    }

    const query = params.toString();
    const path = `/api/v1/paid-apis${query ? `?${query}` : ''}`;
    const raw = await this.request<any>(path);
    const items = Array.isArray(raw.items)
      ? raw.items.map(normalizeCatalogItem)
      : Array.isArray(raw)
        ? raw.map(normalizeCatalogItem)
        : [];

    return {
      items,
      total: raw.total || items.length
    };
  }

  async getApiDetail(apiId: string, network?: string): Promise<CatalogApiItem> {
    const params = new URLSearchParams();
    if (network) params.set('network', network);
    const query = params.toString();
    const path = `/api/v1/paid-apis/${encodeURIComponent(apiId)}${query ? `?${query}` : ''}`;
    const raw = await this.request<any>(path);
    return normalizeCatalogItem(raw);
  }

  async prepareInvoke(apiId: string, options: PrepareInvokeOptions = {}): Promise<InvokePreparation> {
    try {
      const preparation = await this.request<InvokePreparation>(`/api/v1/paid-apis/${encodeURIComponent(apiId)}/invoke`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          network: options.network,
          payload: options.payload ?? {}
        })
      });

      if (!preparation.invoke_url) {
        throw new Error('Preparation response missing invoke_url');
      }

      return preparation;
    } catch (err: any) {
      console.warn(`[Marketplace] /invoke preparation failed for ${apiId}, falling back to direct proxy. Error: ${err.message}`);
      const detail = await this.getApiDetail(apiId, options.network);
      const invokeUrl = detail.payable_url || detail.invoke_url;
      if (!invokeUrl) {
        throw new Error(`API '${apiId}' is missing payable_url/invoke_url and marketplace did not provide an invoke preparation.`);
      }

      return {
        api_id: detail.id,
        invoke_url: invokeUrl,
        method: detail.method || 'POST',
        headers: detail.headers_template || {},
        body: options.payload ?? {}
      };
    }
  }
}
