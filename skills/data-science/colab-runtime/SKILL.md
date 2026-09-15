---
name: colab-runtime
type: skill
description: "Provision and run Python on remote Google Colab GPUs/TPUs (A100/H100) from the terminal via the official Google Colab CLI."
version: 1.0.0
author: local
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Colab, GPU, TPU, Notebook, RemoteRuntime, CloudCompute, google-colab-cli]
    related_skills: [jupyter-live-kernel]
---

# Colab Runtime (thin link)

> **兩層架構薄連結**：實作在中立層，本 skill 只是 Hermes 的入口薄殼。
> Owner binary: `~/capabilities/scripts/colab` → `google-colab-cli`（uv tool 隔離安裝）
> SSoT: `~/capabilities/registry.yaml`（capability: `notebook-runtime`）

Use this skill whenever the user wants remote GPU/TPU compute, to run a local
Python script on a Colab runtime, or to provision accelerators from the terminal.

## Invocation

一律透過中立層 wrapper 呼叫（不要直接依賴 `~/.local/bin/colab` 位置）：

```bash
~/capabilities/scripts/colab <command> [args]
```

## Auth（首次使用）

```bash
~/capabilities/scripts/colab --auth oauth2   # 公開 InstalledAppFlow，開瀏覽器授權
# 或用 Application Default Credentials：
~/capabilities/scripts/colab --auth adc
```

## 常用操作

```bash
~/capabilities/scripts/colab --help              # 列出所有 command
# 典型流程：provision 加速器 → 遠端執行本地 script → 取回 artifact
```

## 平台限制

僅支援 Linux / macOS（Windows 不支援）。Apple Silicon 原生可用。
