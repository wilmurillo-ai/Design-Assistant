---
name: Xiaomi-any2speech
description: 将任意内容（文本/文件/音频/视频）转为可直接播放的语音节目或单人 TTS，最长约 10 分钟，输出 WAV 音频。当用户提到以下任意意图时使用：做成播客/相声/辩论/有声书/Rap/新闻播报/脱口秀/情感电台/课程讲解、帮我读一下/朗读/念出来/转成语音/TTS/生成音频/转成音频、发语音/语音回复/做成XX发给我。
---

# Any2Speech

```bash
BASE=https://miplus-tts-public.ai.xiaomi.com
API_KEY=${API_KEY:-sk-anytospeech-pub-free}
```

## Step 1 · 确认输入来源

| 用户给了什么 | source_type | curl 参数 |
|---|---|---|
| 文字内容 | `text` | `-F "text=内容"` |
| 本地文件 | `file` | `-F "file=@/路径/文件"` |

**来源缺失时**：停下来问"请提供文字内容或文件路径"，不要猜测或用空值执行。

## Step 2 · 构造 instruction

- 用户明确描述了风格 → 直接用
- 用户只说"帮我读/念出来" → `instruction` 留空（单人朗读）
- 用户说了场景但没有细节 → 从下表取最近的模板

| 场景 | instruction |
|---|---|
| 两人播客 | `两人播客，一人理性分析，一人感性追问，偶尔插嘴，5 分钟内` |
| 相声 | `传统相声，甲逗哏（语速快、北京腔），乙捧哏（沉稳正经），至少两个包袱，结尾有收场词` |
| 新闻播报 | `CCTV 新闻联播风格，先播导语，再逐条播报，结尾有总结语` |
| 辩论 | `正反双方，正方激情澎湃，反方逻辑冷静，各做 30 秒总结陈词` |
| Rap | `押韵，节奏感强，两人 battle，明显停顿和连读节奏` |
| 脱口秀 | `单人独白，幽默有深度，有停顿节奏感，偶尔自嘲` |
| 情感电台 | `深夜电台，低沉磁性男声，语速缓慢` |
| 有声书 | `第三人称叙述，情绪随剧情起伏，遇到对话切换人物语气` |
| 短文本 TTS | `女声，职业干练，语速偏快` |

可叠加进阶控制：音色（`声音醇厚磁性，带沙哑感`）、情绪弧线（`开场铺垫，中段碰撞，结尾升华`）、互动（`允许插话，另一人时不时附和`）、环境音（`说到包袱处加观众笑声`）、时长（`控制在 10 分钟内`）、口音（`台湾腔 / 东北腔 / 四川话`）等等。

## Step 3 · 选接口并执行

**默认走同步接口**——大多数请求可在 10-120s 内完成。仅当同步返回 504 或输入为文件时再切异步。

---

### 同步接口（默认）

```bash
OUTPUT=output_$(date +%s).wav
curl -X POST "$BASE/v1/audio/generate" \
  -H "Authorization: Bearer $API_KEY" \
  -F "source_type=text" \
  -F "text=内容" \
  -F "instruction=风格描述" \
  --max-time 600 \
  --output "$OUTPUT"
echo "✓ 保存至 $OUTPUT"
```

### 异步接口（仅同步 504 或文件输入时使用）

```bash
OUTPUT=output_$(date +%s).wav

# 1. 提交，获取 job_id
JOB=$(curl -s -X POST "$BASE/v1/audio/jobs" \
  -H "Authorization: Bearer $API_KEY" \
  -F "source_type=text" \
  -F "text=内容" \
  -F "instruction=两人播客，一人理性分析，一人感性追问，5 分钟内" | jq -r '.job_id')
echo "已提交: $JOB"

# 2. 轮询直到完成（间隔 10s，静默等待，不要逐次向用户打印状态）
while true; do
  STATUS=$(curl -s -H "Authorization: Bearer $API_KEY" \
    "$BASE/v1/audio/jobs/$JOB" | jq -r '.status')
  [ "$STATUS" = "done" ]   && break
  [ "$STATUS" = "failed" ] && echo "生成失败" && exit 1
  sleep 10
done

# 3. 下载
curl -s -H "Authorization: Bearer $API_KEY" \
  "$BASE/v1/audio/jobs/$JOB/download" --output "$OUTPUT"
echo "✓ 保存至 $OUTPUT"
```

## 错误处理（自动重试，不要询问用户）

| 错误 | 处置 |
|---|---|
| 422 | 检查 source_type / text / file 参数后自动重试 |
| 504 | **立即切异步**，不要询问用户 |
| 502 / 500 | 等待 30s 后自动重试一次 |
| 异步失败 | 简化 instruction 后自动重新提交一次 |

## 飞书语音发送

**仅当用户说"发给我"/"发飞书"/"发到群里"时执行。**

前置：`ffmpeg`、`jq`、`$CHAT_ID`，以及 `$FEISHU_TENANT_TOKEN` 或 `$APP_ID`+`$APP_SECRET`（也可从 `~/.openclaw/openclaw.json` 读取）。

**`$CHAT_ID` 缺失时**：停下来问"请提供飞书群的 chat_id"，不要继续执行。

```bash
# 获取 token（三种来源，优先级从高到低）
if [ -z "$FEISHU_TENANT_TOKEN" ]; then
  if [ -n "$APP_ID" ] && [ -n "$APP_SECRET" ]; then
    FEISHU_TENANT_TOKEN=$(curl -s -X POST \
      "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
      -H "Content-Type: application/json" \
      -d "{\"app_id\":\"$APP_ID\",\"app_secret\":\"$APP_SECRET\"}" \
      | jq -r '.tenant_access_token')
  else
    FEISHU_TENANT_TOKEN=$(jq -r '.feishu.tenant_access_token // empty' \
      ~/.openclaw/openclaw.json 2>/dev/null)
  fi
fi
[ -z "$FEISHU_TENANT_TOKEN" ] || [ "$FEISHU_TENANT_TOKEN" = "null" ] && \
  echo "无法获取飞书 token，请检查 APP_ID/APP_SECRET 或 ~/.openclaw/openclaw.json 配置" && exit 1

ffmpeg -y -i "$OUTPUT" -c:a libopus -b:a 32k output.opus
DURATION_MS=$(ffprobe -v quiet -show_entries format=duration \
  -of csv=p=0 "$OUTPUT" | awk '{printf "%d", $1*1000}')
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $FEISHU_TENANT_TOKEN" \
  -F "file=@output.opus" -F "file_type=opus" \
  -F "file_name=tts.opus" -F "duration=$DURATION_MS" \
  | jq -r '.data.file_key')
curl -s -X POST \
  "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $FEISHU_TENANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"receive_id\":\"$CHAT_ID\",\"msg_type\":\"audio\",\"content\":\"{\\\"file_key\\\":\\\"$FILE_KEY\\\"}\"}"
```

无 ffmpeg 时：直接上传 WAV（`file_type=stream`、`msg_type=file`，去掉 `-F "duration=..."`）。

## 注意事项

- 音视频输入时要尽量保证时长小于10min
- 多人节目耗时 30s–10min，短文本 TTS 耗时 10–30s
- 音视频文件 > 20MB 建议先压缩或截短
- 支持格式：`txt` `md` `pdf` `docx` `csv` `json` `html` + 常见音视频格式
- 输出固定为 WAV；用时间戳命名（`output_$(date +%s).wav`）避免覆盖
