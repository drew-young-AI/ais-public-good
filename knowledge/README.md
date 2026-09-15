---
type: explanation
title: capabilities/knowledge — 跨 AI 共用的耐久事實層
description: "各家 AI 的原生記憶不搬、不合併；只做單向蒸餾到這一層，各家唯讀消費。"
tags: [memory, knowledge, context-engineering, vendor-neutral]
status: stable
timestamp: '2026-08-20T15:00:00+08:00'
---

# capabilities/knowledge

## 這一層在解什麼

**不是「把各家記憶合併」——那個目標是錯的。**

2026-08-20 實測比對 claude 與 codex 的記憶，發現它們是**不同種類的記憶**：

| | claude（`~/.claude/projects/*/memory/`） | codex（`~/.codex/memories/`） |
|---|---|---|
| 種類 | 語意記憶：什麼是真的 | 情節記憶：哪次做了什麼、證據在哪 |
| 產生方式 | 人工策展，一事一檔 | 機器從 session rollout 兩階段自動抽取 |
| 結構 | frontmatter + `[[wikilink]]` + MEMORY.md 索引 | Task Group → Task，每筆指回 rollout jsonl |
| 生命週期 | 我寫、我改、我刪 | 管線持續覆寫（`memories_1.sqlite` 有 jobs 佇列） |
| 版本控制 | 無 | **自帶 `.git`** |

合併它們會同時損失兩邊的價值：把 codex 的塞進 claude 格式會丟掉 rollout provenance；
把 claude 的塞進 codex 格式會讓人工策展被機器產生的內容淹沒。

而且 **codex 的記憶是寫入端**——搬走它，下次 session 管線會在原地重建。
這比 hermes skills（唯讀資產，可以搬）的情況嚴重得多。
兩個 AI 寫同一份檔案而沒有鎖，就是 `atomic_state.py` 記載的 lost update。

## 架構：單向蒸餾，不是雙向同步

```
T1  各家原生記憶（不動、各自運作、各自的格式與生命週期）
              │
              │  單向抽取：只取「耐久 + 跨 AI 都成立」的事實
              ▼
T2  capabilities/knowledge/   ← 唯一的共用真相，OKF 格式
              │
              │  唯讀注入（各家讀，永不回寫）
              ▼
T3  各家在 context 裡消費
```

**單向是這個設計的全部重點。** 沒有回寫就沒有寫入衝突，
也就不需要在六個 AI 之間做分散式鎖。

## 為什麼值得做：一個實證

比對當天發現，claude 與 codex 各自有一套 LINE 整合的記憶，
而且**彼此完全不知道對方存在**：

- claude 記著 LINE × **Dify** 橋接（`~/Project/line-dify-bridge/`，2 秒 webhook 上限）
- codex 記著 LINE × **Hermes** gateway（`ai.hermes.gateway`，port 8646，Cloudflare Tunnel）

其中 codex 記下的一條，是本專案定義的假成功原型：

> `hermes gateway start` 回報成功、`gateway_state.json` 寫著 running，
> 但 launchd 的延遲 reload 讓 process 實際已死，LINE 完全不通。

**這條教訓 claude 從來沒看過。** 每家 AI 各自付出代價學到的東西，
其他家再付一次同樣的代價——這就是共用層要消滅的浪費。

## 收錄門檻

一筆知識要進這一層，必須同時滿足：

1. **耐久**：不是「這次 session 發生什麼」，而是「下次遇到會再成立」
2. **跨 AI**：不綁特定 CLI 的內部行為（那屬於各家自己的記憶）
3. **有出處**：`source` 欄位指回原始記憶檔，來源消失要驗得出來
4. **可否證**：寫得夠具體，讓人能反駁它

不滿足第 3 條的一律不收——**無法判定死活的知識必然變殭屍**，
與 registry 沒有 `verify` 的能力是同一個病。

## Resolver v0.1：小而可執行的 pull model

不建立第二份 `index.yaml`，也不把整個目錄塞進每一個 session。初版直接掃描這個
目錄的原子 record；目前只有少量 record，`O(n log n)` 的排序成本比雙寫索引與同步
漂移更低。

