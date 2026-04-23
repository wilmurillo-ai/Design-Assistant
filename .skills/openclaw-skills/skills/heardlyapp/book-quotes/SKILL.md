---
name: book_quotes
description: Extract memorable quotes and passages from books. Get the most inspiring and thought-provoking quotes.
keywords:
  - book
  - quotes
  - passages
  - memorable
  - inspiration
triggers:
  - "quotes from"
  - "memorable quotes"
  - "best quotes"
  - "inspiring passages"
  - "quotes by"
---

# book-quotes

Extract memorable quotes and passages from books.

## What it does

- Search books by title or author
- Extract 5-10 memorable quotes and passages
- Return formatted quotes with attribution
- Show Heardly quotes if available
- Support multiple book sources

## When to use this skill

Use this skill when the user asks:
- "What are the best quotes from Atomic Habits?"
- "Memorable quotes from Deep Work"
- "Inspiring passages from Principles"
- "Quotes by Steve Jobs"
- "Best quotes from The Lean Startup"

## Installation

```bash
clawhub install book-quotes
```

## Usage

```javascript
const BookQuotesSkill = require('book-quotes');
const skill = new BookQuotesSkill();

// Get quotes (returns formatted text)
const result = await skill.getQuotes({
  query: 'Atomic Habits',
  limit: 10
});
console.log(result); // Directly readable text output
```

## Output

Formatted text with:
- Book title and author
- 5-10 memorable quotes
- Attribution for each quote
- Heardly source attribution
- Ready to display to users

## Data Sources

1. **Heardly Database** (5904 books) — quotes field
2. **Extracted from summaries** — key passages

## License

MIT
