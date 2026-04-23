import log from '@apify/log';
import { BASE_URL, fetchHTML, extractNextData, extractJsonLd } from './utils.js';

/**
 * Parse rating distribution from raw data.
 * Returns an object: { 1: pct, 2: pct, 3: pct, 4: pct, 5: pct }
 */
function parseRatingDistribution(raw) {
    if (!raw) return null;
    // May be an array of { stars, count } or { ratingValue, percent }
    if (Array.isArray(raw)) {
        const dist = {};
        for (const item of raw) {
            const star = item.stars || item.ratingValue;
            const pct = item.percentage ?? item.percent ?? null;
            const count = item.count ?? null;
            if (star != null) dist[star] = { percentage: pct, count };
        }
        return dist;
    }
    // May already be a keyed object
    if (typeof raw === 'object') return raw;
    return null;
}

/**
 * Extract business profile from __NEXT_DATA__.
 */
function parseProfileFromNextData(nextData) {
    try {
        const pageProps = nextData?.props?.pageProps;
        if (!pageProps) return null;

        const bu =
            pageProps.businessUnit ||
            pageProps.businessData ||
            pageProps.initialState?.businessUnit;

        if (!bu) return null;

        return {
            name: bu.displayName || bu.name || null,
            domain: bu.websiteUrl || bu.identifyingName || null,
            description: bu.description || null,
            category: bu.categoryGroup?.displayName || bu.mainCategory?.displayName || null,
            trustScore: bu.trustScore || bu.ratingValue || null,
            totalReviews: bu.numberOfReviews || bu.reviewCount || null,
            ratingDistribution: parseRatingDistribution(bu.ratingDistribution || bu.starsDistribution),
            responseRate: bu.responseRate ?? null,
            replyTime: bu.replyTime || bu.averageReplyTime || null,
            location: {
                address: bu.location?.address || bu.address || null,
                city: bu.location?.city || bu.city || null,
                country: bu.location?.country || bu.country || null,
                countryCode: bu.location?.countryCode || bu.countryCode || null,
            },
            website: bu.websiteUrl || null,
            phone: bu.phone || null,
            email: bu.email || null,
            claimed: bu.claimed ?? null,
            verificationStatus: bu.verificationStatus || null,
            profileUrl: bu.identifyingName
                ? `${BASE_URL}/review/${bu.identifyingName}`
                : null,
        };
    } catch { return null; }
}

/**
 * Extract business profile from JSON-LD structured data.
 */
function parseProfileFromJsonLd(jsonLdItems) {
    for (const item of jsonLdItems) {
        if (['LocalBusiness', 'Organization', 'WebSite'].includes(item['@type'])) {
            return {
                name: item.name || null,
                domain: item.url || null,
                description: item.description || null,
                category: item['@type'] || null,
                trustScore: item.aggregateRating?.ratingValue
                    ? Number(item.aggregateRating.ratingValue)
                    : null,
                totalReviews: item.aggregateRating?.reviewCount
                    ? Number(item.aggregateRating.reviewCount)
                    : null,
                ratingDistribution: null,
                responseRate: null,
                replyTime: null,
                location: {
                    address: item.address?.streetAddress || null,
                    city: item.address?.addressLocality || null,
                    country: item.address?.addressCountry || null,
                    countryCode: null,
                },
                website: item.url || null,
                phone: item.telephone || null,
                email: item.email || null,
                claimed: null,
                verificationStatus: null,
                profileUrl: null,
            };
        }
    }
    return null;
}

/**
 * Regex fallback: extract basic profile info from HTML.
 */
function parseProfileFromHtml(html, domain) {
    const nameMatch = html.match(/<h1[^>]*>([^<]+)<\/h1>/i);
    const ratingMatch = html.match(/aria-label="TrustScore ([0-9.]+) out of 5"/i) ||
                        html.match(/trustscore[^"]*"[^>]*>([0-9.]+)</i);
    const reviewCountMatch = html.match(/([0-9,]+)\s+(?:total\s+)?reviews?/i);

    return {
        name: nameMatch ? nameMatch[1].trim() : domain,
        domain,
        description: null,
        category: null,
        trustScore: ratingMatch ? Number(ratingMatch[1]) : null,
        totalReviews: reviewCountMatch ? Number(reviewCountMatch[1].replace(/,/g, '')) : null,
        ratingDistribution: null,
        responseRate: null,
        replyTime: null,
        location: { address: null, city: null, country: null, countryCode: null },
        website: null,
        phone: null,
        email: null,
        claimed: null,
        verificationStatus: null,
        profileUrl: `${BASE_URL}/review/${domain}`,
    };
}

/**
 * Get detailed business profile and stats from Trustpilot.
 *
 * Input:
 *   - businessUrl {string}  Domain or slug, e.g. "stripe.com"
 */
export async function businessProfile(input) {
    const businessUrl = (input.businessUrl || '').trim()
        .replace(/^https?:\/\/(www\.)?trustpilot\.com\/review\//i, '')
        .replace(/\/$/, '');

    if (!businessUrl) throw new Error('businessUrl is required (e.g. "stripe.com")');

    log.info(`Fetching profile for: ${businessUrl}`);

    const fetchOpts = input.proxyUrl ? { proxyUrl: input.proxyUrl } : {};
    const url = `${BASE_URL}/review/${businessUrl}`;
    const html = await fetchHTML(url, fetchOpts);

    let profile = null;

    const nextData = extractNextData(html);
    if (nextData) {
        profile = parseProfileFromNextData(nextData);
    }

    if (!profile) {
        log.debug('__NEXT_DATA__ yielded no profile, trying JSON-LD...');
        const jsonLd = extractJsonLd(html);
        profile = parseProfileFromJsonLd(jsonLd);
    }

    if (!profile) {
        log.debug('JSON-LD yielded no profile, using HTML regex fallback...');
        profile = parseProfileFromHtml(html, businessUrl);
    }

    return {
        business: businessUrl,
        profile,
        summary: profile
            ? `Profile for ${profile.name || businessUrl}: TrustScore ${profile.trustScore ?? 'N/A'}/5 from ${profile.totalReviews ?? 'N/A'} reviews.`
            : `Could not extract profile for ${businessUrl}.`,
    };
}
