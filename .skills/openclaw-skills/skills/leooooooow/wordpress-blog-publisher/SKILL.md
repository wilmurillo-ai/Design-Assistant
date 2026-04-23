---
name: wordpress-blog-publisher
description: Use this skill whenever the user wants to publish, update, or batch-upload blog content to a WordPress site via the REST API. Triggers include any mention of WordPress, WP, wp-json, publishing blog posts, SEO content, pushing Markdown or HTML to a blog, uploading featured images, scheduling posts, or writing a Published URL back to another system.
---

# WordPress Blog Publisher

This skill turns an AI agent into a reliable publisher for WordPress sites via the REST API (`/wp-json/wp/v2/*`). Designed for cross-border SEO bloggers.

## When to use
- Batch-publishing SEO articles from any source
- Updating existing posts (content, SEO title, slug, featured image)
- Uploading media to the WP library
- Scheduling future posts
- Writing permalink back into upstream system (Bitable, Airtable, Sheets)

## Prerequisites
1. Site URL (e.g. https://example.com)
2. Username
3. Application Password (WP Admin > Users > Profile > Application Passwords, NOT the login password)

Auth: HTTP Basic with app password.

## Core operations
### Create a post: POST /wp-json/wp/v2/posts
### Upload media: POST /wp-json/wp/v2/media
### Update a post: POST /wp-json/wp/v2/posts/<id>
### Find by slug: GET /wp-json/wp/v2/posts?slug=my-slug&status=any

## Content handling
- Markdown to HTML conversion (preserve code fences, tables)
- Strip YAML front-matter, use for title/slug/categories/tags
- Upload inline images, rewrite src to source_url
- Image placeholders `![prompt](gen:<prompt>)` trigger image generation if configured

## Batch mode
1. Dry-run first post, show draft URL
2. After confirm, process rest with 1-2s delay
3. Keep per-post status log, show summary
4. On failure, log and continue

## Helper script: scripts/wp_publish.py
Commands: upload-media, create-post, update-post, find-by-slug, publish-markdown

## Common pitfalls
- 401: wrong password type (need Application Password)
- 403: missing publish_posts capability
- Wrong category/tag IDs per site
- Images > 2MB: resize before upload
- Timezone: use date_gmt for UTC certainty

## After publishing
Write permalink back to upstream system and flip status to published.