```text
task context_tags + context_budget_bytes
                │
                ▼
capabilities/scripts/context resolve
  exact tag match → (-matched_tag_count, id) stable sort → first-fit UTF-8 packing
                │
                ├─ bundle（只含選中的正文，最多 byte budget）
                └─ resolution（id、SHA-256、bytes、source path）
                │
                ▼
AIS dispatcher（Tier A）在 host process 啟動前寫 receipt
```

`general` 是最小的跨任務 policy tag，resolver 會自動併入 request；特定 tag 如
`research`、`medical-ai` 必須由 task 顯式宣告。這不是 semantic search，
也不做 tag 階層或 vector retrieval。當精確 tag 已實證不足時，才考慮擴充。

同一份 knowledge snapshot、同一組 tags、同一 byte budget 的 `resolve --json` 輸出必須
完全相同。receipt 只證明 dispatcher 在呼叫 host 前已完成 resolve 與交付準備，**不能
證明模型真的閱讀或遵守內容**。直接執行 vendor CLI 仍是 Tier B/C advisory 路徑。

## Record 契約

每一筆可選取知識都是一個頂層 Markdown 檔，檔名 stem 與 `id` 必須相同：

```yaml
---
id: user-work-policy
type: policy                  # 可讀的 OKF type；不得為 transcript/session-log
tags: [general, user-policy]  # 小寫 ASCII slug，精確匹配
source:
  - path: /absolute/source.md # 絕對路徑或 ~，必須存在且可稽核
    locator: "section or line range"
    digest: sha256:<64-hex>   # 釘選 locator 區段；缺 digest 時才退回整檔 mtime
status: stable                # active 或 stable 才可自動選取
inject: auto                  # auto | manual
timestamp: '2026-08-24T00:00:00+08:00'
ttl_days: 90                  # 選填。到期後自動 withhold + audit 標 STALE，
                               # 不看 source 檔案有沒有變——見下段
---

可注入的正文。單筆最多 4096 UTF-8 bytes。
```

## 秒答事實不進這一層；沒有腳本能秒答的宣稱才進，還要標有效期

判準不是「軟體大小」，是「這件事能不能被一支腳本在幾秒內問到答案」：

- **能秒答的**（裝了沒、版本幾號、有沒有在跑）：不管對象是什麼，一律不進本層，
  改用即時探測（如 `capabilities/scripts/envfacts`）。2026-08-25 實測：手寫在
  `registry.yaml` 的 CLI 版本清單，四筆全部在寫下後數日內過期——維護速度天生
  追不上工具更新速度，不是誰偷懶，這是這類事實的本質。
- **不能秒答、需要判斷或查證的**（廠商行為、協議支援、產品存廢）：這才是本層
  該收的，但這類宣稱通常也有自己的有效期（免費額度、版本相依行為會隨廠商
  更新失效）。這種情況幫 record 加 `ttl_days`：到期後 `context resolve` 自動
  withhold（`ttl-expired:`）、`context audit` 標 STALE，即使 source 檔案內容
  完全沒變。沒有 `ttl_days` 的 record 不受影響，仍是原本的 source-digest/mtime
  判定（見「操作與稽核」一節）。
- 現有 10 筆 record 都沒有掛 `ttl_days`——它們記的是行為模式教訓
  （例如 launchd 假成功樣態），不是版本或額度這類會隨時間單純過期的宣稱，
  耐久性與廠商版本號無關。

- `inject: manual` 的條目永不由 resolver 自動輸出。聯絡資料、個人識別資訊與任何需要
  任務明確授權的內容都只能使用此類型。
- API key、token、password、Bearer credential、private key、chat transcript 與 runtime
  machine state 一律拒絕進入此目錄。
- runtime 真相屬於未來的 TTL probe 層，不能假裝成 durable fact。
- AI 可以直接維護 record，沒有 human approval queue；但每次寫入後必須讓 schema、
  source、secret gate 與 byte limit 通過。這是寫入流程的治理，不是同一 macOS user 下的
  OS-level security boundary。

## 操作與稽核

```bash
${AIS_ROOT}/capabilities/scripts/context resolve \
  --tags research,medical-ai --budget-bytes 8192 --json
${AIS_ROOT}/capabilities/scripts/context audit
${AIS_ROOT}/capabilities/scripts/knowledge-sync status
```

