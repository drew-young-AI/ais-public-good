---
name: browser-automation
type: skill
description: "智能瀏覽器自動化 API 網關：整合 browser-use 與 Kimi WebBridge，提供標準化 REST/MCP 介面供任何 AI CLI 調用。"
version: 2.1.0
---

# 智能瀏覽器自動化 API 網關 (Service Layer)

本技能現已升級為「自動化 API 網關」，允許任何 AI CLI (如 claude-code, codex, opencode) 通過標準指令存取自動化能力。

## 1. 跨 CLI 調用介面 (API Interface)
所有外部 Agent 均可透過本地接口存取瀏覽器能力：

- **啟動服務**: `~/.hermes/scripts/browser_automation_gateway.py`
- **標準接口**:
  - `POST http://127.0.0.1:9999/execute`: 接收任務意圖 (JSON payload)。
  - `GET http://127.0.0.1:9999/health`: 檢測 Camoufox 與 WebBridge 狀態。

## 2. 跨 CLI 調用範例 (供其他 Agent 使用)
其他 Agent 若需調用，請發送以下請求：
```bash
curl -X POST http://127.0.0.1:9999/execute \
  -H "Content-Type: application/json" \
  -d '{"intent": "在 Claude 聊天室送出訊息", "url": "https://claude.ai/...", "action": "send"}'
```

## 3. 自我檢查協議 (Self-Test Protocol)
為確保其他 CLI 能順利接入，每次啟動前 Agent 必須執行：
1. **Health Check**: 發送 `/health` 檢查 daemon 是否存活。
2. **Context Sync**: 確認當前 CLI 可存取 `~/.codex/.env` 中的環境變數。
3. **Bridge Verification**: 確認 `Kimi WebBridge` 能接收跨進程請求。

## 故障排除與限制 (Pitfalls & Limitations)
- **非會話式網關**: 目前 `browser-automation` 網關 (port 9999) 僅支援原子化任務（scrape/e2e-test/form-fill），不支援維護持久化瀏覽器會話、分頁列表查詢或分頁切換。
- **後端狀態**: 網關若回傳 CDP 連線錯誤，表示 Camoufox 後端尚未就緒或與 CDP 介面脫節，此時應跳過分頁查詢，直接以 URL 進行單次抓取任務。
- **連線逾時**: 若 curl 請求超過 10 秒未回應，請檢查網關健康狀態 (`/health`) 或嘗試縮減抓取規模。

- **登入牆**: 對於需要使用者登入的網站（如 Claude.ai、銀行門戶），網關可能無法繞過驗證，導致任務超時或失敗。此時建議改用 `computer-use` 技能或直接提供已登入後可直接存取的 URL 進行 `scrape`。

## 使用指引
- 若用戶詢問分頁狀態，請明確告知此限制，並要求提供目標 URL 以進行 `scrape`。
- 檢查工具連線前，務必先呼叫 `/health` 檢測 Daemon 存活狀態。
