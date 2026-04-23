#!/bin/bash
# create-capsule.sh
# 创建经验胶囊
# 用法: bash create-capsule.sh "<胶囊名称>" "<任务类型>" "<成功模式描述>"
# 任务类型: research | write | refactor | automation | browser | feishu | fetch | subagent | other

set -e

CAPSULES_DIR="$(dirname "$0")/../capsules"
MEMORY_LOG="$HOME/.openclaw/workspace/memory/胶囊创建记录.md"

# 解析参数
NAME="${1:-}"
TYPE="${2:-}"
PATTERN="${3:-}"

if [ -z "$NAME" ] || [ -z "$TYPE" ] || [ -z "$PATTERN" ]; then
  echo "用法: bash create-capsule.sh \"<胶囊名称>\" \"<任务类型>\" \"<成功模式描述>\""
  echo "任务类型: research | write | refactor | automation | browser | feishu | fetch | subagent | other"
  exit 1
fi

# 生成ID
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%H%M%S)
CAP_ID="CAP-$(date +%m%d)-${TIMESTAMP}"

# 创建胶囊目录
mkdir -p "$CAPSULES_DIR"

# 生成胶囊文件
CAPSULE_FILE="$CAPSULES_DIR/${CAP_ID}.md"

cat > "$CAPSULE_FILE" << EOF
---
id: $CAP_ID
name: $NAME
type: $TYPE
created: $DATE
maturity: raw
success_count: 1
trigger_keywords: []
pattern:
  - $PATTERN
result_summary: 首次创建
notes: ""
---

# $NAME

**ID:** $CAP_ID
**类型:** $TYPE
**创建时间:** $DATE
**成熟度:** raw（原始）

## 成功模式
$PATTERN

## 使用记录
| 时间 | 任务 | 结果 |
|:---|:---|:---|
| $DATE | 首次创建 | ✅ 成功 |

## 下次改进
（暂无）
EOF

echo "✅ 胶囊创建成功！"
echo "文件: $CAPSULE_FILE"
echo ""
echo "成熟度说明："
echo "  raw（原始）— 首次成功，记录但不自动触发"
echo "  tested（已验证）— 连续成功2次后升级"
echo "  stable（稳定）— 连续成功5次后升级"
echo ""
echo "💡 胶囊使用成功后会根据连续成功次数自动升级"
