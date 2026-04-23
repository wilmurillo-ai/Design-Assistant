#!/bin/bash
# 飞书文档完整复制脚本
# 用法：./feishu-doc-copy.sh <源文档 ID> <新文档标题>

set -e  # 遇到错误立即退出

SOURCE_DOC_ID="$1"
NEW_DOC_TITLE="$2"
BLOCK_SIZE=9000  # 每块字符数

if [ -z "$SOURCE_DOC_ID" ] || [ -z "$NEW_DOC_TITLE" ]; then
  echo "用法：$0 <源文档 ID> <新文档标题>"
  echo "示例：$0 ABC123xyz 文档标题 - 副本"
  exit 1
fi

# 创建临时目录
TEMP_DIR="/tmp/feishu_copy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEMP_DIR"

echo "📋 开始复制飞书文档..."
echo "   源文档 ID: $SOURCE_DOC_ID"
echo "   新文档标题：$NEW_DOC_TITLE"
echo "   临时目录：$TEMP_DIR"
echo ""

# 步骤 1: 获取源文档信息
echo "📊 步骤 1: 获取源文档信息..."
DOC_INFO=$(openclaw feishu fetch-doc --doc_id "$SOURCE_DOC_ID" --limit 50)
TOTAL_LENGTH=$(echo "$DOC_INFO" | jq -r '.total_length')
SOURCE_TITLE=$(echo "$DOC_INFO" | jq -r '.title')

echo "   源文档标题：$SOURCE_TITLE"
echo "   原文档总长度：$TOTAL_LENGTH 字符"

# 步骤 2: 计算分块数量
BLOCK_COUNT=$(( ($TOTAL_LENGTH + $BLOCK_SIZE - 1) / $BLOCK_SIZE ))
echo "   分块大小：$BLOCK_SIZE 字符/块"
echo "   分块数量：$BLOCK_COUNT 块"
echo ""

# 步骤 3: 分块读取
echo "📥 步骤 3: 分块读取源文档..."
OFFSET=0
BLOCK_NUM=0

while [ $OFFSET -lt $TOTAL_LENGTH ]; do
  echo "   读取块 $BLOCK_NUM（offset: $OFFSET）..."
  
  openclaw feishu fetch-doc \
    --doc_id "$SOURCE_DOC_ID" \
    --limit $BLOCK_SIZE \
    --offset $OFFSET \
    > "$TEMP_DIR/chunk_${BLOCK_NUM}.json"
  
  # 提取 markdown 内容
  cat "$TEMP_DIR/chunk_${BLOCK_NUM}.json" | jq -r '.markdown' > "$TEMP_DIR/chunk_${BLOCK_NUM}.md"
  
  # 检查是否还有更多
  HAS_MORE=$(cat "$TEMP_DIR/chunk_${BLOCK_NUM}.json" | jq -r '.has_more')
  
  if [ "$HAS_MORE" = "false" ]; then
    echo "   ✅ 最后一块读取完成"
    break
  fi
  
  OFFSET=$(( $OFFSET + $BLOCK_SIZE ))
  BLOCK_NUM=$(( $BLOCK_NUM + 1 ))
  
  sleep 0.5
done

TOTAL_BLOCKS=$BLOCK_NUM
echo "   ✅ 共读取 $(( $TOTAL_BLOCKS + 1 )) 块"
echo ""

# 步骤 4: 创建新文档
echo "📝 步骤 4: 创建新文档..."
NEW_DOC=$(openclaw feishu create-doc \
  --title "$NEW_DOC_TITLE" \
  --markdown "# $NEW_DOC_TITLE\n\n正在搬运中...")

NEW_DOC_ID=$(echo "$NEW_DOC" | jq -r '.doc_id')
NEW_DOC_URL=$(echo "$NEW_DOC" | jq -r '.doc_url')

echo "   新文档 ID: $NEW_DOC_ID"
echo "   新文档链接：$NEW_DOC_URL"
echo ""

# 步骤 5: 分块写入
echo "📤 步骤 5: 分块写入新文档..."

for i in $(seq 0 $TOTAL_BLOCKS); do
  CHUNK_FILE="$TEMP_DIR/chunk_${i}.md"
  
  if [ $i -eq 0 ]; then
    MODE="overwrite"
  else
    MODE="append"
  fi
  
  echo "   写入块 $i（$MODE 模式）..."
  
  openclaw feishu update-doc \
    --doc_id "$NEW_DOC_ID" \
    --mode $MODE \
    --markdown @"$CHUNK_FILE"
  
  sleep 1
done

echo "   ✅ 所有块写入完成"
echo ""

# 步骤 6: 验证
echo "🔍 步骤 6: 验证结果..."

NEW_DOC_INFO=$(openclaw feishu fetch-doc --doc_id "$NEW_DOC_ID" --limit 50)
NEW_LENGTH=$(echo "$NEW_DOC_INFO" | jq -r '.total_length')

DIFF=$(( $TOTAL_LENGTH - $NEW_LENGTH ))
PERCENT=$(echo "scale=2; $NEW_LENGTH * 100 / $TOTAL_LENGTH" | bc)

echo "   原文档：$TOTAL_LENGTH 字符"
echo "   新文档：$NEW_LENGTH 字符"
echo "   差异：$DIFF 字符（$PERCENT% 完整）"

if [ $(echo "$PERCENT >= 98" | bc) -eq 1 ]; then
  echo "   ✅ 验证通过（差异 < 2%，主要是图片 token）"
  VERIFICATION_STATUS="✅ 通过"
else
  echo "   ⚠️ 差异较大，请手动检查"
  VERIFICATION_STATUS="⚠️ 需检查"
fi
echo ""

# 步骤 7: 清理
echo "🧹 步骤 7: 清理临时文件..."
rm -rf "$TEMP_DIR"
echo "   ✅ 临时文件已清理"
echo ""

# 输出结果
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 复制完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   源文档：$SOURCE_TITLE"
echo "   新文档：$NEW_DOC_TITLE"
echo "   新文档链接：$NEW_DOC_URL"
echo "   完整性：$VERIFICATION_STATUS"
echo "   原文档：$TOTAL_LENGTH 字符"
echo "   新文档：$NEW_LENGTH 字符"
echo "   差异：$DIFF 字符"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
