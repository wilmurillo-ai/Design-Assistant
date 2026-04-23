import log from '@apify/log';

const TIMEOUT = 30000;
const MAX_RETRIES = 3;
const BASE_URL = 'https://www.trustpilot.com';

export { BASE_URL };

export async function fetchWithRetry(url, options = {}) {
    const timeout = options.timeout || TIMEOUT;
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), timeout);
            const headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                ...(options.headers || {}),
            };
            const fetchOpts = { headers, signal: controller.signal };
            if (options.proxyUrl) {
                const { HttpsProxyAgent } = await import('https-proxy-agent');
                fetchOpts.agent = new HttpsProxyAgent(options.proxyUrl);
            }
            const response = await fetch(url, fetchOpts);
            clearTimeout(timeoutId);
            if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            return response;
        } catch (err) {
            if (attempt === MAX_RETRIES) {
                log.warning(`Failed after ${MAX_RETRIES} attempts: ${url} - ${err.message}`);
                throw err;
            }
            const delay = Math.pow(2, attempt) * 1000 + Math.random() * 1000;
            log.debug(`Attempt ${attempt} failed, retrying in ${Math.round(delay)}ms...`);
            await new Promise(r => setTimeout(r, delay));
        }
    }
}

export async function fetchHTML(url, options = {}) {
    const response = await fetchWithRetry(url, options);
    return await response.text();
}

export async function fetchJSON(url, options = {}) {
    try {
        const response = await fetchWithRetry(url, { ...options, headers: { ...options.headers, 'Accept': 'application/json' } });
        return await response.json();
    } catch (err) {
        log.warning(`fetchJSON failed: ${url} - ${err.message}`);
        return null;
    }
}

/**
 * Extract JSON-LD data from Trustpilot HTML pages.
 * Trustpilot embeds structured data as JSON-LD in script tags.
 */
export function extractJsonLd(html) {
    const results = [];
    const regex = /<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi;
    let match;
    while ((match = regex.exec(html)) !== null) {
        try {
            results.push(JSON.parse(match[1].trim()));
        } catch { /* skip invalid JSON */ }
    }
    return results;
}

/**
 * Extract Next.js __NEXT_DATA__ JSON from HTML.
 * Trustpilot uses Next.js, embedding page data in this script tag.
 */
export function extractNextData(html) {
    const match = html.match(/<script[^>]*id="__NEXT_DATA__"[^>]*>([\s\S]*?)<\/script>/i);
    if (!match) return null;
    try {
        return JSON.parse(match[1].trim());
    } catch { return null; }
}

export function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
}
