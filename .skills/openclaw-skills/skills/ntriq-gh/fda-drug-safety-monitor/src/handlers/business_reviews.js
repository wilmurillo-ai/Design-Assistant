import log from '@apify/log';
import { BASE_URL, fetchHTML, extractNextData, extractJsonLd, sleep } from './utils.js';

/**
 * Extract reviews from __NEXT_DATA__ pageProps.
 * Trustpilot embeds the review list under props.pageProps.reviews.
 */
function parseReviewsFromNextData(nextData) {
    try {
        const pageProps = nextData?.props?.pageProps;
        if (!pageProps) return [];

        // Try common locations in pageProps
        const reviewsList =
            pageProps.reviews ||
            pageProps.reviewsData?.reviews ||
            pageProps.initialState?.reviewsList?.reviews ||
            pageProps.initialState?.reviews;

        if (Array.isArray(reviewsList)) return reviewsList;
    } catch { /* fall through */ }
    return [];
}

/**
 * Normalize a raw review object from __NEXT_DATA__ into the output schema.
 */
function normalizeNextDataReview(raw) {
    return {
        id: raw.id || raw.reviewId || null,
        title: raw.title || raw.reviewTitle || null,
        text: raw.text || raw.reviewBody || raw.content || null,
        rating: raw.rating || raw.stars || null,
        date: raw.dates?.publishedDate || raw.createdAt || raw.date || null,
        author: {
            name: raw.consumer?.displayName || raw.reviewer?.name || raw.authorName || null,
            country: raw.consumer?.countryCode || raw.reviewer?.countryCode || null,
            reviewCount: raw.consumer?.numberOfReviews || raw.reviewer?.reviewCount || null,
        },
        isVerified: raw.labels?.verification?.isVerified ?? raw.isVerified ?? false,
        language: raw.language || null,
        likes: raw.likes || raw.helpfulVotes || 0,
    };
}

/**
 * Extract reviews from JSON-LD (fallback).
 * Looks for @type: "Review" objects in the structured data.
 */
function parseReviewsFromJsonLd(jsonLdItems) {
    const reviews = [];
    for (const item of jsonLdItems) {
        // Top-level Review
        if (item['@type'] === 'Review') {
            reviews.push(normalizeJsonLdReview(item));
        }
        // LocalBusiness or Organization may contain 'review' array
        if (Array.isArray(item.review)) {
            for (const r of item.review) {
                reviews.push(normalizeJsonLdReview(r));
            }
        }
    }
    return reviews;
}

function normalizeJsonLdReview(raw) {
    return {
        id: raw.identifier || null,
        title: raw.name || raw.headline || null,
        text: raw.reviewBody || null,
        rating: raw.reviewRating?.ratingValue ? Number(raw.reviewRating.ratingValue) : null,
        date: raw.datePublished || null,
        author: {
            name: raw.author?.name || null,
            country: null,
            reviewCount: null,
        },
        isVerified: false,
        language: raw.inLanguage || null,
        likes: 0,
    };
}

/**
 * Regex fallback: extract review IDs and basic data from raw HTML.
 * Used when both __NEXT_DATA__ and JSON-LD fail.
 */
function parseReviewsFromHtml(html) {
    const reviews = [];
    // Match data-review-id attributes with surrounding context
    const reviewBlockRegex = /data-review-id="([^"]+)"[^]*?(?=data-review-id="|<\/section>|$)/g;
    let m;
    while ((m = reviewBlockRegex.exec(html)) !== null) {
        const block = m[0];
        const id = m[1];

        const titleMatch = block.match(/class="[^"]*title[^"]*"[^>]*>([^<]+)</i);
        const bodyMatch = block.match(/class="[^"]*body[^"]*"[^>]*>([\s\S]*?)<\/p>/i);
        const ratingMatch = block.match(/aria-label="Rated (\d) out of 5 stars"/i) ||
                            block.match(/data-rating="(\d)"/i);
        const dateMatch = block.match(/datetime="([^"]+)"/i);
        const authorMatch = block.match(/class="[^"]*consumer[^"]*"[^>]*>([^<]+)</i);

        reviews.push({
            id,
            title: titleMatch ? titleMatch[1].trim() : null,
            text: bodyMatch ? bodyMatch[1].replace(/<[^>]+>/g, '').trim() : null,
            rating: ratingMatch ? Number(ratingMatch[1]) : null,
            date: dateMatch ? dateMatch[1] : null,
            author: { name: authorMatch ? authorMatch[1].trim() : null, country: null, reviewCount: null },
            isVerified: false,
            language: null,
            likes: 0,
        });
    }
    return reviews;
}

/**
 * Determine total number of pages from __NEXT_DATA__.
 */
