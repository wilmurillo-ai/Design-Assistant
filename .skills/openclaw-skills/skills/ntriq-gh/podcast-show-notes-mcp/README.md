# Podcast Show Notes MCP Server

Generate structured podcast show notes, chapters, and highlights from audio. Powered by Whisper (OpenAI) and Qwen AI. No full transcript stored — only structured summaries, chapters, and key quotes.

## Features

| Tool | Description | Price |
|------|-------------|-------|
| `generate_show_notes` | Podcast show notes with key takeaways (brief or detailed) | $0.10/use |
| `generate_chapters` | Timestamped chapter markers for navigation | $0.08/use |
| `extract_highlights` | Key quotes and action items (short excerpts only) | $0.12/use |

## Connect via Claude Desktop

Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "podcast-show-notes": {
      "url": "https://ntriqpro--podcast-show-notes-mcp.apify.actor/mcp?token=YOUR_APIFY_TOKEN"
    }
  }
}
```

## Supported Audio Formats

MP3, WAV, M4A, OGG, FLAC, WebM, and other common podcast formats.

## Input Parameters

### generate_show_notes
- `audioUrl` (required): URL of the podcast audio file
- `style` (optional): "brief" (3-5 takeaways) or "detailed" (sections with summary). Default: "detailed"

### generate_chapters
- `audioUrl` (required): URL of the podcast audio file

### extract_highlights
- `audioUrl` (required): URL of the podcast audio file

## Output Examples

### generate_show_notes (detailed)
```json
{
  "status": "success",
  "show_notes": {
    "summary": "This episode discusses quarterly business performance, highlighting new market expansion into Asia...",
    "sections": [
      {
        "title": "Summary",
        "content": "Full summary of the episode..."
      }
    ]
  },
  "key_takeaways": [
    "Revenue growth exceeded targets by 15%",
    "New Asia market shows strong early adoption",
    "Team hiring accelerating Q3-Q4",
    "Product roadmap shifted to include AI features",
    "Budget allocation approved for R&D"
  ],
  "topics": [
    "quarterly review",
    "market expansion",
    "revenue growth",
    "product development"
  ],
  "style": "detailed",
  "disclaimer": "AI-generated show notes. Not approved by or affiliated with podcast creator. For personal reference only. Do not redistribute without creator permission.",
  "model": "whisper + qwen3.5"
}
```

### generate_chapters
```json
{
  "status": "success",
  "chapters": [
    {
      "timestamp": "00:00:00",
      "title": "Introduction"
    },
    {
      "timestamp": "00:12:30",
      "title": "Q1 Results Review"
    },
    {
      "timestamp": "00:25:45",
      "title": "Asia Market Expansion"
    },
    {
      "timestamp": "00:38:20",
      "title": "Product Roadmap Update"
    },
    {
      "timestamp": "00:50:00",
      "title": "Q&A and Closing"
    }
  ],
  "total_chapters": 5,
  "disclaimer": "AI-generated show notes. Not approved by or affiliated with podcast creator. For personal reference only. Do not redistribute without creator permission.",
  "model": "whisper + qwen3.5"
}
```

### extract_highlights
```json
{
  "status": "success",
  "highlights": [
    {
      "quote": "We're seeing 40% month-over-month growth in the Asia region",
      "context": "Discussing new market expansion strategy..."
    },
    {
      "quote": "Our team is doubling down on AI-driven features",
      "context": "Product roadmap update..."
    },
    {
      "quote": "This quarter was our strongest quarter in company history",
      "context": "Reviewing quarterly financial results..."
    }
  ],
  "action_items": [
    "Finalize Asia market expansion plan by end of Q2",
    "Schedule board meeting for budget approval",
    "Begin hiring for new R&D team",
    "Complete AI feature specification document"
  ],
  "speakers_estimated": 2,
  "disclaimer": "AI-generated show notes. Not approved by or affiliated with podcast creator. For personal reference only. Do not redistribute without creator permission.",
  "model": "whisper + qwen3.5"
}
```

## Important Notes

### No Full Transcript Stored
- Only summaries, chapters, and key quotes (short excerpts) are returned
- Full verbatim transcripts are never returned or stored
- Audio is processed in real-time and not retained

### Legal Disclaimer
Users are solely responsible for ensuring they have obtained all necessary consents and authorizations before submitting podcast recordings for processing. This service:
- Does not store audio or generate full transcripts
- Processes audio in real-time only
- Returns structured summaries and insights only
- Complies with privacy and copyright regulations

### Technology Stack
- **Speech Recognition**: OpenAI Whisper (MIT License)
- **Text Analysis**: Qwen 3.5 (Apache 2.0 License)
- **Processing**: Local AI inference (no third-party data sharing)

## Licensing

This service uses the following open source models:
- [OpenAI Whisper](https://github.com/openai/whisper) — MIT License
- [Qwen 3.5](https://huggingface.co/Qwen/Qwen3.5-4B) — Apache 2.0 License

See respective repositories for full license terms.

## Use Cases

- **Content Creators**: Generate show notes and chapters for podcast hosting platforms
- **Researchers**: Extract key points and action items from interviews or seminars
- **Podcast Listeners**: Create personal study guides from educational podcasts
- **Teams**: Document meeting transcripts and action items
- **Media Organizations**: Bulk process podcast catalogs for searchability

Platform usage is free. You only pay per tool use (see pricing above).
