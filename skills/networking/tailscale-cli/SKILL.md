---
name: tailscale-cli
type: skill
description: "Operate the Tailscale mesh VPN (WireGuard-based) from the terminal: check tailnet status, ping/connect to devices across networks, expose local services (serve/funnel), SSH between tailnet machines, transfer files."
version: 1.0.0
author: local
platforms: [macos]
metadata:
  hermes:
    tags: [Tailscale, VPN, WireGuard, Mesh, Networking, RemoteAccess]
    related_skills: [macos-network-troubleshooting]
---

# Tailscale CLI (thin link)

> **兩層架構薄連結**：實作在中立層，本 skill 只是入口薄殼。
> Owner binary: `~/capabilities/scripts/tailscale` → `/usr/local/bin/tailscale`（官方 Tailscale.app 的 CLI shim）
> SSoT: `~/capabilities/registry.yaml`（capability: `mesh-vpn`）

Use this skill whenever the user wants to reach a device across networks (e.g.
MacBook ↔ iPhone ↔ CYCH 端點) without port-forwarding, check tailnet
connectivity, or expose a local dev server to another tailnet device securely.

## 現況（2026-08-17 實測）

- 用的是官方 **Tailscale.app**（GUI menu bar app，`/Applications/Tailscale.app`），
  不是 brew formula（brew 版曾短暫裝過又移除，避免兩個 daemon 打架）
- daemon 由 launchd + app 自身管理，menu bar 開關即可連線/斷線，不需要 sudo 手動起停
- 已登入，tailnet 上有 2 台裝置：`macbook-m5-agent`（本機）、`iphone172`
- 若要在新機器登入：`tailscale up --authkey=<key>`（key 於 Tailscale admin console
  → Settings → Keys 產生，一次性）；本機已透過 app 完成登入，通常不需要重跑

## Invocation

一律透過中立層 wrapper 呼叫（不要直接依賴 `/opt/homebrew/bin/tailscale` 位置）：

```bash
~/capabilities/scripts/tailscale <command> [args]
```

## 常用操作

```bash
# 狀態
~/capabilities/scripts/tailscale status              # 列出 tailnet 上所有裝置與連線狀態
~/capabilities/scripts/tailscale ip                   # 本機 tailnet IP (100.x.x.x)
~/capabilities/scripts/tailscale whoami                # 目前登入身分
~/capabilities/scripts/tailscale netcheck              # 診斷 STUN/DERP/直連品質

# 連線測試
~/capabilities/scripts/tailscale ping <device>          # tailnet 層 ping，回報走 direct 或 DERP relay
~/capabilities/scripts/tailscale nc <device> <port>      # 連到對方某個 port，接 stdin/stdout

# 跨機 SSH（需對方也開 tailscale ssh 或本機已用 ssh 設定）
~/capabilities/scripts/tailscale ssh <device>

# 把本機服務曝露給同一 tailnet 內其他裝置（不經公網）
~/capabilities/scripts/tailscale serve https / http://localhost:3000
~/capabilities/scripts/tailscale serve status

# 把本機服務曝露到公網（經 Tailscale 官方 relay，需帳號啟用 Funnel）
~/capabilities/scripts/tailscale funnel 443 on

# 檔案傳輸（tailnet 內兩台機器互傳，不經雲端）
~/capabilities/scripts/tailscale file cp <path> <device>:
~/capabilities/scripts/tailscale file get

# 帳號操作
~/capabilities/scripts/tailscale up --authkey=<key>     # 登入（首次或重新登入）
~/capabilities/scripts/tailscale down                    # 斷線但不登出
~/capabilities/scripts/tailscale logout                  # 登出並使 node key 失效
```

## 與 Cloudflare Tunnel 的分工

- **Tailscale**：私有 mesh，僅限已加入同一 tailnet 的裝置（本機↔iPhone↔CYCH 端點），無需公開網址。
- **Cloudflare Tunnel**（見 `devops/cloudflare-cli` skill）：對外公開網址（如 LINE webhook 需要公網可達）。
- 兩者用途不重疊，勿混用：內部裝置互連用 Tailscale，需要外部服務（LINE 平台、第三方 webhook）打進來才用 Cloudflare Tunnel。

## 平台限制

僅在此機驗證 macOS（官方 Tailscale.app，Apple Silicon 原生）。daemon 由 app 自身
管理（menu bar 開關 = 連線/斷線），唯讀操作（status/ip/ping/netcheck）不需要 sudo。
