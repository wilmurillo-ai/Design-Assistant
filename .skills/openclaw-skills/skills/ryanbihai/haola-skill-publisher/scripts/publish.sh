#!/bin/bash
# publish.sh - 一键发布 Skill 到 ClawHub + GitHub
# 用法: ./publish.sh <skill-slug>
# 首次使用: cp .env.example .env 并填入 GITHUB_TOKEN

set -e
SKILL=${1:?用法: $0 <slug>}
WORKSPACE="/home/node/.openclaw/workspace"
SKILL_DIR="${WORKSPACE}/skills/${SKILL}"
GIT_DIR="${WORKSPACE}/${SKILL}-github"
ENV_FILE="$(dirname $0)/../.env"

# 加载 .env
if [ -f "$ENV_FILE" ]; then
  set -a
  source "$ENV_FILE"
  set +a
fi

if [ ! -d "$SKILL_DIR" ]; then
  echo "[ERROR] Skill 目录不存在: $SKILL_DIR"; exit 1
fi

VER=$(node -p "require('${SKILL_DIR}/_meta.json').version" 2>/dev/null || echo "1.0.0")
MSG=$(node -p "require('${SKILL_DIR}/_meta.json').changelog" 2>/dev/null || echo "Update")
echo "[INFO] 发布 ${SKILL} v${VER}"

echo "[1/3] 同步到 GitHub..."
if [ -d "$GIT_DIR" ]; then
  cp ${SKILL_DIR}/SKILL.md ${SKILL_DIR}/_meta.json ${GIT_DIR}/ 2>/dev/null || true
  find ${SKILL_DIR} -maxdepth 3 -name "*.js" -o -name "*.json" -o -name "*.md" 2>/dev/null \
    | head -50 | while read f; do
      [ -f "$f" ] && cp "$f" "$GIT_DIR/" 2>/dev/null || true
    done
  cd ${GIT_DIR}
  git add -A && git commit -m "${MSG}" && \
  GIT_TOKEN=${GITHUB_TOKEN} git push 2>/dev/null && echo "[OK] GitHub 已推送" || echo "[WARN] GitHub 无更新或推送失败"
else
  echo "[WARN] GitHub 目录不存在，跳过"
fi

echo "[2/3] 发布 ClawHub..."
cd ${WORKSPACE}/skills/${SKILL}
npx -y clawhub publish . --slug ${SKILL} --version ${VER} --changelog "${MSG}" --tags latest

echo ""
echo "[DONE] ${SKILL} v${VER} 已发布"
echo ""
echo "手动平台: COZE/元器/百炼 → python scripts/gen_submission.py ${SKILL}"
