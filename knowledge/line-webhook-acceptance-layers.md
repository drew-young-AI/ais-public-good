---
id: line-webhook-acceptance-layers
type: reference
title: LINE webhook 驗收必須分層，健康檢查不是對話
description: "Hermes LINE 與任何 LINE webhook：本地 health、公開 endpoint、官方測試、真實來回是四層。Quick Tunnel 不是正式穩定宣稱。"
tags: [line, webhook, hermes, health-check, integration]
source:
  - path: ~/.codex/memories/MEMORY.md
    locator: "Task Group: macOS Hermes LINE gateway verification"
    digest: sha256:ee3eccc83ea1d079043d1f6905a67283a35e7a01104708e4d967eb35307e75db
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
---

# LINE webhook 驗收分層

與 `launchd-service-false-success` 互補：那條講 process 假活著；這條講「連上了也不等於能對話」。

- 本機 Hermes LINE 安裝：LaunchAgent `ai.hermes.gateway`，本機 webhook 路徑 `/line/webhook`，簽名 HMAC-SHA256。port 與憑證是 live state，用前要重查，不把 token 寫進共用層。
- 驗收層必須分開，不可用上一層冒充下一層：
  1. 本地 health / listener
  2. 公開 URL 的 LINE endpoint GET（`active=true` 且 URL 符合預期）
  3. LINE 官方 webhook 測試
  4. 真實入站訊息與出站回覆
- `LINE: webhook listening` 只證明適配器曾經啟動。Quick Tunnel 是暫時開發基礎設施，不是正式穩定宣稱。
- AIS 中立能力：`capabilities/scripts/line-webhook-watchdog`。consumer 自備路徑、憑證、tunnel、排程；不要把 Hermes 專屬值寫進 AIS。
