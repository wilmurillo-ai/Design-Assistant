import log from '@apify/log';
import { fetchJSON, normalizeProduct } from './utils.js';

/**
 * Check current prices for specific product URLs.
 * Input: { productUrls: ["https://allbirds.com/products/mens-tree-runners", ...] }
 */
export async function priceCheck(input) {
    const { productUrls } = input;

    if (!productUrls || !Array.isArray(productUrls) || productUrls.length === 0) {
        throw new Error('productUrls array is required for price_check mode');
    }

    log.info(`Checking prices for ${productUrls.length} product URL(s)...`);

    const products = [];
    for (const url of productUrls) {
        log.info(`Fetching: ${url}`);
        const product = await fetchProductByUrl(url);
        products.push(product);
    }

    const validProducts = products.filter(p => !p.error);
    const prices = validProducts.map(p => p.currentPrice).filter(p => p !== null);
    const avgPrice = prices.length > 0
        ? Math.round((prices.reduce((a, b) => a + b, 0) / prices.length) * 100) / 100
        : null;

    const summary = buildPriceCheckSummary(products.length, validProducts.length, avgPrice);

    return {
        totalRecords: products.length,
        products,
        summary,
    };
}

async function fetchProductByUrl(url) {
    try {
        const parsed = new URL(url);
        const storeUrl = `${parsed.protocol}//${parsed.host}`;
        const pathParts = parsed.pathname.split('/');
        const productsIdx = pathParts.indexOf('products');

        if (productsIdx === -1 || productsIdx + 1 >= pathParts.length) {
            return { url, error: 'Could not extract product handle from URL' };
        }

        const handle = pathParts[productsIdx + 1];
        const apiUrl = `${storeUrl}/products/${handle}.json`;

        const data = await fetchJSON(apiUrl);
        if (!data?.product) {
            return { url, error: 'Product not found or store is not Shopify' };
        }

        const normalized = normalizeProduct(data.product, storeUrl);
        return {
            url,
            title: normalized.title,
            vendor: normalized.vendor,
            productType: normalized.productType,
            currentPrice: normalized.pricing.minPrice,
            maxPrice: normalized.pricing.maxPrice,
            compareAtPrice: normalized.pricing.compareAtPrice,
            onSale: normalized.pricing.onSale,
            inStock: normalized.inStock,
            variantCount: normalized.variantCount,
            availableVariants: normalized.availableVariants,
            firstImage: normalized.firstImage,
            updatedAt: normalized.updatedAt,
        };
    } catch (err) {
        log.warning(`Failed to fetch product at ${url}: ${err.message}`);
        return { url, error: err.message };
    }
}

function buildPriceCheckSummary(total, valid, avgPrice) {
    const parts = [`Checked ${total} product${total !== 1 ? 's' : ''}`];
    if (valid < total) parts.push(`${total - valid} failed`);
    if (avgPrice !== null) parts.push(`Average price: $${avgPrice.toFixed(2)}`);
    return parts.join('. ') + '.';
}
