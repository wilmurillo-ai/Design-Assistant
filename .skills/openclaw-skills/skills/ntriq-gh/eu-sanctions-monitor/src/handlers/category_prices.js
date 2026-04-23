import log from '@apify/log';
import { normalizeStoreUrl, isShopifyStore, fetchJSON, normalizeProduct } from './utils.js';

/**
 * Browse Shopify store products by collection/category.
 * Input: { storeUrl: "allbirds.com", collection: "mens-shoes", maxProducts: 250 }
 */
export async function categoryPrices(input) {
    const { storeUrl, collection, maxProducts = 250 } = input;

    if (!storeUrl) {
        throw new Error('storeUrl is required for category_prices mode');
    }
    if (!collection) {
        throw new Error('collection is required for category_prices mode (e.g. "mens-shoes")');
    }

    const normalizedUrl = normalizeStoreUrl(storeUrl);
    log.info(`Checking store: ${normalizedUrl}`);

    const shopify = await isShopifyStore(normalizedUrl);
    if (!shopify) {
        return {
            totalRecords: 0,
            store: storeUrl,
            collection,
            isShopify: false,
            products: [],
            stats: null,
            summary: `${storeUrl} does not appear to be a Shopify store or is not publicly accessible.`,
        };
    }

    log.info(`Fetching products from collection: ${collection}`);
    const rawProducts = await fetchCollectionProducts(normalizedUrl, collection, maxProducts);

    if (rawProducts === null) {
        return {
            totalRecords: 0,
            store: storeUrl,
            collection,
            isShopify: true,
            products: [],
            stats: null,
            summary: `Collection "${collection}" not found on ${storeUrl}.`,
        };
    }

    const products = rawProducts.map(p => normalizeProduct(p, normalizedUrl));
    log.info(`Fetched ${products.length} products from collection "${collection}"`);

    const stats = computeCategoryStats(products);
    const storeName = new URL(normalizedUrl).host;
    const summary = buildCategorySummary(storeName, collection, stats);

    return {
        totalRecords: products.length,
        store: storeUrl,
        collection,
        isShopify: true,
        products,
        stats,
        summary,
    };
}

async function fetchCollectionProducts(storeUrl, collection, maxProducts) {
    const products = [];
    let page = 1;
    const limit = 250;

    while (products.length < maxProducts) {
        const url = `${storeUrl}/collections/${collection}/products.json?limit=${limit}&page=${page}`;
        const data = await fetchJSON(url);

        if (!data) return null; // collection not found or error
        if (!data.products || data.products.length === 0) break;

        products.push(...data.products);
        log.info(`Fetched page ${page}: ${data.products.length} products from collection (total: ${products.length})`);

        if (data.products.length < limit) break;
        page++;

        // Polite delay between pages
        await new Promise(r => setTimeout(r, 1000));
    }

    return products.slice(0, maxProducts);
}

function computeCategoryStats(products) {
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
        topVendors,
    };
}

function buildCategorySummary(storeName, collection, stats) {
    const parts = [
        `${storeName} / ${collection}: ${stats.totalProducts} products`,
        stats.avgPrice !== null ? `avg price $${stats.avgPrice.toFixed(2)}` : null,
        `${stats.inStockProducts} in stock`,
        `${stats.onSaleCount} on sale`,
        stats.minPrice !== null && stats.maxPrice !== null
            ? `Range: $${stats.minPrice.toFixed(2)}-$${stats.maxPrice.toFixed(2)}`
            : null,
    ].filter(Boolean);
    return parts.join('. ') + '.';
}
