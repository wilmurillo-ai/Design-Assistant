#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
AGENCY_DIR="${OPENCLAW_AGENCY_DIR:-$PROJECT_DIR/reference/agency-agents-main}"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage: plan.sh [OPTIONS] "<task description>"

Analyze a task and generate a team proposal with activation order.

Options:
  -m, --mode MODE     Force mode: micro (1-3 agents), sprint (5-10), full (10+)
                      Default: auto-detect from task complexity
  -o, --output FILE   Write proposal to file (default: stdout)
  -h, --help          Show this help

Example:
  plan.sh "Build a portfolio dashboard with pie charts"
  plan.sh --mode sprint "Optimize image generation prompts using autoresearch"
USAGE
}

mode=""
output=""
task=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--mode)    mode="${2-}"; shift 2 ;;
    -o|--output)  output="${2-}"; shift 2 ;;
    -h|--help)    usage; exit 0 ;;
    *)            task="$1"; shift ;;
  esac
done

if [ -z "$task" ]; then
  echo "Error: task description required" >&2
  usage >&2
  exit 1
fi

task_lower=$(echo "$task" | tr '[:upper:]' '[:lower:]')

domains=()
primary_roster=""

if echo "$task_lower" | grep -qE 'build|implement|code|fix|api|database|frontend|backend|server|deploy|bug|feature'; then
  domains+=("engineering")
  primary_roster="${primary_roster:-agency-engineering}"
fi
if echo "$task_lower" | grep -qE 'image|design|generat|logo|chart|photo|visual|creative|art|brand|ui |ux '; then
  domains+=("creative")
  primary_roster="${primary_roster:-core-artist}"
fi
if echo "$task_lower" | grep -qE 'experiment|optim|tune|analyz|iterat|research|metric|baseline|improve'; then
  domains+=("research")
fi
if echo "$task_lower" | grep -qE 'launch|campaign|content|social|audience|marketing|growth|seo|twitter|tiktok|reddit'; then
  domains+=("marketing")
  primary_roster="${primary_roster:-agency-marketing}"
fi
if echo "$task_lower" | grep -qE 'monitor|report|compliance|finance|analytics|data |dashboard'; then
  domains+=("operations")
fi
if echo "$task_lower" | grep -qE 'ar |vr |xr |vision pro|spatial|immersive|3d '; then
  domains+=("spatial")
fi

