# Launching Chrome with Kimi WebBridge for Hermes CDP

This reference documents the exact steps used in the session to successfully start Chrome with the Kimi WebBridge extension and use Hermes browser tools via CDP.

## Prerequisites
- Kimi WebBridge extension installed in Chrome (visible at `chrome://extensions`).
- Hermes Agent installed.

## Steps

1. **Identify the extension path** (adjust if your Chrome profile differs):
   ```bash
   EXT_PATH="~/Library/Application Support/Google/Chrome/Default/Extensions/fldmhceldgbpfpkbgopacenieobmligc/1.9.13_0"
   ```

2. **Start Chrome with remote debugging and load the extension** (backgrounded, notify on complete):
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
       --remote-debugging-port=9222 \
       --load-extension="$EXT_PATH" \
       --user-data-dir=$(mktemp -d) &
   ```
   *Note:* The `&` backgrounds the process; you can also use `hermes terminal` with `background=true` and `notify_on_complete=true` for better tracking.

3. **Wait a few seconds for Chrome to initialize**, then verify the CDP endpoint:
   ```bash
   curl -s http://127.0.0.1:9222/json/version
   ```
   Expected output includes `"webSocketDebuggerUrl"` and version info.

4. **Configure Hermes to use this CDP endpoint**:
   ```bash
   hermes config set browser.cdp_url http://localhost:9222
   ```

5. **Run browser commands** (example):
   ```bash
   hermes -z "browser_navigate https://example.com && browser_snapshot"
   ```
   You should see the page title and interactive elements.

6. **When finished, clean up the Chrome process**:
   - Find the PID (e.g., via `ps aux | grep 9222`) and kill it, or use Hermes process management if you started it via terminal background.

## Troubleshooting
- If `curl` fails with "Failed to connect to host", ensure Chrome is actually listening on port 9222 (`lsof -iTCP:9222 -sTCP:LISTEN`).
- If the extension does not appear to affect pages, verify it is enabled in the Chrome instance you launched (check `chrome://extensions` → Details → Allow in incognito if needed).
- For repetitive use, consider creating a shell alias or script that wraps the launch command.

## Notes
- The Kimi WebBridge extension runs a local server on port 10086, but this port does **not** expose a standard CDP JSON API. Therefore, Hermes must connect to Chrome's remote debugging port (9222 in this example), not to 10086.
- Loading the extension into a Chrome instance started with `--remote-debugging-port` gives you both the CDP control needed by Hermes and the AI-friendly features of Kimi WebBridge.