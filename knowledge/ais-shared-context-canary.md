---
id: ais-shared-context-canary
type: fact
title: AIS shared-context canary
description: "唯一用途：證明 resolver handshake 有跑。只有 task 顯式宣告 ais-canary 才會出現。不得當一般知識。"
tags: [ais-canary]
source:
  - path: ${AIS_ROOT}/workspace/projects/shared-context-architecture/canary-nonce.txt
    digest: sha256:9b50639194499989a6a6aa4943bb0f03aa63c10c595a4f3e1f6ded1938006ea9
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
---

# AIS shared-context canary

Nonce: `AIS_SHARED_CONTEXT_CANARY_v1`

此 record 不是業務知識。若 instruction 在 AIS dispatcher 路徑出現此 nonce，代表 `context resolve` 已在 host 啟動前執行。直接開 vendor CLI 即使讀到 advisory，也不算 canary 通過。
