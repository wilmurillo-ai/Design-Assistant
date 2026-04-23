# AI Restaurant and Food Brand Marketing Engine: Scrape Reviews, Spy on Competitors and Produce Viral Food Content in 15 Minutes

**Display Name:** AI Restaurant and Food Brand Marketing Engine  
**Version:** 1.0.0
**Author:** @g4dr

## Overview

The restaurant industry runs on reputation and visibility. This skill scrapes Google Maps reviews, Yelp ratings, TikTok food trends and Instagram food content for any restaurant or food brand, identifies exactly what customers love and hate, analyzes competitor menus and pricing, then generates a complete marketing strategy with viral food video scripts produced through AI.

Every restaurant owner, food truck operator, ghost kitchen, meal prep brand and food influencer is your target audience.

Powered by: [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

---

## What This Skill Does

- Scrape Google Maps and Yelp reviews for any restaurant to find what customers praise and complain about
- Extract competitor menus, prices, ratings and review volumes from Google Maps in any city
- Monitor TikTok and Instagram for trending food content, hashtags and viral formats in your niche
- Analyze review sentiment to identify your top 3 strengths and top 3 weaknesses
- Generate a 30-day social media content calendar with food-specific viral hooks
- Produce TikTok and Reels ready food marketing videos with voiceover and captions
- Build a competitive intelligence report showing where you rank vs every nearby restaurant
- Create AI-written responses to negative reviews that protect your reputation
- Design a local SEO strategy based on what customers actually search for

---

## Step 1: Set Up Your Research Engine

This skill uses [Apify](https://www.apify.com?fpr=dx06p) to scrape restaurant data and food trends.

1. Create your free account at [Apify](https://www.apify.com?fpr=dx06p)
2. Go to **Settings > Integrations** and copy your Personal API Token
3. Store it securely:
   ```bash
   export APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxxx
   ```

---

## Step 2: Set Up Your Video Engine

This skill uses [InVideo AI](https://invideo.sjv.io/TBB) to produce food marketing videos.

1. Create your account at [InVideo AI](https://invideo.sjv.io/TBB)
2. Choose a plan with API access
3. Copy your API key:
   ```bash
   export INVIDEO_API_KEY=iv_api_xxxxxxxxxxxxxxxx
   ```

---

## Step 3: Install Dependencies

```bash
npm install apify-client axios
```

---

## Apify Actors Used

| Actor | What It Scrapes | Data Extracted |
|---|---|---|
| [Apify Google Maps Scraper](https://www.apify.com?fpr=dx06p) | Restaurants by keyword + location | Name, rating, reviews, hours, menu link, photos, price level |
| [Apify Google Maps Reviews Scraper](https://www.apify.com?fpr=dx06p) | Customer reviews per restaurant | Review text, star rating, date, owner response |
| [Apify Yelp Scraper](https://www.apify.com?fpr=dx06p) | Yelp restaurant listings | Rating, review count, price range, popular dishes |
| [Apify TikTok Hashtag Scraper](https://www.apify.com?fpr=dx06p) | Food trending videos | Views, likes, shares, hooks, sounds |
| [Apify Instagram Hashtag Scraper](https://www.apify.com?fpr=dx06p) | Food content by hashtag | Engagement, captions, posting time |
| [Apify Google Search Scraper](https://www.apify.com?fpr=dx06p) | Local search results | What people search for + local pack results |
| [Apify Website Content Crawler](https://www.apify.com?fpr=dx06p) | Restaurant websites | Menu items, pricing, online ordering links |
| [Apify Reddit Scraper](https://www.apify.com?fpr=dx06p) | Local food subreddits | What locals recommend and complain about |

---

## Examples

### Scrape All Competitors in Your Area

```javascript
import ApifyClient from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });

async function scrapeLocalCompetitors(cuisine, city, radius = 50) {
  const run = await client.actor("compass~crawler-google-places").call({
    searchStringsArray: [`${cuisine} restaurants in ${city}`],
    maxCrawledPlacesPerSearch: radius,
    language: "en"
  });

  const { items } = await run.dataset().getData();

  return items.map(r => ({
    name: r.title,
    rating: r.totalScore,
    reviewCount: r.reviewsCount,
    priceLevel: r.price || 'N/A',
    address: r.address,
    phone: r.phone,
    website: r.website,
    hours: r.openingHours,
    categories: r.categories || [],
    photos: r.imageUrls || [],
    url: r.url
  })).sort((a, b) => b.rating - a.rating);
}

const competitors = await scrapeLocalCompetitors("Italian", "Austin, TX");
console.log(`Found ${competitors.length} Italian restaurants in Austin`);

// Quick competitive overview
competitors.forEach((r, i) => {
  console.log(`${i + 1}. ${r.name} - ${r.rating}/5 (${r.reviewCount} reviews) ${r.priceLevel}`);
});
```

---

### Deep Review Analysis (Sentiment Mining)

```javascript
async function analyzeReviews(placeUrl, maxReviews = 100) {
  const run = await client.actor("apify/google-maps-reviews-scraper").call({
    startUrls: [{ url: placeUrl }],
    maxReviews: maxReviews,
    reviewsSort: "newest"
  });

  const { items } = await run.dataset().getData();

  // Categorize reviews
  const positive = items.filter(r => r.stars >= 4);
  const negative = items.filter(r => r.stars <= 2);
  const neutral = items.filter(r => r.stars === 3);

  // Extract common themes from review text
  const foodKeywords = ['food', 'taste', 'flavor', 'dish', 'menu', 'portion', 'fresh', 'quality'];
  const serviceKeywords = ['service', 'staff', 'waiter', 'waitress', 'friendly', 'rude', 'slow', 'fast'];
  const ambienceKeywords = ['ambiance', 'atmosphere', 'decor', 'clean', 'noise', 'music', 'cozy', 'vibe'];
  const priceKeywords = ['price', 'expensive', 'cheap', 'value', 'worth', 'overpriced', 'affordable'];

  function countMentions(reviews, keywords) {
    return reviews.filter(r =>
      keywords.some(k => (r.text || '').toLowerCase().includes(k))
    ).length;
  }

  return {
    totalReviews: items.length,
    avgRating: Math.round(items.reduce((s, r) => s + r.stars, 0) / items.length * 10) / 10,
    sentiment: {
      positive: positive.length,
      neutral: neutral.length,
      negative: negative.length
    },
    themes: {
      food: {
        positiveMentions: countMentions(positive, foodKeywords),
        negativeMentions: countMentions(negative, foodKeywords)
      },
      service: {
        positiveMentions: countMentions(positive, serviceKeywords),
        negativeMentions: countMentions(negative, serviceKeywords)
      },
      ambience: {
        positiveMentions: countMentions(positive, ambienceKeywords),
        negativeMentions: countMentions(negative, ambienceKeywords)
      },
      pricing: {
        positiveMentions: countMentions(positive, priceKeywords),
        negativeMentions: countMentions(negative, priceKeywords)
      }
    },
    recentNegative: negative.slice(0, 5).map(r => ({
      text: r.text,
      stars: r.stars,
      date: r.publishedAtDate,
      hasOwnerResponse: !!r.responseFromOwnerText
    })),
    topPraise: positive.slice(0, 3).map(r => r.text?.substring(0, 150))
  };
}

const reviewInsights = await analyzeReviews("https://maps.google.com/?cid=YOUR_PLACE_ID");
console.log(`Rating: ${reviewInsights.avgRating}/5 from ${reviewInsights.totalReviews} reviews`);
console.log(`Food sentiment: +${reviewInsights.themes.food.positiveMentions} / -${reviewInsights.themes.food.negativeMentions}`);
```

---

### Scrape Viral Food Content from TikTok and Instagram

```javascript
async function scrapeFoodTrends(foodType) {
  const hashtags = [foodType, `${foodType}tiktok`, 'foodtok', 'foodreview', `${foodType}lover`];

  const [ttRun, igRun] = await Promise.all([
    client.actor("apify/tiktok-hashtag-scraper").call({
      hashtags: hashtags.slice(0, 3),
      resultsPerPage: 30,
      shouldDownloadVideos: false
    }),
    client.actor("apify/instagram-hashtag-scraper").call({
      hashtags: hashtags.slice(0, 3),
      resultsLimit: 30
    })
  ]);

  const [tt, ig] = await Promise.all([
    ttRun.dataset().getData(),
    igRun.dataset().getData()
  ]);

  // Find winning hooks
  const topTikToks = tt.items
    .sort((a, b) => (b.playCount || 0) - (a.playCount || 0))
    .slice(0, 10);

  const topReels = ig.items
    .sort((a, b) => (b.likesCount || 0) - (a.likesCount || 0))
    .slice(0, 10);

  // Extract formats that work
  const viralFormats = [];
  topTikToks.forEach(v => {
    const text = (v.text || '').toLowerCase();
    if (text.includes('pov')) viralFormats.push('POV format');
    if (text.includes('rating') || text.includes('rate')) viralFormats.push('Rating/review format');
    if (text.includes('trying') || text.includes('tried')) viralFormats.push('First time trying format');
    if (text.includes('secret') || text.includes('hidden')) viralFormats.push('Secret menu/hidden gem format');
    if (text.includes('vs') || text.includes('versus')) viralFormats.push('Comparison format');
    if (text.includes('hack') || text.includes('trick')) viralFormats.push('Food hack format');
  });

  return {
    tiktokTrending: topTikToks.map(v => ({
      text: v.text,
      views: v.playCount,
      likes: v.diggCount,
      sound: v.musicMeta?.musicName
    })),
    instagramTrending: topReels.map(v => ({
      caption: v.caption,
      likes: v.likesCount,
      comments: v.commentsCount
    })),
    viralFormats: [...new Set(viralFormats)],
    trendingSounds: topTikToks
      .filter(v => v.musicMeta?.musicName)
      .map(v => v.musicMeta.musicName)
      .slice(0, 5)
  };
}

const foodTrends = await scrapeFoodTrends("pizza");
console.log("Viral formats:", foodTrends.viralFormats);
console.log("Trending sounds:", foodTrends.trendingSounds);
```

---

### Generate AI Marketing Strategy

```javascript
import axios from 'axios';

async function generateFoodMarketingPlan(restaurant, competitors, reviews, trends) {
  const prompt = `You are a restaurant marketing strategist. Create a complete 30-day marketing plan.

RESTAURANT:
- Name: ${restaurant.name}
- Cuisine: ${restaurant.cuisine}
- Rating: ${reviews.avgRating}/5 (${reviews.totalReviews} reviews)
- Top strength: ${reviews.topPraise[0]?.substring(0, 100)}
- Top weakness: ${reviews.recentNegative[0]?.text?.substring(0, 100)}

COMPETITIVE LANDSCAPE:
- ${competitors.length} competitors in area
- Top competitor: ${competitors[0]?.name} (${competitors[0]?.rating}/5, ${competitors[0]?.reviewCount} reviews)
- Your rank: #${competitors.findIndex(c => c.name === restaurant.name) + 1} of ${competitors.length}

VIRAL FOOD TRENDS RIGHT NOW:
- Formats working: ${trends.viralFormats.join(', ')}
- Trending sounds: ${trends.trendingSounds.join(', ')}

GENERATE:
1. Content Calendar: 30 posts with specific topics, formats and platforms (TikTok + Instagram + Google Posts)
2. Top 5 Video Scripts: Full scripts using proven viral formats from the trends data
3. Review Response Templates: 3 templates for negative reviews that turn complainers into fans
4. Local SEO Quick Wins: 5 specific actions to rank higher in "near me" searches
5. Promotion Ideas: 3 promotions designed to drive foot traffic this month

Keep it actionable and specific to this restaurant. No generic advice.`;

  const { data } = await axios.post('https://api.anthropic.com/v1/messages', {
    model: "claude-sonnet-4-20250514",
    max_tokens: 3000,
    messages: [{ role: "user", content: prompt }]
  }, {
    headers: {
      'x-api-key': process.env.CLAUDE_API_KEY,
      'anthropic-version': '2023-06-01'
    }
  });

  return data.content[0].text;
}
```

---

### Produce Food Marketing Videos with InVideo AI

```javascript
const invideo = axios.create({
  baseURL: 'https://api.invideo.io/v1',
  headers: {
    'Authorization': `Bearer ${process.env.INVIDEO_API_KEY}`,
    'Content-Type': 'application/json'
  }
});

async function produceFoodVideo(script, style = "food-promo") {
  const response = await invideo.post('/videos/generate', {
    script: script,
    format: "9:16",
    duration: "short",
    style: "dynamic",
    voiceover: {
      enabled: true,
      voice: "en-US-male-1",
      speed: 1.1
    },
    captions: {
      enabled: true,
      style: "bold-bottom",
      highlight: true
    },
    music: {
      enabled: true,
      mood: "upbeat",
      volume: 0.25
    }
  });

  const videoId = response.data.videoId;

  // Wait for completion
  let exportUrl = null;
  while (!exportUrl) {
    await new Promise(r => setTimeout(r, 5000));
    const status = await invideo.get(`/videos/${videoId}/status`);
    if (status.data.state === "completed") exportUrl = status.data.exportUrl;
    if (status.data.state === "failed") throw new Error("Video generation failed");
  }

  return { videoId, exportUrl };
}

// Example: produce a "secret menu item" reveal video
const video = await produceFoodVideo(
  "What nobody tells you about ordering at Italian restaurants. Most people order the same 3 dishes every time. But the real ones know to ask for the off-menu burrata. Fresh this morning, drizzled with truffle honey, served on warm sourdough. This is what the staff eats after closing. Next time you go, just ask. You are welcome. Follow for more hidden gems."
);
console.log("Food video ready:", video.exportUrl);
```

---

### Full Pipeline: Research, Analyze, Strategize, Produce

```javascript
import { writeFileSync } from 'fs';

async function fullRestaurantMarketingPipeline(cuisine, city, restaurantName) {
  console.log(`Starting Restaurant Marketing Pipeline for ${restaurantName}...`);

  // STEP 1: Scrape competitors
  const competitors = await scrapeLocalCompetitors(cuisine, city);
  console.log(`Step 1: ${competitors.length} competitors found`);

  // STEP 2: Analyze reviews
  const myRestaurant = competitors.find(c =>
    c.name.toLowerCase().includes(restaurantName.toLowerCase())
  );
  let reviews = null;
  if (myRestaurant?.url) {
    reviews = await analyzeReviews(myRestaurant.url, 50);
    console.log(`Step 2: ${reviews.totalReviews} reviews analyzed`);
  }

  // STEP 3: Scrape food trends
  const trends = await scrapeFoodTrends(cuisine);
  console.log(`Step 3: ${trends.viralFormats.length} viral formats identified`);

  // STEP 4: Generate marketing plan
  const plan = await generateFoodMarketingPlan(
    { name: restaurantName, cuisine },
    competitors,
    reviews || { avgRating: 'N/A', totalReviews: 0, topPraise: [], recentNegative: [] },
    trends
  );
  console.log(`Step 4: Marketing plan generated`);

  // STEP 5: Export everything
  const report = {
    restaurant: restaurantName,
    cuisine,
    city,
    generatedAt: new Date().toISOString(),
    competitorAnalysis: competitors.slice(0, 20),
    reviewInsights: reviews,
    trendData: trends,
    marketingPlan: plan
  };

  const filename = `restaurant-marketing-${restaurantName.replace(/\s+/g, '-')}-${Date.now()}.json`;
  writeFileSync(filename, JSON.stringify(report, null, 2));
  console.log(`Full report exported to ${filename}`);

  return report;
}

await fullRestaurantMarketingPipeline("Italian", "Austin, TX", "My Restaurant");
```

---

## What Makes This Different

| Feature | Generic Marketing Tool | This Skill |
|---|---|---|
| Competitor research | Manual googling | Automated scrape of every competitor in radius |
| Review analysis | Read them one by one | Sentiment mining with theme categorization |
| Content strategy | Generic templates | Based on actual viral food content data |
| Video production | Hire a videographer | AI-produced TikTok/Reels ready videos |
| Local SEO | Guesswork | Data-driven from real search patterns |
| Review management | Ignore them | AI-generated response templates |

---

## Pro Tips

1. Run the competitor scrape monthly to catch new restaurants opening nearby
2. Respond to every negative review within 24 hours using the AI templates
3. Use the trending sounds from TikTok data in your own videos for algorithm boost
4. Post Google Posts weekly (most restaurants ignore this and it is free local SEO)
5. Cross-reference what people praise in your reviews with what competitors lack. That is your marketing angle
6. The "secret menu item" video format consistently outperforms all other food content on TikTok

---

## Cost Estimate

| Action | Tool | Cost |
|---|---|---|
| Scrape 50 competitors | [Apify](https://www.apify.com?fpr=dx06p) | ~$0.04 |
| Analyze 100 reviews | [Apify](https://www.apify.com?fpr=dx06p) | ~$0.05 |
| Scrape food trends (TikTok + IG) | [Apify](https://www.apify.com?fpr=dx06p) | ~$0.10 |
| Generate marketing plan | Claude AI | ~$0.05 |
| Produce 5 food videos | [InVideo AI](https://invideo.sjv.io/TBB) | Plan dependent |
| Full pipeline | Total | Under $1 for research + strategy |

---

## Error Handling

```javascript
try {
  const run = await client.actor("compass~crawler-google-places").call(input);
  const dataset = await run.dataset().getData();
  return dataset.items;
} catch (error) {
  if (error.statusCode === 401) throw new Error("Invalid Apify token. Get yours at https://www.apify.com?fpr=dx06p");
  if (error.statusCode === 429) throw new Error("Rate limit. Reduce batch size.");
  throw error;
}
```

---

## Requirements

- An [Apify](https://www.apify.com?fpr=dx06p) account with API token
- An [InVideo AI](https://invideo.sjv.io/TBB) account for video production
- Claude API key for strategy generation
- Node.js 18+ with `apify-client` and `axios`
