#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Lark OpenClaw Bridge — One-click installer
# Usage: curl -fsSL https://oc.atomecorp.net/lark/install.sh | bash
#        curl -fsSL https://oc.atomecorp.net/lark/install.sh | bash -s -- --reset
# Idempotent: skips already-installed components, preserves existing .env fields
# --reset: wipes bridge dir, .env, arouter config and rebuilds from scratch
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# ── Colors ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}[ OK]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET} $*"; }
error()   { echo -e "${RED}[ERR]${RESET}  $*" >&2; }
die()     { error "$*"; exit 1; }
hr()      { echo -e "${BOLD}────────────────────────────────────────${RESET}"; }

# ── Constants ─────────────────────────────────────────────────────────────────
RELAY_SERVER_URL="wss://oc.atomecorp.net/lark/bridge"
BRIDGE_REPO="git@repo.advai.net:atome-efficiency/lark-openclaw-bridge.git"
BRIDGE_BRANCH="main"
BRIDGE_DIR="$HOME/.openclaw/workspace/skills/lark-openclaw-bridge"
NODE_MIN_VERSION=22
PM2_NAME="lark-openclaw-bridge"

# ── Arguments ─────────────────────────────────────────────────────────────────
DO_RESET=false
DO_UPDATE=false
for arg in "$@"; do
  case "$arg" in
    --reset)  DO_RESET=true ;;
    --update) DO_UPDATE=true ;;
  esac
done

hr
echo -e "${BOLD}🦞 Lark OpenClaw Bridge Installer${RESET}"
if [ "$DO_RESET" = true ]; then
  echo -e "${YELLOW}${BOLD}  ⚠️  RESET MODE — bridge dir, .env and arouter config will be wiped${RESET}"
fi
if [ "$DO_UPDATE" = true ]; then
  echo -e "${BLUE}  ↑  UPDATE MODE — pulling latest code and restarting bridge${RESET}"
fi
hr

if [ "$DO_RESET" = true ]; then
  echo ""
  warn "以下内容将备份并重建："
  echo "  · $BRIDGE_DIR → ${BRIDGE_DIR}.bak（整个目录）"
  echo "  · ~/.openclaw 配置文件中的 arouter 相关条目将被清除"
  echo "    （其他 provider 的 key 和配置不受影响）"
  echo "  · 已安装的包（openclaw、pm2）不受影响"
  echo ""
  read -rp "  确认重置? [y/N]: " _CONFIRM_RESET < /dev/tty
  [[ "$_CONFIRM_RESET" =~ ^[Yy]$ ]] || { info "Reset cancelled."; exit 0; }
  echo ""
fi

# ── 1. OS detection ───────────────────────────────────────────────────────────
OS="$(uname -s)"
case "$OS" in
  Darwin) info "OS: macOS" ;;
  Linux)  info "OS: Linux" ;;
  *)      die "Unsupported OS: $OS" ;;
esac

# ── 2. Check / install Node.js ────────────────────────────────────────────────
check_node() {
  if command -v node &>/dev/null; then
    NODE_VER=$(node -e 'process.stdout.write(process.versions.node.split(".")[0])')
    if [ "$NODE_VER" -ge "$NODE_MIN_VERSION" ]; then
      success "Node.js $(node --version) is installed"
      return 0
    else
      warn "Node.js $(node --version) is too old (need v${NODE_MIN_VERSION}+)"
    fi
  fi
  return 1
}

