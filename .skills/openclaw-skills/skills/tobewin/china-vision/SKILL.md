---
name: china-vision
description: 多模态图片理解工具。Use when user wants to analyze, describe, or understand images using AI vision models. Supports scene analysis, object recognition, chart interpretation, food identification, and detailed image descriptions. Uses Qwen2.5-VL-72B. 图片识别、图片分析、视觉理解。
version: 1.0.1
license: MIT-0
metadata: {"openclaw": {"emoji": "👁️", "requires": {"bins": ["curl", "python3"], "env": ["SILICONFLOW_API_KEY"]}, "primaryEnv": "SILICONFLOW_API_KEY"}}
---

# China Vision - 多模态图片理解

使用AI视觉语言模型分析和理解图片内容。

## 与 china-doc-ocr 的区别

| 功能 | china-doc-ocr | china-vision |
|------|---------------|--------------|
| 文档识别 | ✅ 优秀 | ⚠️ 一般 |
| 表格提取 | ✅ 优秀 | ⚠️ 一般 |
| 发票/证件 | ✅ 优秀 | ❌ 不适合 |
| 图片描述 | ❌ 不支持 | ✅ 优秀 |
| 场景分析 | ❌ 不支持 | ✅ 优秀 |
| 图表解读 | ⚠️ 一般 | ✅ 优秀 |
| 商品识别 | ❌ 不支持 | ✅ 优秀 |

## 适用场景

| 场景 | 示例 |
|------|------|
| 图片描述 | "这张图片是什么内容？" |
| 场景分析 | "分析这张风景照的构图" |
| 图表解读 | "这个柱状图说明什么？" |
| 商品识别 | "这是什么品牌的产品？" |
| 食物识别 | "这是什么菜？怎么做的？" |
| 人物分析 | "描述这张照片中的人物" |

## Trigger Conditions

- "这是什么图片" / "What is this image?"
- "描述这张图片" / "Describe this image"
- "分析这张照片" / "Analyze this photo"
- "这个图表说明什么" / "What does this chart show?"
- "这是什么菜" / "What food is this?"
- "这是什么品牌" / "What brand is this?"
- "china-vision"

---

## 模型说明

使用 **Qwen2.5-VL-72B-Instruct** 视觉语言模型：

- ✅ 强大的图片理解能力
- ✅ 支持中英文对话
- ⚠️ 收费模型（按token计费）
- ✅ 国内直连
- ✅ 效果优秀

**注意**：这是付费模型，请注意token消耗

---

## Step 1: 识别请求类型

```
用户输入图片 → 判断请求类型：

"描述这张图片"     → 详细描述模式
"这是什么"         → 识别模式
"分析..."          → 分析模式
"对比..."          → 对比模式（多张图）
未指定             → 默认描述模式
```

---

## Step 2: 图片分析

### 单张图片分析

```bash
IMAGE_PATH="/path/to/image.jpg"

# 编码为 base64
BASE64_DATA=$(python3 -c "
import base64
with open('$IMAGE_PATH', 'rb') as f:
    print(base64.b64encode(f.read()).decode('utf-8'))
")

# 判断格式
EXT="${IMAGE_PATH##*.}"
case "$EXT" in
  jpg|jpeg) MIME="image/jpeg" ;;
  png)      MIME="image/png" ;;
  webp)     MIME="image/webp" ;;
  *)        MIME="image/jpeg" ;;
esac

# 用户请求类型
USER_REQUEST="请详细描述这张图片的内容"

# 调用 Qwen2.5-VL
curl -s -X POST "https://api.siliconflow.cn/v1/chat/completions" \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"Qwen/Qwen2.5-VL-72B-Instruct\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {
            \"type\": \"image_url\",
            \"image_url\": {
              \"url\": \"data:${MIME};base64,${BASE64_DATA}\"
            }
          },
          {
            \"type\": \"text\",
            \"text\": \"$USER_REQUEST\"
          }
        ]
      }
    ],
    \"max_tokens\": 2048
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data['choices'][0]['message']['content'])
"
```

### 图片URL分析

```bash
IMAGE_URL="https://example.com/photo.jpg"

curl -s -X POST "https://api.siliconflow.cn/v1/chat/completions" \
  -H "Authorization: Bearer $SILICONFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"Qwen/Qwen2.5-VL-72B-Instruct\",
    \"messages\": [
      {
        \"role\": \"user\",
        \"content\": [
          {
            \"type\": \"image_url\",
            \"image_url\": {
              \"url\": \"$IMAGE_URL\"
            }
          },
          {
            \"type\": \"text\",
            \"text\": \"请详细描述这张图片\"
          }
        ]
      }
    ],
    \"max_tokens\": 2048
  }" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data['choices'][0]['message']['content'])
"
```

---

## Prompt 模板

### 图片描述

```
请详细描述这张图片的内容，包括：
1. 主要对象/人物
2. 场景/背景
3. 颜色/光线
4. 构图/布局
5. 整体氛围
```

### 场景分析

```
请分析这张照片的：
1. 拍摄场景
2. 时间/天气
3. 地点特征
4. 主体行为
5. 摄影技巧
```

### 图表解读

```
请解读这张图表：
1. 图表类型
2. 横轴/纵轴含义
3. 主要数据趋势
4. 关键数据点
5. 结论/洞察
```

### 商品识别

```
请识别这张图片中的商品：
1. 商品类型
2. 品牌（如果可见）
3. 产品特征
4. 用途/功能
5. 参考价格（如果知道）
```

### 食物识别

```
请识别这张食物图片：
1. 菜品名称
2. 菜系（中餐/西餐/日料等）
3. 主要食材
4. 可能的口味
5. 制作方法简述
```

---

## 输出格式

### 图片描述

```
┌──────────────────────────────────────────────┐
│  👁️ 图片分析结果                              │
└──────────────────────────────────────────────┘

📸 图片描述
这是一张在城市街道拍摄的夜景照片。画面中可以看到
灯火通明的商业区，高楼林立，车流穿梭...

🎨 画面构成
├─ 主体: 城市街道夜景
├─ 背景: 高层建筑群
├─ 光线: 人工照明，暖色调
└─ 构图: 仰拍视角

💡 分析
这张照片展现了现代都市的繁华夜生活，拍摄者
选择了仰拍角度，突出了建筑的高度感...
```

---

## 与 china-doc-ocr 的协作

```
用户上传发票照片
    ↓
优先尝试 china-doc-ocr (OCR模型)
    ↓
如果识别效果不好
    ↓
降级到 china-vision (视觉语言模型)
```

---

## Notes

- 使用 Qwen2.5-VL-72B-Instruct 视觉语言模型
- 需要 SILICONFLOW_API_KEY
- 适合图片理解和分析，不适合文档OCR
- 文档OCR请使用 china-doc-ocr
