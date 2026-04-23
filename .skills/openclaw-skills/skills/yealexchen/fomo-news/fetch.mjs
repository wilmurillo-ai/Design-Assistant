#!/usr/bin/env node

/**
 * fomo-news fetcher — pulls trending GitHub repos, social posts, and breaking news
 * Usage: node fetch.mjs <category> [--limit <n>] [--json]
 * Categories: all, github, social, tech, ai, economics, politics, news
 */

const CATEGORIES = ["all", "github", "social", "tech", "ai", "economics", "politics", "news"];
const args = process.argv.slice(2);
const category = (args[0] || "all").toLowerCase();
const limitIdx = args.indexOf("--limit");
const limit = limitIdx !== -1 ? parseInt(args[limitIdx + 1], 10) : 10;
const jsonMode = args.includes("--json");

if (!CATEGORIES.includes(category)) {
  console.error(`Unknown category: ${category}`);
  console.error(`Valid categories: ${CATEGORIES.join(", ")}`);
  process.exit(1);
}

// --- GitHub Trending ---
const GITHUB_QUERIES = [
  { q: "stars:>50 created:>{weekAgo}", sort: "stars", per_page: 15, label: "trending" },
  { q: "topic:ai stars:>20 created:>{weekAgo}", sort: "stars", per_page: 10, label: "ai" },
  { q: "topic:llm stars:>10 created:>{weekAgo}", sort: "stars", per_page: 10, label: "llm" },
];

async function fetchGitHub(max) {
  const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().split("T")[0];
  const headers = { "Accept": "application/vnd.github.v3+json", "User-Agent": "fomo-news/1.0" };
  if (process.env.GITHUB_TOKEN) headers["Authorization"] = `Bearer ${process.env.GITHUB_TOKEN}`;

  const seen = new Set();
  const repos = [];

  const results = await Promise.allSettled(
    GITHUB_QUERIES.map(async ({ q, sort, per_page }) => {
      const query = q.replace(/{weekAgo}/g, weekAgo);
      const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(query)}&sort=${sort}&order=desc&per_page=${per_page}`;
      const res = await fetch(url, { headers });
      if (!res.ok) throw new Error(`GitHub API ${res.status}`);
      return (await res.json()).items || [];
    })
  );

  for (const r of results) {
    if (r.status !== "fulfilled") continue;
    for (const item of r.value) {
      if (seen.has(item.id)) continue;
      seen.add(item.id);
      repos.push({
        name: item.full_name,
        description: (item.description || "").slice(0, 150),
        stars: item.stargazers_count,
        forks: item.forks_count,
        language: item.language || "Unknown",
        url: item.html_url,
        topics: (item.topics || []).slice(0, 5),
        created: item.created_at,
      });
    }
  }

  repos.sort((a, b) => b.stars - a.stars);
  return repos.slice(0, max);
}

// --- RSS Feed Parser (lightweight, no deps) ---
function parseRSSItems(xml, maxItems = 10) {
  const items = [];
  const itemRegex = /<item>([\s\S]*?)<\/item>/gi;
  let match;
  while ((match = itemRegex.exec(xml)) !== null && items.length < maxItems) {
    const block = match[1];
    const get = (tag) => {
      const m = block.match(new RegExp(`<${tag}[^>]*>\\s*(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?\\s*</${tag}>`, "i"));
      return m ? m[1].trim() : "";
    };
    items.push({
      title: get("title").replace(/<[^>]*>/g, ""),
      link: get("link"),
      pubDate: get("pubDate"),
      snippet: get("description").replace(/<[^>]*>/g, "").slice(0, 200),
    });
  }
  return items;
}

async function fetchRSS(url, maxItems = 10) {
  try {
    const res = await fetch(url, {
      headers: { "User-Agent": "fomo-news/1.0" },
      signal: AbortSignal.timeout(10000),
    });
    if (!res.ok) return [];
    const xml = await res.text();
    return parseRSSItems(xml, maxItems);
  } catch {
    return [];
  }
}

// --- Social Feeds ---
const SOCIAL_SOURCES = [
  { name: "Sam Altman", handle: "sama", query: "Sam Altman OpenAI when:3d", category: "ai" },
  { name: "Elon Musk", handle: "elonmusk", query: "Elon Musk when:3d", category: "tech" },
  { name: "Jensen Huang", handle: "nvidia", query: "Jensen Huang NVIDIA when:3d", category: "ai" },
  { name: "Dario Amodei", handle: "dabornico", query: "Dario Amodei Anthropic when:3d", category: "ai" },
  { name: "Satya Nadella", handle: "satyanadella", query: "Satya Nadella Microsoft when:3d", category: "tech" },
  { name: "Sundar Pichai", handle: "sundarpichai", query: "Sundar Pichai Google when:3d", category: "tech" },
  { name: "Mark Zuckerberg", handle: "zuck", query: "Mark Zuckerberg Meta when:3d", category: "tech" },
  { name: "Tim Cook", handle: "timcook", query: "Tim Cook Apple when:3d", category: "tech" },
  { name: "Demis Hassabis", handle: "demabornico", query: "Demis Hassabis DeepMind when:3d", category: "ai" },
  { name: "Ilya Sutskever", handle: "ilyasut", query: "Ilya Sutskever when:3d", category: "ai" },
  { name: "Andrej Karpathy", handle: "karpathy", query: "Andrej Karpathy when:3d", category: "ai" },
  { name: "Yann LeCun", handle: "ylecun", query: "Yann LeCun when:3d", category: "ai" },
];

async function fetchSocial(max) {
  const results = await Promise.allSettled(
    SOCIAL_SOURCES.map(async (src) => {
      const url = `https://news.google.com/rss/search?q=${encodeURIComponent(src.query)}&hl=en-US&gl=US&ceid=US:en`;
      const items = await fetchRSS(url, 3);
      return items.map((item) => ({
        author: src.name,
        handle: src.handle,
        category: src.category,
        title: item.title,
        link: item.link,
        pubDate: item.pubDate,
        snippet: item.snippet,
      }));
    })
  );

  const posts = results
    .filter((r) => r.status === "fulfilled")
    .flatMap((r) => r.value);

  posts.sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate));
  return posts.slice(0, max);
}

