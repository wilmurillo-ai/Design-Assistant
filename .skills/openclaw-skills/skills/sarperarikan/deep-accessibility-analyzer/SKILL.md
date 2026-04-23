# 🌍 Universal Deep Accessibility Analyzer Skill

## Skill Definition

**Name:** `deep-accessibility-analyzer`
**Version:** 2.0.0
**Description:** Enterprise-grade WCAG 2.2 deep analysis with VoiceOver simulation, visual analysis, screenshot-based color detection, semantic analysis, and multi-page crawling (40+ pages)

## Capabilities

### 1. VoiceOver Deep Simulation
- Real macOS VoiceOver integration via Guidepup
- Keyboard navigation testing (Tab, Shift+Tab, Arrow keys)
- Landmark navigation (R, C, F, H keys)
- Heading hierarchy navigation (1-6 keys)
- Form interaction testing
- Modal dialog testing
- Focus trap detection
- Screen reader announcements validation

### 2. Visual Analysis (Full-Page Screenshot)
- Full-page color screenshot capture (not grayscale)
- Color contrast analysis (WCAG 1.4.3)
- Visual hierarchy detection
- Layout breakage detection at different viewports
- Text clipping/overflow detection
- Interactive element visibility check
- Focus indicator visibility validation

### 3. Semantic & Meaning Analysis
- Content meaning coherence
- Link context appropriateness
- Image alt text relevance (AI-powered)
- Form label clarity
- Error message helpfulness
- Navigation logic flow
- Cognitive load assessment

### 4. Multi-Disability Coverage
- **Blind users:** Screen reader compatibility, keyboard navigation
- **Low vision:** Color contrast, zoom 200%/400%, text spacing
- **Motor impairments:** Keyboard accessibility, timing adjustments
- **Cognitive:** Clear language, consistent navigation, error prevention
- **Hearing:** Captions, transcripts, visual alternatives

### 5. Intelligent Multi-Page Crawling
- Minimum 40 pages per scan
- Same-domain only (no external links)
- Depth-first + breadth-first hybrid
- Loop prevention with visited set
- Dynamic route discovery (SPA support)
- Priority pages: Forms, Products, Checkout, Navigation
- Rate limiting: 3-5 seconds between pages (human-like)

### 6. Security Stealth Mode
- Human-like browsing patterns
- Random delays between actions
- Natural scroll behavior
- Realistic mouse movements
- Proper User-Agent rotation
- No automation detection flags
- Cloudflare/WAF bypass

### 7. AI Strategy (Gemini 2.5 Flash)
- Token-efficient analysis
- Smart batching (group similar issues)
- Progressive analysis (critical first)
- Context-aware prompting
- No full DOM sending (snippets only)
- Cache results to avoid re-analysis
- Limit: ~50,000 tokens per page max

## Output Requirements

### Detailed Issue Reports (NOT summaries)
For EACH issue:
1. **Exact location:** URL + CSS selector + XPath
2. **Screenshot:** Annotated with issue highlighted
3. **Code snippet:** Actual HTML from page
4. **WCAG mapping:** Criterion + Level + Success/Failure
5. **Disability impact:** Which user groups affected
6. **Root cause:** Why this fails
7. **Technical solution:** Copy-paste ready code fix
8. **Priority:** Critical/Serious/Moderate/Minor
9. **Effort estimate:** Dev hours to fix
10. **Business impact:** Legal/UX/SEO impact

### Process Analysis
- Scan timeline (start/end per page)
- Pages discovered vs scanned
- Issues per page breakdown
- Trend analysis (improving/worsening)
- Comparison with industry benchmarks

### Final Deliverables
1. **HTML Report:** Professional, accessible, with charts
2. **JSON Report:** Machine-readable, API-ready
3. **Markdown Report:** Human-readable summary
4. **Jira Tickets:** One per issue, ready to import
5. **CSV Export:** For Excel analysis
6. **Screenshots Folder:** Annotated images per issue

## Technical Stack

- **Browser:** Playwright (Chromium + WebKit for Safari simulation)
- **Screen Reader:** Guidepup (macOS VoiceOver)
- **AI:** Gemini 2.5 Flash (Google AI Studio)
- **Screenshots:** Playwright full-page + element screenshots
- **Color Analysis:** node-color-contrast + custom algorithms
- **Crawling:** Custom BFS/DFS hybrid with priority queue
- **Storage:** Local filesystem + optional S3

## Performance Targets

- **Pages per hour:** 40-60 (with deep analysis)
- **Token usage:** <100k tokens per 10 pages average
- **False positive rate:** <5%
- **Issue detection accuracy:** >95%
- **Report generation:** <2 minutes after scan complete

## Error Handling

- Retry failed pages (max 3 attempts)
- Skip inaccessible pages (log reason)
- Continue on AI API errors (use deterministic fallback)
- Graceful degradation (partial reports OK)
- Detailed error logging for debugging

## Usage Example

```bash
# Full deep scan (40+ pages)
node deep-accessibility-analyzer.js https://www.arcelik.com.tr --pages=40 --depth=5

# Quick scan (10 pages)
node deep-accessibility-analyzer.js https://example.com --pages=10

# Single page deep dive
node deep-accessibility-analyzer.js https://example.com/product/123 --single

# With VoiceOver (requires macOS)
node deep-accessibility-analyzer.js https://example.com --voiceover

# Export formats
node deep-accessibility-analyzer.js https://example.com --format=html,json,md,jira,csv
```

## Configuration

```javascript
const CONFIG = {
  // Scan settings
  minPages: 40,
  maxPages: 100,
  maxDepth: 5,
  timeout: 60000,
  delayBetweenPages: 4000,
  
  // AI settings
  geminiModel: 'gemini-2.5-flash',
  maxTokensPerPage: 50000,
  tokenBudget: 500000, // Total per scan
  
  // Screenshot settings
  fullPageScreenshot: true,
  elementScreenshots: true,
  annotateIssues: true,
  
  // VoiceOver settings
  enableVoiceOver: true, // macOS only
  voiceOverRate: 300, // Words per minute
  
  // Output
  outputDir: './audits',
  formats: ['html', 'json', 'md', 'jira', 'csv'],
  
  // Stealth
  stealthMode: true,
  randomDelays: true,
  humanScrolling: true
};
```

## Success Criteria

✅ Minimum 40 pages scanned
✅ Full-page color screenshots for all pages
✅ VoiceOver simulation completed
✅ Color contrast analysis for all text elements
✅ Semantic coherence validated by AI
✅ No security triggers (WAF/Cloudflare bypassed)
✅ Detailed issue reports (not summaries)
✅ Copy-paste ready code fixes
✅ Jira tickets generated
✅ Process timeline documented
✅ Under token budget

---

**This skill replaces all previous WCAG scanning scripts.**
**Default behavior: Deep, comprehensive, production-ready analysis.**
