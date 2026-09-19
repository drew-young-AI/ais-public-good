---
id: mlx-endpoint-start-path
type: fact
title: 本機 MLX 端點的啟動路徑
description: "MLX server 的啟動腳本位置與端點約定；直接 curl 前先確認服務是由該腳本起的。"
tags: [ais, mlx, local-llm, endpoint]
source:
  - path: private-source   # 原始位置在私有機器上，digest 仍可由來源持有者驗證
    digest: sha256:d0ee0347b3bd1b7121a13e2cd46f6f0358f8ae0a5044086c3d2c31ad993082b2
status: stable
inject: auto
timestamp: '2026-09-01T21:10:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

`~/ENV/activate_mlx_llm.sh` is still the historical/documented entry point any tool sources to make sure the MLX local LLM is up, but as of 2026-09-01 it no longer starts a server itself — it just calls `mlx-server ensure`.

The mlx_lm.server process is now a launchd-managed singleton (label `ai.ais.mlx-server`, `KeepAlive` + `ThrottleInterval=30`). Full lifecycle control lives at `${AIS_ROOT}/capabilities/scripts/mlx-server` (`status|install|ensure|stop|logs`); the actual worker process is `${AIS_ROOT}/capabilities/scripts/mlx-server-run`, exec'd only by launchd — never call it directly, and never point the entry point script at it, or the entry point would restart the very launchd job it belongs to.

Config (model path, port, acceleration params) still loads from `~/ENV/mlx_llm_server.env` via the venv at `~/ENV/localLLM/mlx_venv/bin/python` — that file remains the single source of truth for those values; nothing else should duplicate them.

Reason for the change: the old script `exec`'d a brand-new server on every `source` with no already-running check. Claude Code / Codex / Hermes each source it independently, so uncoordinated launches accumulated orphaned processes once the invoking shell exited. See `mlx-call-discipline` for the separate, still-open model-mismatch issue (`contract-pairs mlx-model-matches-server`) and `launchd-service-false-success` for why status here is a real probe, not launchd's self-report.