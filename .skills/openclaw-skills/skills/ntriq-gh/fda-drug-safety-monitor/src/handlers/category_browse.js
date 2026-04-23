import log from '@apify/log';
import { BASE_URL, fetchHTML, extractNextData, sleep } from './utils.js';

/**
 * Normalize a raw business entry from category page __NEXT_DATA__.
 */
function normalizeCategoryBusiness(raw) {
    return {
        name: raw.displayName || raw.name || null,
        domain: raw.websiteUrl || raw.identifyingName || raw.domain || null,
        trustScore: raw.trustScore || raw.ratingValue || null,
        totalReviews: raw.numberOfReviews || raw.reviewCount || null,
        category: raw.categoryGroup?.displayName || raw.mainCategory?.displayName || null,
        url: raw.identifyingName
            ? `${BASE_URL}/review/${raw.identifyingName}`
            : raw.profileUrl || null,
        claimed: raw.claimed ?? null,
        location: raw.location?.country || raw.country || null,
    };
}

/**
 * Extract business list from category page __NEXT_DATA__.
 */
function parseBusinessesFromNextData(nextData) {
    try {
        const pageProps = nextData?.props?.pageProps;
        if (!pageProps) return [];

        const list =
            pageProps.businesses ||
            pageProps.businessUnits ||
            pageProps.categoryBusinessUnits ||
            pageProps.initialState?.category?.businessUnits;

        if (Array.isArray(list)) {
            return list.map(normalizeCategoryBusiness);
        }
    } catch { /* fall through */ }
    return [];
}

/**
 * Determine total pages for the category from __NEXT_DATA__.
 */
function getTotalPagesFromNextData(nextData) {
    try {
        const pageProps = nextData?.props?.pageProps;
        const pagination =
            pageProps?.pagination ||
            pageProps?.initialState?.category?.pagination;

        if (pagination?.totalPages) return pagination.totalPages;
        if (pagination?.count && pagination?.perPage) {
            return Math.ceil(pagination.count / pagination.perPage);
        }
    } catch { /* fall through */ }
    return null;
}

/**
 * Regex fallback: extract business links from category HTML.
 */
function parseBusinessesFromHtml(html) {
    const businesses = [];
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
                location: null,
            });
        }
    }
    return businesses;
}

/**
 * Browse Trustpilot businesses by category.
 *
 * Input:
 *   - category    {string}  Category slug, e.g. "software_company", "bank", "insurance_agency"
 *   - maxResults  {number}  Maximum businesses to return (default 50)
 *
 * Example category slugs:
 *   bank, insurance_agency, software_company, electronics_technology,
 *   travel_vacation, online_shopping, real_estate, education, health_medical
 */
export async function categoryBrowse(input) {
    const category = (input.category || '').trim();
    const maxResults = Math.min(input.maxResults || 50, 500);
    const fetchOpts = input.proxyUrl ? { proxyUrl: input.proxyUrl } : {};

    if (!category) throw new Error('category is required (e.g. "software_company")');

    log.info(`Browsing category: "${category}" (max: ${maxResults})`);

    const businesses = [];
    let page = 1;
    let totalPages = null;

    while (businesses.length < maxResults) {
        const url = `${BASE_URL}/categories/${category}?page=${page}`;
        log.debug(`Fetching category page ${page}: ${url}`);

        let html;
        try {
            html = await fetchHTML(url, fetchOpts);
        } catch (err) {
            log.warning(`Failed to fetch category page ${page}: ${err.message}`);
            break;
        }

        const nextData = extractNextData(html);
        let pageBusinesses = [];

        if (nextData) {
            pageBusinesses = parseBusinessesFromNextData(nextData);

            if (page === 1 && totalPages === null) {
                totalPages = getTotalPagesFromNextData(nextData);
                log.info(`Total pages estimated: ${totalPages ?? 'unknown'}`);
            }
        }

        if (pageBusinesses.length === 0) {
            log.debug('__NEXT_DATA__ yielded no results, trying HTML regex fallback...');
            pageBusinesses = parseBusinessesFromHtml(html);
        }

        if (pageBusinesses.length === 0) {
            log.info(`No businesses found on page ${page}, stopping.`);
            break;
        }

        for (const b of pageBusinesses) {
            if (businesses.length >= maxResults) break;
            businesses.push(b);
        }

        log.info(`Page ${page}: collected ${pageBusinesses.length} businesses (total so far: ${businesses.length})`);

        if (totalPages !== null && page >= totalPages) break;
        if (businesses.length >= maxResults) break;

        page++;
        await sleep(1000 + Math.random() * 1000);
    }

    // Sort by trust score descending (nulls last)
    businesses.sort((a, b) => {
        if (a.trustScore == null && b.trustScore == null) return 0;
        if (a.trustScore == null) return 1;
        if (b.trustScore == null) return -1;
        return b.trustScore - a.trustScore;
    });

    return {
        totalRecords: businesses.length,
        category,
        businesses,
        summary: `Found ${businesses.length} businesses in category '${category}'.`,
    };
}
