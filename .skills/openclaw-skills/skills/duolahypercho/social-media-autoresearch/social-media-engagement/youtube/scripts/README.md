# YouTube Engagement Scripts

This folder contains JavaScript utilities for YouTube Shorts engagement automation.

## Scripts

### comment-inject.js
Injects a comment into YouTube Shorts using JavaScript injection.

## Usage

### In Browser Automation
Run the JavaScript directly in the browser context:

```javascript
// Full inline script - use this exact code
const ce = document.getElementById('contenteditable-root');
if (!ce) {
  const alt = document.querySelector('div[contenteditable]');
  if (alt) {
    alt.innerText = 'Your comment here 🧡';
    alt.dispatchEvent(new Event('input', { bubbles: true }));
    return { success: true, method: 'alt' };
  }
  return { error: 'No element found' };
}
ce.innerText = 'Your comment here 🧡';
ce.dispatchEvent(new Event('input', { bubbles: true }));
ce.dispatchEvent(new Event('change', { bubbles: true }));
return { success: true };
```

## Workflow Summary

1. Navigate to YouTube Shorts
2. Find relevant content (AI, productivity, motivation, etc.)
3. Watch the video (~30 seconds)
4. Click Like button
5. Click "View comments"
6. Click the comment textbox to activate it
7. Run comment injection script
8. Click "Comment" button to submit
9. Like your own comment

## Troubleshooting

- **Element not found**: Click the comment textbox first to activate it
- **Comment not submitting**: Make sure to trigger both 'input' and 'change' events
- **Text cleared**: YouTube may clear text if you don't trigger events properly
