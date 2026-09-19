---
id: session-archive-storage-choice
type: policy
title: 各家 AI session 封存的儲存選型與分層
description: "攝入層用嵌入式 SQLite 不用 MongoDB：codex 自己就是 JSONL 當 SSoT ＋ SQLite 當可重建投影。十家來源實測。圖層（Kuzu/Graphiti）是之後的衍生投影，不是攝入層。"
tags: [knowledge, memory, storage, ais, session]
source:
  - path: ${AIS_ROOT}/capabilities/scripts/session-ingest
    digest: sha256:90c88567216c6e9f465607090d19f5df6dffb9f4dff3d515c43a34b41f7355ac
  - path: ${AIS_ROOT}/workspace/memory/decisions.md
    digest: sha256:d3446b7f890c6ade8b54719a5f09ae377dc76eb8ac8e4619e491a4fbcc809223
status: stable
inject: auto
timestamp: '2026-08-31T02:00:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

# session 封存的儲存選型

- **攝入層用嵌入式 SQLite（＋FTS5），不用 MongoDB。** 五個理由，前兩個最硬：
  1. **codex 自己就是這樣做的。** `~/.codex/sessions/**.jsonl` 是 append-only rollout（SSoT），`~/.codex/thread_history_1.sqlite` 是可重建的查詢投影。實測：JSONL 涵蓋 2026-05-25 起 55 個 session，SQLite 只有最近 14 個 thread——**投影是快取不是檔案庫**。
  2. **不需要 server。** Mongo 要常駐 daemon；本機是被動散熱的筆電（§5c），多一個常駐行程就多一個「忘了開 → 看起來沒資料」的假成功來源。SQLite 是一個檔案，沒有「服務沒起來」這種狀態。
  3. FTS5 內建於標準庫 sqlite3；Mongo 等價物要 Atlas Search（雲端）或外掛。
  4. 可重現：同一批來源檔 → 同一個 DB（sha256 冪等），符合 §5b。
  5. 搬機器＝複製一個檔案。

- **2026-08-31 擴張到十家，選型被強化、一個附帶結論被推翻。**
  - **JSONL 當 SSoT、SQLite 當投影，不只是 codex 的習慣。** grok（`updates.jsonl` ＋ `session_search.sqlite`）與 copilot（`events.jsonl` ＋ `session-store.db`）是同一分工。三家獨立收斂到同一解。
  - **唯二不走 JSONL 的兩家仍然選 SQLite。** quickwork 直接寫 `session_messages` 表；kiro-cli（Amazon Q 改名）把整段會話塞進 `conversations_v2` 的單一 JSON blob。十家裡沒有一家選 document server。
  - **被推翻：「qoder 與 kiro-cli 沒有逐字稿」。** 那是掃 `~/.qoder/logs` 與 `~/.kiro` 得到的；真正的路徑是 `~/.qoder/projects/` 與 `~/Library/Application Support/kiro-cli/data.sqlite3`。**結論的有效範圍取決於當時的掃描範圍**——[[knowledge-bitemporal-supersede]] 記載的同一類錯誤，同月重演。故來源表把「已查證無逐字稿」（結論）與「路徑已知但沒樣本」（待辦）分成兩個狀態，不可合併。

- **自動累積用定時不用 hooks。** 十家裡只有少數有 hook。為每家各接一種會得到十套各自可能靜默失效的路徑，而「三家有 hook」易被讀成「已自動化」。定時夠用是因為攝入 sha256 冪等（335 檔全掃 3–4 秒）。健康判定不讀自報欄位，而是比對磁碟最新 mtime 與 DB 最新 `ingested_at`——見 [[launchd-service-false-success]]。解析器的靜默丟棄見 [[parser-silent-drop]]。

- **圖層（Kuzu / Graphiti）留在路線圖上，位置是「衍生投影」不是「攝入層」。** Kuzu 是嵌入式、無 server，符合 §5c；等真的出現需要圖遍歷的查詢（沿革、推翻鏈、跨 session 的實體關聯）再從 SQLite 這個可重建的 SSoT 長出來。**先建圖再想要查什麼，會得到一個沒人查的圖。** 見 [[knowledge-bitemporal-supersede]]。

- **攝入 ≠ 知識。** 攝入層存的是「誰在何時說了什麼」的原始事實，可以無條件保存；知識 record 是「這件事為真」的宣稱，會被 `context resolve` 注入到每一家 CLI 的 prompt。讓萃取結果自動變成知識 record，等於把 hallucination 升級成基礎建設。故萃取產物一律 `status: draft` + `gate: pending-human`。

- **web 對話沒有 API。** claude.ai 與 chatgpt.com 的官方匯出都是「寄 email 給 24 小時過期的 ZIP」，只能人工觸發；自動化只涵蓋「ZIP 進 drop 目錄之後」那一半。ChatGPT 的 `conversations.json` 是**樹狀** mapping，必須從 `current_node` 往回走再反轉——直接遍歷會收進被放棄的分支且順序錯誤。

- **L1 萃取的瓶頸是 MLX 模型換載，不是連續呼叫**（2026-09-01 更正舊歸因）。詳見 [[mlx-call-discipline]]，已由 `contract-pairs` 的 `mlx-model-matches-server` 守住。
