#!/usr/bin/env bash
# Script to send a message in Claude using Kimi WebBridge with fallback strategies
# Intended to be used as a support file for the browser-automation skill.

source ~/.codex/.env

WEBSOCKET="http://127.0.0.1:10086/command"
SESSION="claude-noon-task"
URL="https://claude.ai/chat/3de5ab24-f384-447c-bcc7-7006f989ea97"

webridge() {
    local action="$1"
    local args="$2"
    if [ -z "$args" ]; then
        args="{}"
    fi
    curl -s -X POST "$WEBSOCKET" -H "Content-Type: application/json" \
        -d "{\"action\":\"$action\",\"args\":$args,\"session\":\"$SESSION\"}"
}

# Navigate to the URL
echo "Navigating to $URL"
NAV_RESP=$(webridge 'navigate' "{\"url\":\"$URL\"}")
if ! echo "$NAV_RESP" | grep -q '"ok":true'; then
    echo "Navigation failed: $NAV_RESP"
    exit 1
fi
# Wait for page to load
sleep 3

# Try to click the send button by aria-label
echo "Attempting to click send button via aria-label..."
CLICK1=$(webridge 'click' '{"selector":"button[aria-label=\"Send message\"]"}')
if echo "$CLICK1" | grep -q '"ok":true'; then
    echo "Send button clicked via aria-label"
    sleep 3
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID&text=✅ Claude message sent via Kimi WebBridge (aria-label) at $(date)"
    fi
    exit 0
fi

# Try to click by evaluating JavaScript to find the button by text
echo "Attempting to click via JavaScript evaluation..."
CLICK2=$(webridge 'evaluate' '{"expression":"Array.from(document.querySelectorAll(\"button\")).find(b => b.textContent.trim() === \"Send\")?.click();"}')
if echo "$CLICK2" | grep -q '"ok":true'; then
    echo "Send button clicked via evaluation"
    sleep 3
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID&text=✅ Claude message sent via Kimi WebBridge (evaluation) at $(date)"
    fi
    exit 0
fi

# Try to send Enter to the input box
echo "Attempting to send Enter to input box..."
KEYS=$(webridge 'send_keys' '{"selector":"div[role=\"textbox\"], div[contenteditable=\"true\"]","text":"\\n"}')
if echo "$KEYS" | grep -q '"ok":true'; then
    echo "Enter key sent to input box"
    sleep 3
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID&text=✅ Claude message sent via Kimi WebBridge (send_keys) at $(date)"
    fi
    exit 0
fi

# Try to type a message and then send Enter
echo "Attempting to type a message and then send..."
TYPE=$(webridge 'send_keys' '{"selector":"div[role=\"textbox\"], div[contenteditable=\"true\"]","text":"Test message from automation\\n"}')
if echo "$TYPE" | grep -q '"ok":true'; then
    echo "Message typed and sent"
    sleep 3
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
            -d "chat_id=$TELEGRAM_CHAT_ID&text=✅ Claude message sent via Kimi WebBridge (type and send) at $(date)"
    fi
    exit 0
fi

echo "All attempts failed"
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d "chat_id=$TELEGRAM_CHAT_ID&text=❌ Failed to send message in Claude after multiple attempts at $(date)"
fi
exit 1