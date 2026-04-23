#!/bin/bash

################################################################################
# Agent Ops Toolkit Setup Wizard
#
# Interactive setup for nightly extraction, morning briefs, heartbeat monitoring,
# memory decay, and PARA scaffold.
#
# Does NOT auto-run commands. User runs `openclaw cron add` manually.
# All configs written to current directory.
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Defaults
DEFAULT_TIMEZONE="America/New_York"
DEFAULT_EXTRACTION_MODEL="anthropic/claude-haiku-4-5"
DEFAULT_BRIEF_MODEL="anthropic/claude-haiku-4-5"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Agent Ops Toolkit Setup Wizard${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to prompt with default
prompt_with_default() {
    local prompt_text="$1"
    local default_value="$2"
    local user_input
    
    read -p "$prompt_text [$default_value]: " user_input
    
    if [ -z "$user_input" ]; then
        echo "$default_value"
    else
        echo "$user_input"
    fi
}

# Function to prompt required field
prompt_required() {
    local prompt_text="$1"
    local user_input
    
    while true; do
        read -p "$prompt_text: " user_input
        if [ -z "$user_input" ]; then
            echo -e "${RED}Error: This field is required.${NC}"
        else
            echo "$user_input"
            return
        fi
    done
}

# 1. Timezone
echo -e "${YELLOW}1. Timezone${NC}"
echo "Used for scheduling nightly extractions and morning briefs."
TIMEZONE=$(prompt_with_default "Timezone" "$DEFAULT_TIMEZONE")
echo -e "${GREEN}✓ Timezone: $TIMEZONE${NC}"
echo ""

# 2. Telegram Chat ID (optional)
echo -e "${YELLOW}2. Telegram Chat ID (optional)${NC}"
echo "Where morning briefs are delivered. Leave blank to skip."
read -p "Telegram Chat ID [leave blank to skip]: " TELEGRAM_CHAT_ID
if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo -e "${GREEN}✓ Telegram: skipped (no morning brief)${NC}"
else
    echo -e "${GREEN}✓ Telegram Chat ID: $TELEGRAM_CHAT_ID${NC}"
fi
echo ""

# 3. Agent ID
echo -e "${YELLOW}3. Agent ID${NC}"
echo "Identifies your agent in logs and cron jobs."
# Try to read from openclaw config, otherwise use a generic default
DEFAULT_AGENT_ID="agent-$(whoami)"
if [ -f ~/.openclaw/config.json ]; then
    DEFAULT_AGENT_ID=$(grep -o '"agent_id":\s*"[^"]*"' ~/.openclaw/config.json 2>/dev/null | head -1 | cut -d'"' -f4 || echo "$DEFAULT_AGENT_ID")
fi
AGENT_ID=$(prompt_with_default "Agent ID" "$DEFAULT_AGENT_ID")
echo -e "${GREEN}✓ Agent ID: $AGENT_ID${NC}"
echo ""

# 4. Extraction Model
echo -e "${YELLOW}4. Extraction Model${NC}"
echo "Fast, cheap model for nightly fact extraction. Default: Haiku."
EXTRACTION_MODEL=$(prompt_with_default "Extraction Model" "$DEFAULT_EXTRACTION_MODEL")
echo -e "${GREEN}✓ Extraction Model: $EXTRACTION_MODEL${NC}"
echo ""

# 5. Morning Brief Model
echo -e "${YELLOW}5. Morning Brief Model${NC}"
echo "Model for synthesis and summary generation. Default: Haiku."
BRIEF_MODEL=$(prompt_with_default "Morning Brief Model" "$DEFAULT_BRIEF_MODEL")
echo -e "${GREEN}✓ Brief Model: $BRIEF_MODEL${NC}"
echo ""

# Generate cron configs
echo -e "${BLUE}Generating configuration files...${NC}"
echo ""

# Nightly extraction cron config
NIGHTLY_CONFIG=$(cat <<EOF
{
  "name": "nightly-extraction-${AGENT_ID}",
  "schedule": "0 23 * * *",
  "timezone": "${TIMEZONE}",
  "agent_id": "${AGENT_ID}",
  "description": "Nightly memory extraction: consolidate conversations and decisions into atomic facts",
  "command": "echo 'Nightly extraction running for ${AGENT_ID}' && echo 'Extract from daily notes and update items.json'",
  "model": "${EXTRACTION_MODEL}",
  "memory_path": "memory/",
  "output_path": "life/"
}
EOF
)

# Morning brief cron config
MORNING_CONFIG=$(cat <<EOF
{
  "name": "morning-brief-${AGENT_ID}",
  "schedule": "0 8 * * *",
  "timezone": "${TIMEZONE}",
  "agent_id": "${AGENT_ID}",
  "description": "Morning brief: curated summary of hot facts and priorities",
  "command": "echo 'Morning brief for ${AGENT_ID}'",
  "model": "${BRIEF_MODEL}",
  "memory_path": "memory/",
  "delivery_channel": $([ -z "$TELEGRAM_CHAT_ID" ] && echo "null" || echo "\"telegram\""),
  "delivery_target": $([ -z "$TELEGRAM_CHAT_ID" ] && echo "null" || echo "\"$TELEGRAM_CHAT_ID\"")
}
EOF
)

# Write configs to current directory
echo "$NIGHTLY_CONFIG" > nightly-extraction-cron.json
echo "$MORNING_CONFIG" > morning-brief-cron.json

echo -e "${GREEN}✓ Created nightly-extraction-cron.json${NC}"
echo -e "${GREEN}✓ Created morning-brief-cron.json${NC}"
echo ""

# Create PARA scaffold
echo -e "${BLUE}Creating PARA scaffold directories...${NC}"
mkdir -p life/projects
mkdir -p life/areas
mkdir -p life/resources
mkdir -p life/archives

echo -e "${GREEN}✓ Created life/projects/${NC}"
echo -e "${GREEN}✓ Created life/areas/${NC}"
echo -e "${GREEN}✓ Created life/resources/${NC}"
echo -e "${GREEN}✓ Created life/archives/${NC}"
echo ""

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Setup Complete!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

echo -e "${YELLOW}Configuration Summary:${NC}"
echo "  Timezone: $TIMEZONE"
echo "  Agent ID: $AGENT_ID"
echo "  Extraction Model: $EXTRACTION_MODEL"
echo "  Morning Brief Model: $BRIEF_MODEL"
if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "  Telegram: (skipped)"
else
    echo "  Telegram Chat ID: $TELEGRAM_CHAT_ID"
fi
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Review the generated config files:"
echo "   - nightly-extraction-cron.json"
echo "   - morning-brief-cron.json"
echo ""
echo "2. Activate cron jobs manually:"
echo "   ${BLUE}openclaw cron add < nightly-extraction-cron.json${NC}"
echo "   ${BLUE}openclaw cron add < morning-brief-cron.json${NC}"
echo ""
echo "3. Verify your PARA scaffold:"
echo "   ${BLUE}ls -la life/${NC}"
echo ""
echo "4. Start using your agent:"
echo "   - Add your MEMORY.md to workspace root (see persona-builder skill)"
echo "   - Review nightly extraction output in memory/YYYY-MM-DD.md"
echo "   - Check morning briefs in your Telegram (if configured)"
echo ""

echo -e "${GREEN}Done!${NC}"
