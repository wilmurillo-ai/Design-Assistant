import log from '@apify/log';
import { normalizeStoreUrl, isShopifyStore, fetchAllShopifyProducts, normalizeProduct } from './utils.js';

/**
 * List all products from a Shopify store with pricing analysis.
 * Input: { storeUrl: "allbirds.com", maxProducts: 500 }
 */
export async function storeProducts(input) {
    const { storeUrl, maxProducts = 500 } = input;

    if (!storeUrl) {
        throw new Error('storeUrl is required for store_products mode');
    }

    const normalizedUrl = normalizeStoreUrl(storeUrl);
    log.info(`Checking store: ${normalizedUrl}`);

    const shopify = await isShopifyStore(normalizedUrl);
    if (!shopify) {
        return {
            totalRecords: 0,
            store: storeUrl,
            isShopify: false,
            products: [],
            stats: null,
            summary: `${storeUrl} does not appear to be a Shopify store or is not publicly accessible.`,
        };
    }

    log.info(`Confirmed Shopify store. Fetching up to ${maxProducts} products...`);
    const rawProducts = await fetchAllShopifyProducts(normalizedUrl, maxProducts);
    const products = rawProducts.map(p => normalizeProduct(p, normalizedUrl));

    log.info(`Normalized ${products.length} products. Computing stats...`);
    const stats = computeStoreStats(products);

    const storeName = new URL(normalizedUrl).host;
    const summary = buildStoreSummary(storeName, stats);

    return {
        totalRecords: products.length,
        store: storeUrl,
        isShopify: true,
        products,
        stats,
        summary,
    };
}

function computeStoreStats(products) {
    const allPrices = products
        .map(p => p.pricing.minPrice)
        .filter(p => p !== null && !isNaN(p));

    const inStockProducts = products.filter(p => p.inStock).length;
    const onSaleCount = products.filter(p => p.pricing.onSale).length;

    const avgPrice = allPrices.length > 0
        ? Math.round((allPrices.reduce((a, b) => a + b, 0) / allPrices.length) * 100) / 100
        : null;
    const minPrice = allPrices.length > 0 ? Math.min(...allPrices) : null;
    const maxPrice = allPrices.length > 0 ? Math.max(...allPrices) : null;

    const priceDistribution = {
        under25: allPrices.filter(p => p < 25).length,
        '25to50': allPrices.filter(p => p >= 25 && p < 50).length,
        '50to100': allPrices.filter(p => p >= 50 && p < 100).length,
        '100to200': allPrices.filter(p => p >= 100 && p < 200).length,
        over200: allPrices.filter(p => p >= 200).length,
    };

    const productTypes = {};
    for (const p of products) {
        const type = p.productType || 'Unknown';
        productTypes[type] = (productTypes[type] || 0) + 1;
    }

    const topVendors = {};
    for (const p of products) {
        const vendor = p.vendor || 'Unknown';
        topVendors[vendor] = (topVendors[vendor] || 0) + 1;
    }

    return {
        totalProducts: products.length,
        inStockProducts,
        avgPrice,
        minPrice,
        maxPrice,
        priceDistribution,
        onSaleCount,
        productTypes,
        topVendors,
    };
}

function buildStoreSummary(storeName, stats) {
    const parts = [
        `${storeName}: ${stats.totalProducts} products`,
        stats.avgPrice !== null ? `avg price $${stats.avgPrice.toFixed(2)}` : null,
        `${stats.inStockProducts} in stock`,
        `${stats.onSaleCount} on sale`,
        stats.minPrice !== null && stats.maxPrice !== null
            ? `Range: $${stats.minPrice.toFixed(2)}-$${stats.maxPrice.toFixed(2)}`
            : null,
    ].filter(Boolean);
    return parts.join('. ') + '.';
}