[ ${#domains[@]} -eq 0 ] && domains+=("general")
[ -z "$primary_roster" ] && primary_roster="core-ceo"

if [ -z "$mode" ]; then
  if [ ${#domains[@]} -ge 3 ]; then
    mode="full"
  elif [ ${#domains[@]} -ge 2 ]; then
    mode="sprint"
  else
    mode="micro"
  fi
fi

count_agents() {
  local dir="$1"
  [ -d "$dir" ] && find "$dir" -name "*.md" -not -name "README*" -not -name "CONTRIB*" -not -name "LICENSE*" | wc -l | tr -d ' '
}

generate_proposal() {
  echo "## Team Proposal"
  echo ""
  echo "### Task"
  echo "$task"
  echo ""
  echo "### Classification"
  echo "- Domains: ${domains[*]}"
  echo "- Mode: $mode"
  echo "- Primary roster: $primary_roster"
  echo ""

  echo "### Proposed Team"
  echo ""
  echo "| Role | Agent | Roster | Phase |"
  echo "|------|-------|--------|-------|"
  echo "| Leader | CEO | Core | 1-SCOPE |"

  case "$mode" in
    micro)
      for domain in "${domains[@]}"; do
        case "$domain" in
          creative)   echo "| Visual | Artist | Core | 2-BUILD |" ;;
          engineering)
            echo "| Developer | Senior Developer | Agency/Engineering | 2-BUILD |"
            ;;
          marketing)
            echo "| Marketing | Growth Hacker | Agency/Marketing | 2-BUILD |"
            ;;
          operations)
            echo "| Analytics | Analytics Reporter | Agency/Specialized | 2-BUILD |"
            ;;
          spatial)
            echo "| Spatial Dev | XR Immersive Developer | Agency/Spatial | 2-BUILD |"
            ;;
          research)
            echo "| Experiment | Research Lab | Research | 2-BUILD |"
            ;;
        esac
      done
      echo "| QA | Evidence Collector | Agency/Testing | 3-REVIEW |"
      ;;

    sprint)
      echo "| Scoping | Senior PM | Agency/PM | 1-SCOPE |"
      echo "| Prioritization | Sprint Prioritizer | Agency/Product | 1-SCOPE |"
      for domain in "${domains[@]}"; do
        case "$domain" in
          creative)
            echo "| Visual | Artist | Core | 2-BUILD |"
            echo "| Prompts | Image Prompt Engineer | Agency/Design | 2-BUILD |"
            ;;
          engineering)
            echo "| Frontend | Frontend Developer | Agency/Engineering | 2-BUILD |"
            echo "| Backend | Backend Architect | Agency/Engineering | 2-BUILD |"
            ;;
          marketing)
            echo "| Growth | Growth Hacker | Agency/Marketing | 2-BUILD |"
            echo "| Content | Content Creator | Agency/Marketing | 2-BUILD |"
            ;;
          operations)
            echo "| Analytics | Analytics Reporter | Agency/Specialized | 2-BUILD |"
            ;;
          spatial)
            echo "| Spatial | XR Interface Architect | Agency/Spatial | 2-BUILD |"
            echo "| Spatial Dev | XR Immersive Developer | Agency/Spatial | 2-BUILD |"
            ;;
          research)
            echo "| Experiment | Research Lab | Research | 2-BUILD |"
            echo "| Tracking | Experiment Tracker | Agency/PM | 2-BUILD |"
            ;;
        esac
      done
      echo "| QA | Evidence Collector | Agency/Testing | 3-REVIEW |"
      echo "| Gate | Reality Checker | Agency/Testing | 3-REVIEW |"
      ;;

    full)
      echo "| Scoping | Senior PM | Agency/PM | 1-SCOPE |"
      echo "| Prioritization | Sprint Prioritizer | Agency/Product | 1-SCOPE |"
      echo "| Orchestration | Agents Orchestrator | Agency/Specialized | 1-SCOPE |"
      for domain in "${domains[@]}"; do
        case "$domain" in
          creative)
            echo "| Visual | Artist | Core | 2-BUILD |"
            echo "| Prompts | Image Prompt Engineer | Agency/Design | 2-BUILD |"
            echo "| Brand | Brand Guardian | Agency/Design | 2-BUILD |"
            echo "| UX | UX Architect | Agency/Design | 2-BUILD |"
            ;;
          engineering)
            echo "| Frontend | Frontend Developer | Agency/Engineering | 2-BUILD |"
            echo "| Backend | Backend Architect | Agency/Engineering | 2-BUILD |"
            echo "| DevOps | DevOps Automator | Agency/Engineering | 2-BUILD |"
            echo "| Senior Dev | Senior Developer | Agency/Engineering | 2-BUILD |"
            ;;
          marketing)
            echo "| Growth | Growth Hacker | Agency/Marketing | 2-BUILD |"
            echo "| Content | Content Creator | Agency/Marketing | 2-BUILD |"
            echo "| Social | Social Media Strategist | Agency/Marketing | 2-BUILD |"
            ;;
          operations)
            echo "| Analytics | Analytics Reporter | Agency/Specialized | 2-BUILD |"
            echo "| Finance | Finance Tracker | Agency/Support | 2-BUILD |"
            ;;
          spatial)
            echo "| XR Arch | XR Interface Architect | Agency/Spatial | 2-BUILD |"
            echo "| XR Dev | XR Immersive Developer | Agency/Spatial | 2-BUILD |"
            echo "| Metal | Metal Engineer | Agency/Spatial | 2-BUILD |"
            ;;
          research)
            echo "| Experiment | Research Lab | Research | 2-BUILD |"
            echo "| Tracking | Experiment Tracker | Agency/PM | 2-BUILD |"
            ;;
        esac
      done
      echo "| QA Lead | Evidence Collector | Agency/Testing | 3-REVIEW |"
      echo "| Gate | Reality Checker | Agency/Testing | 3-REVIEW |"
      echo "| Final | CEO | Core | 3-REVIEW |"
      ;;
  esac

  echo ""
  echo "### Activation Order"
  echo ""
  echo '```'
  echo "Phase 1: SCOPE"
  echo "  → Senior PM breaks task into sub-tasks with acceptance criteria"
  echo "  → Sprint Prioritizer orders by impact and dependencies"
  echo ""
  echo "Phase 2: BUILD"
  echo "  → Domain specialists execute sub-tasks"
  echo "  → Dev↔QA loops: implement → validate → iterate (max 3 retries)"
  echo ""
  echo "Phase 3: REVIEW"
  echo "  → Evidence Collector: first-pass QA (screenshots, logs)"
  echo "  → Reality Checker: production-readiness gate"
  echo "  → CEO: final sign-off"
  echo '```'
  echo ""
  echo "### Agent Activation Commands"
  echo ""
  echo "Load agent personalities before delegation:"
  echo '```bash'
  for domain in "${domains[@]}"; do
    case "$domain" in
      creative)
        echo "# Artist agent (already active as core)"
        ;;
      engineering)
        echo "bash ${SKILL_DIR}/scripts/activate.sh --division engineering --agent senior-developer"
        echo "bash ${SKILL_DIR}/scripts/activate.sh --division engineering --agent frontend-developer"
        ;;
      marketing)
        echo "bash ${SKILL_DIR}/scripts/activate.sh --division marketing --agent growth-hacker"
        ;;
    esac
  done
  echo "bash ${SKILL_DIR}/scripts/activate.sh --division testing --agent evidence-collector"
  echo '```'
}

if [ -n "$output" ]; then
  generate_proposal > "$output"
  echo "Proposal written to $output"
else
  generate_proposal
fi