function getTotalPages(nextData, maxReviews) {
    try {
        const pageProps = nextData?.props?.pageProps;
        const pagination =
            pageProps?.filters?.pagination ||      // actual path: pageProps.filters.pagination
            pageProps?.pagination ||
            pageProps?.reviewsData?.pagination ||
            pageProps?.initialState?.reviewsList?.pagination;

        if (pagination?.totalPages) return pagination.totalPages;
        if (pagination?.totalCount && pagination?.perPage) {
            return Math.ceil(pagination.totalCount / pagination.perPage);
        }
        if (pagination?.count && pagination?.perPage) {
            return Math.ceil(pagination.count / pagination.perPage);
        }
        // Fallback: estimate from totalReviews
        const total =
            pageProps?.businessUnit?.numberOfReviews ||
            pageProps?.reviewsData?.totalReviews ||
            pageProps?.businessData?.numberOfReviews;
        if (total) return Math.ceil(Math.min(total, maxReviews) / 20);
    } catch { /* fall through */ }
    return null;
}

/**
 * Scrape reviews for a specific Trustpilot business.
 *
 * Input:
 *   - businessUrl {string}  Domain or slug, e.g. "stripe.com"
 *   - maxReviews  {number}  Maximum reviews to collect (default 100)
 */
export async function businessReviews(input) {
    const businessUrl = (input.businessUrl || '').trim().replace(/^https?:\/\/(www\.)?trustpilot\.com\/review\//i, '').replace(/\/$/, '');
    const maxReviews = Math.min(input.maxReviews || 100, 1000);
    const fetchOpts = input.proxyUrl ? { proxyUrl: input.proxyUrl } : {};

    if (!businessUrl) throw new Error('businessUrl is required (e.g. "stripe.com")');

    log.info(`Scraping reviews for: ${businessUrl} (max: ${maxReviews})`);

    const reviews = [];
    let page = 1;
    let totalPages = null;
    let avgRating = null;

    while (reviews.length < maxReviews) {
        const url = `${BASE_URL}/review/${businessUrl}?page=${page}`;
        log.debug(`Fetching page ${page}: ${url}`);

        let html;
        try {
            html = await fetchHTML(url, fetchOpts);
        } catch (err) {
            log.warning(`Failed to fetch page ${page}: ${err.message}`);
            break;
        }

        const nextData = extractNextData(html);
        let pageReviews = [];

        if (nextData) {
            pageReviews = parseReviewsFromNextData(nextData).map(normalizeNextDataReview);

            // Determine total pages on first successful fetch
            if (page === 1 && totalPages === null) {
                totalPages = getTotalPages(nextData, maxReviews);
                log.info(`Total pages estimated: ${totalPages ?? 'unknown'}`);

                // Extract average rating from businessUnit data
                try {
                    const pp = nextData?.props?.pageProps;
                    const bu = pp?.businessUnit || pp?.businessData;
                    avgRating = bu?.trustScore || bu?.ratingValue || null;
                } catch { /* ignore */ }
            }
        }

        // Fallback to JSON-LD if __NEXT_DATA__ yielded nothing
        if (pageReviews.length === 0) {
            log.debug('__NEXT_DATA__ yielded no reviews, trying JSON-LD...');
            const jsonLd = extractJsonLd(html);
            pageReviews = parseReviewsFromJsonLd(jsonLd);
        }

        // Fallback to HTML regex
        if (pageReviews.length === 0) {
            log.debug('JSON-LD yielded no reviews, trying HTML regex fallback...');
            pageReviews = parseReviewsFromHtml(html);
        }

        if (pageReviews.length === 0) {
            log.info(`No reviews found on page ${page}, stopping.`);
            break;
        }

        for (const r of pageReviews) {
            if (reviews.length >= maxReviews) break;
            reviews.push(r);
        }

        log.info(`Page ${page}: collected ${pageReviews.length} reviews (total so far: ${reviews.length})`);

        // Stop if we've reached the last known page
        if (totalPages !== null && page >= totalPages) break;
        if (reviews.length >= maxReviews) break;

        page++;
        // Polite delay between requests (1–2 seconds)
        await sleep(1000 + Math.random() * 1000);
    }

    // Compute average rating from collected reviews if not obtained from metadata
    if (avgRating === null && reviews.length > 0) {
        const rated = reviews.filter(r => r.rating != null);
        if (rated.length > 0) {
            avgRating = (rated.reduce((sum, r) => sum + r.rating, 0) / rated.length).toFixed(1);
        }
    }

    return {
        totalRecords: reviews.length,
        business: businessUrl,
        reviews,
        summary: `Scraped ${reviews.length} reviews for ${businessUrl}. Average rating: ${avgRating ?? 'N/A'}/5.`,
    };
}