install_node_via_nvm() {
  info "Installing Node.js v${NODE_MIN_VERSION}+ via nvm..."
  if [ ! -d "$HOME/.nvm" ]; then
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  fi
  export NVM_DIR="$HOME/.nvm"
  # shellcheck disable=SC1090
  [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
  nvm install "$NODE_MIN_VERSION"
  nvm use "$NODE_MIN_VERSION"
  nvm alias default "$NODE_MIN_VERSION"
  success "Node.js $(node --version) installed and set as default"
}

if ! check_node; then
  install_node_via_nvm
  check_node || die "Node.js installation failed. Please install manually and retry."
fi

# Remove npm prefix/globalconfig from ~/.npmrc if present — these conflict with nvm
if [ -f "$HOME/.npmrc" ] && grep -qE '^(prefix|globalconfig)=' "$HOME/.npmrc" 2>/dev/null; then
  sed -i.bak '/^prefix=/d;/^globalconfig=/d' "$HOME/.npmrc" && rm -f "$HOME/.npmrc.bak"
  warn "Removed conflicting prefix/globalconfig from ~/.npmrc (nvm compatibility)"
fi

# Ensure nvm binaries are in PATH for current session
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"

# Add nvm init to shell profile if not already present
for RC in "$HOME/.bashrc" "$HOME/.zshrc"; do
  if [ -f "$RC" ] && ! grep -q 'NVM_DIR' "$RC"; then
    { echo ''; echo '# nvm'; echo 'export NVM_DIR="$HOME/.nvm"'; echo '[ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"'; } >> "$RC"
    info "Added nvm init to $RC"
  fi
done

# ── Helper: fetch deploy key for git access ───────────────────────────────────
setup_deploy_key() {
  _DEPLOY_KEY_FILE="$(mktemp)"
  if curl -fsSL "https://oc.atomecorp.net/lark/deploy_key" -o "$_DEPLOY_KEY_FILE" 2>/dev/null; then
    chmod 600 "$_DEPLOY_KEY_FILE"
    export GIT_SSH_COMMAND="ssh -i $_DEPLOY_KEY_FILE -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"
    trap 'rm -f "$_DEPLOY_KEY_FILE"; unset GIT_SSH_COMMAND' EXIT
    return 0
  else
    rm -f "$_DEPLOY_KEY_FILE"
    return 1
  fi
}

# ── Update: pull latest code and restart (no interaction) ────────────────────
if [ "$DO_UPDATE" = true ]; then
  if [ ! -d "$BRIDGE_DIR/.git" ]; then
    die "Bridge not installed at $BRIDGE_DIR. Run the installer without --update first."
  fi

  # Ensure deploy key / SSH access for git pull
  REPO_HOST=$(echo "$BRIDGE_REPO" | sed 's/git@//;s/:.*//')
  _SSH_OUT=$(ssh -T -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 "git@${REPO_HOST}" < /dev/null 2>&1 || true)
  if ! echo "$_SSH_OUT" | grep -qi "welcome"; then
    info "No SSH access to $REPO_HOST, using deploy key..."
    setup_deploy_key || die "Failed to fetch deploy key from server"
  fi

  info "Pulling latest changes..."
  git -C "$BRIDGE_DIR" pull --ff-only || die "git pull failed. Try --reset if there are local conflicts."
  success "Code updated"

  info "Installing dependencies..."
  cd "$BRIDGE_DIR" && npm install --silent
  success "Dependencies ready"

  info "Restarting bridge..."
  if pm2 describe "$PM2_NAME" &>/dev/null; then
    pm2 restart "$PM2_NAME" --update-env --cwd "$BRIDGE_DIR"
    success "Bridge restarted"
  else
    pm2 start "$BRIDGE_DIR/scripts/server.mjs" --name "$PM2_NAME" --cwd "$BRIDGE_DIR"
    success "Bridge started"
  fi
  pm2 save --force &>/dev/null

  hr
  echo -e "${GREEN}${BOLD}✅ Update complete!${RESET}"
  echo ""
  echo "Bridge logs:  pm2 logs $PM2_NAME"
  hr
  exit 0
fi

# ── Reset: wipe local state (runs after node is available) ───────────────────
if [ "$DO_RESET" = true ]; then
  hr
  info "Resetting local state..."

  # Stop and remove pm2 process
  if command -v pm2 &>/dev/null && pm2 describe "$PM2_NAME" &>/dev/null 2>&1; then
    pm2 delete "$PM2_NAME" 2>/dev/null || true
    success "Bridge pm2 process removed"
  fi

  # Back up bridge directory (also backs up .env inside it)
  if [ -d "$BRIDGE_DIR" ]; then
    rm -rf "${BRIDGE_DIR}.bak"
    mv "$BRIDGE_DIR" "${BRIDGE_DIR}.bak"
    success "Bridge directory backed up: ${BRIDGE_DIR}.bak"
  fi

  # Selectively strip arouter-related entries from config files (preserve everything else)
  node - <<'RESET_CFG_EOF'
const fs = require('fs');
const home = process.env.HOME;

// --- auth-profiles.json: remove only arouter (and legacy openrouter) profiles ---
const authPath = home + '/.openclaw/agents/main/agent/auth-profiles.json';
let authSource = authPath;
// If file doesn't exist but .bak does (left by a previous old-style reset), restore from backup first
if (!fs.existsSync(authPath) && fs.existsSync(authPath + '.bak')) {
  fs.copyFileSync(authPath + '.bak', authPath);
  console.log('auth-profiles.json: restored from .bak (previous reset had removed it)');
  authSource = authPath + '.bak';
}
try {
  const auth = JSON.parse(fs.readFileSync(authPath, 'utf8'));
  if (authSource === authPath) fs.writeFileSync(authPath + '.bak', JSON.stringify(auth, null, 2));
  if (auth.profiles) {
    delete auth.profiles['arouter:default'];
    delete auth.profiles['openrouter:default'];
  }
  if (auth.lastGood)   { delete auth.lastGood['arouter']; delete auth.lastGood['openrouter']; }
  if (auth.usageStats) { delete auth.usageStats['arouter:default']; delete auth.usageStats['openrouter:default']; }
  fs.writeFileSync(authPath, JSON.stringify(auth, null, 2));
  console.log('auth-profiles.json: arouter entries removed (other profiles preserved)');
} catch { console.log('auth-profiles.json: not found, skipping'); }

// --- models.json: remove only arouter (and legacy openrouter) provider ---
const modelsPath = home + '/.openclaw/agents/main/agent/models.json';
if (!fs.existsSync(modelsPath) && fs.existsSync(modelsPath + '.bak')) {
  fs.copyFileSync(modelsPath + '.bak', modelsPath);
  console.log('models.json: restored from .bak (previous reset had removed it)');
}
try {
  const models = JSON.parse(fs.readFileSync(modelsPath, 'utf8'));
  fs.writeFileSync(modelsPath + '.bak', JSON.stringify(models, null, 2));
  if (models.providers) {
    delete models.providers['arouter'];
    delete models.providers['openrouter'];
  }
  fs.writeFileSync(modelsPath, JSON.stringify(models, null, 2));
  console.log('models.json: arouter provider removed (other providers preserved)');
} catch { console.log('models.json: not found, skipping'); }

// --- openclaw.json: strip arouter sections, keep everything else ---
const ocPath = home + '/.openclaw/openclaw.json';
try {
  const cfg = JSON.parse(fs.readFileSync(ocPath, 'utf8'));
  fs.writeFileSync(ocPath + '.bak', JSON.stringify(cfg, null, 2));
  if (cfg.models?.providers)  { delete cfg.models.providers.arouter; delete cfg.models.providers.openrouter; }
  if (cfg.auth?.profiles)     { delete cfg.auth.profiles['arouter:default']; delete cfg.auth.profiles['openrouter:default']; }
  if (cfg.agents?.defaults)   delete cfg.agents.defaults.model;
  // Clean up legacy invalid key from older install versions
  if (cfg.agents?.defaults?.tools) delete cfg.agents.defaults.tools;
  fs.writeFileSync(ocPath, JSON.stringify(cfg, null, 2));
  console.log('openclaw.json: arouter config cleared (other settings preserved)');
} catch { console.log('openclaw.json: not found, skipping'); }
RESET_CFG_EOF
  success "Arouter config cleared (existing credentials preserved)"

  success "Reset complete — continuing with fresh install..."
  hr
fi

# ── 3. Check git ──────────────────────────────────────────────────────────────
command -v git &>/dev/null || die "git not found. Please install git first."
success "git $(git --version | awk '{print $3}') is installed"

# ── 4. Fix npm registry (taobao mirror cert has expired) ─────────────────────
CURRENT_REGISTRY=$(npm config get registry 2>/dev/null || echo "")
if echo "$CURRENT_REGISTRY" | grep -q "taobao\|npmmirror"; then
  warn "npm registry is set to $CURRENT_REGISTRY (cert may be expired)"
  npm config set registry https://registry.npmjs.org
  success "npm registry reset to https://registry.npmjs.org"
fi

# ── 5. Install OpenClaw ───────────────────────────────────────────────────────
if command -v openclaw &>/dev/null; then
  success "OpenClaw $(openclaw --version 2>/dev/null || echo '') already installed"
else
  info "Installing OpenClaw..."
  npm install -g openclaw
  success "OpenClaw installed"
fi

# ── 6. OpenClaw config preference (ask now, apply after we have App ID) ───────
# Check if arouter provider is already configured (idempotent)
HAS_AROUTER=$(node -e "
try {
  const cfg = JSON.parse(require('fs').readFileSync(process.env.HOME+'/.openclaw/openclaw.json','utf8'));
  process.stdout.write(cfg?.models?.providers?.arouter ? 'yes' : 'no');
} catch { process.stdout.write('no'); }
" 2>/dev/null || echo "no")

if [ "$HAS_AROUTER" = "yes" ]; then
  success "OpenClaw already configured with company arouter, skipping"
  OC_CONFIG_CHOICE="1"
else
  hr
  echo -e "${BOLD}⚙️  Configure OpenClaw${RESET}"
  echo ""
  echo "  Choose your configuration mode:"
  echo ""
  echo -e "  ${BOLD}[1] 默认配置（推荐）${RESET}"
  echo "      使用公司统一的 Ark API 账号（arouter）"
  echo "      · 已内置 LLM key 和 provider 配置"
  echo "      · 按 App ID 自动统计用量"
  echo "      · 适合大多数用户，开箱即用"
  echo ""
  echo -e "  ${BOLD}[2] 自定义配置${RESET}"
  echo "      手动配置 OpenClaw，使用自己的 API key"
  echo ""
  read -rp "  请选择 [1/2，默认 1]: " OC_CONFIG_CHOICE < /dev/tty
  OC_CONFIG_CHOICE="${OC_CONFIG_CHOICE:-1}"
fi

# ── 6. Install pm2 ────────────────────────────────────────────────────────────
if command -v pm2 &>/dev/null; then
  success "pm2 already installed, skipping"
else
  info "Installing pm2..."
  npm install -g pm2
  success "pm2 installed"
fi

# ── 7. Clone / update Bridge ──────────────────────────────────────────────────
mkdir -p "$(dirname "$BRIDGE_DIR")"

# Check SSH access to repo host via -T (GitLab prints "Welcome" on success, exit code is always non-0)
REPO_HOST=$(echo "$BRIDGE_REPO" | sed 's/git@//;s/:.*//')
_SSH_OUT=$(ssh -T -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=5 "git@${REPO_HOST}" < /dev/null 2>&1 || true)
if echo "$_SSH_OUT" | grep -qi "welcome"; then
  success "SSH access to $REPO_HOST confirmed"
else
  info "No SSH access to $REPO_HOST, using deploy key..."
  setup_deploy_key || die "Failed to fetch deploy key from server"
fi

if [ -d "$BRIDGE_DIR/.git" ]; then
  success "Bridge already exists at $BRIDGE_DIR, skipping clone"
  info "Pulling latest changes..."
  git -C "$BRIDGE_DIR" pull --ff-only 2>/dev/null || warn "git pull failed, continuing with local code"
  success "Bridge code updated"
elif [ -d "$BRIDGE_DIR" ]; then
  warn "Directory $BRIDGE_DIR exists but is not a git repo — skipping"
else
  info "Cloning lark-openclaw-bridge to $BRIDGE_DIR..."
  git clone -b "$BRIDGE_BRANCH" "$BRIDGE_REPO" "$BRIDGE_DIR"
  success "Cloned to $BRIDGE_DIR"
fi

cd "$BRIDGE_DIR"
npm install --silent
success "Dependencies installed"

# ── 8. Configure Lark App ─────────────────────────────────────────────────────
ENV_FILE="$BRIDGE_DIR/.env"
[ -f "$ENV_FILE" ] || touch "$ENV_FILE"

env_get()    { grep -E "^$1=" "$ENV_FILE" 2>/dev/null | head -1 | cut -d= -f2- || true; }
env_set()    { echo "$1=$2" >> "$ENV_FILE"; }
env_update() {
  if grep -qE "^$1=" "$ENV_FILE" 2>/dev/null; then
    sed -i.bak "s|^$1=.*|$1=$2|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    echo "$1=$2" >> "$ENV_FILE"
  fi
}

hr
echo -e "${BOLD}📋 Configure Lark App Credentials${RESET}"
echo ""
echo "  Before proceeding, set up your Lark app:"
echo ""
echo "  Step 1: Create the app"
echo "          Go to: https://open.larksuite.com/app"
echo "          Click '创建企业自建应用 (Create Internal Enterprise App)'"
echo ""
echo "  Step 2: Enable Bot capability"
echo "          Navigate to: 添加应用能力 (Add App Features)"
echo "          Enable: 机器人 (Bot)"
echo ""
echo "  Step 3: Enable required permissions"
echo "          Navigate to: 权限管理 (Permissions & Scopes) → 批量配置"
echo "          Click '权限申请 | 批量导入', paste the JSON below:"
echo ""
echo '          {"scopes":{"tenant":["contact:user.base:readonly","contact:contact.base:readonly","im:chat","im:chat.members:read","im:chat:read","im:chat:readonly","im:message","im:message.group_at_msg:readonly","im:message.group_msg:readonly","im:message.p2p_msg:readonly","im:message.pins:read","im:message.reactions:read","im:message.reactions:write_only","im:message:readonly","im:message:send_as_bot","im:resource"],"user":[]}}'
echo ""
echo "  Step 4: Subscribe to message events"
echo "          Navigate to: 事件与回调 (Events & Callbacks)"
echo "          Add event: im.message.receive_v1 (接收消息)"
echo ""
echo "  Step 5: From 凭证与基础信息 (Credentials & Basic Info),"
echo "          copy App ID and App Secret"
echo ""
echo "  Step 6: From 事件与回调 > 加密策略 (Events & Callbacks > Encryption),"
echo "          copy Verification Token"
echo "          ⚠️  Encrypt Key 和 回调配置 暂时不需要填写，跳过即可"
echo ""

# Generate lark-permissions.json
cat > "$BRIDGE_DIR/lark-permissions.json" << 'PERM_EOF'
{
  "scopes": {
    "tenant": [
      "contact:user.base:readonly",
      "contact:contact.base:readonly",
      "im:chat",
      "im:chat.members:read",
      "im:chat:read",
      "im:chat:readonly",
      "im:message",
      "im:message.group_at_msg:readonly",
      "im:message.group_msg:readonly",
      "im:message.p2p_msg:readonly",
      "im:message.pins:read",
      "im:message.reactions:read",
      "im:message.reactions:write_only",
      "im:message:readonly",
      "im:message:send_as_bot",
      "im:resource"
    ],
    "user": []
  }
}
PERM_EOF
success "Generated lark-permissions.json"

# Credentials: show current value as default, Enter to keep, type new value to overwrite
HAS_APP_ID="$(env_get LARK_APP_ID)"
HAS_APP_SECRET="$(env_get LARK_APP_SECRET)"
HAS_VERIFY_TOKEN="$(env_get LARK_VERIFICATION_TOKEN)"

# App ID
if [ -n "$HAS_APP_ID" ]; then
  read -rp "App ID [${HAS_APP_ID}]: " INPUT_APP_ID < /dev/tty
  INPUT_APP_ID="${INPUT_APP_ID:-$HAS_APP_ID}"
else
  read -rp "App ID (cli_xxx): " INPUT_APP_ID < /dev/tty
fi
[ -z "$INPUT_APP_ID" ] && die "App ID is required"
env_update "LARK_APP_ID" "$INPUT_APP_ID"

# App Secret
if [ -n "$HAS_APP_SECRET" ]; then
  echo "(已配置，按回车保留 / 输入新值覆盖)"
  read -rsp "App Secret: " INPUT_APP_SECRET < /dev/tty
  echo ""
  INPUT_APP_SECRET="${INPUT_APP_SECRET:-$HAS_APP_SECRET}"
else
  echo "(Input hidden for security — type normally and press Enter)"
  read -rsp "App Secret: " INPUT_APP_SECRET < /dev/tty
  echo ""
fi
[ -z "$INPUT_APP_SECRET" ] && die "App Secret is required"
env_update "LARK_APP_SECRET" "$INPUT_APP_SECRET"

# Verification Token
echo "  在飞书开放平台找到 Verification Token 的路径："
echo "    应用详情页 → 事件与回调 → 加密策略 → Verification Token（验证令牌）"
echo "  ⚠️  Encrypt Key 和回调 URL 暂时不需要填写，跳过即可"
echo ""
if [ -n "$HAS_VERIFY_TOKEN" ]; then
  echo "(已配置，按回车保留 / 输入新值覆盖)"
  read -rsp "Verification Token: " INPUT_VERIFY_TOKEN < /dev/tty
  echo ""
  INPUT_VERIFY_TOKEN="${INPUT_VERIFY_TOKEN:-$HAS_VERIFY_TOKEN}"
else
  echo "(Input hidden for security — type normally and press Enter)"
  read -rsp "Verification Token: " INPUT_VERIFY_TOKEN < /dev/tty
  echo ""
fi
[ -z "$INPUT_VERIFY_TOKEN" ] && die "Verification Token is required"
env_update "LARK_VERIFICATION_TOKEN" "$INPUT_VERIFY_TOKEN"

# Relay Secret (default: atome)
if [ -z "$(env_get RELAY_SECRET)" ]; then
  env_update "RELAY_SECRET" "atome"
  success "RELAY_SECRET set to default"
fi

# Relay URL — always ensure it matches the canonical value
EXISTING_RELAY_URL="$(env_get RELAY_SERVER_URL)"
if [ -z "$EXISTING_RELAY_URL" ]; then
  env_update "RELAY_SERVER_URL" "$RELAY_SERVER_URL"
  success "RELAY_SERVER_URL set to $RELAY_SERVER_URL"
elif [ "$EXISTING_RELAY_URL" != "$RELAY_SERVER_URL" ]; then
  env_update "RELAY_SERVER_URL" "$RELAY_SERVER_URL"
  warn "RELAY_SERVER_URL updated: $EXISTING_RELAY_URL → $RELAY_SERVER_URL"
fi

success ".env configured"

# ── Apply OpenClaw config (now that we have App ID) ───────────────────────────
FINAL_APP_ID="$(env_get LARK_APP_ID)"
if [ "$OC_CONFIG_CHOICE" = "2" ]; then
  hr
  info "自定义配置：请手动运行以下命令完成 OpenClaw 配置："
  echo ""
  echo -e "  ${GREEN}openclaw configure${RESET}"
  echo ""
  echo "  按照提示填写 LLM provider、API key 和 Gateway token。"
  echo ""
  read -rp "  已完成配置，继续安装? [Y/n]: " CONTINUE_CHOICE < /dev/tty
  if [[ "$CONTINUE_CHOICE" =~ ^[Nn]$ ]]; then
    echo ""
    echo "  安装已暂停。配置完成后重新运行："
    echo -e "  ${YELLOW}curl -fsSL https://oc.atomecorp.net/lark/install.sh | bash${RESET}"
    exit 0
  fi
else
  # ── SSO Authentication ───────────────────────────────────────────
  # Authenticate via Lark SSO so the provisioned API key can be linked
  # to a real person. auth-link sends a JWT to a local callback server.
  AUTH_TOKEN=""
  AUTH_USER_NAME=""
  hr
  echo -e "${BOLD}🔐 身份认证${RESET}"
  echo ""
  echo "  正在认证你的飞书账号，以便将 API Key 与你的身份关联。"
  echo "  即将打开浏览器，请完成飞书登录..."
  echo ""

  # Ensure auth callback port (12345) is free before starting
  _AUTH_PORT=12345
  _SKIP_AUTH=false
  _AUTH_PORT_PID=$(lsof -ti :"$_AUTH_PORT" 2>/dev/null || true)
  if [ -n "$_AUTH_PORT_PID" ]; then
    warn "认证回调端口 $_AUTH_PORT 被占用 (pid $_AUTH_PORT_PID)"
    echo ""
    echo "  认证需要在本地启动一个临时 HTTP 服务 (端口 $_AUTH_PORT)。"
    echo "  当前该端口已被其他进程占用，需要先停止该进程才能继续。"
    echo ""
    echo "  [1] 终止占用进程并继续认证"
    echo "  [2] 跳过认证（API Key 将以匿名方式创建）"
    echo "  [3] 退出安装（请手动释放端口后重新运行）"
    echo ""
    read -rp "  请选择 [1/2/3，默认 1]: " _AUTH_PORT_CHOICE < /dev/tty
    _AUTH_PORT_CHOICE="${_AUTH_PORT_CHOICE:-1}"

    case "$_AUTH_PORT_CHOICE" in
      1)
        info "正在终止占用端口 $_AUTH_PORT 的进程 (pid $_AUTH_PORT_PID)..."
        kill "$_AUTH_PORT_PID" 2>/dev/null || true
        for _aw in 1 2 3; do
          sleep 1
          lsof -ti :"$_AUTH_PORT" &>/dev/null || break
        done
        if lsof -ti :"$_AUTH_PORT" &>/dev/null; then
          kill -9 "$(lsof -ti :"$_AUTH_PORT")" 2>/dev/null || true
          sleep 1
        fi
        if lsof -ti :"$_AUTH_PORT" &>/dev/null; then
          error "无法释放端口 $_AUTH_PORT"
          error "请手动检查: lsof -i :$_AUTH_PORT"
          die "端口 $_AUTH_PORT 释放失败，请手动处理后重新运行安装脚本"
        fi
        success "端口 $_AUTH_PORT 已释放"
        ;;
      2)
        warn "跳过认证"
        _SKIP_AUTH=true
        ;;
      *)
        echo ""
        info "请手动释放端口后重新运行："
        echo "  lsof -i :$_AUTH_PORT"
        echo "  kill \$(lsof -ti :$_AUTH_PORT)"
        exit 0
        ;;
    esac
  fi

  # Start a local HTTP callback server (Node.js), open the browser, wait for token.
  _AUTH_RESULT=""
  if [ "$_SKIP_AUTH" = false ]; then
  _AUTH_RESULT=$(node - 2>/dev/tty <<'AUTH_NODE_EOF'
const http = require('http');
const { exec } = require('child_process');
const os = require('os');

const PORT = 12345;
const AUTH_URL = 'http://apps.advancegroup.com/auth-link/login';
let done = false;

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(204); res.end(); return; }
  if (req.method !== 'POST') { res.writeHead(405); res.end(); return; }
  const chunks = [];
  req.on('data', c => chunks.push(c));
  req.on('end', () => {
    let body;
    try { body = JSON.parse(Buffer.concat(chunks).toString()); } catch { res.writeHead(400); res.end(); return; }
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ ok: true }));
    if (!done && body.token) {
      done = true;
      process.stdout.write(body.token);
      server.close();
      process.exit(0);
    }
  });
});

