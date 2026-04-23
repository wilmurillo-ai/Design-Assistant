# ai-seo-content-writer

Generate SEO-optimized blog posts, articles, and website copy using AI. Takes a topic, target keywords, and optional brief to produce publish-ready content.

## Usage

```
Write an SEO article about [topic], targeting [keyword1, keyword2]
Generate a blog post about [subject], 800 words, friendly tone
Create product copy for [product description]
Write a landing page section for [product/service]
```

## What It Produces

- **Blog posts** — structured with H1/H2/H3, intro hook, body sections, conclusion with CTA
- **SEO articles** — keyword density optimized, meta description included, internal linking suggestions
- **Product descriptions** — feature-focused, benefit-oriented, conversion-driven
- **Landing page copy** — headline + subheadline + 3 bullet points + CTA
- **Social media posts** — platform-adapted (Twitter threads, LinkedIn posts, Instagram captions)

## Input Fields

| Field | Description | Default |
|-------|-------------|---------|
| topic | Main subject or product | required |
| keywords | Target SEO keywords (comma-separated) | — |
| word_count | Target length in words | 600 |
| tone | Professional / Casual / Technical / Friendly | Professional |
| format | Blog / Article / Landing Page / Social / Product | Article |
| audience | Who is this for? | General |
| cta | Call to action text (for landing pages) | — |

## Output

Returns markdown-formatted content with:
- Optimized headline and meta description
- Suggested internal link anchors
- Estimated reading time
- Flesch-Kincaid readability score

## Notes

- Best results with specific topics (not generic "make me famous")
- For technical content, provide more context in topic field
- Includes "SEO tips" section at the end with keyword placement reminders
