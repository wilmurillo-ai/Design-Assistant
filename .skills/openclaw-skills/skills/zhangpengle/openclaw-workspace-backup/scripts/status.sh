#!/bin/bash

# Workspace Backup Status Script
# 动态读取 openclaw.json 中的 agents 配置，显示所有工作空间状态

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
DEFAULT_WORKSPACE="$HOME/.openclaw/workspace"

# Get default workspace from openclaw.json
get_default_workspace() {
    if [[ -f "$OPENCLAW_CONFIG" ]]; then
        python3 -c "
import json
with open('$OPENCLAW_CONFIG') as f:
    config = json.load(f)
    workspace = config.get('agents', {}).get('defaults', {}).get('workspace', '$DEFAULT_WORKSPACE')
    print(workspace)
" 2>/dev/null || echo "$DEFAULT_WORKSPACE"
    else
        echo "$DEFAULT_WORKSPACE"
    fi
}

# Get agents list from openclaw.json
get_agents_list() {
    if [[ -f "$OPENCLAW_CONFIG" ]]; then
        python3 -c "
import json
with open('$OPENCLAW_CONFIG') as f:
    config = json.load(f)
    agents = config.get('agents', {}).get('list', [])
    for agent in agents:
        agent_id = agent.get('id', '')
        workspace = agent.get('workspace', '')
        if agent_id:
            print(f'{agent_id}|{workspace}')
" 2>/dev/null
    fi
}

echo "=== Workspace Backup Status ==="
echo ""

DEFAULT_WS=$(get_default_workspace)

# Show status for each agent workspace
while IFS='|' read -r agent_id custom_workspace; do
    if [[ -n "$agent_id" ]]; then
        workspace_path="${custom_workspace:-$DEFAULT_WS}"
        echo "--- $agent_id (branch: $agent_id, path: $workspace_path) ---"
        if [[ -d "$workspace_path" ]]; then
            cd "$workspace_path" && git status --short 2>/dev/null || echo "Not a git repo"
        else
            echo "Directory does not exist"
        fi
        echo ""
    fi
done < <(get_agents_list)

echo "=== Last Backup Log ==="
tail -20 ~/.openclaw/logs/backup.log 2>/dev/null || echo "No backup log found"