server.on('error', (err) => {
  if (err.code === 'EADDRINUSE') {
    process.stderr.write('\n  [AUTH] ❌ 端口 ' + PORT + ' 被占用，无法启动认证回调服务\n');
    process.stderr.write('  请手动检查: lsof -i :' + PORT + '\n\n');
  } else {
    process.stderr.write('[AUTH] Server error: ' + err.message + '\n');
  }
  process.exit(1);
});

server.listen(PORT, '127.0.0.1', () => {
  process.stderr.write('  认证回调服务已启动 (port ' + PORT + ')\n');
  const platform = os.platform();
  if (platform === 'darwin') {
    exec('open "' + AUTH_URL + '"');
  } else {
    exec('xdg-open "' + AUTH_URL + '" 2>/dev/null || sensible-browser "' + AUTH_URL + '" 2>/dev/null || true');
  }
  process.stderr.write('  如果浏览器未自动打开，请手动访问:\n  ' + AUTH_URL + '\n\n');
});

setTimeout(() => {
  if (!done) {
    process.stderr.write('[AUTH] 认证超时（2分钟）\n');
    server.close();
    process.exit(1);
  }
}, 120000);
AUTH_NODE_EOF
  ) || true
  fi

  if [ -n "$_AUTH_RESULT" ]; then
    AUTH_TOKEN="$_AUTH_RESULT"
    # Decode JWT payload (base64url, middle segment) to extract display name
    AUTH_USER_NAME=$(AUTH_TOKEN="$AUTH_TOKEN" node -e "
const t = process.env.AUTH_TOKEN || '';
try {
  const b = t.split('.')[1].replace(/-/g,'+').replace(/_/g,'/');
  const d = JSON.parse(Buffer.from(b + '==='.slice((b.length+3)%4), 'base64').toString('utf8'));
  process.stdout.write(d.name || d.email || '');
} catch {}" 2>/dev/null || echo "")
    success "认证成功：$AUTH_USER_NAME"
  else
    die "认证失败或超时 — 请重新运行安装脚本并完成飞书登录"
  fi

  info "Fetching company default OpenClaw config (appId=${FINAL_APP_ID})..."
  if [ -n "$AUTH_TOKEN" ]; then
    COMPANY_CONFIG=$(curl -sf "https://oc.atomecorp.net/lark/openclaw-config?appId=${FINAL_APP_ID}" \
      -H "Authorization: Bearer ${AUTH_TOKEN}" \
      2>/dev/null || echo "")
  else
    COMPANY_CONFIG=$(curl -sf "https://oc.atomecorp.net/lark/openclaw-config?appId=${FINAL_APP_ID}" \
      2>/dev/null || echo "")
  fi
  if [ -n "$COMPANY_CONFIG" ] && echo "$COMPANY_CONFIG" | grep -q '"models"'; then
    OPENCLAW_CONFIG_DIR="$HOME/.openclaw"
    OPENCLAW_JSON="$OPENCLAW_CONFIG_DIR/openclaw.json"
    AUTH_PROFILES_JSON="$OPENCLAW_CONFIG_DIR/agents/main/agent/auth-profiles.json"
    mkdir -p "$OPENCLAW_CONFIG_DIR"
    mkdir -p "$(dirname "$AUTH_PROFILES_JSON")"
    # Merge provider config into openclaw.json and write API key to auth-profiles.json
    node - <<MERGE_EOF
const fs = require('fs');
const configPath = '$OPENCLAW_JSON';
const authPath = '$AUTH_PROFILES_JSON';
const incoming = $COMPANY_CONFIG;

// Extract and remove the provisioned API key (it belongs in auth-profiles.json, not openclaw.json)
const provisionedKey = incoming._provisionedApiKey || '';
delete incoming._provisionedApiKey;

// Deep merge helpers
function mergeObj(target, src) {
  for (const [k, v] of Object.entries(src)) {
    if (v && typeof v === 'object' && !Array.isArray(v) && target[k] && typeof target[k] === 'object') {
      mergeObj(target[k], v);
    } else {
      target[k] = v;
    }
  }
}

// Merge into openclaw.json (models, auth profile metadata, agents defaults)
let existing = {};
try { existing = JSON.parse(fs.readFileSync(configPath, 'utf8')); } catch {}

// Clean up any legacy apiKey that was incorrectly placed in openclaw.json
if (existing?.auth?.profiles?.['arouter:default']?.apiKey) {
  delete existing.auth.profiles['arouter:default'].apiKey;
  console.log('Removed legacy apiKey from auth.profiles in openclaw.json');
}

mergeObj(existing, incoming);
fs.writeFileSync(configPath, JSON.stringify(existing, null, 2));
console.log('Merged into openclaw.json');

// Write API key to auth-profiles.json (the credential store)
if (provisionedKey) {
  let authProfiles = { version: 1, profiles: {}, usageStats: {} };
  try { authProfiles = JSON.parse(fs.readFileSync(authPath, 'utf8')); } catch {}
  authProfiles.profiles = authProfiles.profiles || {};
  // Remove legacy openrouter entries
  delete authProfiles.profiles['openrouter:default'];
  if (authProfiles.lastGood) delete authProfiles.lastGood['openrouter'];
  if (authProfiles.usageStats) delete authProfiles.usageStats['openrouter:default'];
  // Write arouter profile
  authProfiles.profiles['arouter:default'] = {
    type: 'api_key',
    provider: 'arouter',
    key: provisionedKey,
  };
  fs.writeFileSync(authPath, JSON.stringify(authProfiles, null, 2));
  console.log('API key written to auth-profiles.json');
}

// Write arouter provider to models.json
const modelsPath = require('path').join(process.env.HOME, '.openclaw/agents/main/agent/models.json');
let modelsConfig = { providers: {} };
try { modelsConfig = JSON.parse(fs.readFileSync(modelsPath, 'utf8')); } catch {}
modelsConfig.providers = modelsConfig.providers || {};
delete modelsConfig.providers['openrouter'];
modelsConfig.providers['arouter'] = {
  baseUrl: 'https://oc.atomecorp.net/arouter/v1',
  api: 'openai-completions',
  authHeader: true,
  ...(provisionedKey ? { apiKey: provisionedKey } : {}),
  models: [
    { id: 'deepseek-v3-2-251201',              name: 'DeepSeek V3 (Default)',        reasoning: false, input: ['text'], cost: { input: 1.0,  output: 2.0,  cacheRead: 0,    cacheWrite: 0 }, contextWindow: 64000, maxTokens: 8192, api: 'openai-completions' },
    { id: 'doubao-seed-2-0-lite-260215',        name: 'Doubao Seed 2.0 Lite (Fast)',  reasoning: false, input: ['text'], cost: { input: 0.6,  output: 3.6,  cacheRead: 0.12, cacheWrite: 0 }, contextWindow: 32000, maxTokens: 4096, api: 'openai-completions' },
    { id: 'doubao-seed-2-0-pro-260215',         name: 'Doubao Seed 2.0 Pro (Smart)',  reasoning: false, input: ['text'], cost: { input: 3.2,  output: 16.0, cacheRead: 0.64, cacheWrite: 0 }, contextWindow: 32000, maxTokens: 4096, api: 'openai-completions' },
    { id: 'doubao-seed-2-0-code-preview-260215',name: 'Doubao Seed 2.0 Code (Pro)',   reasoning: false, input: ['text'], cost: { input: 3.2,  output: 16.0, cacheRead: 0.64, cacheWrite: 0 }, contextWindow: 32000, maxTokens: 4096, api: 'openai-completions' },
  ],
};
fs.mkdirSync(require('path').dirname(modelsPath), { recursive: true });
fs.writeFileSync(modelsPath, JSON.stringify(modelsConfig, null, 2));
console.log('Wrote arouter provider to models.json');
MERGE_EOF
    success "Company OpenClaw config merged into ~/.openclaw/openclaw.json"
  else
    warn "Could not fetch company config. Run 'openclaw configure' to set up manually."
  fi
fi

# ── Select default model ──────────────────────────────────────────────────────
if [ "$OC_CONFIG_CHOICE" != "2" ]; then
  MODELS_JSON="$HOME/.openclaw/agents/main/agent/models.json"
  if [ -f "$MODELS_JSON" ]; then
    node - <<'LISTMODELS_EOF'
const fs = require('fs');
const p = process.env.HOME + '/.openclaw/agents/main/agent/models.json';
let cfg = {};
try { cfg = JSON.parse(fs.readFileSync(p, 'utf8')); } catch { process.exit(0); }
const models = cfg.providers?.arouter?.models || [];
if (models.length === 0) process.exit(0);
console.log('\n  可用的 arouter 模型：\n');
models.forEach((m, i) => {
  console.log(`  [${i + 1}] arouter/${m.id}  (${m.name || m.id})`);
});
console.log('  [0] 跳过（保持当前设置）');
LISTMODELS_EOF

    echo ""
    read -rp "  请选择默认模型 [默认 1]: " MODEL_CHOICE < /dev/tty
    MODEL_CHOICE="${MODEL_CHOICE:-1}"

    if [ "$MODEL_CHOICE" != "0" ]; then
      MODEL_ID=$(node -e "
try {
  const fs = require('fs');
  const cfg = JSON.parse(fs.readFileSync(process.env.HOME + '/.openclaw/agents/main/agent/models.json', 'utf8'));
  const models = cfg.providers?.arouter?.models || [];
  const idx = parseInt('$MODEL_CHOICE') - 1;
  if (idx >= 0 && idx < models.length) process.stdout.write('arouter/' + models[idx].id);
} catch {}" 2>/dev/null || echo "")
      if [ -n "$MODEL_ID" ]; then
        openclaw models set "$MODEL_ID"
        success "Default model set to $MODEL_ID"
      else
        warn "Invalid choice, skipping model selection"
      fi
    fi
  fi
fi

# ── Check / setup gateway.auth.token ─────────────────────────────────────────
OPENCLAW_JSON="$HOME/.openclaw/openclaw.json"
HAS_GW_TOKEN=$(node -e "
try {
  const cfg = JSON.parse(require('fs').readFileSync('$OPENCLAW_JSON','utf8'));
  process.stdout.write(cfg?.gateway?.auth?.token ? 'yes' : 'no');
} catch { process.stdout.write('no'); }
" 2>/dev/null || echo "no")

if [ "$HAS_GW_TOKEN" = "no" ]; then
  info "Gateway token not set — generating one automatically..."
  node - <<'GW_TOKEN_EOF'
const fs = require('fs');
const crypto = require('crypto');
const path = process.env.HOME + '/.openclaw/openclaw.json';

let cfg = {};
try { cfg = JSON.parse(fs.readFileSync(path, 'utf8')); } catch {}

const token = crypto.randomBytes(32).toString('hex');
cfg.gateway = cfg.gateway || {};
cfg.gateway.auth = cfg.gateway.auth || {};
cfg.gateway.auth.mode = 'token';
cfg.gateway.auth.token = token;

fs.writeFileSync(path, JSON.stringify(cfg, null, 2));
console.log('Gateway token set: ' + token.slice(0, 8) + '...');
GW_TOKEN_EOF
  success "Gateway auth token generated and saved"
else
  success "Gateway token already configured"
fi

# ── Configure gateway denyCommands (prevent agent from sending messages directly) ─
node - <<'DENY_CMD_EOF'
const fs = require('fs');
const cfgPath = process.env.HOME + '/.openclaw/openclaw.json';
let cfg = {};
try { cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8')); } catch {}
cfg.gateway = cfg.gateway || {};
cfg.gateway.nodes = cfg.gateway.nodes || {};
const deny = cfg.gateway.nodes.denyCommands || [];
if (!deny.includes('message')) deny.push('message');
cfg.gateway.nodes.denyCommands = deny;
fs.writeFileSync(cfgPath, JSON.stringify(cfg, null, 2));
console.log('gateway.nodes.denyCommands configured:', JSON.stringify(deny));
DENY_CMD_EOF
success "gateway.nodes.denyCommands configured"

# ── 9. Start / restart Bridge ─────────────────────────────────────────────────
hr
info "Starting lark-openclaw-bridge..."

# Ensure the webhook port is free before starting (prevents EADDRINUSE after reset)
WEBHOOK_PORT_VAL="$(env_get WEBHOOK_PORT)"
WEBHOOK_PORT_VAL="${WEBHOOK_PORT_VAL:-18791}"
_PORT_PID=$(lsof -ti :"$WEBHOOK_PORT_VAL" 2>/dev/null || true)
if [ -n "$_PORT_PID" ]; then
  warn "Port $WEBHOOK_PORT_VAL is still in use (pid $_PORT_PID), killing..."
  kill "$_PORT_PID" 2>/dev/null || true
  # Wait up to 5 seconds for port to be released
  for _w in 1 2 3 4 5; do
    sleep 1
    lsof -ti :"$WEBHOOK_PORT_VAL" &>/dev/null || break
  done
  if lsof -ti :"$WEBHOOK_PORT_VAL" &>/dev/null; then
    kill -9 "$(lsof -ti :"$WEBHOOK_PORT_VAL")" 2>/dev/null || true
    sleep 1
  fi
fi

if pm2 describe "$PM2_NAME" &>/dev/null; then
  pm2 restart "$PM2_NAME" --update-env --cwd "$BRIDGE_DIR"
  success "Bridge restarted"
else
  pm2 start "$BRIDGE_DIR/scripts/server.mjs" --name "$PM2_NAME" --cwd "$BRIDGE_DIR"
  success "Bridge process registered"
fi

pm2 save --force &>/dev/null

# ── 10. Verify bridge startup ─────────────────────────────────────────────────
# Note: HTTP health check may fail because the OpenClaw gateway can bind to the
# same port with auth proxy, returning 401 to unauthenticated requests.
# Use pm2 process status instead — it's reliable regardless of gateway state.
info "Waiting for Bridge to start..."
BRIDGE_OK=false

for _i in 1 2 3 4 5; do
  sleep 2
  PM2_STATUS=$(pm2 jlist 2>/dev/null | node -e "
    let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>{
      try { const p=JSON.parse(d).find(x=>x.name==='$PM2_NAME');
        process.stdout.write(p?.pm2_env?.status||'unknown');
      } catch { process.stdout.write('unknown'); }
    });" 2>/dev/null || echo "unknown")
  if [ "$PM2_STATUS" = "online" ]; then
    BRIDGE_OK=true
    break
  fi
done

if [ "$BRIDGE_OK" = true ]; then
  success "Bridge is running (pid $(pm2 pid $PM2_NAME 2>/dev/null))"
else
  error "Bridge did not start correctly within 10 seconds (status: $PM2_STATUS)"
  error "Run the following to diagnose:"
  echo  "    pm2 logs $PM2_NAME --lines 30"
  echo  "    pm2 show $PM2_NAME"
fi

RELAY_STATUS=$(curl -sf "https://oc.atomecorp.net/lark/health" 2>/dev/null || echo "unreachable")
if echo "$RELAY_STATUS" | grep -q '"status":"ok"'; then
  BRIDGES=$(echo "$RELAY_STATUS" | grep -o '"bridges":[0-9]*' | grep -o '[0-9]*')
  success "Relay is up — $BRIDGES bridge(s) connected"
else
  warn "Could not reach Relay. Check your network or contact your admin."
fi

# ── 11. Done ──────────────────────────────────────────────────────────────────
hr
echo -e "${GREEN}${BOLD}✅ Installation complete!${RESET}"
echo ""

CONFIGURED_APP_ID="$(env_get LARK_APP_ID)"
if [ -n "$CONFIGURED_APP_ID" ]; then
  echo -e "${BOLD}📌 Next: configure Lark Webhook${RESET}"
  echo "  Go to: https://open.larksuite.com/app → 事件与回调"
  echo "  Set Request URL to:"
  echo -e "  ${GREEN}https://oc.atomecorp.net/lark/webhook/${CONFIGURED_APP_ID}${RESET}"
  echo "  Click 'Verify' — you should see a green checkmark"
  echo ""
  echo -e "${YELLOW}⚠️  Then publish your app: 创建版本 → 申请上线${RESET}"
  echo "  Permissions and events take effect only after publishing."
  echo ""
fi

echo "Bridge status:  pm2 status $PM2_NAME"
echo "Bridge logs:    pm2 logs $PM2_NAME"
echo "Relay logs:     https://oc.atomecorp.net/lark/logs?token=$(env_get RELAY_SECRET)&appId=${CONFIGURED_APP_ID}&format=html"
echo ""

hr
echo -e "${BOLD}📌 Required Lark Permissions${RESET}"
echo "  Permissions JSON (for 权限申请 | 批量导入):"
echo ""
echo '  {"scopes":{"tenant":["contact:user.base:readonly","contact:contact.base:readonly","im:chat","im:chat.members:read","im:chat:read","im:chat:readonly","im:message","im:message.group_at_msg:readonly","im:message.group_msg:readonly","im:message.p2p_msg:readonly","im:message.pins:read","im:message.reactions:read","im:message.reactions:write_only","im:message:readonly","im:message:send_as_bot","im:resource"],"user":[]}}'
echo ""
echo "  Full JSON also saved to: $BRIDGE_DIR/lark-permissions.json"
hr
