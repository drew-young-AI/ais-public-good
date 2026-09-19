---
id: copilot-headless-write-false-success
type: reference
title: Copilot headless 寫入假成功與帳號輪替
description: "未設 COPILOT_ALLOW_ALL 時寫入會落到 session-state 仍回報 DONE。帳號在 ~/.accounts。文件宣稱 classic PAT 不可用，實測可。"
tags: [copilot, false-success, accounts]
source:
  - path: private-source   # 原始位置在私有機器上，digest 仍可由來源持有者驗證
    digest: sha256:25e8738db23491c80825a4db7d9fd3a6f0c376c4c72b91b3526c6c0da3f0f608
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

# Copilot headless 寫入假成功

- 寫入需要 `COPILOT_ALLOW_ALL=true`（AIS `capability_map` 的 env）。不設時，被拒後改寫到 `~/.copilot/session-state/` 仍回報 DONE。這是假成功，不是完成。
- 多帳號寫在 `~/.accounts`（權限 600），段名是帳號、段內 `copilot-cli = <token>`。加一行即進輪替，不必改程式。token 本身不進共用層。
- 官方 help 寫 classic PAT 不受支援；實測帶 `copilot` scope 的 classic PAT 可以覆寫耗盡中的預設身分。文件與實測衝突時以實測為準。
- 憑證在 macOS Keychain；`COPILOT_HOME` 不覆蓋既有憑證。判別「env token 是否生效」要用耗盡 vs 有額度帳號對照，不要只看 rc。
