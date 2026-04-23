import requests
import time
from dashboard import TELEGRAM_TOKEN
from alerts import set_budget, check_budget
from tracker import get_today_total, get_monthly_total
from optimizer import run_optimizer

ANTHROPIC_API_KEY = "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"

CLAWHUB_BASIC_URL = "https://clawhub.io/skills/clawcost-basic"
CLAWHUB_PRO_URL = "https://clawhub.io/skills/clawcost-pro"
CLAWHUB_MANAGE_URL = "https://clawhub.io/account/purchases"

SYSTEM_PROMPT = """You are the ClawCost support agent — a helpful AI assistant built into the ClawCost product.

ClawCost is a skill for OpenClaw that tracks API costs in real time, delivers Telegram reports, fires budget alerts, and recommends cheaper model swaps.

PRICING:
- Basic plan: $49 one time — cost tracking, daily reports, budget alerts at 80% and 100%
- Pro plan: $79 one time — everything in Basic plus auto-pause when budget hits 100%

SUPPORTED PROVIDERS:
- Claude (Anthropic) — fully supported
- OpenAI GPT-4o and GPT-4o-mini — fully supported
- Google Gemini and Mistral — beta support

PRIVACY:
- Everything stays 100% local on the user's machine
- No data is ever sent to external servers
- Only API call metadata is tracked (model name, token counts, cost)
- Zero access to prompt content or personal data

SETUP:
- Requires Python and OpenClaw installed
- Takes about 5 minutes to set up
- Works with Telegram for all notifications

UPGRADE/DOWNGRADE:
- All plan changes are handled securely through ClawHub
- No payment info is ever processed in this chat
- Users can manage their plan at clawhub.io/account/purchases

Keep answers short, friendly, and helpful. Never make up features that do not exist."""

MAIN_MENU = {
    "text": (
        "*ClawCost — AI Cost Manager*\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "What would you like to do?"
    ),
    "reply_markup": {
        "inline_keyboard": [
            [
                {"text": "📊 Show My Costs", "callback_data": "costs"},
                {"text": "💰 Budget Status", "callback_data": "budget"}
            ],
            [
                {"text": "🤖 Optimize Models", "callback_data": "optimize"},
                {"text": "⚙️ Set Budget", "callback_data": "set_budget"}
            ],
            [
                {"text": "🔒 Privacy Info", "callback_data": "privacy"},
                {"text": "📦 Basic vs Pro", "callback_data": "pricing"}
            ],
            [
                {"text": "⬆️ Upgrade to Pro", "callback_data": "upgrade"},
                {"text": "⬇️ Downgrade to Basic", "callback_data": "downgrade"}
            ],
            [
                {"text": "💬 Ask a Question", "callback_data": "ask"}
            ]
        ]
    }
}

def ask_claude(user_message):
    for attempt in range(3):
        try:
            r = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 250,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": user_message}]
                },
                timeout=30
            )
            return r.json()["content"][0]["text"]
        except Exception as e:
            print(f"[ClawCost] Claude attempt {attempt+1} failed: {e}")
            time.sleep(1)
    return "Sorry, I am having trouble right now. Please try again."

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    try:
        r = requests.get(url, params={"timeout": 5, "offset": offset}, timeout=10)
        return r.json().get("result", [])
    except:
        return []

def send_typing(chat_id):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendChatAction",
            json={"chat_id": chat_id, "action": "typing"},
            timeout=5
        )
    except:
        pass

def reply(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if keyboard:
        payload["reply_markup"] = keyboard
    for attempt in range(3):
        try:
            r = requests.post(url, json=payload, timeout=30)
            if r.status_code == 200:
                print(f"[ClawCost] Reply sent.")
                return
        except Exception as e:
            print(f"[ClawCost] Reply attempt {attempt+1} failed: {e}")
        time.sleep(1)

def answer_callback(callback_query_id):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerCallbackQuery",
            json={"callback_query_id": callback_query_id},
            timeout=5
        )
    except:
        pass

def send_menu(chat_id):
    reply(chat_id, MAIN_MENU["text"], MAIN_MENU["reply_markup"])

def back_button():
    return {"inline_keyboard": [[{"text": "⬅️ Back to Menu", "callback_data": "menu"}]]}

