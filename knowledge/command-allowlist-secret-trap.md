---
id: command-allowlist-secret-trap
type: reference
title: 指令 allow-list 會把密鑰寫進設定
description: "核准含密鑰的整段指令後，密鑰會留在 config、log、conversation db。agy 的權限檔路徑與複合指令行為也在此。"
tags: [agy, permissions, secrets, security]
source:
  - path: private-source   # 原始位置在私有機器上，digest 仍可由來源持有者驗證
    digest: sha256:8033ec11fa1cda915278417d1ea7adab3ab83fff61a8bf9c99cbc334187ebb9a
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

# 指令 allow-list 的密鑰陷阱

- 這不是 agy 獨有：allow-list 會永久存下整段被核准的指令。指令裡若有密鑰，密鑰會進 config，並外擴到 log 與 conversation db。核准前先看指令字串。
- agy 權限檔實際路徑是 `~/.gemini/antigravity-cli/settings.json`，不是 `~/.gemini/settings.json`。錯誤訊息只寫 settings.json，會導向錯檔。
- 複合指令（`mkdir && printf && cat`）整條一起檢查；一個 token 不在 allow-list，整條被拒。看起來「已放行的 echo 仍被拒」，成因通常是這條。
- agy 無法把權限限縮到單一 workspace：`allowNonWorkspaceAccess` 為真、trusted workspace 含整個家目錄時，只有全域放行或不放行。不要再談「只放行 AIS 目錄」。
- headless（`-p`）拒絕寫入/執行與有沒有 TTY 無關。讀檔在 headless 下仍可能通過。
- 本 record 不含任何密鑰值。
