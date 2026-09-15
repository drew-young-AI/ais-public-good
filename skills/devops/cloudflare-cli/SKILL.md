---
name: cloudflare-cli
type: skill
description: "Operate Cloudflare from the terminal: expose local services via Tunnel (cloudflared), and manage/deploy Workers + call Workers AI inference via Wrangler or the REST API."
version: 1.0.0
author: local
platforms: [macos]
metadata:
  hermes:
    tags: [Cloudflare, Tunnel, Workers, WorkersAI, Wrangler, Edge]
    related_skills: [tailscale-cli]
---

# Cloudflare CLI (thin link)

> **兩層架構薄連結**：實作在中立層，本 skill 只是入口薄殼。
> Owner binaries:
>   - `~/capabilities/scripts/cloudflared` → `/opt/homebrew/bin/cloudflared`（brew，ARM-native）
>   - `~/capabilities/scripts/wrangler` → `npx --yes wrangler`（不全域安裝，同 m365-admin 模式）
> SSoT: `~/capabilities/registry.yaml`（capability: `cloudflare-tunnel`, `cloudflare-workers`）

## 兩個子能力，用途不同

| | cloudflared (Tunnel) | wrangler (Workers / Workers AI) |
|---|---|---|
| 用途 | 把本機服務曝露到公網或 Zero Trust 私有網路 | 部署/管理 Cloudflare Workers、呼叫 Workers AI 推論 |
| 現況 | binary 已裝，2026-08-17 實測可執行；tunnel 認證另需 cert 或 remote token | binary 可跑（npx），**帳號認證失效待補**（見下） |
| 認證 | `cloudflared tunnel login`（產生 cert.pem）或 Zero Trust dashboard 建立的 `--token` | 環境變數 `CLOUDFLARE_API_TOKEN` 或 `wrangler login` |

## ⚠️ 認證狀態（2026-08-17 實測，非猜測）

`~/.env` 內的 `CLOUDFLARE_API_KEY` 已失效：
- `wrangler whoami` → `Invalid access token [code: 9109]`
- REST `GET /accounts/{id}/ai/models/search` → `{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}`

**在使用 wrangler / Workers AI 前，須先請使用者到 Cloudflare dashboard
（My Profile → API Tokens）重新產生一個 token**，權限至少包含：
- `Account.Workers Scripts:Edit`
- `Account.Workers AI:Edit`
- `Account.Account Settings:Read`

拿到新 token 後更新 `~/.env` 的 `CLOUDFLARE_API_KEY`，並同步 export 成
`CLOUDFLARE_API_TOKEN`（wrangler 與 REST API 認的變數名）：

```bash
export CLOUDFLARE_API_TOKEN="$(grep '^CLOUDFLARE_API_KEY=' ~/.env | cut -d= -f2)"
export CLOUDFLARE_ACCOUNT_ID="$(grep '^CLOUDFLARE_ACCOUNT_ID=' ~/.env | cut -d= -f2)"
~/capabilities/scripts/wrangler whoami   # 應顯示帳號 email，不再是 code 9109
```

`~/.env` 現有：`CLOUDFLARE_TUNNEL_ID`、`CLOUDFLARE_ACCOUNT_ID`、`CLOUDFLARE_API_KEY`
（LINE webhook 曝露用途，見 memory `line_dify_bridge`）。

---

## cloudflared（Tunnel）操作

一律透過中立層 wrapper：

```bash
~/capabilities/scripts/cloudflared tunnel login              # 首次：瀏覽器授權，產生 cert.pem
~/capabilities/scripts/cloudflared tunnel create <name>       # 建立具名 tunnel
~/capabilities/scripts/cloudflared tunnel route dns <name> <hostname>
~/capabilities/scripts/cloudflared tunnel run <name>           # 前景執行
~/capabilities/scripts/cloudflared tunnel list                 # 列出帳號下所有 tunnel

# 若 tunnel 是在 Zero Trust dashboard 建立的「remotely-managed」型（本機 CLOUDFLARE_TUNNEL_ID 屬此類）：
~/capabilities/scripts/cloudflared tunnel run --token <TUNNEL_TOKEN> <name>

# 臨時測試用（不需帳號，隨機 trycloudflare.com 網址，重啟即失效）：
~/capabilities/scripts/cloudflared tunnel --url http://localhost:3000
```

## wrangler（Workers / Workers AI）操作

一律透過中立層 wrapper（首次呼叫會經 npx 下載，稍慢；之後走 npx cache）：

```bash
~/capabilities/scripts/wrangler whoami                 # 驗證登入身分
~/capabilities/scripts/wrangler init <name>              # 建立新 Worker 專案
~/capabilities/scripts/wrangler dev                       # 本機開發伺服器
~/capabilities/scripts/wrangler deploy                    # 部署 Worker

# Workers AI 模型管理
~/capabilities/scripts/wrangler ai models                  # 列出可用模型
```

### Workers AI 推論：兩種呼叫方式

**A. 不部署 Worker，直接 REST API 呼叫模型**（最快，適合單次推論/測試）：

```bash
curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct" \
  -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```

**B. 部署一個 Worker，Worker 內用 AI binding 呼叫**（適合正式服務、要接 webhook 的場景，
例如 LINE×Dify bridge 若要把某段推論搬到 edge）：

```toml
# wrangler.toml
[ai]
binding = "AI"
```

```js
export default {
  async fetch(request, env) {
    const response = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
      messages: [{ role: 'user', content: 'test' }],
    });
    return Response.json(response);
  },
};
```

## 與本機 Qwen MLX 的分工

- 本機 Qwen3.6-35B-A3B（`http://127.0.0.1:9000`）：離線、免費、無資料外流，優先用於含 PHI/敏感資料的推論。
- Workers AI：需要公網可達（如 webhook 觸發的輕量推論、或超出本機模型能力的任務）才考慮，
  **禁止**輸入病患可識別資訊（PHI）——與 openevidence MCP 的風險規則一致。

## 平台限制

cloudflared / wrangler 皆為 ARM64 原生（cloudflared 為 brew bottle；wrangler 為 Node，
架構中立）。wrangler 走 `npx --yes`，不全域安裝。
