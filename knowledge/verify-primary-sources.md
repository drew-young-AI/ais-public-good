---
id: verify-primary-sources
type: policy
title: 工具能力邊界先查一手來源
description: "對外部工具「能不能做 Y / 重疊多少」的具體宣稱，先讀官方 repo 與 docs，二手部落格只找線索不定案。"
tags: [research, sources, architecture]
source:
  - path: private-source   # 原始位置在私有機器上，digest 仍可由來源持有者驗證
    digest: sha256:3f42fbcc98780a4b6225c41104770190523186b657810d0d09571c729cd47313
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

# 工具能力邊界先查一手來源

- 任何關於外部工具或框架能力邊界的具體宣稱（重疊多少、支援什麼、協議長怎樣），下結論前先讀一手來源：官方 repo README、官方 docs、協議文件。
- 二手搜尋與部落格只用來找線索，不用來定案。
- 實證：判斷 ORCA 與 AIS 重疊時，二手來源估 15–20%；讀 stablyai/orca README 與 onorca.dev 後上修到 30–35%。二手轉述系統性低估 orchestration 成熟度。
- 一手文件也可能過時。文件與實測衝突時，以可重跑實測為準，並標明文件被推翻的範圍。
