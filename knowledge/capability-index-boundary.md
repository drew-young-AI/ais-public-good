---
id: capability-index-boundary
type: reference
title: AIS registry 與各專案自己的能力索引，是兩層不是兩份
description: "判準是「別的 AI 工具需要直接呼叫它嗎」：是→AIS registry（含 verify）；否→留在專案的能力表。兩邊都登記就是自己造一份會分岔的副本。"
tags: [capabilities, registry, governance, ais, reachability]
source:
  - path: ~/ENV/Devops/docs/Reachability.md
    digest: sha256:f7fdc182bcb8c94c01df6f3ed70c46055179e99b07c4a49e3785b7917ecd0c6a
status: stable
inject: auto
timestamp: '2026-09-02T20:00:00+08:00'
---

# 能力索引的邊界

- **AIS `capabilities/registry.yaml` 管的是跨 AI 工具邊界的能力**：任何一隻 CLI（claude / grok / agy / hermes / colab / m365）都該找得到、且能以 `verify` 判定死活。規模刻意小（2026-09-02 為 17 筆）。
- **專案自己的能力表管的是該 repo 的內部組件**：只有在那個 repo 的脈絡裡才有意義。以 `~/ENV/Devops` 為例，2026-09-02 有 **90 支**能力，索引在各 `platform/*/README.md` 的能力表，並由 `platform/docs/capability_graph.py --catalog` 產生 `evidence/capabilities.json`。
- **判準只有一句**：「別的 AI 工具需要直接呼叫它嗎？」是 → AIS registry；否 → 留在專案。
- **兩邊都登記是錯的。** 那是自己造一份會分岔的副本，而**過期的索引讀起來和正確的索引一模一樣**——Devops repo 的 `platform/README.md` 曾有第二份能力索引，停在 2026-08-10、宣稱「唯一剩餘是 Public URL」，而那是 Kubernetes、第二台機器、跨架構映像守衛之前的事。
- **把專案的 90 支全部登記進 registry 也是錯的**：17 筆變成 100+ 筆，而 100+ 筆的清單沒有人看——那正好製造出這條規則要防的東西。目前只有 `devops-k8s-cluster` 一筆跨界，理由是叢集是其他工作也會用到的基礎設施；那個判準是對的。
- **專案端的可達性做法可以借用**（四層：文件可達 / 頁面出處 / 功能可達 / 重複偵測），細節見 source 的 `docs/Reachability.md`。核心結論：**被程式呼叫不等於找得到**，而**可達性證不到內容還是不是真的**。
