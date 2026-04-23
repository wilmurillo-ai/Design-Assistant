#!/usr/bin/env bash
# skill-guard.sh — Main security scanner for OpenClaw skills
# Usage: bash skill-guard.sh <skill-dir> [--json] [--scan-all]
#
# Modes:
#   <skill-dir>      Scan a single skill directory
#   --scan-all       Scan all installed skills (skills/ + .openclaw/skills/)
#   --json           Output results as JSON
#   --baseline       Generate hash baseline for all skills
#   --diff           Check drift against baseline
#   --vt-api KEY     Enable VirusTotal scanning (free tier: 500 req/day)

set -uo pipefail

# ─── Config ──────────────────────────────────────────────────────────────────
HASH_ALGO="sha256"
BASELINE_FILE=""
SCAN_JSON=false
SCAN_VT=false
VT_API_KEY=""
SCAN_ALL=false
DIFF_MODE=false
BASELINE_MODE=false
REPORT_DIR=""
TARGET=""

# ─── Colors ──────────────────────────────────────────────────────────────────
# Detect color support
if [[ -t 1 ]] && command -v tput &>/dev/null && [[ $(tput colors 2>/dev/null) -ge 8 ]]; then
  RED='\033[0;31m'; YELLOW='\033[1;33m'; GREEN='\033[0;32m'
  ORANGE='\033[0;33m'; BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'
else
  RED=''; YELLOW=''; GREEN=''; ORANGE=''; BLUE=''; NC=''; BOLD=''
fi

# ─── Args ────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)       SCAN_JSON=true; shift ;;
    --scan-all)   SCAN_ALL=true; shift ;;
    --baseline)   BASELINE_MODE=true; shift ;;
    --diff)       DIFF_MODE=true; shift ;;
    --vt-api)     VT_API_KEY="$2"; SCAN_VT=true; shift 2 ;;
    --report-dir) REPORT_DIR="$2"; shift 2 ;;
    *)            break ;;
  esac
done

TARGET="${1:-}"

# ─── Helpers ─────────────────────────────────────────────────────────────────
skill_name() { basename "$1"; }

