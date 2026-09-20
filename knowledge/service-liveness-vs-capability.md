---
id: service-liveness-vs-capability
type: policy
title: 服務活著不等於那件事做得到——健康探測與能力探測必須分開
description: "MLX 端點連續半個月回 200、selftest rc=0，但每次真實推理都 404（設定的模型本機不存在）。健康探測只證明服務在；要證明能力，必須發一次最小的真實請求。"
tags: [false-success, health-check, verification, local-llm, mlx, registry]
source:
  - path: ${AIS_ROOT}/capabilities/scripts/mlx
    locator: "symbol:main"
    digest: sha256:aca6f7bfaaffa14c61b8bb8a2b5e73bf77af03ccbd92a3d2add15eda28fb59f2
status: stable
inject: auto
timestamp: '2026-09-19T22:00:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

# 健康探測 ≠ 能力探測

## 實證（2026-09-19）

本機 MLX 的登記是 `verify: mlx selftest`，而那個 selftest 只打 `/v1/models`，
回得出清單就 rc=0。**它半個月來每次都綠**；同一時間每一次真實推理都回 404，
因為腳本預設請求的模型**本機根本不存在**。服務活著、埠有人聽、清單回得出來——
但清單裡那個不是我們要的那個。

診斷用詞也值得記：一開始（含契約紀錄）都寫成「兩邊設定不一致」，查下去才發現是
**指向一個不存在的東西**。「不一致」聽起來可以權衡，「不存在」則是壞的——
**描述用詞會決定它被排到什麼優先序**。

## 規則

| 層 | 問什麼 | 做法 | 證明不了 |
|---|---|---|---|
| 健康探測 | 服務在嗎 | `/v1/models`、`/healthz`、行程在、埠有人聽 | 你要的那個可不可用 |
| 能力探測 | 這件事做得到嗎 | 發一次**最小的真實請求**（`max_tokens=1`、`tools/list`、no-op 寫入） | — |

登記表寫法：`verify` 放健康探測，`reachable` 放能力探測。判不出能力的，
狀態要是 **NOT-READY 而不是 ACTIVE**。

「真的做一次很慢」只對了一半：慢的是**有用的**推理，不是**最小的**推理——
`max_tokens=1` 約 1–3 秒就分得開 404 與 200。

## 同形狀的前例

- **MCP**：只驗 `initialize` 會放行「握手正確但工具是空的」stub（disk-report 事故）
- **需授權的 CLI**：`colab --help` 印得出說明就判 ACTIVE，而它完全未授權
- **`wrangler whoami`**：未授權時**仍 exit 0**，只在輸出裡寫 not authenticated

共同形狀：**探測的東西比宣稱的東西小一號**，而兩者用同一個綠燈表示。

## 能力探測本身也會假成功：肯定句是否定句的子字串

替三支要登入的 CLI 加「驗真的登入了」時，斷言寫成 `expect_present: "Logged in"`。
未登入的輸出是 `Not logged in`——**子字串比對命中**，登出的 CLI 被判就緒。
差一點上線，救回來的是負控制，不是複查程式碼。

斷言要挑**只在成功時出現**的字串（`Credentials:`、`Email:`），或用否定斷言兜底。
危險字眼：logged in、authenticated、connected、ready、available、enabled、active。
已在 `cap` 的 registry lint 加規則（正負控制各一）擋下次。

## 新加的探測也要走既有的閘

加上 `--servable` 後 `bypass-scan` 當場紅：那次請求（即使只有一個 token）繞過了
「本機推理一律序列」的鎖。**「成本很小」不是豁免理由**。修法是走 `acquire_lock()`
並在 `finally` 釋放——少了 `finally`，失敗一次就把鎖留著卡住後續全部推理。
