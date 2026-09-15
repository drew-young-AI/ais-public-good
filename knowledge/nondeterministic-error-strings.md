---
id: nondeterministic-error-strings
type: reference
title: 網路逾時的錯誤字串不確定，據以分支的守衛是靠運氣才對的
description: "同一個故障、同一個指令，連跑三次可以得到三種不同的錯誤訊息。把診斷分支建在這種字串上，會在寫的當天通過、日後在沒人看的時候悄悄給出錯誤答案。判準：重跑三次，字串不同就不可當依據。"
tags: [devops, platform, diagnostics, error-handling, guard-design, flaky, kubernetes]
source:
  - agent: claude
    path: ~/ENV/Devops/docs/Backlog.md
    locator: "T2 的缺陷那半"
    digest: sha256:ef353920f5282009a1f9da07896d3ca85080659209b36ab6b6e19e63ff033fe7
    note: "kubectl 對同一個黑洞 IP 三次回三種字串"
status: stable
inject: auto
timestamp: '2026-09-05T00:00:00+08:00'
---

# 逾時訊息不能當判別依據

## 實測

對同一台不可達主機、同一條 `kubectl` 指令，連跑三次：

| 次數 | 回傳 |
|---|---|
| 1 | `context deadline exceeded (Client.Timeout exceeded while awaiting headers)` |
| 2 | `dial tcp <ip>:6443: connect: no route to host` |
| 3 | `dial tcp <ip>:6443: connect: host is down` |

名字解析不到的情況同樣有兩種變體。**故障沒變，訊息變了。**

## 為什麼會這樣

逾時路徑上有多個計時器在賽跑（HTTP client timeout、TCP connect、
ARP/ND 解析、DNS 解析），哪一個先到就決定了訊息。
負載、快取狀態與網路瞬時狀況都會改變順序。

## 判準

**重跑三次。字串不同 → 不可作為分支依據。**

這個判準很便宜，而且它是唯一有效的——讀原始碼判斷不出來，
因為每一條路徑單獨看都是確定的。

## 哪些可以用

同一輪實測中確定的有兩條：

- **TLS 名稱不符**：`x509: certificate is valid for …, not <name>`
  ——固定，因為它在賽跑開始前就失敗了
- **連線被拒**：`connection to the server <host>:<port> was refused`
  ——固定，且回答的是另一個問題：**主機活著、服務沒在跑**

共同性質：**這兩者都不是逾時**。逾時才是不確定的來源。

## 設計原則

診斷探針在無法確定原因時，**帶出原始訊息，不要下結論**。

```
if <確定的簽章> in stderr:  回報具名的原因
else:                      回報「連不上」＋ 原始那一行
```

讀者能據以行動的證據，勝過我們猜的原因。
更常見的反模式是**把 stderr 整個丟掉換成一句事先寫好的固定句**——
那會讓三種不同原因在板面上長得一模一樣。