// --- News Feeds ---
const NEWS_SOURCES = [
  { name: "TechCrunch", url: "https://techcrunch.com/feed/", category: "tech" },
  { name: "Ars Technica", url: "https://feeds.arstechnica.com/arstechnica/index", category: "tech" },
  { name: "The Verge", url: "https://www.theverge.com/rss/index.xml", category: "tech" },
  { name: "Hacker News", url: "https://hnrss.org/frontpage", category: "tech" },
  { name: "Wired", url: "https://www.wired.com/feed/rss", category: "tech" },
  { name: "MIT Tech Review", url: "https://www.technologyreview.com/feed/", category: "ai" },
  { name: "VentureBeat", url: "https://venturebeat.com/feed/", category: "ai" },
  { name: "Reuters Business", url: "https://feeds.reuters.com/reuters/businessNews", category: "economics" },
  { name: "CNBC", url: "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114", category: "economics" },
  { name: "MarketWatch", url: "https://feeds.marketwatch.com/marketwatch/topstories/", category: "economics" },
  { name: "AP News", url: "https://rsshub.app/apnews/topics/apf-topnews", category: "politics" },
  { name: "BBC News", url: "https://feeds.bbci.co.uk/news/world/rss.xml", category: "politics" },
  { name: "NPR News", url: "https://feeds.npr.org/1001/rss.xml", category: "politics" },
];

