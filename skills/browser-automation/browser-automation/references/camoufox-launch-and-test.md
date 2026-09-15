# Camoufox Launch and Test Notes

## Launch Camoufox with REST API
```bash
# Assuming you have cloned the camoufox-browser repo
cd ~/camofox-browser
npm install   # first time only
npm start     # starts server on http://localhost:9377
```
The server responds with JSON indicating status:
```json
{"ok":true,"enabled":true,"running":false,"engine":"camoufox","browserConnected":false,"browserRunning":false}
```
Note: `browserRunning:false` means the browser itself hasn't been launched yet; the REST API is ready to create tabs.

## Create a tab and navigate via Camoufox REST API (manual test)
```bash
TAB_ID=$(curl -s -X POST http://localhost:9377/tabs \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","sessionKey":"test"}' | jq -r .tabId)

curl -s -X POST http://localhost:9377/tabs/$TAB_ID/navigate \
  -H "Content-Type: application/json" \
  -d '{"userId":"test","url":"https://example.com"}'

curl -s "http://localhost:9377/tabs/$TAB_ID/snapshot?userId=test"
```
This demonstrates that Camoufox can be controlled via its REST API, but Hermes browser tools currently rely on CDP or Playwright engine, not this API.

## Verify Hermes config for Camoufox (as of this session)
Set the following in Hermes config (or via CLI):
```bash
hermes config set browser.engine camoufox
hermes config set browser.camofox.user_id test
hermes config set browser.camofox.session_key test
hermes config set browser.camofox.managed_persistence true
```
Note: Setting `browser.engine = camoufox` instructs Hermes to attempt to use the Camoufox engine; however, during testing the `browser_navigate` command timed out, suggesting the engine integration may not be functional or requires additional setup not yet documented.

## Chrome + Kimi WebBridge (working method)
1. Start Chrome with remote debugging and load the Kimi extension:
```bash
CHROME_USER_DATA_DIR=/tmp/chrome_kimi_bridge
mkdir -p "$CHROME_USER_DATA_DIR"
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --load-extension="~/Library/Application Support/Google/Chrome/Default/Extensions/fldmhceldgbpfpkbgopacenieobmligc/1.9.13_0" \
  --user-data-dir="$CHROME_USER_DATA_DIR" \
  about:blank &
```
2. Verify CDP endpoint:
```bash
curl -s http://localhost:9222/json/version
```
Should return JSON with `webSocketDebuggerUrl`.
3. Configure Hermes:
```bash
hermes config set browser.cdp_url http://localhost:9222
```
4. Use Hermes browser tools as normal.

## Troubleshooting tips
- If `hermes -z "browser_navigate https://example.com && browser_snapshot"` times out:
  - For Camoufox: ensure the server is reachable (`curl http://localhost:9377/`) and that the `browser.engine` is set correctly.
  - For Chrome: verify the CDP endpoint responds (`curl http://localhost:9222/json/version`).
- The Kimi WebBridge extension's local server on port 10086 does **not** provide a CDP API; do not point `browser.cdp_url` to that port.