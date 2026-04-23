# Browser Skill

## Description

This skill provides the ability to render modern, JavaScript-heavy web pages and extract their clean, text-based content. It uses SkillBoss API Hub's web scraping capability, replacing the need for a local headless browser like Puppeteer. This allows the agent to accurately read and understand web content as a human would see it in a browser.

## Dependencies

- Node.js 18+ (built-in `fetch`)

## Environment Variables

- `SKILLBOSS_API_KEY` — SkillBoss API Hub 认证密钥

## Usage Example

The skill is executed via a Node.js script from the workspace root:

```bash
SKILLBOSS_API_KEY=your_key node skills/browser/index.js read https://example.com
```
