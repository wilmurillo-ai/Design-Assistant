# find-book

Local book search. 5904 nonfiction books, no network calls.

## What it does

- Search 5904 books by title or author
- Return book metadata: title, author, rating, summary, link
- Generate markdown suggestions for knowledge base

## Installation

```bash
clawhub install find-book
```

## Usage

```javascript
const FindBookSkill = require('find-book');
const skill = new FindBookSkill();
const result = skill.search('Atomic Habits');
```

## Data

- Source: Heardly database
- Format: Local JSON cache
- Books: 5904 nonfiction titles
- Network: Zero external calls
- Cost: Free

## License

MIT
