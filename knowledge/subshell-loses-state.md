---
id: subshell-loses-state
type: reference
title: 命令替換是子 shell——陣列累積會靜默消失（同一 repo 兩次，第二次代價 421GB）
description: "X=\"$(f)\" 裡 f 對陣列的追加隨子 shell 消失，父行程看到空陣列。清理迴圈因此從未刪過任何東西，而所有輸出都正常。跨子 shell 累積要用檔案。"
tags: [bash, subshell, silent-failure, cleanup, disk]
source:
  - agent: claude
    path: private-source   # 原始位置在私有機器上，digest 仍可由來源持有者驗證
    locator: "§25 磁碟是被測試套件填滿的"
    digest: sha256:91c6cba24e73668ab86351bcc40c30c0e1a40bbf056b10abfe931ce488283403
    note: "第一次：合成控制的計數器永遠到不了 3。第二次：測試 sandbox 註冊表從未清理過任何東西，421GB 累積於 $TMPDIR"
status: stable
inject: auto
timestamp: '2026-09-04T00:00:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

# 子 shell 是狀態去被遺忘的地方

## 樣態

```bash
ITEMS=()
make_thing() { t="$(mktemp -d)"; ITEMS+=("$t"); echo "$t"; }
cleanup()    { for i in "${ITEMS[@]}"; do rm -rf "$i"; done; }

X="$(make_thing)"     # ← 命令替換＝子 shell
cleanup               # ← ITEMS 是空的，什麼都沒刪
```

`$(...)` 開子 shell。`ITEMS+=` 改的是**子 shell 的副本**，
父行程的陣列自始至終是空的。`cleanup` 迭代空集合、刪掉零個東西、
**回傳 0、不印任何錯誤**。

## 為什麼難發現

- 沒有錯誤訊息、沒有非零回傳碼
- `make_thing` 本身完全正常，`cleanup` 本身邏輯也正確
- **唯一的症狀在別的地方**：磁碟慢慢滿。而磁碟滿的時候，
  沒有人會回頭懷疑一個「看起來有在清理」的 cleanup 函式

實測代價：測試套件每次執行留下多 GB 的 sandbox，三天累積 **421GB**，
把整台機器的磁碟填滿並停掉平台。而該平台當時正在為「磁碟沒有被監控」建監控——
**監控蓋的洞比它自己的成因高了一層。**

## 修法

**要跨子 shell 累積就用檔案，不要用變數。**

```bash
REGISTRY="$(mktemp)"; export REGISTRY
make_thing() { t="$(mktemp -d)"; printf '%s\n' "$t" >> "$REGISTRY"; echo "$t"; }
cleanup() { while IFS= read -r i; do rm -rf "$i"; done < "$REGISTRY"; : > "$REGISTRY"; }
```

寫檔穿得過子 shell，因為它寫的是檔案系統不是 shell 記憶體。

## 兩個連帶的判斷

- **清理要註冊在 trap 上，不要只放在正常路徑的結尾。**
  但注意 `trap X EXIT` 是**取代**不是疊加——多個地方各自註冊會互相覆蓋，
  需要一個可累加的 `on_exit` 機制。
- **驗收要量副作用，不要量回傳碼**：跑完一次之後 `$TMPDIR` 有沒有變大。
  一個「有在清理」的函式和一個「刪了零個」的函式，回傳碼一模一樣。
