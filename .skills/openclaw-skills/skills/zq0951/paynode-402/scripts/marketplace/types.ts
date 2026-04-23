export interface SellerInfo {
  name?: string;
  wallet_address?: string;
}

export interface CatalogApiItem {
  id: string;
  name: string;
  description?: string;
  tags?: string[];
  price_per_call?: string;
  currency?: string;
  network?: string;
  seller?: SellerInfo;
  method?: string;
  payable_url?: string;
  invoke_url?: string;
  input_schema?: Record<string, any>;
  sample_response?: any;
  headers_template?: Record<string, string>;
  [key: string]: any;
}

export interface CatalogListResponse {
  items: CatalogApiItem[];
  total?: number;
}

export interface InvokePreparation {
  api_id: string;
  invoke_url: string;
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  network?: string;
  [key: string]: any;
}
