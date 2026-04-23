---
name: ai-elearning-video
version: "1.0.0"
displayName: "AI eLearning Video Maker — Create Online Course and Training Videos with AI"
description: >
  Create professional eLearning videos, online course modules, and digital training content using AI-powered production. NemoVideo segments raw lecture recordings into structured lessons, generates animated overlays from slide content, syncs screen recordings with instructor footage, inserts knowledge-check interstitials, and exports in platform-specific formats for Udemy, Coursera, Teachable, and SCORM-compliant LMS systems.
metadata: {"openclaw": {"emoji": "📚", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# AI eLearning Video Maker — Online Course and Training Videos

The eLearning industry generates $400 billion annually, and the overwhelming majority of that content is unwatchable — not because the instructors lack expertise, but because expertise in a subject and expertise in video production are entirely different skills, and the average course creator spends 200 hours building curriculum, hits record, and discovers that the camera doesn't care how much they know. The result: talking-head footage with no visual variation, slides read aloud verbatim, 45-minute lectures that should be 12 minutes, and screen recordings where the cursor wanders aimlessly while the instructor says "so basically what we want to do here is, uh..." NemoVideo solves the production gap so instructors can focus on teaching. It auto-segments raw recordings into lesson modules at topic boundaries, generates animated overlays when slide text is too small to read, inserts knowledge-check questions at retention-critical intervals, syncs screen recordings with face-cam footage for hybrid layouts, normalizes audio across modules, burns in captions (89% of learners watch on mobile without sound), and exports in the exact spec required by each platform — because Udemy, Coursera, Teachable, and Thinkific all have different resolution, bitrate, and container requirements that no instructor should need to memorize.

## Use Cases

1. **Udemy Course Module (4-6 lessons × 10-15 min)** — An instructor records 55 minutes of screen-share with webcam overlay for a Python programming course module. NemoVideo auto-segments into 4 lessons at topic boundaries, adds chapter markers within each, generates code-zoom overlays when terminal text is too small, inserts a 3-question quiz after each lesson, creates branded intro/outro bumpers, and exports each lesson as separate MP4 files meeting Udemy's 1080p H.264 AAC specification.
2. **Corporate Compliance Training (10-15 min per module)** — An L&D team needs GDPR, harassment prevention, and workplace safety modules. NemoVideo produces: scenario-based content (animated workplace situations), knowledge checks after each section (80% pass threshold), SCORM 2004 packaging with completion tracking, and multilingual captions in English, Spanish, and French. Each module is self-contained with its own quiz and certificate trigger.
3. **Micro-Course for Social Media (5 × 3 min)** — Convert a 60-minute masterclass into five 3-minute vertical lessons for TikTok/Reels. NemoVideo identifies the five highest-value segments by audience-engagement prediction, crops to 9:16, burns in large-font captions, adds lesson numbers ("Lesson 3/5"), and inserts "Full course link in bio" CTA at each clip's end.
4. **Cohort-Based Live Course Recording (6 modules)** — A leadership coach runs a live cohort course via Zoom. Each 90-minute session is recorded. NemoVideo processes each session into: a polished 20-minute pre-recorded lesson (trimming Q&A, technical issues, and off-topic discussion), a 2-minute animated recap generated from the transcript, and a discussion-prompt card for the cohort forum.
5. **Interactive Branching Scenario (5-8 min)** — A sales training video with choose-your-path decision points. At each branch, the learner selects a response and sees the consequence play out. NemoVideo renders each path as a separate video segment connected by chapter metadata, compatible with LMS platforms that support branching (Articulate, iSpring, custom xAPI).

## How It Works

### Step 1 — Upload Source Material
Provide raw lecture recordings, screen captures, slide decks (PDF/PPTX), and supplementary assets (diagrams, code files, brand kit). NemoVideo accepts up to 10 hours of raw footage per project.

### Step 2 — Define Course Structure
Specify the module/lesson breakdown, or let NemoVideo auto-segment by topic detection. Set target lesson length (8-15 min recommended for retention). Define quiz questions if using knowledge checks.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "ai-elearning-video",
    "prompt": "Produce Module 4 of a Data Science with Python course: Pandas DataFrames. Source: 62-minute screen-share recording with small webcam overlay. Auto-segment into 4 lessons at topic boundaries (creating DataFrames, selecting/filtering, groupby/aggregation, merging/joining). Generate code-zoom overlay when terminal or Jupyter cell text is below 14pt. Insert 3-question multiple-choice quiz after each lesson. Branded intro bumper with course logo. Normalize audio to -16 LUFS. Burn in English captions. Export as separate MP4s per lesson, Udemy spec 1080p H.264 AAC.",
    "duration": "4 lessons × ~12 min",
    "style": "screen-share-course",
    "platform": "udemy",
    "captions": true,
    "knowledge_checks": true,
    "code_zoom": true,
    "format": "16:9"
  }'
```

### Step 4 — Review and Publish
Preview each lesson in the NemoVideo editor. Adjust cut points, verify quiz answers, refine code-zoom timing. Export and upload directly to the course platform.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the course module, topic, and production requirements |
| `duration` | string | | Target per-lesson length: "10 min", "15 min", or total |
| `style` | string | | "screen-share-course", "talking-head-lecture", "slide-narration", "scenario-branching", "micro-course" |
| `platform` | string | | Target specs: "udemy", "coursera", "teachable", "thinkific", "scorm-1.2", "scorm-2004", "xapi" |
| `captions` | boolean | | Burn in or generate sidecar captions (default: true) |
| `knowledge_checks` | boolean | | Insert quiz interstitials between lessons (default: false) |
| `code_zoom` | boolean | | Auto-zoom on code/terminal when text is small (default: false) |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "aelv-20260328-001",
  "status": "completed",
  "module_title": "Data Science with Python — Module 4: Pandas DataFrames",
  "lessons": [
    {
      "lesson": 1,
      "title": "Creating DataFrames",
      "duration_seconds": 698,
      "file": "m4-lesson1-creating-dataframes.mp4",
      "quiz": {"questions": 3, "format": "multiple-choice"}
    },
    {
      "lesson": 2,
      "title": "Selecting and Filtering Data",
      "duration_seconds": 724,
      "file": "m4-lesson2-selecting-filtering.mp4",
      "quiz": {"questions": 3, "format": "multiple-choice"}
    },
    {
      "lesson": 3,
      "title": "GroupBy and Aggregation",
      "duration_seconds": 682,
      "file": "m4-lesson3-groupby-aggregation.mp4",
      "quiz": {"questions": 3, "format": "multiple-choice"}
    },
    {
      "lesson": 4,
      "title": "Merging and Joining DataFrames",
      "duration_seconds": 716,
      "file": "m4-lesson4-merging-joining.mp4",
      "quiz": {"questions": 3, "format": "multiple-choice"}
    }
  ],
  "total_duration_minutes": 47,
  "code_zoom_events": 34,
  "platform_compliance": "udemy-1080p-h264-aac ✓"
}
```

## Tips

1. **Keep lessons under 15 minutes** — Course completion rates drop 40% past 15 minutes on every major platform. NemoVideo segments at natural topic boundaries to hit this target.
2. **Captions are accessibility AND engagement infrastructure** — 89% of mobile learners watch without sound at least some of the time. Burned-in captions aren't optional.
3. **Code-zoom prevents squinting** — A full-screen IDE has 200 elements. NemoVideo's code_zoom auto-detects when terminal or code text falls below readable size and zooms to the active region.
4. **Knowledge checks boost retention 25-35%** — A 3-question quiz between lessons activates recall. Passive watching produces passive forgetting.
5. **Record at highest available quality, export per-platform** — 4K source downscales cleanly to 1080p and 720p. 720p source cannot upscale to 1080p without quality loss.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Udemy / Coursera / Teachable / website |
| MP4 9:16 | 1080p | TikTok / Reels micro-course clip |
| SCORM 1.2/2004 | — | Corporate LMS with completion tracking |
| SRT/VTT | — | Sidecar captions for accessibility |

## Related Skills

- [ai-explainer-video-maker](/skills/ai-explainer-video-maker) — Explainer video production
- [ai-presentation-video](/skills/ai-presentation-video) — Presentation video creation
- [ai-interview-video](/skills/ai-interview-video) — Interview video editing
