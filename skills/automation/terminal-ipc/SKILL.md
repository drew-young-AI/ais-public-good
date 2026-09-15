---
name: terminal-ipc
type: skill
description: |
  Terminal IPC v1.1.0 — 透過 tmux 對「其他 AI CLI 的終端」注入按鍵、回讀畫面、等待握手，
  全程留 markdown 稽核軌。用於多 agent 終端協作與跨 AI 狀態互相確認。
  解決的實測問題：agy「could not open TTY」、grok「Device not configured」等 CLI 在無 TTY 環境失效；
  以及對 Claude Code 這類 TUI，send-keys rc=0 並不代表畫面真的吃到字。
version: 1.1.0
platforms: [macos, linux]
requires: [tmux]
metadata:
  hermes:
    tags: [automation, terminal, tmux, ipc, multi-agent, handshake, audit, tui]
    category: automation
---

# Terminal IPC（tmux）

對**具名終端**注入指令、**讀回畫面**、**等待握手**，並把每一步寫進 markdown 稽核軌。
任何 AI CLI（claude / hermes / codex / grok / agy…）都可呼叫同一支腳本，因此能**互相確認對方 shell 狀態**。

## 為什麼用 tmux（而不是 AppleScript / Accessibility）

| 方式 | 能注入 | 能**讀回畫面** | 需權限 | 判定 |
|---|---|---|---|---|
| **tmux**（本 skill） | ✅ | ✅ `capture-pane` | 否 | **採用** |
| AppleScript / Accessibility | ✅ | ❌ 不可靠 | 是，且搶焦點 | 否決 |
| reptyr 偷 PTY | — | — | macOS 無可靠對應（SIP 擋 ptrace） | 否決 |

**讀不回畫面 = 沒有握手 = 這套機制的價值歸零**，故只採用 tmux。
**tmux 回傳 rc=0 ≠ 對方吃到字**。成功條件是畫面指紋改變，或 `wait` 看到 pattern。

## 指令

```
scripts/tmux-ipc <子指令>

  list                              列出所有可用目標（session:window.pane）
  status <target>                   command / alternate / state / last
  ready  <target> [secs]            等畫面穩定（TUI 注入前必做；逾時 rc=3）
  scan   [pattern]                  pane 行程 + 哪些 CLI 可接續 / 需重啟
  spawn  <name> [cmd]               建具名 session（給 CLI 一個真 TTY）
  send   <target> <text...>         送文字 + Enter，並確認畫面變化
  type   <target> <text...>         送文字（不按 Enter），並確認畫面變化
  key    <target> <key...>          送特殊鍵（C-c / Escape / Enter）
  read   <target> [lines]           回讀畫面（TUI＝可見區；shell＝含歷史）
  wait   <target> <pattern> [secs]  等畫面出現 pattern（握手；逾時 rc=3）
  interactive <target> <text> [interval] [max]
                                    注入並觀察至畫面穩定；從未變動 rc=3
  kill   <target>
  log                               稽核軌路徑與最近記錄
```

**退出碼**（供自動化判定，非文字自評）：`0` 成功｜`2` 目標不存在｜`3` 等待逾時／未觀察到畫面變化｜`1` 其他
**預覽不送出**：`TMUX_IPC_DRYRUN=1`
**關閉畫面確認**（舊行為，不建議）：`TMUX_IPC_CONFIRM=0`

## 能不能接續「已經在跑的 AI CLI」？

- **已在 tmux 內** → ✅ 可以，`list` / `scan` 看得到就能直接 `ready` → `send` / `read`，**不必重啟**。
- **跑在一般 Terminal.app / iTerm** → ❌ **不行**（tmux 只能對自己的 pane 送鍵，硬限制）。
  用 `scan` 會把這些標成 ⚠；在該終端執行 `tmux new -s <名字>` 後重跑 CLI 即可納管。

**建議**：日後啟動 AI CLI 一律用 `spawn`，就永遠可控。

## 標準協作流程（給任何 AI 遵循）

```bash
IPC=${AIS_ROOT}/capabilities/skills/automation/terminal-ipc/scripts/tmux-ipc

$IPC scan                                  # 1. 先看誰可接續（含 pane 行程）
$IPC spawn agent-a 'claude'                # 2. 沒有就開一個（真 TTY）
$IPC ready agent-a 20                      # 3. 等 TUI/prompt 穩定（禁止 sleep 代替）
$IPC send  agent-a '請分析 X'               # 4. 注入任務（失敗＝畫面沒變，rc=3）
$IPC wait  agent-a '完成' 120               # 5. 握手：等關鍵字出現（rc=3 代表逾時）
$IPC read  agent-a 60                      # 6. 讀回結果
```

對**內嵌互動程式**（Claude Code / Codex / Grok TUI）：`ready` 不可省略。對方正在產生輸出時硬送，字會進錯緩衝或變成空 Enter。

## 紀律（呼叫端必須遵守）

1. **先 `status` / `read` 再 `send`**：確認對方處於可接收狀態，不要盲送。
2. **TUI 先 `ready`**：以畫面指紋穩定為準，不用 `sleep`，也不要用已刪除的 `DELAY_BEFORE_ACTION`。
3. **握手用 `wait` 而非 `sleep`**：以畫面出現的字串為準，不猜時間。
4. **空字串禁止送出**：空 `send` 等於對 Claude Code 盲按 Enter。
5. **危險指令先 `TMUX_IPC_DRYRUN=1` 預覽**。
6. **稽核軌不可刪**：`logs/YYYY-MM-DD.md` 是跨 AI 對帳依據。`before` / `after` 必須是最後一行非空內容。
7. **完成與否看退出碼**，不看 LLM 自報。`rc=0` 在 v1.1 起代表畫面已確認變化。

## 注入方法

| 情況 | 方法 | 原因 |
|---|---|---|
| 單行、對方是 shell | `send-keys -l` | 字面 UTF-8，不把 `C-c` 當按鍵名 |
| TUI（`alternate_on=1` 或 claude/codex/grok/hermes/vim） | `paste-buffer -p` | 括號貼上，多行不會中途被當 Enter |
| 文字含換行 | `paste-buffer -p` | 同上 |

覆寫：`TMUX_IPC_METHOD=paste|keys`。

## 稽核軌格式

`logs/YYYY-MM-DD.md`：

| 時間 | 動作 | 目標 | 內容 |
|---|---|---|---|
| 15:12:37 | before | agent-a | drew@70 ~ % |
| 15:12:37 | send | agent-a | echo HANDSHAKE_OK_42 |
| 15:12:37 | after | agent-a | HANDSHAKE_OK_42 |
| 15:12:38 | wait-ok | agent-a | pattern=HANDSHAKE_OK_42 after 0s |

`send` 會記 `before`（最後一行非空）與 `after`。若 `before` 空白，那是 bug，不是「當時沒畫面」。

## 自測

```bash
${AIS_ROOT}/capabilities/skills/automation/terminal-ipc/scripts/tmux-ipc-selftest
```

隔離 session，不碰 `tmux_cli_integration` / `devops_dataops_llmops`。exit 0 = 契約成立。

## 已驗證

- v1.0（2026-08，macOS + tmux 3.6b）：spawn / send / read / wait / kill；接續已在跑的 REPL；rc=2 / rc=3；DRYRUN
- v1.1（2026-08-19）：拒絕空 send；`read` 不再輸出字面 `\n`；`before` 取最後非空行；send 以畫面指紋確認；interactive 穩定即結束（不再空轉 45s）；TUI 走 paste-buffer；`status` / `ready` / `scan` 顯示 pane 行程
