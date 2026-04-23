#!/bin/bash

# Workspace Backup Script
# 动态读取 openclaw.json 中的 agents 配置，备份所有工作空间到 GitHub 仓库的不同分支

OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
LOG_FILE="$HOME/.openclaw/logs/backup.log"
DEFAULT_WORKSPACE="$HOME/.openclaw/workspace"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

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
import sys
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

backup_workspace() {
    local workspace_path="$1"
    local branch="$2"
    local workspace_name="$3"

    log "Starting backup for $workspace_name (branch: $branch, path: $workspace_path)"

    if [[ ! -d "$workspace_path" ]]; then
        log "WARNING: Workspace directory does not exist: $workspace_path"
        return 0
    fi

    cd "$workspace_path" || {
        log "ERROR: Cannot cd to $workspace_path"
        return 1
    }

    # Check if it's a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "WARNING: Not a git repository: $workspace_path"
        return 0
    fi

    # Add all changes first
    git add -A

    # Check if there are changes to commit
    if git diff --cached --quiet; then
        log "No changes to commit for $workspace_name"
        return 0
    fi

    # Commit with timestamp
    commit_msg="Backup $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$commit_msg" || {
        log "ERROR: Failed to commit for $workspace_name"
        return 1
    }

    # Push to remote
    git push origin "$branch" || {
        log "ERROR: Failed to push $workspace_name"
        return 1
    }

    log "Successfully backed up $workspace_name"
    return 0
}

# Main
log "========== Workspace Backup Started =========="

DEFAULT_WS=$(get_default_workspace)
log "Default workspace: $DEFAULT_WS"

# Backup each agent workspace
while IFS='|' read -r agent_id custom_workspace; do
    if [[ -n "$agent_id" ]]; then
        # Use custom workspace if specified, otherwise use default
        workspace_path="${custom_workspace:-$DEFAULT_WS}"
        backup_workspace "$workspace_path" "$agent_id" "$agent_id"
    fi
done < <(get_agents_list)

log "========== Workspace Backup Completed =========="
