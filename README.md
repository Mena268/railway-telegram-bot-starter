# Railway Telegram Webhook Bot

A minimal Flask app that runs 24/7 on Railway. It receives POST webhooks at `/signal` and forwards them to a Telegram chat.

## Quick Start (GitHub → Railway)

1. Create a new **GitHub repo**, add these files: `app.py`, `requirements.txt`, `Procfile`.
2. On **Railway**, create a new project → *Deploy from GitHub* → select your repo.
3. In Railway → *Variables*, set:
   - `TELEGRAM_BOT_TOKEN` = `123456:ABC...`
   - `TELEGRAM_CHAT_ID` = your chat or group id
   - `WEBHOOK_SECRET` = any strong string (optional but recommended)
4. Deploy. Railway will give you a URL like: `https://your-app.up.railway.app`

### Endpoints
- `GET /` → JSON status
- `GET /health` → healthcheck
- `GET /test?msg=Hello` → manually send a Telegram message
- `POST /signal` → main webhook

### Testing via cURL
```
curl -X POST "https://your-app.up.railway.app/signal" \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR_SECRET" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "BUY",
    "price": 60123.45,
    "timeframe": "15m",
    "note": "Test order"
  }'
```

If `WEBHOOK_SECRET` is not set, the endpoint will accept requests without the header.

### Telegram Notes
- Use `@BotFather` to create a bot and get `TELEGRAM_BOT_TOKEN`.
- Use `@userinfobot` or a quick test message to retrieve your `TELEGRAM_CHAT_ID`.
- For groups, add the bot to the group and send any message to create the chat ID.

### Why `app.py` (not `bot.py`)?
Railway detects a Python web app and the `Procfile` starts `gunicorn app:app`.
This means: in `app.py` there must be a Flask **variable named `app`**. If you name the file or the app object differently, update the Procfile accordingly.
