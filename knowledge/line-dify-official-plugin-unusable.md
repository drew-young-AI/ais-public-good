---
id: line-dify-official-plugin-unusable
type: fact
title: Dify 官方 LINE 外掛架構上無法滿足 2 秒上限
description: "kevintsai/linebot 在 Dify Cloud 同步等 LLM，超過 LINE 2 秒 2xx 規格；改自建橋接。Claude 有這條、Codex 沒有。"
tags: [line, dify, webhook, integration]
source:
  - path: ~/.claude/projects/-Users-drew/memory/line_dify_bridge.md
    digest: sha256:3cc624ec9f8b38cd254f24f72d2a74e709fe1d79fa8e0b0112aaa87cba2352f3
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
---

# Dify 官方 LINE 外掛不可用

- LINE 要求 bot server 在 2 秒內回 2xx。Dify Cloud 官方 LINE 外掛（kevintsai/linebot）在 webhook 請求內同步等待 LLM，實測整段 4–7 秒，架構上無法達標。不要再修外掛。
- Dify 文件寫明 endpoint 不是 long-running service；回應後不保證存活。
- 取代方案在 `~/Project/line-dify-bridge/`：Cloudflare Workers（`ctx.waitUntil()`）與 FastAPI（`BackgroundTasks`）行為一致。需要資料留在內網的場景用 FastAPI 落地。
- 既有 conversation 鎖住建立當下的 app 設定快照；改提示詞或知識庫對舊對話無效。reply token 一次性且時效短，非同步路徑必須有 push 後備。
- 不把 channel secret、token 或病人資料寫進共用層。
