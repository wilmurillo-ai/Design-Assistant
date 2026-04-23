---
name: mysta-sync
description: >-
  Sync local OpenClaw skills to a remote NanoClaw agent on Mysta. Use when the
  user says "sync my skills", "upload skills to mysta", "push skills to my
  nanoclaw agent", or wants to make their local skills available on their cloud
  agent. Connects to the Mysta MCP server to list agents and upload skill files.
  Requires network access and a Mysta API key (obtained from app.mysta.tech).
  Reads local SKILL.md files from the skills directory.
license: MIT
compatibility: >-
  Requires network access to the Mysta MCP server (api.dev.mysta.tech or custom base URL).
  Requires curl and jq for MCP protocol calls. Reads local SKILL.md files from the
  OpenClaw skills directory (~/.openclaw/skills or ~/Workspace/openclaw/skills).
  User must provide a Mysta API key (starts with mysta_) obtained from
  http://app.dev.mysta.tech/en/profile#api-keys.
metadata:
  author: mysta
  version: "0.2.0"
  openclaw:
    emoji: "☁️"
    requires:
      allBins: ["curl", "jq"]
      tools: ["read", "exec"]
  clawhub: { "tags": ["mysta", "nanoclaw", "sync", "skills", "cloud"] }
homepage: "http://app.dev.mysta.tech"
---

# Mysta Skill Sync

Sync local OpenClaw skills to a remote NanoClaw agent on the Mysta platform via MCP (Model Context Protocol).

## Authentication

The user needs a Mysta API key (starts with `mysta_`). If they haven't provided one:

1. Open their browser to the API keys page:

```bash
open "http://app.dev.mysta.tech/en/profile#api-keys"
```

2. Tell them: **"I've opened the Mysta API keys page in your browser. Log in if needed, then create a new API key and paste it here."**

3. Wait for the user to paste their key.

The default MCP server URL is `http://api.dev.mysta.tech/api/v2/mcp`.

## MCP Protocol

All communication uses the MCP Streamable HTTP transport. Each request is a JSON-RPC call via HTTP POST. The flow is:

1. **Initialize** a session (get a session ID)
2. **Call tools** using the session ID
3. **Close** the session when done

### Initialize session

```bash
MCP_RESPONSE=$(curl -sf -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "Authorization: Bearer ${MYSTA_API_KEY}" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"openclaw","version":"1.0.0"}}}' \
  -D /tmp/mcp-headers.txt)

MCP_SESSION=$(grep -i "mcp-session-id" /tmp/mcp-headers.txt | tr -d '\r' | awk '{print $2}')
```

Then send the initialized notification:

```bash
curl -sf -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MYSTA_API_KEY}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}'
```

### Call a tool

```bash
RESULT=$(curl -sf -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${MYSTA_API_KEY}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d "$(jq -n --arg name "TOOL_NAME" --argjson args 'ARGS_JSON' \
    '{jsonrpc:"2.0",id:2,method:"tools/call",params:{name:$name,arguments:$args}}')")
```

The response may be SSE (text/event-stream) — parse `data:` lines for JSON-RPC results.

### Close session

```bash
curl -sf -X DELETE "${MCP_URL}" \
  -H "Authorization: Bearer ${MYSTA_API_KEY}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}"
```

## Workflow

### Step 1: Initialize MCP session

Initialize using the protocol above. Store `MCP_SESSION` for all subsequent calls.

### Step 2: List agents

Call the `mysta_list_agents` tool:

```bash
RESULT=$(curl -sf -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${MYSTA_API_KEY}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"mysta_list_agents","arguments":{}}}')
```

Parse the response to find agent IDs and names.

- If **no agents** found, tell the user to create one at http://app.dev.mysta.tech
- If **one agent**, auto-select it
- If **multiple**, ask which one to sync to

### Step 3: Scan local skills

Find all SKILL.md files in the OpenClaw skills directories:

```bash
find ~/Workspace/openclaw/skills -maxdepth 2 -name "SKILL.md" -type f 2>/dev/null
```

For each skill, the name is the parent directory name.

Present the list and ask:
- **"all"** → sync everything
- **specific names** → sync only those
- **"cancel"** → abort

### Step 4: Upload skills via MCP

For each selected skill, read the content and call `mysta_sync_skill`:

```bash
SKILL_CONTENT=$(cat "$SKILL_PATH")
RESULT=$(curl -sf -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${MYSTA_API_KEY}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d "$(jq -n --arg name "$SKILL_NAME" --arg content "$SKILL_CONTENT" --arg agentId "$AGENT_ID" \
    '{jsonrpc:"2.0",id:3,method:"tools/call",params:{name:"mysta_sync_skill",arguments:{agentId:$agentId,skillName:$name,content:$content}}}')")
```

Alternatively, use `mysta_sync_all_skills` to batch upload:

```bash
# Build skills JSON array
SKILLS_JSON=$(for skill_path in $SELECTED_SKILLS; do
  name=$(basename $(dirname "$skill_path"))
  content=$(cat "$skill_path")
  jq -n --arg name "$name" --arg content "$content" '{name:$name,content:$content}'
done | jq -s '.')

RESULT=$(curl -sf -X POST "${MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${MYSTA_API_KEY}" \
  -H "Mcp-Session-Id: ${MCP_SESSION}" \
  -d "$(jq -n --arg agentId "$AGENT_ID" --argjson skills "$SKILLS_JSON" \
    '{jsonrpc:"2.0",id:3,method:"tools/call",params:{name:"mysta_sync_all_skills",arguments:{agentId:$agentId,skills:$skills}}}')")
```

### Step 5: Close session and report results

Close the MCP session, then show a summary:
- Total skills synced
- Any failures with error details
- If the agent's dev pod was running, skills are live immediately
- If not running, tell user to start the dev pod on http://app.dev.mysta.tech to apply skills

## Notes

- Skills are uploaded to OSS for audit and pushed to the agent's NAS-mounted storage.
- Skills persist across pod restarts.
- Re-uploading a skill with the same name overwrites it (idempotent).
- This does NOT publish the agent. Publishing is a separate action on the Mysta platform.
- The MCP server handles auth, OSS audit, DB metadata update, and live push to running pods — all in one call.
