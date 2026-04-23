import json
import os
import time
import urllib.request
import urllib.error


TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_BASE = os.getenv("TELEGRAM_API_BASE", "https://api.telegram.org")
MODERATION_CORE_ENDPOINT = os.getenv("MODERATION_CORE_ENDPOINT", "")
MODERATION_CORE_TOKEN = os.getenv("MODERATION_CORE_TOKEN", "")
WARN_MESSAGE_TEMPLATE = os.getenv("TELEGRAM_WARN_MESSAGE_TEMPLATE", "请勿发布广告、引流或联系方式内容。")
MUTE_SECONDS = int(os.getenv("TELEGRAM_MUTE_SECONDS", "600"))
ADMIN_REVIEW_CHAT_ID = int(os.getenv("TELEGRAM_ADMIN_REVIEW_CHAT_ID", "0"))


def http_json(method, url, payload, headers=None, timeout=10):
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=body, method=method)
    final_headers = headers or {}
    for key, value in final_headers.items():
        request.add_header(key, value)
    request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def verify_secret(provided):
    if not TELEGRAM_WEBHOOK_SECRET:
        return True
    return provided == TELEGRAM_WEBHOOK_SECRET


def pick_message(update):
    for field in ["message", "edited_message", "channel_post", "edited_channel_post"]:
        if isinstance(update.get(field), dict):
            return field, update[field]
    return None, None


def normalize(update):
    update_type, message = pick_message(update)
    if not message:
        return None
    chat = message.get("chat") or {}
    sender = message.get("from") or {}
    text = message.get("text", "")
    caption = message.get("caption", "")
    return {
        "platform": "telegram",
        "update_type": update_type,
        "chat_id": chat.get("id", 0),
        "message_id": message.get("message_id", 0),
        "user_id": sender.get("id", 0),
        "username": sender.get("username", ""),
        "content": (text + "\n" + caption).strip(),
        "raw_has_photo": bool(message.get("photo")),
        "raw_has_video": isinstance(message.get("video"), dict),
    }


def moderate(payload):
    headers = {}
    if MODERATION_CORE_TOKEN:
        headers["Authorization"] = "Bearer " + MODERATION_CORE_TOKEN
    return http_json("POST", MODERATION_CORE_ENDPOINT, {
        "platform": "telegram",
        "id": payload["message_id"],
        "title": "",
        "content": payload["content"],
        "imgs": [],
        "videos": [],
        "other": {
            "chat_id": payload["chat_id"],
            "user_id": payload["user_id"],
            "username": payload["username"],
            "raw_has_photo": payload["raw_has_photo"],
            "raw_has_video": payload["raw_has_video"],
        }
    }, headers=headers, timeout=15)


def telegram_call(method, payload):
    url = TELEGRAM_API_BASE.rstrip("/") + "/bot" + TELEGRAM_BOT_TOKEN + "/" + method
    return http_json("POST", url, payload, timeout=10)


def send_warning(chat_id, message_id):
    return telegram_call("sendMessage", {
        "chat_id": chat_id,
        "text": WARN_MESSAGE_TEMPLATE,
        "reply_to_message_id": message_id,
    })


def delete_message(chat_id, message_id):
    return telegram_call("deleteMessage", {
        "chat_id": chat_id,
        "message_id": message_id,
    })


def mute_user(chat_id, user_id):
    return telegram_call("restrictChatMember", {
        "chat_id": chat_id,
        "user_id": user_id,
        "permissions": {
            "can_send_messages": False,
            "can_send_audios": False,
            "can_send_documents": False,
            "can_send_photos": False,
            "can_send_videos": False,
            "can_send_video_notes": False,
            "can_send_voice_notes": False,
            "can_send_polls": False,
            "can_send_other_messages": False,
            "can_add_web_page_previews": False,
            "can_change_info": False,
            "can_invite_users": False,
            "can_pin_messages": False,
            "can_manage_topics": False,
        },
        "until_date": int(time.time()) + MUTE_SECONDS,
    })


def ban_user(chat_id, user_id):
    return telegram_call("banChatMember", {
        "chat_id": chat_id,
        "user_id": user_id,
    })


def notify_review(payload, result, action):
    if ADMIN_REVIEW_CHAT_ID <= 0:
        return None
    text = "[review]\nchat_id: {chat_id}\nmessage_id: {message_id}\nuser_id: {user_id}\nusername: {username}\naction: {action}\nreason: {reason}".format(
        chat_id=payload["chat_id"],
        message_id=payload["message_id"],
        user_id=payload["user_id"],
        username=payload["username"],
        action=action,
        reason=result.get("reason", ""),
    )
    return telegram_call("sendMessage", {"chat_id": ADMIN_REVIEW_CHAT_ID, "text": text})


def handle_update(update, provided_secret):
    if not verify_secret(provided_secret):
        return {"ok": False, "error": "invalid webhook secret"}, 403

    payload = normalize(update)
    if not payload:
        return {"ok": True, "skipped": "unsupported update"}, 200

    result = moderate(payload)
    status = result.get("audit_status", "review")
    risk = result.get("risk_level", "medium")

    if status == "pass":
        return {"ok": True, "action": "allow"}, 200

    if status == "reject":
        delete_message(payload["chat_id"], payload["message_id"])
        send_warning(payload["chat_id"], payload["message_id"])
        if risk == "high":
            mute_user(payload["chat_id"], payload["user_id"])
        return {"ok": True, "action": "delete_and_warn"}, 200

    notify_review(payload, result, "review")
    return {"ok": True, "action": "review"}, 200


if __name__ == "__main__":
    sample_update = {
        "message": {
            "message_id": 1,
            "chat": {"id": -100123, "type": "supergroup"},
            "from": {"id": 777, "username": "spam_user"},
            "text": "加V了解一下",
        }
    }
    response, status_code = handle_update(sample_update, TELEGRAM_WEBHOOK_SECRET)
    print(status_code)
    print(json.dumps(response, ensure_ascii=False))