async function fetchNews(categories, max) {
  const sources = categories
    ? NEWS_SOURCES.filter((s) => categories.includes(s.category))
    : NEWS_SOURCES;

  const results = await Promise.allSettled(
    sources.map(async (src) => {
      const items = await fetchRSS(src.url, 5);
      return items.map((item) => ({
        source: src.name,
        category: src.category,
        title: item.title,
        link: item.link,
        pubDate: item.pubDate,
        snippet: item.snippet,
      }));
    })
  );

  const articles = results
    .filter((r) => r.status === "fulfilled")
    .flatMap((r) => r.value);

  articles.sort((a, b) => new Date(b.pubDate) - new Date(a.pubDate));
  return articles.slice(0, max);
}

// --- Time formatting ---
function timeAgo(dateStr) {
  if (!dateStr) return "recently";
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

// --- Formatters ---
function formatGitHub(repos) {
  if (!repos.length) return "No trending repos found.\n";
  let out = "## ⭐ GitHub Trending\n\n";
  out += "| Repo | Stars | Language | Description |\n";
  out += "|------|------:|----------|-------------|\n";
  for (const r of repos) {
    out += `| [${r.name}](${r.url}) | ${r.stars.toLocaleString()} | ${r.language} | ${r.description.slice(0, 80)} |\n`;
  }
  return out + "\n";
}

function formatSocial(posts) {
  if (!posts.length) return "No social updates found.\n";
  let out = "## 💬 Social Updates\n\n";
  for (const p of posts) {
    out += `- **${p.author}** — [${p.title}](${p.link}) · ${timeAgo(p.pubDate)}\n`;
  }
  return out + "\n";
}

function formatNews(articles, label) {
  if (!articles.length) return `No ${label} news found.\n`;
  const emojis = { tech: "💻", ai: "🤖", economics: "📈", politics: "🏛️", news: "📰" };
  let out = `## ${emojis[label] || "📰"} ${label.charAt(0).toUpperCase() + label.slice(1)} News\n\n`;
  for (const a of articles) {
    out += `- **[${a.title}](${a.link})** — ${a.source} · ${timeAgo(a.pubDate)}\n`;
    if (a.snippet) out += `  ${a.snippet.slice(0, 120)}\n`;
  }
  return out + "\n";
}

// --- Main ---
async function main() {
  const sections = [];

  if (category === "all" || category === "github") {
    const repos = await fetchGitHub(limit);
    if (jsonMode) sections.push({ type: "github", data: repos });
    else sections.push(formatGitHub(repos));
  }

  if (category === "all" || category === "social") {
    const posts = await fetchSocial(limit);
    if (jsonMode) sections.push({ type: "social", data: posts });
    else sections.push(formatSocial(posts));
  }

  if (category === "all" || category === "news") {
    const articles = await fetchNews(null, limit * 3);
    if (jsonMode) sections.push({ type: "news", data: articles });
    else sections.push(formatNews(articles, "news"));
  }

  if (category === "tech") {
    const articles = await fetchNews(["tech"], limit);
    if (jsonMode) sections.push({ type: "tech", data: articles });
    else sections.push(formatNews(articles, "tech"));
  }

  if (category === "ai") {
    const articles = await fetchNews(["ai"], limit);
    if (jsonMode) sections.push({ type: "ai", data: articles });
    else sections.push(formatNews(articles, "ai"));
  }

  if (category === "economics") {
    const articles = await fetchNews(["economics"], limit);
    if (jsonMode) sections.push({ type: "economics", data: articles });
    else sections.push(formatNews(articles, "economics"));
  }

  if (category === "politics") {
    const articles = await fetchNews(["politics"], limit);
    if (jsonMode) sections.push({ type: "politics", data: articles });
    else sections.push(formatNews(articles, "politics"));
  }

  if (jsonMode) {
    console.log(JSON.stringify(sections, null, 2));
  } else {
    console.log(sections.join("\n---\n\n"));
  }
}

main().catch((err) => {
  console.error(`Error: ${err.message}`);
  process.exit(1);
});
