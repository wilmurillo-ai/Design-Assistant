---
name: strider-netflix
description: Manage Netflix via Strider Labs MCP connector. Browse catalog, search content, manage watchlist, control playback, get recommendations. Complete autonomous streaming control for your AI agent.
metadata:
  openclaw:
    requires:
      bins: ["npx"]
    category: "entertainment"
    author: "Strider Labs"
    homepage: "https://striderlabs.ai"
---

# Strider Netflix Connector

MCP connector for managing Netflix — browse catalog, search content, manage watchlist, control playback, and get personalized recommendations. Part of the Strider Labs action execution layer for AI agents.

## Installation

```bash
npm install @striderlabs/mcp-netflix
```

## MCP Configuration

Add to your MCP client configuration (Claude Desktop, Cursor, etc.):

```json
{
  "mcpServers": {
    "netflix": {
      "command": "npx",
      "args": ["-y", "@striderlabs/mcp-netflix"]
    }
  }
}
```

## Available Tools

### netflix.search
Search for movies and TV shows.

**Input Schema:**
```json
{
  "query": "string (title, actor, director)",
  "type": "string (optional: movie, series)",
  "genre": "string (optional: comedy, drama, action, etc.)"
}
```

**Output:**
```json
{
  "results": [{
    "id": "string",
    "title": "string",
    "type": "string",
    "year": "number",
    "rating": "string (TV-MA, PG-13, etc.)",
    "match_score": "number (percent match)",
    "synopsis": "string"
  }]
}
```

### netflix.get_details
Get full details for a title including cast, seasons, and episodes.

### netflix.add_to_list
Add a title to My List.

### netflix.remove_from_list
Remove a title from My List.

### netflix.get_my_list
Get current My List contents.

### netflix.get_continue_watching
Get titles in progress.

### netflix.play
Start playback of a title.

**Input Schema:**
```json
{
  "title_id": "string",
  "season": "number (optional: for series)",
  "episode": "number (optional: for series)",
  "device": "string (optional: tv, phone, laptop)"
}
```

### netflix.get_recommendations
Get personalized recommendations.

**Output:**
```json
{
  "rows": [{
    "category": "string (Top 10, Because You Watched, etc.)",
    "titles": [...]
  }]
}
```

### netflix.get_new_releases
Get newly added content.

## Authentication

First use triggers OAuth with Netflix account. Profile selection supported. Tokens stored encrypted per-user.

## Usage Examples

**Find something:**
```
What's new on Netflix this week?
```

**Search:**
```
Search Netflix for sci-fi movies released in the last year
```

**Add to list:**
```
Add Stranger Things to my Netflix list
```

**Play content:**
```
Play The Office on Netflix, season 3 episode 1
```

**Get recommendations:**
```
What should I watch on Netflix based on my history?
```

## Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| AUTH_EXPIRED | Session expired | Re-authenticate |
| PROFILE_REQUIRED | Multiple profiles | Prompt profile selection |
| NOT_AVAILABLE | Content removed | Suggest alternatives |
| DEVICE_LIMIT | Too many streams | Stop another device |

## Use Cases

- Movie night: find something to watch
- Binge planning: add series to watchlist
- Discovery: explore new releases and recommendations
- Playback control: start content on specific devices

## Links

- npm: https://npmjs.com/package/@striderlabs/mcp-netflix
- Strider Labs: https://striderlabs.ai