find_skills() {
  local dirs=()
  # Check workspace skills/
  [[ -d "skills" ]] && dirs+=("skills")
  # Check .openclaw workspace skills
  [[ -d ".openclaw/workspace/skills" ]] && dirs+=(".openclaw/workspace/skills")
  # Check global OpenClaw skills
  local global
  global="$(npm root -g 2>/dev/null)/openclaw/skills" || true
  [[ -d "$global" ]] && dirs+=("$global")
  for d in "${dirs[@]}"; do
    for sub in "$d"/*/; do
      [[ -f "$sub/SKILL.md" ]] && echo "$sub"
    done
  done
}

# Skills to exclude from scanning (self + reference files)
EXCLUDE_PATTERNS="security-patterns.md"

file_count() { find "$1" -type f ! -name "*.skill" | wc -l; }
total_size() { du -sh "$1" 2>/dev/null | cut -f1; }

# ─── Pattern Scanning ────────────────────────────────────────────────────────
# Categories: exec, network, filesystem, secrets, obfuscation, elevated

declare -A PATTERNS
# Exec patterns (HIGH risk)
PATTERNS[exec_danger]="exec\(|child_process|os\.system|subprocess|spawn|eval\(|Function\("
# Network patterns (MEDIUM risk)
PATTERNS[network]="curl |wget |fetch\(|http\.get|http\.post|axios|requests\.(get|post)|urllib"
# Filesystem outside workspace (MEDIUM risk)
PATTERNS[fs_external]="rm -rf|/etc/|/var/|/tmp/|chmod 777|chown"
# Secret patterns (HIGH risk)
PATTERNS[secrets]="AKIA[0-9A-Z]{16}|ghp_[0-9a-zA-Z]{36}|sk_live_[0-9a-zA-Z]{24}|xox[bposa]-[0-9-]+|eyJ[a-zA-Z0-9._-]+\.eyJ"
# Obfuscation (HIGH risk)
PATTERNS[obfuscation]="base64 -d|atob\(|Buffer\.from.*encoding|\\\\x[0-9a-fA-F]{2}.*\\\\x[0-9a-fA-F]{2}"
# Elevated (HIGH risk)
PATTERNS[elevated]="sudo |su -|runas|Set-ExecutionPolicy Bypass|New-Object System.Diagnostics.Process"

scan_patterns() {
  local dir="$1"
  local results=()
  for category in "${!PATTERNS[@]}"; do
    local matches
    matches=$(grep -r -n -E -I "${PATTERNS[$category]}" "$dir" \
      --include="*.md" --include="*.sh" --include="*.js" --include="*.ts" --include="*.py" \
      --exclude-dir=references 2>/dev/null || true)
    if [[ -n "$matches" ]]; then
      local count
      count=$(echo "$matches" | wc -l)
      results+=("$category:$count")
    fi
  done
  printf '%s\n' "${results[@]}"
}

# ─── Risk Scoring ───────────────────────────────────────────────────────────
calculate_risk() {
  local dir="$1"
  local score=0
  local level="LOW"
  local color="$GREEN"
  local emoji="🟢"

  local pattern_results
  pattern_results=$(scan_patterns "$dir")
  
  while IFS=: read -r category count; do
    [[ -z "$category" ]] && continue
    case "$category" in
      exec_danger)  ((score += count * 20)) ;;
      network)      ((score += count * 10)) ;;
      fs_external)  ((score += count * 15)) ;;
      secrets)      ((score += count * 25)) ;;
      obfuscation)  ((score += count * 30)) ;;
      elevated)     ((score += count * 20)) ;;
    esac
  done <<< "$pattern_results"

  # File count factor
  local fc
  fc=$(file_count "$dir")
  ((fc > 20)) && ((score += 10))

  if (( score >= 60 )); then
    level="HIGH"; color="$RED"; emoji="🔴"
  elif (( score >= 30 )); then
    level="MEDIUM"; color="$ORANGE"; emoji="🟠"
  elif (( score >= 10 )); then
    level="LOW"; color="$YELLOW"; emoji="🟡"
  else
    level="MINIMAL"; color="$GREEN"; emoji="🟢"
  fi

  echo "$level:$score:$emoji"
}

# ─── Permission Footprint ───────────────────────────────────────────────────
check_permissions() {
  local dir="$1"
  local perms=()
  
  grep -r -q -E -I "exec\(|child_process|spawn|subprocess|os\.system" "$dir" --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null && perms+=("⚡ Shell execution")
  grep -r -q -E -I "curl |wget |fetch\(|axios|requests\." "$dir" --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null && perms+=("🌐 Network access")
  grep -r -q -E -I "read|open\(|fs\.|path\.|os\.path" "$dir" --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null && perms+=("📂 File read")
  grep -r -q -E -I "write|append|fs\.write|>\s*|" "$dir" --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null && perms+=("✏️ File write")
  grep -r -q -E -I "sudo |runas|chmod|chown|admin" "$dir" --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null && perms+=("🔑 Elevated permissions")
  grep -r -q -E -I "AKIA|ghp_|sk_live|token|secret|password|api.key|API_KEY" "$dir" --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null && perms+=("🔐 References secrets/API keys")
  grep -r -q -E -I "cron|schedule|setInterval|setTimeout.*loop" "$dir" --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null && perms+=("⏰ Scheduled tasks")

  if [[ ${#perms[@]} -eq 0 ]]; then
    echo "📄 Read-only (SKILL.md only)"
  else
    printf '%s\n' "${perms[@]}"
  fi
}

# ─── Hash Baseline ──────────────────────────────────────────────────────────
generate_baseline() {
  local dir="$1"
  find "$dir" -type f ! -name "*.skill" -exec "$HASH_ALGO"sum {} \; 2>/dev/null
}

check_drift() {
  local skill_dir="$1"
  local baseline_dir="$2"
  local name
  name=$(skill_name "$skill_dir")
  local baseline_file="$baseline_dir/${name}.hashes"
  
  if [[ ! -f "$baseline_file" ]]; then
    echo "NO_BASELINE"
    return
  fi

  local current_hashes
  current_hashes=$(generate_baseline "$skill_dir")
  local diff_result
  diff_result=$(diff <(echo "$current_hashes" | sort) <(sort "$baseline_file") 2>/dev/null || true)
  
  if [[ -z "$diff_result" ]]; then
    echo "CLEAN"
  else
    local changed_files
    changed_files=$(echo "$diff_result" | grep "^>" -c 2>/dev/null || echo "0")
    local added_files
    added_files=$(echo "$diff_result" | grep "^<" -c 2>/dev/null || echo "0")
    echo "DRIFTED:~$((changed_files + added_files)) files changed"
  fi
}

# ─── VirusTotal ─────────────────────────────────────────────────────────────
vt_scan_file() {
  local file="$1"
  local hash
  hash=$(sha256sum "$file" 2>/dev/null | awk '{print $1}')
  
  if [[ -z "$hash" ]]; then
    echo "HASH_ERROR"
    return
  fi

  # Check existing report first (doesn't count against rate limit)
  local response
  response=$(curl -s -f "https://www.virustotal.com/api/v3/files/$hash" \
    -H "x-apikey: $VT_API_KEY" 2>/dev/null || echo '{}')
  
  local last_analysis
  last_analysis=$(echo "$response" | grep -o '"last_analysis_results":{' | head -1 || true)
  
  if [[ -n "$last_analysis" ]]; then
    local stats
    stats=$(echo "$response" | grep -o '"malicious":[0-9]*' | head -1)
    local malicious
    malicious=$(echo "$stats" | grep -o '[0-9]*' || echo "0")
    echo "VT:${malicious}"
    return
  fi

  # File not previously scanned — skip upload for large files, just note it
  local fsize
  fsize=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
  if (( fsize > 32000000 )); then
    echo "VT:TOO_LARGE"
    return
  fi

  # Upload for scanning (counts against rate limit)
  response=$(curl -s -f --request POST "https://www.virustotal.com/api/v3/files" \
    -H "x-apikey: $VT_API_KEY" \
    -F "file=@$file" 2>/dev/null || echo '{}')
  echo "VT:UPLOADED"
}

# ─── Domain Reputation ──────────────────────────────────────────────────────
extract_domains() {
  local dir="$1"
  grep -r -o -E -I 'https?://[^ ")\x27>\x60,;]+' "$dir" \
    --include="*.md" --include="*.sh" --include="*.js" --include="*.py" 2>/dev/null \
    | grep -v 'https\?://localhost' \
    | sed 's|https\?://||;s|/.*||;s|www\.||' \
    | grep -E '^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' \
    | sort -u
}

# ─── Report Generation ──────────────────────────────────────────────────────
generate_report() {
  local skill_dir="$1"
  local name
  name=$(skill_name "$skill_dir")
  local risk_data
  risk_data=$(calculate_risk "$skill_dir")
  local risk_level risk_score risk_emoji
  IFS=: read -r risk_level risk_score risk_emoji <<< "$risk_data"
  local fc size author version
  fc=$(file_count "$skill_dir")
  size=$(total_size "$skill_dir")
  
  # Extract metadata from SKILL.md frontmatter (proper YAML parsing)
  author=$(awk '/^---/{f++;next} f==1 && /^author:/{gsub(/^author:[[:space:]]*["'"'"']?/,""); gsub(/["'"'"']?[[:space:]]*$/,""); print; exit}' "$skill_dir/SKILL.md" 2>/dev/null || echo "unknown")
  version=$(awk '/^---/{f++;next} f==1 && /^version:/{gsub(/^version:[[:space:]]*["'"'"']?/,""); gsub(/["'"'"']?[[:space:]]*$/,""); print; exit}' "$skill_dir/SKILL.md" 2>/dev/null || echo "unknown")
  [[ -z "$author" || "$author" == *"author"* ]] && author="unknown"
  [[ -z "$version" || "$version" == *"version"* ]] && version="unknown"

  local pattern_results
  pattern_results=$(scan_patterns "$skill_dir")
  local pattern_details=""
  if [[ -n "$pattern_results" ]]; then
    while IFS=: read -r cat count; do
      [[ -z "$cat" ]] && continue
      case "$cat" in
        exec_danger)  pattern_details+="  ⚡ Shell execution: $count matches\n" ;;
        network)      pattern_details+="  🌐 Network calls: $count matches\n" ;;
        fs_external)  pattern_details+="  📂 External filesystem: $count matches\n" ;;
        secrets)      pattern_details+="  🔐 Secret patterns: $count matches\n" ;;
        obfuscation)  pattern_details+="  🔒 Obfuscation: $count matches\n" ;;
        elevated)     pattern_details+="  🔑 Elevated permissions: $count matches\n" ;;
      esac
    done <<< "$pattern_results"
  fi

  local permissions
  permissions=$(check_permissions "$skill_dir")

  local domains
  domains=$(extract_domains "$skill_dir")
  local domain_section=""
  if [[ -n "$domains" ]]; then
    domain_section="  Domains referenced:\n"
    while IFS= read -r d; do
      domain_section+="    - $d\n"
    done <<< "$domains"
  fi

  local vt_section=""
  if $SCAN_VT; then
    local scripts
    scripts=$(find "$skill_dir/scripts" -type f 2>/dev/null || true)
    if [[ -n "$scripts" ]]; then
      vt_section="  VirusTotal scan:\n"
      while IFS= read -r f; do
        local vt_result
        vt_result=$(vt_scan_file "$f" 2>/dev/null || echo "VT:ERROR")
        vt_section+="    $(basename "$f"): $vt_result\n"
      done <<< "$scripts"
    fi
  fi

  if $SCAN_JSON; then
    local perm_json
    perm_json=$(echo "$permissions" | sed 's/"/\\"/g' | awk '{printf "%s%s", sep, $0; sep=", "}' | sed 's/^/"/;s/$/"/')
    local pat_json="["
    local first=true
    while IFS=: read -r cat count; do
      [[ -z "$cat" ]] && continue
      $first && first=false || pat_json+=","
      pat_json+="{\"category\":\"$cat\",\"count\":$count}"
    done <<< "$pattern_results"
    pat_json+="]"
    cat <<JSONEOF
{
  "skill": "$name",
  "risk_level": "$risk_level",
  "risk_score": $risk_score,
  "file_count": $fc,
  "size": "$size",
  "author": "$author",
  "version": "$version",
  "permissions": [$perm_json],
  "patterns": $pat_json
}
JSONEOF
  else
    cat <<EOF
${risk_emoji} ${BOLD}$name${NC} — Risk: ${risk_level} (${risk_score}pts)
   Files: $fc | Size: $size | Author: $author | Version: $version

   Permissions:
$(echo "$permissions" | sed 's/^/   /')

   Pattern matches:
$(echo -e "$pattern_details")
$(echo -e "$domain_section")
$(echo -e "$vt_section")
EOF
  fi
}

# ─── Main ───────────────────────────────────────────────────────────────────
main() {
  if $SCAN_ALL; then
    local skills
    skills=$(find_skills)
    if [[ -z "$skills" ]]; then
      echo "No skills found."
      exit 0
    fi

    local total_score=0 skill_count=0
    while IFS= read -r skill_dir; do
      [[ -z "$skill_dir" ]] && continue
      ((skill_count++))
      generate_report "$skill_dir"
      echo ""
    done <<< "$skills"

    echo "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BOLD}Scanned $skill_count skills${NC}"

  elif $BASELINE_MODE; then
    local baseline_dir="${REPORT_DIR:-.skill-guard/baselines}"
    mkdir -p "$baseline_dir"
    local skills
    skills=$(find_skills)
    while IFS= read -r skill_dir; do
      [[ -z "$skill_dir" ]] && continue
      local name
      name=$(skill_name "$skill_dir")
      generate_baseline "$skill_dir" > "$baseline_dir/${name}.hashes"
      echo "🟢 Baseline saved: $name"
    done <<< "$skills"
    echo "Baselines stored in: $baseline_dir"

  elif $DIFF_MODE; then
    local baseline_dir="${REPORT_DIR:-.skill-guard/baselines}"
    local skills
    skills=$(find_skills)
    while IFS= read -r skill_dir; do
      [[ -z "$skill_dir" ]] && continue
      local name
      name=$(skill_name "$skill_dir")
      local drift
      drift=$(check_drift "$skill_dir" "$baseline_dir")
      case "$drift" in
        CLEAN)     echo "🟢 $name: No changes detected" ;;
        NO_BASELINE) echo "🟡 $name: No baseline found (run --baseline first)" ;;
        *)         echo "🔴 $name: $drift" ;;
      esac
    done <<< "$skills"

  elif [[ -n "$TARGET" && -d "$TARGET" ]]; then
    generate_report "$TARGET"
  else
    echo "Usage: skill-guard.sh <skill-dir> [--scan-all] [--json] [--baseline] [--diff] [--vt-api KEY]"
    echo "       skill-guard.sh --scan-all [--json] [--vt-api KEY]"
    echo "       skill-guard.sh --baseline [--report-dir DIR]"
    echo "       skill-guard.sh --diff [--report-dir DIR]"
    exit 1
  fi
}

main "$@"
