# Shuttle QC AI Chatbot v2.1.0

自動化操作 Shuttle QC AI Chatbot，支援單次查詢與批次執行。

## 安裝

```bash
clawhub install shuttle-qc-ai-chatbot
```

## 使用

### 單次查詢
```bash
shuttle-qc-ai-chatbot query "SB860R8 spec" --output text
shuttle-qc-ai-chatbot query "DL30N vs DL40N"  # 產品比較
```

### 批次查詢
```bash
shuttle-qc-ai-chatbot batch queries.txt --output json
```

### 查詢列表檔案內容（queries.txt）
```txt
DL30N
DL40N
SB860R8
P55U
```

## 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `query` | 單次查詢文字 | - |
| `batch` | 批次查詢檔案路徑（每行一筆） | - |
| `--url` | 目標網頁 URL | `http://192.168.100.98:8888/v1` |
| `--timeout` | 等待回應超時秒數 | `30` |
| `--output` | 輸出格式：`json` 或 `text` | `json` |

## 進階用法

- **產品比較**：使用 "vs" 或 "and" 進行多型號比較，例如 `"DL30N vs DL40N"`、`"Compare SB860 and DB860"`
- **批次驗證**：適用於 QC 流程中驗證多個型號的規格一致性
- **長詢**：若 AI 回應較慢，可增加 `--timeout 60`

## 注意事項

- 確保本地服務 `192.168.100.98:8888` 已啟動且可訪問
- 第一次使用會自動啟動 Brave 瀏覽器
- 批次查詢時建議加上 `--headless`（如需）避免干擾
- 回應內容大小影響解析時間，可視需要調整 `--timeout`

詳見 [SKILL.md](SKILL.md)。