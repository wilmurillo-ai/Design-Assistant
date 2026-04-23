# book-summary

Generate podcast-style and text summaries of books. Convert book content into engaging audio scripts.

## Installation

```bash
clawhub install book-summary
```

## Usage

```javascript
const BookSummarySkill = require('book-summary');
const skill = new BookSummarySkill();

// Generate podcast script
const podcastResult = skill.generatePodcastSummary({
  title: 'Atomic Habits',
  author: 'James Clear',
  summary: 'Small changes compound into big results...'
});

// Generate text summary
const textResult = skill.generateTextSummary({
  title: 'Atomic Habits',
  author: 'James Clear',
  summary: 'Small changes compound into big results...'
});
```

## Features

- Podcast-style script generation
- Text summary with key ideas
- Actionable takeaways
- Duration estimation
- Single narrator format

## Output Format

### Podcast Script
- Hook (attention-grabbing opening)
- Intro (book and author context)
- 3 Key Ideas (with narratives and takeaways)
- Synthesis (connecting ideas)
- Call to Action (immediate next step)

### Text Summary
- Book metadata
- Original summary
- 3 key ideas with takeaways

## License

MIT
