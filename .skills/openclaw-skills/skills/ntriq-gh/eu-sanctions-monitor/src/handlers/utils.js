import log from '@apify/log';

const TIMEOUT = 30000;
const MAX_RETRIES = 3;

export async function fetchWithRetry(url, options = {}) {
    const timeout = options.timeout || TIMEOUT;
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            const headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json,text/html',
                ...(options.headers || {}),
            };
            const response = await fetch(url, { ...options, headers, signal: controller.signal });
            clearTimeout(timeoutId);
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            return response;
        } catch (err) {
            if (attempt === MAX_RETRIES) {
                log.warning(`Failed after ${MAX_RETRIES} attempts: ${url} - ${err.message}`);
                throw err;
            }
            const delay = Math.pow(2, attempt) * 1000;
            log.debug(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
            await new Promise(r => setTimeout(r, delay));
        }
    }
}

export async function fetchJSON(url, options = {}) {
    try {
        const response = await fetchWithRetry(url, options);
        return await response.json();
    } catch (err) {
        log.warning(`fetchJSON failed: ${url} - ${err.message}`);
        return null;
    }
}

/**
 * Normalize a Shopify store URL to its base domain.
 * Handles various input formats: "store.myshopify.com", "https://store.com", etc.
 */
export function normalizeStoreUrl(input) {
    let url = input.trim();
    if (!url.startsWith('http')) url = `https://${url}`;
    try {
        const parsed = new URL(url);
        return `${parsed.protocol}//${parsed.host}`;
    } catch {
        return `https://${input.replace(/\/+$/, '')}`;
    }
}

/**
 * Check if a site is a Shopify store by checking for Shopify indicators.
 */
export async function isShopifyStore(storeUrl) {
    try {
        const data = await fetchJSON(`${storeUrl}/products.json?limit=1`);
        return data && Array.isArray(data.products);
    } catch {
        return false;
    }
}

/**
 * Fetch all products from a Shopify store using products.json pagination.
 * Shopify returns max 250 products per page.
 */
export async function fetchAllShopifyProducts(storeUrl, maxProducts = 1000) {
    const products = [];
    let page = 1;
    const limit = 250;

    while (products.length < maxProducts) {
        const url = `${storeUrl}/products.json?limit=${limit}&page=${page}`;
        const data = await fetchJSON(url);

        if (!data?.products || data.products.length === 0) break;

        products.push(...data.products);
        log.info(`Fetched page ${page}: ${data.products.length} products (total: ${products.length})`);

        if (data.products.length < limit) break;
        page++;

        // Polite delay between pages
        await new Promise(r => setTimeout(r, 1000));
    }

    return products.slice(0, maxProducts);
}

/**
 * Extract normalized product data from a Shopify product object.
 */
export function normalizeProduct(product, storeUrl) {
    const variants = product.variants || [];
    const prices = variants.map(v => parseFloat(v.price)).filter(p => !isNaN(p));
    const comparePrices = variants.map(v => parseFloat(v.compare_at_price)).filter(p => !isNaN(p));

    return {
        id: product.id,
        title: product.title,
        vendor: product.vendor || '',
        productType: product.product_type || '',
        tags: product.tags || [],
        url: `${storeUrl}/products/${product.handle}`,
        createdAt: product.created_at,
        updatedAt: product.updated_at,
        publishedAt: product.published_at,
        pricing: {
            minPrice: prices.length > 0 ? Math.min(...prices) : null,
            maxPrice: prices.length > 0 ? Math.max(...prices) : null,
            avgPrice: prices.length > 0 ? Math.round((prices.reduce((a, b) => a + b, 0) / prices.length) * 100) / 100 : null,
            compareAtPrice: comparePrices.length > 0 ? Math.min(...comparePrices) : null,
            onSale: comparePrices.length > 0 && prices.length > 0 && prices[0] < comparePrices[0],
            currency: 'USD', // default, may vary
        },
        variantCount: variants.length,
        availableVariants: variants.filter(v => v.available).length,
        inStock: variants.some(v => v.available),
        images: (product.images || []).length,
        firstImage: product.images?.[0]?.src || null,
    };
}
