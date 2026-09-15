# Telegram API Testing & Debugging

This reference documents common patterns for verifying and interacting with the Telegram Bot API via CLI/Terminal.

## Connectivity Verification
Use `curl` to verify the endpoint is reachable and the Bot Token is valid.

```bash
# Replace <BOT_TOKEN> with your actual token
# Success result: HTTP 200, JSON body with "ok": true
curl -s -o /dev/null -w "%{http_code}" https://api.telegram.org/bot<BOT_TOKEN>/getMe
```

## Common HTTP Responses
- **200 OK**: Bot Token is correct and connection is established.
- **401 Unauthorized**: Bot Token is invalid (check your .env/env file).
- **404 Not Found**: Bot Token path structure is wrong (check `bot<TOKEN>` path syntax).
- **429 Too Many Requests**: Rate limited. Wait and retry.

## Environment Variables
Ensure these are present in your `~/.codex/.env` or equivalent project environment file:
- `TELEGRAM_BOT_TOKEN`: The API key provided by @BotFather.
- `TELEGRAM_CHAT_ID`: Your unique numeric chat ID (use a bot like @userinfobot to retrieve this).

## Integration Pattern
When setting up a new service, prioritize a silent check (as above) before attempting message transmission to ensure the credential/network layer is solid.
