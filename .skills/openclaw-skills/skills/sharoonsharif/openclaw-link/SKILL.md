---
name: clawlink
description: >
  Cross-instance agent communication for OpenClaw. ClawLink lets multiple OpenClaw
  sessions discover each other, delegate tasks, share knowledge, collaboratively
  edit files, and work as a coordinated agent mesh — across different machines on
  a network or across the internet. Use this skill whenever the user mentions
  connecting OpenClaw instances, multi-agent workflows, agent-to-agent communication,
  delegating tasks between sessions, collaborative AI work, agent discovery, swarm
  tasks, or running agents on multiple machines. Also trigger when the user says
  things like "ask my other agent to...", "have another Claude work on...",
  "set up agent communication", "multi-machine", "agent mesh", "distributed agents",
  or "ClawLink". If the user wants two or more AI sessions to work together in any
  way, this is the skill to use.
---

# ClawLink — Cross-Instance Agent Communication

ClawLink turns isolated OpenClaw sessions into a **collaborative agent mesh**. Any
OpenClaw instance on any machine can join the network to delegate tasks, share
findings, co-edit files, and coordinate work — like a team of AI agents that
can actually talk to each other.

## Architecture

```
  Machine A (OpenClaw)          Machine B (OpenClaw)          Machine C (OpenClaw)
       │                              │                              │
       └──── HTTP/WebSocket ──────────┼──── HTTP/WebSocket ──────────┘
                                      │
                              ┌───────┴───────┐
                              │  ClawLink      │
                              │  Relay Server  │
                              │  (any machine) │
                              └────────────────┘
```

One machine runs the relay server. All others connect as agent clients. The relay
is lightweight (~200 lines of Python) and handles message routing, queuing, and
agent registry.

## Quick Start

### Step 1: Start the Relay Server

On any machine that's reachable by all agents (can be one of the agent machines):

```bash
# Install dependencies
pip install aiohttp requests

# Optional: LAN auto-discovery
pip install zeroconf

# Start the relay
python3 scripts/server.py --host 0.0.0.0 --port 9077
```

The server will print its LAN IP and port. If zeroconf is installed, other machines
on the LAN will auto-discover it.

For internet-wide access, use a tunnel:
```bash
# Option A: ngrok
ngrok http 9077

# Option B: Cloudflare Tunnel
cloudflared tunnel --url localhost:9077
```

### Step 2: Register This Agent

Once the relay is running, register this OpenClaw session as an agent. Run this
in the terminal:

```bash
python3 /path/to/clawlink/scripts/client.py \
  --relay http://RELAY_IP:9077 \
  register \
  --name "DESCRIPTIVE_NAME" \
  --caps "COMMA_SEPARATED_CAPABILITIES" \
  --description "What this agent specializes in"
```

Choose a descriptive name that tells other agents what you do (e.g., "researcher",
"coder", "reviewer", "writer"). Capabilities should reflect what this session is
good at (e.g., "code,debug,test" or "search,summarize,analyze").

The client saves your agent identity to `~/.clawlink/agent_state.json` so you
don't need to re-register after reconnecting.

### Step 3: Discover and Communicate

See who's online:
```bash
python3 scripts/client.py --relay http://RELAY_IP:9077 discover
```

## Core Operations

When you need to perform ClawLink operations, use the client CLI tool. Here are
the operations available and when to use each one.

### Discovering Peers

Before delegating or communicating, check who's online:

```bash
python3 scripts/client.py discover
```

This returns a table of online agents with their IDs, names, capabilities, and
machines. Use the agent_id to target specific agents.

### Delegating Tasks

When the user wants another agent to do something, or when a task would benefit
from a different agent's capabilities:

```bash
python3 scripts/client.py delegate \
  --to TARGET_AGENT_ID \
  --task "Clear description of what needs to be done" \
  --context '{"key": "relevant context data"}' \
  --priority normal
```

Good delegation practices:
- Be specific about the task and expected output format
- Include relevant context (file paths, URLs, constraints)
- Choose the right agent based on their declared capabilities
- Use priority levels: "low", "normal", "high", "urgent"

### Receiving and Responding to Tasks

Poll for incoming messages regularly:

```bash
python3 scripts/client.py poll
```

When you receive a task_delegation message, execute the task and respond:

```bash
python3 scripts/client.py respond \
  --to REQUESTING_AGENT_ID \
  --msg-id ORIGINAL_MESSAGE_ID \
  --result "Task result or summary of work done"
```

### Broadcasting Knowledge

When you discover something useful that all agents should know:

```bash
python3 scripts/client.py broadcast \
  --content "Description of the finding or knowledge" \
  --topic "category" \
  --tags "tag1,tag2,tag3"
```

Use broadcasts for:
- Research findings that change the direction of work
- Errors or blockers other agents should know about
- Status updates on long-running tasks
- Shared decisions or conclusions

### Collaborative File Editing

To share a file with the mesh:

```bash
# Upload/update a shared file
python3 scripts/client.py file-put --key "report.md" --file ./report.md

# Download a shared file
python3 scripts/client.py file-get --key "report.md" --output ./report.md

# See all shared files
python3 scripts/client.py file-list
```

File collaboration pattern:
1. One agent creates the initial file with `file-put`
2. Other agents retrieve it with `file-get`
3. Each agent makes their additions/edits
4. Updated version goes back with `file-put` (version is auto-incremented)
5. Agents are notified of updates automatically

## Behavioral Guidelines for Agents

When operating as a ClawLink agent, follow these principles:

### As a Task Receiver
1. **Poll regularly** — Check for messages every 30-60 seconds during active work,
   or when the user asks "any messages?" or "check ClawLink"
2. **Acknowledge receipt** — When you get a task, let the requesting agent know
   you're working on it (respond with status "in_progress")
3. **Be thorough** — Complete the full task before responding. Include enough
   detail that the requester can use your output directly.
4. **Report failures** — If you can't complete a task, respond with status "failed"
   and explain why.

### As a Task Delegator
1. **Match capabilities** — Use `discover` to find the right agent for the job.
   Don't send code tasks to a research agent.
2. **Provide context** — Include file paths, URLs, constraints, and output format
   in the context field. The receiving agent has no access to your local state.
3. **Be patient** — The other agent may take time. Poll for responses rather than
   re-delegating.

### As a Knowledge Sharer
1. **Broadcast important findings** — If you learn something that changes the
   approach, broadcast it immediately.
2. **Use topics and tags** — Help other agents filter relevant broadcasts.
3. **Don't spam** — Only broadcast genuinely useful information.

### General
- Always tell the user what's happening on the network
- Surface incoming messages proactively
- Suggest delegation when a task would benefit from another agent's specialization
- Keep heartbeats alive during long sessions

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Check relay is running and IP/port are correct |
| Can't find relay on LAN | Install zeroconf, or use explicit --relay URL |
| Messages not arriving | Check agent_id matches, run heartbeat to re-register |
| Agent shows "stale" | The agent hasn't heartbeated in 120s — restart or heartbeat |
| Need internet access | Use ngrok or cloudflare tunnel on the relay machine |

## Protocol Reference

For the full message format specification, transport layer details, and workflow
patterns, read `references/protocol.md`.
