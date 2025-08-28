# app.py
from flask import Flask, request
import requests, os

app = Flask(__name__)

# Yahan apna Telegram Bot Token daalna hai
TELEGRAM_BOT_TOKEN = "8430719482:AAG2jY9ssIFNlLYXGLPnxktKwc9QHV1xbTU"

# Yahan apna Telegram Chat ID daalna hai
TELEGRAM_CHAT_ID = "7695071336"

# Yahan apna secret (kisi bhi random string jese 'mysecret123') daalna hai
WEBHOOK_SECRET = "MackMehrab_2025_secret"


def send_telegram(text):
    """Message bhejne ka function"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    requests.post(url, data=payload)


@app.route("/webhook", methods=["POST"])
def webhook():
    """Webhook receive karne ka route"""
    secret = request.headers.get("X-Webhook-Secret")
    if secret != WEBHOOK_SECRET:
        return {"status": "forbidden"}, 403

    data = request.json
    message = f"📩 Webhook Received:\n{data}"
    send_telegram(message)

    return {"status": "ok"}, 200


@app.route("/")
def home():
    return "✅ Bot is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
