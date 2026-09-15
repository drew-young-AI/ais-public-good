---
id: git-commit-autonomy-policy
type: policy
title: "Git commit 時機的自主授權"
description: "專案一旦確認需要 git 版本控制，AI 可自行決定一般 commit 的時機，不必逐次詢問；破壞性操作不在授權範圍。"
tags: [git, governance, ais]
source:
  - path: ${AIS_ROOT}/AGENTS.md
    locator: "Git commit 時機"
    digest: sha256:c5dc62beb02180454867e1ee19808da07ad55f95ce1798041b62ebf56e726e9a
status: stable
inject: auto
timestamp: '2026-08-25T15:30:00+08:00'
---

一旦使用者與 AI 在專案討論中已經確認「這個專案／子目錄需要 git 版本控制」，AI 不需要每次
都另外問「現在可以 commit 嗎」——可以自行決定一般 commit 的時機，條件是：

1. 已經走過驗證（該專案既有的測試／lint／audit 全綠，沒有已知失敗）。
2. 確認沒有機密、大型二進位、或會產生壞掉的 embedded-repo 洩漏進 staging。
3. 只限一般 commit——force-push、amend 已發布的 commit、跳過 hook、rewrite history
   這類破壞性操作，仍然一律要明確詢問，不受本條授權涵蓋。

授權範圍只是「commit 的時機判斷」，不是「要不要導入 git」本身——後者仍須在專案開始階段
與使用者討論後才能決定。首例：AIS 根目錄 2026-08-25 git init，`cross-cli-canary-pilot`
兩輪真機驗證＋回歸測試全綠後才 commit（`9e2e5d8`），未再另外詢問。
