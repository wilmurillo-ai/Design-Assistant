import log from '@apify/log';
import { normalizeStoreUrl, isShopifyStore, fetchAllShopifyProducts, normalizeProduct } from './utils.js';

/**
 * Compare prices across multiple Shopify stores for similar products.
 * Input: { stores: ["allbirds.com", "greats.com"], maxProductsPerStore: 100 }
 */
export async function priceComparison(input) {
    const { stores, maxProductsPerStore = 100 } = input;

    if (!stores || !Array.isArray(stores) || stores.length === 0) {
        throw new Error('stores array is required for price_comparison mode');
    }

    log.info(`Comparing prices across ${stores.length} store(s)...`);

    const storeResults = [];
    for (const store of stores) {
        log.info(`Fetching products from: ${store}`);
        const storeData = await fetchStoreData(store, maxProductsPerStore);
        storeResults.push(storeData);
    }

    const validStores = storeResults.filter(s => s.isShopify && s.products.length > 0);
    const categoryComparison = buildCategoryComparison(validStores);
    const cheapestBy = findCheapestByCategory(categoryComparison);
    const summary = buildComparisonSummary(storeResults);

    return {
        totalRecords: storeResults.length,
        stores: storeResults.map(s => ({
            name: s.name,
            isShopify: s.isShopify,
            productCount: s.products.length,
            avgPrice: s.avgPrice,
            error: s.error || null,
        })),
        categoryComparison,
        cheapestBy,
        summary,
    };
}

async function fetchStoreData(storeInput, maxProducts) {
    const normalizedUrl = normalizeStoreUrl(storeInput);
    const name = new URL(normalizedUrl).host;

    const shopify = await isShopifyStore(normalizedUrl);
    if (!shopify) {
        return { name, isShopify: false, products: [], avgPrice: null, error: 'Not a Shopify store' };
    }

    const rawProducts = await fetchAllShopifyProducts(normalizedUrl, maxProducts);
    const products = rawProducts.map(p => normalizeProduct(p, normalizedUrl));

    const prices = products
        .map(p => p.pricing.minPrice)
        .filter(p => p !== null && !isNaN(p));
    const avgPrice = prices.length > 0
        ? Math.round((prices.reduce((a, b) => a + b, 0) / prices.length) * 100) / 100
        : null;

    return { name, isShopify: true, products, avgPrice };
}

function buildCategoryComparison(stores) {
    // Collect all product types across stores
    const allTypes = new Set();
    for (const store of stores) {
        for (const product of store.products) {
            const type = product.productType || 'Unknown';
            if (type) allTypes.add(type);
        }
    }

    const comparison = {};
    for (const type of allTypes) {
        comparison[type] = {};
        for (const store of stores) {
            const typeProducts = store.products.filter(p => (p.productType || 'Unknown') === type);
            if (typeProducts.length === 0) continue;

            const prices = typeProducts
                .map(p => p.pricing.minPrice)
                .filter(p => p !== null && !isNaN(p));
            if (prices.length === 0) continue;

            const avgPrice = Math.round((prices.reduce((a, b) => a + b, 0) / prices.length) * 100) / 100;
            comparison[type][store.name] = {
                avgPrice,
                count: typeProducts.length,
            };
        }
        // Remove empty categories
        if (Object.keys(comparison[type]).length === 0) {
            delete comparison[type];
        }
    }
    return comparison;
}

function findCheapestByCategory(categoryComparison) {
    const cheapestBy = {};
    for (const [category, storeData] of Object.entries(categoryComparison)) {
        let cheapestStore = null;
        let lowestPrice = Infinity;
        for (const [storeName, data] of Object.entries(storeData)) {
            if (data.avgPrice < lowestPrice) {
                lowestPrice = data.avgPrice;
                cheapestStore = storeName;
            }
        }
        if (cheapestStore) cheapestBy[category] = cheapestStore;
    }
    return cheapestBy;
}

function buildComparisonSummary(storeResults) {
    const valid = storeResults.filter(s => s.isShopify);
    if (valid.length === 0) {
        return `Compared ${storeResults.length} store(s). No Shopify stores found.`;
    }
    const storeSummaries = valid.map(s => `${s.name} avg $${s.avgPrice?.toFixed(2) ?? 'N/A'}`);
    return `Compared ${storeResults.length} store(s). ${storeSummaries.join(', ')}.`;
}
