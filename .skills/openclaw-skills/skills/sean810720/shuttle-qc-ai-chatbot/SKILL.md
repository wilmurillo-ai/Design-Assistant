# shuttle-qc-ai-chatbot Skill v2.1.0

## 📖 概述

自動化操作 Shuttle QC AI Chatbot，支援單次查詢與批次執行，無需手動操控瀏覽器。

## ✨ 功能

- 🔗 自動啟動瀏覽器並載入目標頁面
- 📝 輸入任意查詢文字（產品型號、問題等）
- ⏳ 智能等待 AI 回應（可設定 timeout）
- 📋 提取完整回應內容（結構化資料）
- 🚀 支援批次查詢（多個指令一次執行）
- 📊 輸出結果為 JSON 或純文字
- 🔄 支援產品比較（e.g., "DL30N vs DL40N"）

## 🛠️ 使用方式

### CLI 指令

```bash
# 單次查詢
shuttle-qc-ai-chatbot query "p55u?"

# 批次查詢（從檔案讀取）
shuttle-qc-ai-chatbot batch queries.txt

# 指定自訂 URL
shuttle-qc-ai-chatbot query "p55u?" --url http://192.168.100.98:8888/v1
```

### 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `query` | 單次查詢文字 | - |
| `batch` | 批次查詢檔案路徑（每行一筆） | - |
| `--url` | 目標網頁 URL | `http://192.168.100.98:8888/v1` |
| `--timeout` | 等待回應超時秒數 | `30` |
| `--output` | 輸出格式：`json` 或 `text` | `json` |
| `--headless` | 無頭模式（不顯示瀏覽器） | `false` |

## 📥 輸入格式

### 單次查詢
直接傳入查詢字串：
```bash
shuttle-qc-ai-chatbot query "p25n"
```

### 批次查詢
檔案格式（每行一筆）：
```txt
p25n
p55u?
xpc?
```

## 📤 輸出格式

### JSON（預設）
```json
{
  "url": "http://192.168.100.98:8888/v1",
  "query": "p55u?",
  "response": "Hello!👋🏻 ... 產品規格表 ...",
  "timestamp": "2026-03-17T14:20:00+08:00"
}
```

### Text
```
=== 查詢：p55u? ===
[回應內容]
Hello!👋🏻 I am AI intelligent assistant...
[規格資料]
- Model: P55U
...
==================
```

## 🔧 工作原理

1. 啟動 OpenClaw browser 工具（Brave）
2. 導航到目標 URL
3. 使用 `evaluate` 執行 JavaScript 動查找並點擊輸入框
4. 輸入查詢內容到 textbox
5. 按下 Enter 送出
6. 監控頁面變化，等待 AI 回覆出現
7. 提取完整對話內容（包含產品規格）
8. 關閉瀏覽器（或保留根據設定）

## 🧩 相依性

- OpenClaw 環境（內建 `browser` 工具）
- Brave 瀏覽器（或可用 Chrome）

## 📦 安裝

從 ClawHub 安裝：
```bash
clawhub install shuttle-qc-ai-chatbot
```

或手動複製到 `~/.openclaw/workspace/skills/` 目錄。

## 📌 使用範例

### 基本產品查詢
```bash
shuttle-qc-ai-chatbot query "DL30N spec"
shuttle-qc-ai-chatbot query "P55U?"
```

### 產品系列比較（進階）
```bash
shuttle-qc-ai-chatbot query "Compare DL30N and DL40N"
shuttle-qc-ai-chatbot query "DL30N vs DL40N"
```

### 批次查詢
建立 `queries.txt`：
```txt
DL30N
DL40N
SB860R8
P55U
```

執行：
```bash
shuttle-qc-ai-chatbot batch queries.txt --output json
```

### 自訂參數
```bash
shuttle-qc-ai-chatbot query "NE20N spec" --timeout 60 --output text
```

## ⚠️ 注意事項

- 確保Local服務（192.168.100.98:8888）已啟動
- 第一次使用會啟動 Brave 瀏覽器
- 批次查詢時建議設定 `--headless` 避免干擾
- 等待時間依伺服器負載而定，可調整 `--timeout`

## 📄 變更歷史

### v1.0.1 (2026-03-17)
- **文件更新**：新增產品比較使用範例
- **skill.json**：新增 comparison tag，提升版本號
- **README**：新增進階用法、產品比較範例、注意事項
- **描述更新**：強調支援產品比較功能（如 DL30N vs DL40N）

### v1.0.0 (2026-03-17)
- 初版發佈
- 支援單次與批次查詢
- 自動化瀏覽器操作
- JSON/Text 輸出格式

---

**作者**：Shuttle AI
**來源**：https://clawhub.com/skills/shuttle-qc-ai-chatbot
