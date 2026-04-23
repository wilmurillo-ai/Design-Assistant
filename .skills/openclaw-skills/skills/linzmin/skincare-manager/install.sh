#!/bin/bash
# 护肤管家安装脚本

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SKILL_DIR/data"
DATABASE_DIR="$SKILL_DIR/database"

echo "🧴 正在安装护肤管家..."

# 创建数据目录
mkdir -p "$DATA_DIR"
mkdir -p "$DATABASE_DIR/official"

# 初始化数据文件
if [ ! -f "$DATA_DIR/routines.json" ]; then
    echo "📝 创建护肤流程数据..."
    cat > "$DATA_DIR/routines.json" << 'EOF'
{
  "user_id": "PLACEHOLDER",
  "morning": [],
  "night": [],
  "updated_at": ""
}
EOF
fi

if [ ! -f "$DATA_DIR/products.json" ]; then
    echo "📦 创建产品库存数据..."
    cat > "$DATA_DIR/products.json" << 'EOF'
{
  "products": [],
  "updated_at": ""
}
EOF
fi

# 初始化成分数据库（基础版）
if [ ! -f "$DATA_DIR/ingredients.json" ]; then
    echo "🔬 创建基础成分数据库..."
    cat > "$DATA_DIR/ingredients.json" << 'EOF'
{
  "烟酰胺": {
    "inci_name": "Niacinamide",
    "aliases": ["维生素 B3", "尼克酰胺"],
    "efficacy": [
      {
        "effect": "美白淡斑",
        "mechanism": "抑制黑色素转移",
        "source": "国家药监局",
        "authority": 5
      }
    ],
    "safety": {
      "cosdna_rating": "0-1",
      "comedogenic": 1
    }
  },
  "透明质酸": {
    "inci_name": "Hyaluronic Acid",
    "aliases": ["玻尿酸", "HA"],
    "efficacy": [
      {
        "effect": "保湿补水",
        "mechanism": "吸收自身重量 1000 倍水分",
        "source": "《化妆品化学》",
        "authority": 4
      }
    ],
    "safety": {
      "cosdna_rating": "0",
      "comedogenic": 0
    }
  }
}
EOF
fi

# 初始化肤质数据
if [ ! -f "$DATA_DIR/skin-types.json" ]; then
    echo "📋 创建肤质类型数据..."
    cat > "$DATA_DIR/skin-types.json" << 'EOF'
{
  "types": [
    {
      "id": "oily",
      "name": "油性皮肤",
      "features": ["全脸出油", "毛孔粗大", "易长痘", "妆容易脱"],
      "care_tips": ["控油", "深层清洁", "清爽保湿", "定期去角质"]
    },
    {
      "id": "dry",
      "name": "干性皮肤",
      "features": ["皮肤干燥", "易起皮", "细纹明显", "易敏感"],
      "care_tips": ["补水", "保湿", "滋润", "温和清洁"]
    },
    {
      "id": "combination",
      "name": "混合性皮肤",
      "features": ["T 区油腻", "U 区干燥", "毛孔中等", "偶尔长痘"],
      "care_tips": ["T 区控油", "U 区保湿", "分区护理"]
    },
    {
      "id": "sensitive",
      "name": "敏感性皮肤",
      "features": ["易泛红", "易刺痛", "易过敏", "角质层薄"],
      "care_tips": ["温和", "修护屏障", "避免刺激", "简化护肤"]
    },
    {
      "id": "normal",
      "name": "中性皮肤",
      "features": ["水油平衡", "毛孔细致", "不易过敏", "状态稳定"],
      "care_tips": ["基础保湿", "防晒", "维持现状"]
    }
  ]
}
EOF
fi

# 添加 cron 任务（每周一检查到期）
echo "⏰ 添加到期提醒任务..."
(crontab -l 2>/dev/null | grep -v "skincare-manager" || true; echo "0 9 * * 1 $SKILL_DIR/scripts/check-expiry.js >> ~/.openclaw/logs/skincare.log 2>&1") | crontab -

echo ""
echo "✅ 护肤管家安装完成！"
echo ""
echo "🎯 快速开始："
echo "  1. 肤质测试：./scripts/skin-test.js"
echo "  2. 查询成分：./scripts/query-ingredient.js \"烟酰胺\""
echo "  3. 添加流程：./scripts/add-routine.js --time morning --product \"洁面\""
echo ""
echo "📝 查看文档：cat SKILL.md"
echo ""
