# app.py
# Flask webhook -> Telegram forwarder for 24/7 hosting on Railway
from flask import Flask, request, jsonify
import os, json, requests, hmac, hashlib, time

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # optional but recommended


def send_telegram(text: str, parse_mode: str | None = None) -> dict:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return {"ok": False, "error": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"}
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def verify_secret(req) -> bool:
    """Accept either header X-Webhook-Secret or JSON field 'secret'."""
    if not WEBHOOK_SECRET:
        return True  # no secret set; allow all (not recommended for production)
    # Header check
    header_secret = req.headers.get("X-Webhook-Secret")
    if header_secret and hmac.compare_digest(header_secret, WEBHOOK_SECRET):
        return True
    # JSON/body check
    try:
        data = req.get_json(force=False, silent=True) or {}
        body_secret = data.get("secret")
        if body_secret and hmac.compare_digest(str(body_secret), WEBHOOK_SECRET):
            return True
    except Exception:
        pass
    return False


@app.get("/")
def root():
    return jsonify({"ok": True, "message": "Railway Telegram Bot is running", "time": int(time.time())})


@app.get("/health")
def health():
    # Simple health endpoint for Railway
    return "OK", 200


@app.get("/test")
def test():
    """Send a quick manual test message: /test?msg=Hello"""
    msg = request.args.get("msg", "Test: Bot is live ✅")
    res = send_telegram(msg)
    code = 200 if res.get("ok") else 500
    return jsonify(res), code


@app.post("/signal")
def signal():
    """Main webhook endpoint. Accepts JSON from any source (TV, GitHub, custom)."""
    if not verify_secret(request):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    data = request.get_json(force=False, silent=True) or {}
    # Common fields you might send from strategies
    symbol = str(data.get("symbol", "")).upper()
    side = str(data.get("side", data.get("action", ""))).upper()  # BUY/SELL or LONG/SHORT
    price = data.get("price")
    timeframe = data.get("timeframe", data.get("tf", ""))
    note = data.get("note", "")
    raw = data if data else {}

    lines = []
    if symbol or side or price:
        lines.append("📣 *Signal Received*")
        if symbol:
            lines.append(f"• *Symbol:* `{symbol}`")
        if side:
            lines.append(f"• *Side:* `{side}`")
        if price is not None:
            lines.append(f"• *Price:* `{price}`")
        if timeframe:
            lines.append(f"• *TF:* `{timeframe}`")
        if note:
            lines.append(f"• *Note:* {note}")
    else:
        lines.append("📣 *Signal (Raw Payload)*")
    lines.append("—")
    pretty = json.dumps(raw, ensure_ascii=False, indent=2)
    lines.append(f"```json\n{pretty}\n```")

    text = "\n".join(lines)
    res = send_telegram(text, parse_mode="Markdown")
    code = 200 if res.get("ok") else 500
    return jsonify(res), code


if __name__ == "__main__":
    # Local run: python app.py
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
