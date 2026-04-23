/**
 * YouTube Shorts — Comment Injection Script
 *
 * Injects text into the YouTube Shorts comment box using JavaScript.
 * Use this as a FALLBACK when normal click+type doesn't work.
 *
 * IMPORTANT: YouTube uses a contenteditable div, not a standard <input>.
 * We must trigger 'input' and 'change' events or YouTube won't register the text.
 *
 * Browser engine compatibility: Use ES5 syntax (var, not const/let).
 *
 * USAGE:
 *   browser(action="act", targetId="<tabId>", kind="evaluate", fn="<THIS_SCRIPT>")
 *
 * TIP: Run a snapshot FIRST to confirm the comment panel is open.
 */

var ce = null;

// Try YouTube's specific ID first (most reliable on Shorts)
ce = document.getElementById('contenteditable-root');

// Fallback: any contenteditable in the comment area
if (!ce) {
  var allEditable = document.querySelectorAll('div[contenteditable]');
  for (var i = 0; i < allEditable.length; i++) {
    var el = allEditable[i];
    if (el.offsetWidth > 0 && el.offsetHeight > 0) {
      ce = el;
      break;
    }
  }
}

// Fallback 2: inside ytd-comment-simplebox-renderer
if (!ce) {
  var commentArea = document.querySelector('ytd-comment-simplebox-renderer');
  if (commentArea) {
    var editableInArea = commentArea.querySelector('[contenteditable]');
    if (editableInArea) ce = editableInArea;
  }
}

if (!ce) {
  return {
    success: false,
    error: 'Comment box element not found',
    hint: 'Click the comment textbox first to activate it, then try the script again'
  };
}

// Inject the text — replace COMMENT_TEXT_PLACEHOLDER before running
ce.innerText = 'YOUR COMMENT TEXT HERE';

// Trigger YouTube's input detection
ce.dispatchEvent(new Event('input', { bubbles: true, cancelable: true }));
ce.dispatchEvent(new Event('change', { bubbles: true, cancelable: true }));
ce.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true, cancelable: true }));

return {
  success: true,
  method: 'contenteditable',
  textLength: ce.innerText.length,
  textPreview: ce.innerText.substring(0, 50)
};

/*
 * HOW TO USE THIS SCRIPT:
 *
 * 1. Open the script in the browser's evaluate context
 * 2. Find and replace "YOUR COMMENT TEXT HERE" with your actual comment
 * 3. The comment will be injected into the active comment textbox
 *
 * Example:
 *   ce.innerText = 'This hits different because it\'s true. 🧡';
 */
