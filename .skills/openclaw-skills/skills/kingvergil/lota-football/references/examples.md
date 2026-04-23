# Lota Football 技能使用示例

## 环境设置
使用前需配置环境变量：
```bash
# 设置API密钥（必需）
export LOTA_API_KEY="your_api_key_here"

# 设置API基础URL（可选，默认为 http://deepdata.lota.tv/）
export LOTA_API_BASE_URL="http://deepdata.lota.tv/"
```

## 在Claude Code中使用

### 基本查询
```
/lota_football 获取今日竞彩列表
/lota_football 查询北单比赛
/lota_football 查找明天英超竞彩比赛
```

### 联赛查询
```
/lota_football 英超比赛有哪些
/lota_football 查看本周西甲比赛
/lota_football 意甲竞彩比赛
/lota_football 德甲北单比赛
```

### 日期查询
```
/lota_football 今天竞彩足球比赛
/lota_football 明天北单比赛
/lota_football 昨天已完赛的比赛
/lota_football 本周未开赛的比赛
/lota_football 周末英超比赛
```

### 状态查询
```
/lota_football 未开赛的竞彩比赛
/lota_football 已完赛的北单比赛
/lota_football 正在进行的比赛
```

### 球队查询
```
/lota_football 曼联的比赛
/lota_football 皇马对巴萨的比赛
/lota_football 曼城 vs 利物浦
/lota_football 阿森纳对阵切尔西
```

### 特征文本查询
```
/lota_football 曼联对切尔西的特征文本
/lota_football 获取皇马对巴萨的特征数据
/lota_football 曼城对利物浦的比赛特征
```

## 直接使用脚本
技能的网络访问逻辑封装在 `scripts/` 目录中，可直接调用：

### 基本脚本调用
```bash
# 进入技能目录
cd /path/to/.claude/skills/lota_football

# 使用Python脚本查询
python scripts/lota_api_client.py "查询今日竞彩比赛"
python scripts/lota_api_client.py "获取曼联对切尔西的特征文本"
python scripts/lota_api_client.py "查找明天英超比赛"
```

### 脚本输出示例
```bash
$ python scripts/lota_api_client.py "获取今日竞彩列表"

============================================================
📋 LOTA API CURL 命令生成
============================================================

🔍 查询: 获取今日竞彩列表

📊 解析参数: {'date': 'today', 'lottery_type': 'jingcai'}

🎯 API参数: {'is_jingcai': 'true', 'status': '未开赛', 'limit': '10', 'start_date': '2025-03-15', 'end_date': '2025-03-15'}

============================================================
🔗 CURL 命令:
============================================================

curl -X GET 'http://deepdata.lota.tv/predictions/api/v2/matches/?is_jingcai=true&status=未开赛&limit=10&start_date=2025-03-15&end_date=2025-03-15' \
  -H 'Authorization: Bearer your_api_key' \
  -H 'Accept: application/json'

============================================================
📖 使用说明:
============================================================
  1. 复制上面的curl命令并在终端执行
  2. 命令将返回比赛列表JSON数据
  3. 从返回的数据中找到想要的比赛的lota_id
  4. 使用以下命令获取特征文本（替换YOUR_LOTA_ID）：
     curl -X GET 'http://deepdata.lota.tv/predictions/api/v2/compact-fet/?lota_id=YOUR_LOTA_ID' \
       -H 'Authorization: Bearer your_api_key' \
       -H 'Accept: application/json'
  提示：执行第一个命令获取比赛列表后，找到对应比赛的lota_id，替换YOUR_LOTA_ID执行第二个命令
```

## 手动curl命令示例

### 比赛查询命令
```bash
# 查询今天英超比赛（前10场）
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?league=英超&limit=10"

# 查询明天竞彩比赛
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?is_jingcai=true&start_date=$(date -v+1d +%Y-%m-%d)&end_date=$(date -v+1d +%Y-%m-%d)"

# 查询本周北单比赛
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?is_beidan=true&start_date=$(date -v-monday +%Y-%m-%d)&end_date=$(date -v+sunday +%Y-%m-%d)"

# 查询特定球队比赛（曼联）
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?limit=50" | jq '.data.matches[] | select(.home_name | contains("曼联") or .away_name | contains("曼联"))'
```

