---
name: m365-cli
type: skill
description: "Manage Microsoft 365 — Teams, SharePoint, OneDrive, Entra, Viva — from the terminal via the CLI for Microsoft 365 (m365)."
version: 1.0.0
author: local
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [M365, Teams, SharePoint, OneDrive, Entra, Microsoft365, pnp, m365]
    related_skills: [office-documents]
---

# Microsoft 365 CLI (thin link)

> **兩層架構薄連結**：實作在中立層，本 skill 只是 Hermes 的入口薄殼。
> Owner: `@pnp/cli-microsoft365` via `npx`（不全域安裝，首次進 npx cache）
> Wrapper: `~/capabilities/scripts/m365`  |  SSoT: `~/capabilities/registry.yaml`（capability: `m365-admin`）

Use this skill whenever the user references Teams, SharePoint, OneDrive, Entra ID
(Azure AD), Viva, or any Microsoft 365 admin/automation task.

## Invocation

一律透過中立層 wrapper 呼叫：

```bash
~/capabilities/scripts/m365 <command>
```

## Auth（首次使用）

```bash
~/capabilities/scripts/m365 login        # device-code / interactive OAuth
~/capabilities/scripts/m365 status       # 確認登入狀態（未登入回 "Logged out"）
```

## 常用操作

```bash
~/capabilities/scripts/m365 version                    # → v11.9.0
~/capabilities/scripts/m365 spo site list              # SharePoint 站台
~/capabilities/scripts/m365 teams team list            # Teams 團隊
~/capabilities/scripts/m365 entra user list            # Entra 使用者
```

## 備註

npx 首次呼叫會下載套件到 cache（冷啟動較慢），之後轉快。升級：清 npx cache 即取最新版。