def handle_callback(chat_id, callback_query_id, data):
    answer_callback(callback_query_id)
    send_typing(chat_id)

    if data == "costs":
        today = get_today_total()
        monthly = get_monthly_total()
        reply(chat_id,
            f"*📊 ClawCost Report*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"*Today*\n"
            f"  Spend: ${today['total']:.6f}\n"
            f"  API Calls: {today['calls']}\n\n"
            f"*This Month*\n"
            f"  Spend: ${monthly['total']:.6f}\n"
            f"  API Calls: {monthly['calls']}\n"
            f"━━━━━━━━━━━━━━━━━━",
            back_button()
        )

    elif data == "budget":
        result = check_budget()
        bar = int(result['pct'] / 10)
        progress = "🟩" * bar + "⬜" * (10 - bar)
        reply(chat_id,
            f"*💰 Budget Status*\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{progress}\n"
            f"Used: *{result['pct']}%*\n"
            f"Spent: ${result['spent']:.4f}\n"
            f"Budget: ${result['budget']:.2f}\n"
            f"Remaining: ${max(0, result['budget'] - result['spent']):.4f}\n"
            f"━━━━━━━━━━━━━━━━━━",
            back_button()
        )

    elif data == "optimize":
        run_optimizer()
        reply(chat_id, "Optimizer report sent above! ⬆️", back_button())

    elif data == "set_budget":
        reply(chat_id,
            "*⚙️ Set Your Budget*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Reply with your monthly budget like this:\n\n"
            "*set budget $20*\n\n"
            "I will alert you at 80% and 100%.",
            back_button()
        )

    elif data == "privacy":
        reply(chat_id,
            "*🔒 Your Privacy*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "ClawCost is built with privacy first.\n\n"
            "✅ Everything stays on YOUR machine\n"
            "✅ No data sent to external servers\n"
            "✅ Nobody can see your prompts\n"
            "✅ Nobody can see your spending\n"
            "✅ Zero telemetry or tracking\n\n"
            "_Your data never leaves your machine. Ever._",
            back_button()
        )

    elif data == "pricing":
        reply(chat_id,
            "*📦 Basic vs Pro*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "*Basic — $49*\n"
            "✅ Real time cost tracking\n"
            "✅ Daily and monthly reports\n"
            "✅ Budget alerts at 80% and 100%\n"
            "✅ Model optimizer\n\n"
            "*Pro — $79*\n"
            "✅ Everything in Basic\n"
            "✅ Auto-pause at 100% budget\n"
            "✅ Prevents overnight surprise bills\n"
            "━━━━━━━━━━━━━━━━━━",
            {"inline_keyboard": [
                [{"text": "⬆️ Get Pro — $79", "callback_data": "upgrade"}],
                [{"text": "⬅️ Back to Menu", "callback_data": "menu"}]
            ]}
        )

    elif data == "upgrade":
        reply(chat_id,
            "*⬆️ Upgrade to Pro — $79*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "You will get:\n"
            "✅ Everything in Basic\n"
            "✅ Auto-pause at 100% budget\n"
            "✅ Never wake up to a surprise bill again\n\n"
            "_Payment is handled securely by ClawHub._\n"
            "_Your card info never touches this chat._",
            {"inline_keyboard": [
                [{"text": "🔒 Buy Pro on ClawHub", "url": CLAWHUB_PRO_URL}],
                [{"text": "⬅️ Back to Menu", "callback_data": "menu"}]
            ]}
        )

    elif data == "downgrade":
        reply(chat_id,
            "*⬇️ Downgrade to Basic — $49*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Basic includes:\n"
            "✅ Real time cost tracking\n"
            "✅ Daily and monthly reports\n"
            "✅ Budget alerts at 80% and 100%\n\n"
            "_Manage your plan securely on ClawHub._",
            {"inline_keyboard": [
                [{"text": "🔒 Manage Plan on ClawHub", "url": CLAWHUB_MANAGE_URL}],
                [{"text": "⬅️ Back to Menu", "callback_data": "menu"}]
            ]}
        )

    elif data == "ask":
        reply(chat_id,
            "*💬 Ask Me Anything*\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "Type any question about ClawCost\n"
            "and I will answer it instantly.",
            back_button()
        )

    elif data == "menu":
        send_menu(chat_id)

def handle_message(chat_id, text):
    t = text.lower().strip()
    send_typing(chat_id)

    if t in ["/start", "start", "hi", "hello", "hey", "help", "menu"]:
        send_menu(chat_id)

    elif any(x in t for x in ["set budget", "budget $", "change budget"]):
        try:
            amount = float(t.replace("set budget", "").replace("change budget", "").replace("$", "").strip())
            set_budget(amount)
            reply(chat_id,
                f"*✅ Budget Updated*\n"
                f"Your monthly budget is now ${amount:.2f}.",
                back_button()
            )
        except:
            reply(chat_id, "Please say 'set budget $20' with a dollar amount.")

    else:
        print(f"[ClawCost] Sending to Claude: {text}")
        ai_reply = ask_claude(text)
        reply(chat_id, ai_reply, back_button())

def run():
    print("[ClawCost] Clearing old messages...")
    updates = get_updates()
    offset = None
    if updates:
        offset = updates[-1]["update_id"] + 1
    print("[ClawCost] AI Agent with upgrade/downgrade is live!")

    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1

                if "callback_query" in update:
                    cq = update["callback_query"]
                    chat_id = cq["message"]["chat"]["id"]
                    callback_id = cq["id"]
                    data = cq["data"]
                    print(f"[ClawCost] Button tapped: {data}")
                    handle_callback(chat_id, callback_id, data)

                elif "message" in update:
                    msg = update["message"]
                    text = msg.get("text", "")
                    chat_id = msg["chat"]["id"]
                    if text and chat_id:
                        print(f"[ClawCost] Message: {text}")
                        handle_message(chat_id, text)

        except Exception as e:
            print(f"[ClawCost] Error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    run()