`context audit` 對 schema、source existence 與 source freshness 做稽核。有 `digest`
時比對 locator 區段的 SHA-256（`<!-- AIS-CONSTITUTION:` 之後的注入區塊不進入 digest），
因此 constitution sync 改寫 `CLAUDE.md` 不會把未變的蒸餾打成 STALE。沒有 digest 時才
退回整檔 mtime。來源內容真的變了，record 會被標記 `STALE` 並 withheld，直到複查後更新
digest。`knowledge-sync status` 轉呼叫 `context audit`，自身只另外盤點各家記憶存放區。

## 現有 record

Resolver 只掃描頂層 `*.md`，不含本 README。`general` 會自動併入每次 resolve；
未列 `general` 的 record 必須由 task 顯式宣告 tag。下表由
`capabilities/scripts/context sync-readme-table` 產生，勿手改——新增/修改/刪除
record 後重跑一次即可同步（`--check` 只驗證是否同步、不寫檔）。

<!-- AIS-RECORD-TABLE:START -->
| id | type | 主要 tags | TTL | 何時注入 |
|---|---|---|---|---|
| agent-skills-open-standard | reference | ais, capabilities, interoperability, skills, standards | — | 顯式宣告 tag：ais, capabilities, interoperability, skills, standards |
| ais-shared-context-canary | fact | ais-canary | — | 顯式宣告 tag：ais-canary |
| bsd-gnu-portability-traps | reference | bash, ci, false-success, linux, macos, portability | — | 顯式宣告 tag：bash, ci, false-success, linux, macos, portability |
| capability-index-boundary | reference | ais, capabilities, governance, reachability, registry | — | 顯式宣告 tag：ais, capabilities, governance, reachability, registry |
| command-allowlist-secret-trap | reference | agy, permissions, secrets, security | — | 顯式宣告 tag：agy, permissions, secrets, security |
| copilot-headless-write-false-success | reference | accounts, copilot, false-success | — | 顯式宣告 tag：accounts, copilot, false-success |
| free-credit-arsenal | reference | ais, cli, cost, false-success | — | 顯式宣告 tag：ais, cli, cost, false-success |
| git-commit-autonomy-policy | policy | ais, git, governance | — | 顯式宣告 tag：ais, git, governance |
| guard-matches-own-prose | reference | false-positive, guard-design, static-analysis, testing | — | 顯式宣告 tag：false-positive, guard-design, static-analysis, testing |
| knowledge-bitemporal-supersede | policy | ais, governance, knowledge, memory | — | 顯式宣告 tag：ais, governance, knowledge, memory |
| launchd-service-false-success | reference | false-success, health-check, hermes, launchd, macos | — | 顯式宣告 tag：false-success, health-check, hermes, launchd, macos |
| line-dify-official-plugin-unusable | fact | dify, integration, line, webhook | — | 顯式宣告 tag：dify, integration, line, webhook |
| line-webhook-acceptance-layers | reference | health-check, hermes, integration, line, webhook | — | 顯式宣告 tag：health-check, hermes, integration, line, webhook |
| mlx-call-discipline | policy | ais, local-llm, mlx | — | 顯式宣告 tag：ais, local-llm, mlx |
| mlx-endpoint-start-path | fact | ais, endpoint, local-llm, mlx | — | 顯式宣告 tag：ais, endpoint, local-llm, mlx |
| parser-silent-drop | policy | ais, data-integrity, false-success, parser | — | 顯式宣告 tag：ais, data-integrity, false-success, parser |
| session-archive-storage-choice | policy | ais, knowledge, memory, session, storage | — | 顯式宣告 tag：ais, knowledge, memory, session, storage |
| subshell-loses-state | reference | bash, cleanup, disk, silent-failure, subshell | — | 顯式宣告 tag：bash, cleanup, disk, silent-failure, subshell |
| user-professional-context | fact | career, medical-ai, research | — | 顯式宣告 tag：career, medical-ai, research |
| user-work-policy | policy | apple-silicon, development, environment, general, macos, user-policy | — | 自動併入（general） |
| verify-primary-sources | policy | architecture, research, sources | — | 顯式宣告 tag：architecture, research, sources |
<!-- AIS-RECORD-TABLE:END -->

未蒸餾、刻意排除：email/NTU id、MLX 是否在聽、venv/Docker 現況、各家 persona、
Hermes USER.md 裡「gateway 正在跑」的 runtime 宣稱、Google API key 狀態。
