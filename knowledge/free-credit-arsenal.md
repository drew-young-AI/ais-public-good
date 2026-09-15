---
id: free-credit-arsenal
type: reference
title: 免費 credit 彈藥庫：三支後備 CLI 的旗標與假成功形狀
description: "qodercli / kiro-cli / devin 於 2026-08-31 實跑納入 execute 鏈。三支各有一種缺旗標就 rc=0 卻沒做事的形狀；kiro-cli 是唯一回傳結構化成敗與計費的一支。"
tags: [cli, false-success, cost, ais]
source:
  - path: ~/.claude/projects/-Users-drew/memory/free_credit_arsenal.md
    digest: sha256:c497a76e83c2a4cd7651de24f3f00fc63dd5cb6d75fe5fb94fd6a6fa43de729b
status: stable
inject: auto
timestamp: '2026-08-31T01:30:00+08:00'
---

# 免費 credit 彈藥庫

2026-08-31 實跑（讀取型與寫入型皆過）後納入 AIS `execute` 鏈：
`codex-cli → claude-code → qodercli → kiro-cli → devin → local`。
排在兩顆主力**之後**是刻意的——彈藥庫的意義是主力耗盡時還有東西可打，
主力沒問題時燒它們等於把彈藥花在不需要的地方。

| CLI | 非互動模板 | 成本訊號 | 缺旗標時的失效形狀 |
|---|---|---|---|
| `qodercli` | `qodercli --permission-mode accept_edits -p` | 無 | **rc=0、有輸出、檔案沒建** |
| `kiro-cli` | `config/kiro_bridge.py`（stdin） | `meteringUsage` 結構化欄位 | v1 engine 不支援 stream-json，回 runError |
| `devin` | `devin --permission-mode accept-edits --respect-workspace-trust false -p` | 無（apk_/cog_） | 未信任目錄下非互動直接失敗 |

## 三件不能靠推論得到的事

1. **`kiro-cli` 就是 Amazon Q Developer CLI 改名。** binary 內含 `q_cli` ×428、
   `codewhisperer` ×221、`AmazonQKiroCLI` 字串。所以是三支不是四支。
   （`~/.quickwork` 是另一個 Amazon 產品 Amazon Quick Suite，別混。）

2. **旗標拼法不可互抄。** qoder 用底線 `accept_edits`，devin 用連字號
   `accept-edits`。抄錯不會報錯，只會靜默退回不能寫檔的模式——
   而模型多半仍會回報做完。這正是 copilot 少了 `COPILOT_ALLOW_ALL`
   那次實測過的假成功，換一家重演。

3. **`kiro-cli` 是三支裡唯一回傳機器可讀成敗的。**
   `--agent-engine v2 --output-format stream-json` 給 ACP JSON Lines，含
   `runFinished.status`、`stopReason`、`finalTextTruncated`、`meteringUsage`。
   其餘兩支只能靠 rc 推測，而 **rc=0 正是假成功最愛穿的衣服**。
   改走 bridge 的主要理由是這個，不是剝 ANSI；剝 ANSI 只是順帶。

## 攔截機制

`outcome_rules.yaml` 的 `permission_mode_blocked`（priority 1144）攔第 2 點：
要求 `permission` 與 `accept` **同時**出現才判 blocked——用 `any:` 會把
「任務本身在討論權限模式」的正常回答誤判掉。
模板補旗標可以避免問題，但**旗標會被改掉，規則不會**。
