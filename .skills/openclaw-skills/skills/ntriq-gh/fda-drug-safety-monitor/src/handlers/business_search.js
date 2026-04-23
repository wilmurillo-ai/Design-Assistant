import log from '@apify/log';
import { BASE_URL, fetchHTML, extractNextData, extractJsonLd } from './utils.js';

/**
 * Normalize a raw business entry from __NEXT_DATA__ search results.
 */
function normalizeBusiness(raw) {
    return {
        name: raw.displayName || raw.name || null,
        domain: raw.websiteUrl || raw.identifyingName || raw.domain || null,
        trustScore: raw.trustScore || raw.ratingValue || null,
        totalReviews: raw.numberOfReviews || raw.reviewCount || null,
        category: raw.categoryGroup?.displayName || raw.mainCategory?.displayName || raw.category || null,
        url: raw.identifyingName
            ? `${BASE_URL}/review/${raw.identifyingName}`
            : raw.profileUrl || null,
        claimed: raw.claimed ?? null,
    };
}

/**
 * Extract businesses from __NEXT_DATA__ search page props.
 */
function parseSearchFromNextData(nextData) {
    try {
        const pageProps = nextData?.props?.pageProps;
        if (!pageProps) return [];

        const businessUnits =
            pageProps.businesses ||
            pageProps.businessUnits ||
            pageProps.searchResults ||
            pageProps.initialState?.search?.businessUnits;

        if (Array.isArray(businessUnits)) {
            return businessUnits.map(normalizeBusiness);
        }
    } catch { /* fall through */ }
    return [];
}

/**
 * Regex fallback: extract business listings from HTML.
 */
function parseSearchFromHtml(html) {
    const businesses = [];

    // Match links to /review/ paths as business entries
    const linkRegex = /href="\/review\/([^"?#]+)"[^>]*>([^<]+)</g;
    const seen = new Set();
    let m;
    while ((m = linkRegex.exec(html)) !== null) {
        const domain = m[1].trim();
        const name = m[2].trim();
        if (domain && name && !seen.has(domain)) {
            seen.add(domain);
            businesses.push({
                name,
                domain,
                trustScore: null,
                totalReviews: null,
                category: null,
                url: `${BASE_URL}/review/${domain}`,
                claimed: null,
            });
        }
    }
    return businesses;
}

/**
 * Search for businesses on Trustpilot.
 *
 * Input:
 *   - searchTerm  {string}  Search query, e.g. "cloud hosting"
 *   - maxResults  {number}  Maximum businesses to return (default 20)
 */
export async function businessSearch(input) {
    const searchTerm = (input.searchTerm || '').trim();
    const maxResults = Math.min(input.maxResults || 20, 100);
    const fetchOpts = input.proxyUrl ? { proxyUrl: input.proxyUrl } : {};

    if (!searchTerm) throw new Error('searchTerm is required (e.g. "cloud hosting")');

    log.info(`Searching Trustpilot for: "${searchTerm}" (max: ${maxResults})`);

    const encodedQuery = encodeURIComponent(searchTerm);
    const url = `${BASE_URL}/search?query=${encodedQuery}`;
    log.debug(`Fetching: ${url}`);

    const html = await fetchHTML(url, fetchOpts);
    let businesses = [];

    const nextData = extractNextData(html);
    if (nextData) {
        businesses = parseSearchFromNextData(nextData);
    }

    if (businesses.length === 0) {
        log.debug('__NEXT_DATA__ yielded no results, trying HTML regex fallback...');
        businesses = parseSearchFromHtml(html);
    }

    // Deduplicate by domain
    const seen = new Set();
    const unique = businesses.filter(b => {
        const key = b.domain || b.name;
        if (!key || seen.has(key)) return false;
        seen.add(key);
        return true;
    });

    const limited = unique.slice(0, maxResults);

    return {
        totalRecords: limited.length,
        businesses: limited,
        summary: `Found ${limited.length} businesses matching '${searchTerm}'.`,
    };
}
