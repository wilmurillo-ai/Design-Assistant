package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "os"
    "strings"
    "time"
)

type updateEnvelope map[string]interface{}

type moderationResult struct {
    AuditStatus string `json:"audit_status"`
    RiskLevel   string `json:"risk_level"`
    Reason      string `json:"reason"`
}

func env(key, fallback string) string {
    value := os.Getenv(key)
    if value == "" {
        return fallback
    }
    return value
}

func verifySecret(provided string) bool {
    expected := env("TELEGRAM_WEBHOOK_SECRET", "")
    if expected == "" {
        return true
    }
    return provided == expected
}

func pickMessage(update updateEnvelope) (string, map[string]interface{}) {
    fields := []string{"message", "edited_message", "channel_post", "edited_channel_post"}
    for _, field := range fields {
        if value, ok := update[field].(map[string]interface{}); ok {
            return field, value
        }
    }
    return "", nil
}

func normalize(update updateEnvelope) map[string]interface{} {
    updateType, message := pickMessage(update)
    if message == nil {
        return nil
    }

    chat, _ := message["chat"].(map[string]interface{})
    sender, _ := message["from"].(map[string]interface{})
    text, _ := message["text"].(string)
    caption, _ := message["caption"].(string)

    return map[string]interface{}{
        "platform":      "telegram",
        "update_type":   updateType,
        "chat_id":       chat["id"],
        "message_id":    message["message_id"],
        "user_id":       sender["id"],
        "username":      sender["username"],
        "content":       strings.TrimSpace(text + "\n" + caption),
        "raw_has_photo": message["photo"] != nil,
        "raw_has_video": message["video"] != nil,
    }
}

func postJSON(url string, payload interface{}, token string, timeout time.Duration, out interface{}) error {
    body, err := json.Marshal(payload)
    if err != nil {
        return err
    }

    req, err := http.NewRequest("POST", url, bytes.NewReader(body))
    if err != nil {
        return err
    }
    req.Header.Set("Content-Type", "application/json")
    if token != "" {
        req.Header.Set("Authorization", "Bearer "+token)
    }

    client := &http.Client{Timeout: timeout}
    resp, err := client.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()

    if out != nil {
        return json.NewDecoder(resp.Body).Decode(out)
    }
    return nil
}

func moderate(payload map[string]interface{}) (moderationResult, error) {
    endpoint := env("MODERATION_CORE_ENDPOINT", "")
    token := env("MODERATION_CORE_TOKEN", "")
    req := map[string]interface{}{
        "platform": "telegram",
        "id":       payload["message_id"],
        "title":    "",
        "content":  payload["content"],
        "imgs":     []string{},
        "videos":   []string{},
        "other": map[string]interface{}{
            "chat_id":       payload["chat_id"],
            "user_id":       payload["user_id"],
            "username":      payload["username"],
            "raw_has_photo": payload["raw_has_photo"],
            "raw_has_video": payload["raw_has_video"],
        },
    }

    var result moderationResult
    err := postJSON(endpoint, req, token, 15*time.Second, &result)
    return result, err
}

func telegramCall(method string, payload interface{}) error {
    botToken := env("TELEGRAM_BOT_TOKEN", "")
    apiBase := strings.TrimRight(env("TELEGRAM_API_BASE", "https://api.telegram.org"), "/")
    url := apiBase + "/bot" + botToken + "/" + method
    return postJSON(url, payload, "", 10*time.Second, nil)
}

func main() {
    update := updateEnvelope{
        "message": map[string]interface{}{
            "message_id": 1,
            "chat": map[string]interface{}{"id": -100123, "type": "supergroup"},
            "from": map[string]interface{}{"id": 777, "username": "spam_user"},
            "text": "加V了解一下",
        },
    }

    if !verifySecret(env("TELEGRAM_WEBHOOK_SECRET", "")) {
        fmt.Println("invalid webhook secret")
        return
    }

    payload := normalize(update)
    if payload == nil {
        fmt.Println("unsupported update")
        return
    }

    result, err := moderate(payload)
    if err != nil {
        panic(err)
    }

    if result.AuditStatus == "reject" {
        _ = telegramCall("deleteMessage", map[string]interface{}{
            "chat_id":    payload["chat_id"],
            "message_id": payload["message_id"],
        })
        _ = telegramCall("sendMessage", map[string]interface{}{
            "chat_id":             payload["chat_id"],
            "text":                env("TELEGRAM_WARN_MESSAGE_TEMPLATE", "请勿发布广告、引流或联系方式内容。"),
            "reply_to_message_id": payload["message_id"],
        })
    }

    if result.AuditStatus == "review" {
        adminReviewChatID := env("TELEGRAM_ADMIN_REVIEW_CHAT_ID", "")
        if adminReviewChatID != "" {
            _ = telegramCall("sendMessage", map[string]interface{}{
                "chat_id": adminReviewChatID,
                "text": fmt.Sprintf("[review]\nchat_id: %v\nmessage_id: %v\nuser_id: %v\nusername: %v\nreason: %s",
                    payload["chat_id"], payload["message_id"], payload["user_id"], payload["username"], result.Reason),
            })
        }
    }

    fmt.Println("done")
}