### 特征文本获取命令
```bash
# 获取特定比赛的特征文本（替换LOTA_ID）
LOTA_ID="Lota4343308"
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=$LOTA_ID"

# 使用Bearer Token认证
curl -H "Authorization: Bearer $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=$LOTA_ID"

# 批量获取多场比赛特征文本
for LOT_ID in Lota4343308 Lota4343309 Lota4343310; do
  echo "=== 获取比赛 $LOT_ID 的特征文本 ==="
  curl -s -H "X-API-Key: $LOTA_API_KEY" \
    "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=$LOT_ID" | jq -r '.compact_fet'
  echo ""
done
```

## 实际工作流示例

### 示例1：分析今日竞彩比赛
```bash
# 1. 查询今日竞彩比赛列表
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?is_jingcai=true&status=未开赛&limit=20" \
  > matches_today.json

# 2. 提取比赛ID和基本信息
cat matches_today.json | jq '.data.matches[] | {lota_id, home_name, away_name, league_name, match_time, jingcai_id}'

# 3. 选择感兴趣的比赛，获取特征文本
SELECTED_ID="Lota4343308"
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=$SELECTED_ID" \
  > feature_$SELECTED_ID.json

# 4. 查看特征文本
cat feature_$SELECTED_ID.json | jq -r '.compact_fet'
```

### 示例2：批量分析周末英超比赛
```bash
#!/bin/bash
# weekend_analysis.sh

# 获取本周六日期
SATURDAY=$(date -v+saturday +%Y-%m-%d)
SUNDAY=$(date -v+sunday +%Y-%m-%d)

echo "分析周末（$SATURDAY 至 $SUNDAY）英超比赛..."

# 查询周末英超比赛
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?league=英超&start_date=$SATURDAY&end_date=$SUNDAY&status=未开赛" \
  > weekend_premier.json

# 提取比赛ID列表
MATCH_IDS=$(cat weekend_premier.json | jq -r '.data.matches[].lota_id')

# 为每场比赛获取特征文本
for ID in $MATCH_IDS; do
  echo "处理比赛: $ID"
  curl -s -H "X-API-Key: $LOTA_API_KEY" \
    "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=$ID" \
    | jq -r '.compact_fet' > "feature_${ID}.txt"
done

echo "完成！共处理 $(echo $MATCH_IDS | wc -w) 场比赛。"
```

### 示例3：监控赔率变化
```bash
#!/bin/bash
# odds_monitor.sh

MATCH_ID="Lota4343308"
INTERVAL=300  # 5分钟

echo "监控比赛 $MATCH_ID 赔率变化，每 $INTERVAL 秒更新一次..."

while true; do
  TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
  echo "=== $TIMESTAMP ==="

  # 获取当前特征文本
  curl -s -H "X-API-Key: $LOTA_API_KEY" \
    "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=$MATCH_ID" \
    | jq -r '.compact_fet | match("\\[欧赔\\].*") | .string' \
    | head -1

  echo ""
  sleep $INTERVAL
done
```

## 故障排除示例

### 问题1：认证失败
```bash
# 错误信息
{"code": 2, "message": "Authentication failed", "data": null}

# 解决方案
# 检查环境变量是否正确设置
echo $LOTA_API_KEY
# 重新设置环境变量
export LOTA_API_KEY="your_correct_api_key"
```

### 问题2：比赛未找到
```bash
# 错误信息
{"code": 3, "message": "Match not found", "data": null}

# 解决方案
# 1. 确认比赛ID是否正确
# 2. 检查比赛是否已过期
# 3. 查询比赛列表确认ID
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?lota_id=Lota4343308"
```

### 问题3：网络连接问题
```bash
# 错误信息
curl: (7) Failed to connect to deepdata.lota.tv port 80: Connection refused

# 解决方案
# 1. 检查网络连接
ping deepdata.lota.tv
# 2. 尝试使用IP地址
export LOTA_API_BASE_URL="http://113.31.103.148:3013/"
# 3. 检查防火墙设置
```

## 最佳实践

### 1. 环境变量管理
```bash
# 创建环境变量配置文件
cat > ~/.lota_env << EOF
export LOTA_API_KEY="your_api_key"
export LOTA_API_BASE_URL="http://deepdata.lota.tv/"
EOF

# 在脚本中加载
source ~/.lota_env
```

