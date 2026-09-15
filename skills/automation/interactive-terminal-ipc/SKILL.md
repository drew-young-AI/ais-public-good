---
name: interactive-terminal-ipc
type: skill
description: Use observe-act-verify for tmux terminal IPC.
version: 1.1.0
platforms: [macos, linux]
requires: [tmux, terminal-ipc]
metadata:
  hermes:
    tags: [automation, terminal, tmux, ipc, interactive, observe-act-verify]
    category: automation
---

# Interactive Terminal IPC

對 tmux pane **邊注入邊觀察**，直到畫面指紋穩定。禁止 fire-and-forget，也禁止固定 sleep 當成功條件。

契約與退出碼以 `terminal-ipc` 為單一事實來源：

`${AIS_ROOT}/capabilities/skills/automation/terminal-ipc/SKILL.md`

## 何時用這個而不是 `send`

- 對方是長任務、TUI、或會停下來問你的互動程式（Claude Code / build / REPL）。
- 需要看畫面是否真的在動，而不是只看到 `send` 的 rc。

短指令、已知 pattern 的握手：直接用 `send` + `wait`。

## 用法

```bash
IPC=${AIS_ROOT}/capabilities/skills/automation/terminal-ipc/scripts/tmux-ipc

$IPC status <target>
$IPC ready  <target> 20
$IPC interactive <target> "<command>" [interval_s] [max_checks]
```

預設 `interval=2`、`max_checks=15`。畫面已變過且連續 2 輪指紋不變 → 提前結束。觀察期間畫面從未變 → rc=3。

## 不要做的事

- 不要為了「等 Claude 準備好」在腳本裡加 `DELAY_BEFORE_ACTION` 或寫 debug 檔。用 `ready`。
- 不要把 `interactive` 的 rc=0 當成任務完成；那只代表畫面穩定。任務完成仍用 `wait <pattern>`。
