---
id: user-work-policy
type: policy
title: 使用者跨工具工作政策
description: "跨 AI 可重用的輸出、環境與工作區慣例；不含 vendor persona、credentials 或 runtime state。"
tags: [general, user-policy, environment, macos, apple-silicon, development]
source:
  - path: ~/.claude/CLAUDE.md
    locator: "Identity Context; Machine Identity; Core Operating Principles"
    digest: sha256:38a149469b4db5a0c1a4f72b0d6afa656877a5c42eeb64f36c199fa246e31f9e
status: stable
inject: auto
timestamp: '2026-08-24T17:12:00+08:00'
---

# 使用者跨工具工作政策

- 輸出使用繁體中文；內部推理可使用英文。
- 本機是 Apple Silicon 的 MacBook Pro。優先使用 ARM-native binary 或 image，除非明確要求，不使用 x86 emulation。
- 不全域安裝套件、不修改 `/usr/local` 或系統層目錄。Python、Node 與其他工具必須使用可重現的隔離環境。
- 暫存測試與中間產物放在專案內的 `temp/`，工作完成後清除；正式 workspace 是唯一真相來源。
- 對外部工具或本機服務，以可重跑觀測驗證實際行為，不以設定存在、PID 檔或單次 HTTP 200 宣稱完成。
