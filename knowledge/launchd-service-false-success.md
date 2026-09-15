---
id: launchd-service-false-success
type: reference
title: launchd 服務「回報成功但實際已死」的假成功樣態
description: "hermes gateway start 回 success、狀態檔寫 running，但 launchd 延遲 reload 讓 process 已死；本機服務的健康判定不可只信服務自報。"
tags: [launchd, macos, false-success, health-check, hermes]
source:
  - agent: codex
    path: ~/.codex/memories/MEMORY.md
    locator: "Task Group: macOS Hermes LINE gateway verification"
    digest: sha256:ee3eccc83ea1d079043d1f6905a67283a35e7a01104708e4d967eb35307e75db
    note: "由 codex 管線自 session rollout 抽取"
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
---

# launchd 服務的假成功

**出處**：`~/.codex/memories/MEMORY.md`（codex 自 session rollout 抽取，Task Group:
macOS Hermes LINE gateway）。蒸餾進共用層的理由：claude 側完全沒有這條，
而它是本專案定義的假成功原型，且適用於本機所有 launchd 服務，不限 hermes。

## 樣態

`hermes gateway start` 回報成功、`gateway_state.json` 寫著 `running`——
但 launchd 的**延遲 reload** 可能讓 process 實際已死，服務完全不通。
狀態檔與真實狀態脫節，而所有「檢查」都只讀狀態檔。

## 為什麼騙得過檢查

服務自報的狀態是**它自己寫的**，不是觀測到的。
`start` 成功只證明「指令被接受」，不證明「process 活著並在服務」。
這與 rc=0 被當成完成、`kubectl apply` 成功被當成規則生效，是同一個結構。

## 判定方式（不可只做其中一項）

1. `launchctl print gui/$(id -u)/<label>` —— 問 launchd 而不是問服務
2. 實際 PID 是否存活
3. port / socket 探測（該服務的實際監聽埠）
4. log 檔的**時間戳是否新鮮**（舊 log 等於沒有證據）

## 兩個推論（適用於任何本機服務）

- **本地 HTTP 200 只證明本地在監聽**，不證明對外可達、簽章處理正確、
  agent 真的執行、或回覆真的送出去。本地與端對端必須是**兩道分開的驗收閘**。
- 沙箱環境下 `launchctl kickstart` 會 `Operation not permitted`；
  需要提權的重啟路徑，不要當成一般失敗重試。

## 與 AIS 的關係

`adapters/doctor.py` 的服務探測、以及任何未來的 K8s readiness 判定，
都適用同一條原則：**判定必須來自觀測，不能來自被判定者的自報。**