### 2. 错误处理
```bash
# 在脚本中添加错误处理
response=$(curl -s -w "%{http_code}" -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?limit=1")

http_code=${response: -3}
body=${response:0:-3}

if [ "$http_code" -eq 200 ]; then
  echo "请求成功"
  echo "$body" | jq .
else
  echo "请求失败，HTTP代码: $http_code"
  echo "$body"
fi
```

### 3. 数据缓存
```bash
# 实现简单缓存机制
CACHE_DIR="/tmp/lota_cache"
mkdir -p "$CACHE_DIR"

get_match_list() {
  local cache_file="$CACHE_DIR/matches_$(date +%Y%m%d%H).json"

  # 如果缓存存在且小于1小时，使用缓存
  if [ -f "$cache_file" ] && [ $(($(date +%s) - $(stat -f%c "$cache_file"))) -lt 3600 ]; then
    cat "$cache_file"
  else
    curl -s -H "X-API-Key: $LOTA_API_KEY" \
      "$LOTA_API_BASE_URL/predictions/api/v2/matches/?limit=100" \
      | tee "$cache_file"
  fi
}
```

### 4. 脚本自动化
```bash
#!/bin/bash
# daily_report.sh - 每日比赛报告

# 生成报告目录
REPORT_DIR="$HOME/lota_reports/$(date +%Y-%m-%d)"
mkdir -p "$REPORT_DIR"

# 1. 获取今日竞彩比赛
echo "获取今日竞彩比赛..." > "$REPORT_DIR/report.txt"
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?is_jingcai=true&status=未开赛" \
  | jq '.data.matches[] | {lota_id, home_name, away_name, match_time, jingcai_id}' \
  >> "$REPORT_DIR/report.txt"

# 2. 为每场比赛获取特征文本
echo -e "\n\n特征文本摘要:" >> "$REPORT_DIR/report.txt"
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?is_jingcai=true&status=未开赛" \
  | jq -r '.data.matches[].lota_id' \
  | while read LOT_ID; do
    echo "=== $LOT_ID ===" >> "$REPORT_DIR/report.txt"
    curl -s -H "X-API-Key: $LOTA_API_KEY" \
      "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=$LOT_ID" \
      | jq -r '.compact_fet | match("^.*\\n.*\\n.*\\n.*\\n.*") | .string' \
      >> "$REPORT_DIR/report.txt"
    echo "" >> "$REPORT_DIR/report.txt"
  done

echo "报告生成完成: $REPORT_DIR/report.txt"
```

## 进阶使用

### 与jq结合进行数据分析
```bash
# 提取所有比赛的联赛分布
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?limit=100" \
  | jq '.data.matches[] | .league_name' \
  | sort | uniq -c | sort -rn

# 统计不同状态的比赛数量
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?limit=200" \
  | jq '.data.matches[] | .state_name' \
  | sort | uniq -c

# 提取比赛时间分布
curl -s -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?limit=150" \
  | jq -r '.data.matches[] | .match_time | sub("T"; " ") | sub(":\\d{2}$"; "")' \
  | sort | uniq -c
```

### 集成到其他工具中
```bash
# Python脚本集成示例
#!/usr/bin/env python3
import os
import json
import subprocess

def get_lota_matches(league=None, date=None):
    """调用Lota API获取比赛列表"""
    api_key = os.environ.get('LOTA_API_KEY')
    base_url = os.environ.get('LOTA_API_BASE_URL', 'http://deepdata.lota.tv/')

    cmd = ['curl', '-s', '-H', f'X-API-Key: {api_key}']

    url = f'{base_url.rstrip("/")}/predictions/api/v2/matches/'
    params = ['limit=50']

    if league:
        params.append(f'league={league}')
    if date:
        params.append(f'start_date={date}')
        params.append(f'end_date={date}')

    if params:
        url += '?' + '&'.join(params)

    cmd.append(url)

    result = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(result.stdout)

# 使用示例
matches = get_lota_matches(league='英超', date='2025-03-15')
for match in matches.get('data', {}).get('matches', []):
    print(f"{match['home_name']} vs {match['away_name']} - {match['match_time']}")
```

这些示例展示了Lota Football技能的各种使用场景，您可以根据实际需求进行调整和扩展。