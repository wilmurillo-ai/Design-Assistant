---
name: software-demo-video
version: "1.0.0"
displayName: "Software Demo Video Maker — Create App Walkthroughs and SaaS Demo Videos"
description: >
  Software Demo Video Maker — Create App Walkthroughs and SaaS Demo Videos.
metadata: {"openclaw": {"emoji": "🖥️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Software Demo Video Maker — App Walkthroughs and SaaS Demo Videos

The sales demo is in twenty minutes, the prospect has seen the pitch deck twice, and they've said the words every sales engineer dreads: "Can you just show me how it works?" The screen share begins, the demo environment loads with test data that looks like someone mashed the keyboard (Customer: asdfghjkl, Email: test@test.test, Company: ACME Corp #47), the presenter clicks the wrong menu, says "Let me just..." four times while navigating back to the right screen, and discovers that the feature they planned to demo was disabled by a deployment that happened during lunch. Software demos should be the most persuasive content a company produces — seeing the product solve the problem in real time converts better than any slide deck — but live demos go wrong because software is unpredictable and humans under pressure click the wrong thing. This tool transforms screen recordings, prototype flows, and app walkthroughs into polished software demo videos — clean cursor paths with click-ripple effects that guide the eye, zoom-and-pan on the relevant UI elements while the rest dims, step-numbered annotations that label each action in the workflow, realistic test data that looks like a real business is using the product, error-state handling that shows what happens when things go wrong (and how the software recovers), and the narrative pacing that turns a feature list into a story about the user's problem being solved. Built for sales teams building demo libraries for every prospect vertical, product marketers creating feature-launch announcement videos, customer-success teams producing onboarding walkthroughs, SaaS founders recording investor-demo videos that won't crash, developer-tools companies demonstrating API integrations and dashboard capabilities, and any software company that's ever lost a deal because the live demo went sideways.

## Example Prompts

### 1. SaaS Onboarding Walkthrough — New User First 5 Minutes
"Create a 4-minute onboarding walkthrough for our project-management SaaS. Show a brand-new user's first experience — from signup to first project created. The goal: reduce the time-to-value from 'What do I click?' to 'Oh, this is useful' in under 5 minutes. Signup (0-30 sec): Google SSO click — 'One click. No 14-field registration form. You're in.' The empty dashboard appears with the onboarding checklist overlay. Step 1 — Create a workspace (30-60 sec): cursor clicks 'New Workspace,' types a realistic name (not 'Test Workspace' — use 'Horizon Marketing Q2'), selects a template (show the template gallery briefly), workspace populates with sample data. Callout: 'Templates give you a starting structure. Delete what you don't need — it's faster than building from blank.' Step 2 — Invite the team (60-100 sec): click 'Invite,' type three email addresses, assign roles from the dropdown (Admin, Member, Viewer). Show the invitation email preview. 'They'll get an email that actually explains what this is. Not the "You've been invited to..." mystery link that everyone ignores.' Step 3 — Create first task (100-160 sec): click 'New Task' in the board view, type a task title, assign it (show the team member avatars appearing), set a due date with the calendar picker (zoom into the date picker interaction), add a priority label. Drag the task from 'To Do' to 'In Progress' — 'Drag and drop. The board updates for everyone in real time. No refresh needed.' Step 4 — Connect integrations (160-200 sec): navigate to Settings → Integrations, show Slack, GitHub, and Figma tiles. Click Slack — OAuth flow, select channel, done in 3 clicks. 'When a task status changes, your Slack channel knows. No one has to ask "What's the status on...?" ever again.' Closing (200-240 sec): return to the dashboard — it's no longer empty. Projects, tasks, team members, a Slack notification in the corner. 'Five minutes ago this was a blank screen. Now your team has a workspace, a workflow, and one fewer reason to send a status-update email.' CTA: 'Start your free workspace.' Brand colors throughout, clean UI with no visual clutter, cursor with click-ripple effects, step numbers in corner."

### 2. Enterprise Sales Demo — Prospect-Specific Vertical
"Build a 6-minute sales demo video for a healthcare prospect evaluating our data platform. This is the video the AE sends after the first call — it needs to feel like it was made for this prospect, not ripped from a generic demo library. Opening: 'Your team spends 3 hours daily reconciling patient data across 4 systems. Here's what that looks like with Meridian.' Dashboard (0-60 sec): the platform loaded with healthcare-specific data — patient records (HIPAA-compliant synthetic data), insurance claims, lab results. Not 'Row 1, Row 2' — realistic entries like 'Chen, Margaret — Claim #MH-2024-8847 — Status: Pending Review.' The dashboard shows a data-quality score: 94% — 'Your current score is probably around 60%. We've seen the spreadsheets.' Data reconciliation (60-180 sec): show the core workflow — two data sources side by side with mismatches highlighted in red. Click a mismatch: the AI suggests the resolution, shows confidence score (98.2%), one click to accept. 'Your team does this manually. It takes 3 hours. The platform does it in 11 seconds. I timed it.' Show the timer in the corner. After resolving 5 mismatches: 'Data quality score: 94% → 97%. Three clicks. Eleven seconds. Your compliance team just exhaled.' Reporting (180-280 sec): navigate to Reports → Compliance Ready. Show a pre-built report template: 'This report took one of your analysts 2 days to build last quarter. It updates in real time. Click Export → PDF and it's board-ready.' Show the export, open the PDF briefly. Audit trail (280-340 sec): click on any resolved mismatch — show the full audit log: who changed what, when, the AI confidence score, the approval chain. 'When the auditor asks "Who approved this change?" — this is your answer. Not a spreadsheet, not an email thread, a timestamped audit record.' Closing (340-360 sec): return to dashboard — 'From 3 hours to 11 seconds. From 60% data quality to 97%. From "Where's that spreadsheet?" to a live compliance dashboard.' CTA: 'Ready for a live demo with your data? Let's schedule it.' Professional, healthcare-appropriate design — clean blues and whites, HIPAA badge visible, realistic but synthetic data throughout."

### 3. Developer Tool — API and Dashboard Demo
"Produce a 5-minute demo of our monitoring and observability platform for a developer audience. Tone: technical, zero fluff, show-don't-tell. Opening: a terminal with a failing health check — 'Your service is returning 503s. Your PagerDuty is screaming. Here's how you find the problem in 90 seconds instead of 90 minutes.' Alert triage (0-60 sec): the alert dashboard showing a spike in error rate — click the alert, it opens the service map with the affected node highlighted in red. 'The platform already knows which service is failing. You don't need to grep through 47 log files to find it.' Trace the request (60-160 sec): click the failing node — distributed trace view. Show the waterfall: request enters the API gateway (2ms), hits the auth service (15ms), reaches the payment service (timeout — 30,000ms, highlighted red). 'There it is. The payment service is hanging. Let's find out why.' Click into the payment service — show the recent deployments timeline: 'A deploy happened 12 minutes ago. The error rate spiked 11 minutes ago. Coincidence? The platform shows you the correlation without you having to check Slack for deploy messages.' Logs in context (160-240 sec): click 'View Logs' — filtered automatically to the time window and service. Show the error: 'Connection refused: postgres:5432.' Zoom in. 'The database connection pool is exhausted. The new deploy increased the worker count from 4 to 16 but nobody updated the max connections. Classic.' Show the fix: link to the config file, the one-line change needed. Metrics dashboard (240-280 sec): navigate to the custom dashboard — latency percentiles (p50, p95, p99), error rate, throughput. 'This dashboard auto-generates from your service topology. No Grafana JSON, no PromQL, no 45-minute configuration session.' Show the comparison: before deploy vs after deploy, side by side. Closing (280-300 sec): return to the alert — click 'Resolve,' add the root cause note, tag the deploy. 'Alert to root cause in 90 seconds. Your mean-time-to-resolution just dropped from "however long it takes to wake up the on-call" to "less time than making coffee."' CTA: 'Start with 14 days free. Bring your own infra.' Dark-mode UI throughout, developer aesthetic — monospace labels, terminal-style elements, no marketing fluff in the interface."

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the software, user flow, key features to demo, and target audience |
| `duration` | string | | Target video length (e.g. "4 min", "6 min") |
| `style` | string | | Demo style: "onboarding-walkthrough", "sales-vertical", "developer-tool", "feature-launch", "investor-pitch" |
| `music` | string | | Background audio: "corporate-subtle", "tech-ambient", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `cursor_effects` | boolean | | Add click-ripple and guided cursor path effects (default: true) |
| `test_data` | string | | Data style: "realistic-business", "healthcare-hipaa", "developer-technical", "generic" |

## Workflow

1. **Describe** — Outline the user flow, features to highlight, pain points to address, and audience
2. **Upload** — Add screen recordings, UI mockups, prototype clicks, or Figma exports
3. **Generate** — AI produces the demo with clean cursor paths, zoom-and-dim focus, and annotations
4. **Review** — Preview the demo, verify the click-flow accuracy, adjust pacing and callout text
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "software-demo-video",
    "prompt": "Create a 4-minute SaaS onboarding walkthrough: Google SSO signup, create workspace with Horizon Marketing Q2 template, invite 3 team members with roles, create and drag first task, connect Slack integration in 3 clicks, closing showing populated dashboard vs empty start. Click-ripple cursor, step numbers, brand colors",
    "duration": "4 min",
    "style": "onboarding-walkthrough",
    "cursor_effects": true,
    "test_data": "realistic-business",
    "music": "corporate-subtle",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Use realistic test data, never "test@test.com"** — "Chen, Margaret — Claim #MH-2024-8847" makes the demo feel real; "User 1, test@test.test" makes it feel unfinished. Specify your audience's industry and the AI populates screens with contextually appropriate synthetic data.
2. **Show the before-and-after metric** — "From 3 hours to 11 seconds" is the single most persuasive frame in a software demo. Place the time/cost/effort comparison at the end of each workflow section and the AI renders it as an animated transformation graphic.
3. **Dim the background, zoom the action** — When you click a dropdown or fill a field, the rest of the UI should recede. "Zoom into the date picker interaction" tells the AI to apply focus-dim on the surrounding elements so the viewer's eye goes exactly where it should.
4. **Narrate the pain, then show the solution** — "Your team does this manually in 3 hours" before showing the 11-second automated version creates the contrast that drives conversion. The AI sequences problem-statement cards before each feature demonstration.
5. **End every section with a result, not a feature** — "Your Slack channel knows when tasks change" is a result; "Slack integration is available" is a feature. Results show value, features show capability. The AI renders result statements as callout cards at section transitions.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Website product tour / YouTube demo / sales deck |
| MP4 9:16 | 1080p | TikTok / Instagram Reels feature teaser |
| MP4 1:1 | 1080p | LinkedIn feed / product-launch post |
| GIF | 720p | Feature highlight loop / email embed |

## Related Skills

- [product-demo-video](/skills/product-demo-video) — Product walkthrough and feature demo videos
- [coding-tutorial-video](/skills/coding-tutorial-video) — Programming walkthrough and dev tutorial videos
- [tech-review-video](/skills/tech-review-video) — Tech review and comparison videos
