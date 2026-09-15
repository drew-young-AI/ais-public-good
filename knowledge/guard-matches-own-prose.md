---
id: guard-matches-own-prose
type: reference
title: 文字比對的守衛會匹配到自己的散文（單一檔案內六次）
description: "grep 式的靜態規則活在它所搜尋的語料裡：規則的實作、註解與 fixture 都會被自己抓到。這不是疏忽，是方法的定義性質，新增規則時要預設它會發生。"
tags: [static-analysis, guard-design, false-positive, testing]
source:
  - agent: claude
    path: ~/ENV/Devops/docs/Backlog.md
    locator: "§25 磁碟是被測試套件填滿的"
    digest: sha256:91c6cba24e73668ab86351bcc40c30c0e1a40bbf056b10abfe931ce488283403
    note: "同一個檔案內累計六次；前三次已被該檔自己的註解記錄下來"
status: stable
inject: auto
timestamp: '2026-09-04T00:00:00+08:00'
---

# 文字比對的守衛會抓到自己

## 樣態

寫一條「禁止某種寫法」的靜態規則，用 `grep` 掃原始碼。
規則生效，然後**它把自己標紅**——因為：

1. 規則的**實作**含有那個樣式（`grep "sed -i ''"` 本身就含 `sed -i ''`）
2. 規則的**斷言訊息**含有那個樣式（「every `stat -f` must be preceded by…」）
3. 規則的**合成控制 fixture** 含有那個樣式（`printf 'ghcr.io/Bad-Name/x'`）
4. 規則的**註解**含有那個樣式（「這個套件不 source lib.sh」被
   `grep -q 'lib.sh'` 的豁免條件抓到，於是該套件被錯誤豁免）

第 4 種最陰險：它不是誤報，是**誤免**——守衛安靜地放過了它該抓的東西。

## 為什麼這不是疏忽

單一檔案內累計**六次**，跨數週、由不同的規則造成。
六次之後結論是：**一個文字比對的守衛，活在它所搜尋的語料裡。**
這是方法的定義性質，不是執行者的失誤。

## 設計時就要假設它會發生

- **樣式用組裝的，不要寫字面**：`Q="$(printf '\047')"; PAT="sed -i $Q$Q"`
- **fixture 內容用變數組**：`printf 'x: %s/y' "$UPPER_OWNER"`，
  不要 `printf 'x: ghcr.io/Upper-Name/y'`
- **匹配呼叫而不是文字**：豁免條件要匹配 `^\s*(source|\.)\s+.*lib\.sh`
  （真正的 source 行），不是字串 `lib.sh`
- **先剝註解再比對**：`sed 's/[[:space:]]*#.*$//'`
- **每條規則都要有雙向合成控制**：一個必須被抓的 fixture、
  一個必須不被抓的 fixture。只有前者的話，一條「抓所有東西」的壞規則也會通過

## 一句話

**規則的描述、實作與 fixture 都是語料。** 寫規則時先問：
「這條規則掃到它自己這一行會怎樣？」
