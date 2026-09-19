---
id: sleeping-host-breaks-continuity
type: reference
title: 「連續為真」的告警條件在會睡的宿主上結構性地無法被滿足
description: "Prometheus 的 for:、任何 N 分鐘連續條件、以及 launchd/cron 的區間排程，都假設宿主一直醒著。筆電會睡，於是條件從未改變的訊號會在 firing 與 pending 之間彈跳，而板面看起來像訊號消失。修法是用時間窗取代連續性，參數要量不要猜。"
tags: [devops, platform, monitoring, alerting, prometheus, laptop-host, scheduling, false-negative]
source:
  - agent: claude
    path: private-source   # 原始位置在私有機器上，digest 仍可由來源持有者驗證
    locator: "追記 2026-09-05：下限修好之後，才看見它擋在前面的第二個缺陷"
    digest: sha256:adc7636117515d19e568c8b7c73f041cc8dc0d46e4b34eba0d7c59d996dfefe3
    note: "COVID-19 漂移告警：條件連續 30 小時未變，卻在 firing/pending 之間彈跳"
status: stable
inject: auto
timestamp: '2026-09-05T00:00:00+08:00'
shareable: true
reviewed_at: '2026-09-19'
---

# 會睡的宿主會把「連續為真」變成「時有時無」

## 樣態

在筆電上跑監控。某個條件**持續為真且數值完全沒變**，
但告警在 `firing` 與 `pending` 之間反覆跳，板面有時顯示 0 個告警。
看起來像訊號消失或資料有問題，實際上兩者都不是。

## 機制

`for: 2h` 要求條件在**每一次求值**都成立。宿主睡著時求值停止；
醒來後第一次求值，最後一個樣本已超過 staleness 窗（Prometheus 預設 5 分鐘），
瞬時向量回空 → 條件視為不成立 → **計時器歸零重數**。

同一族的還有：`launchd` 的 `StartInterval` 與 `cron` 在睡眠期間不觸發，
而且醒來後**不是立刻補跑**——實測 FullWake 後 10 分鐘仍未補，
它等到下一個區間邊界。所以小時級的工作在一次睡眠後可以落後兩小時，
而「排程壞了」與「宿主睡了」寫出來的板面**字串完全相同**。

## 判別

不要用「板面顯示什麼」判斷，用告警自己的 activeAt：

```promql
ALERTS_FOR_STATE{alertname="<name>"}   # 值就是 activeAt 的 epoch
```

若這個值在每次喚醒後**前進**，就是計時器被歸零了。
歷史形狀可用 `query_range` 對 `ALERTS{alertstate="firing"}` 壓成區間看出來。

## 修法

用**時間窗**取代連續性假設：

```promql
max_over_time(<expr>[1h]) > <threshold>
```

**視窗長度要量，不要挑。** 量法：對 `up` 系列做 `query_range`，
找出樣本之間的空洞分佈，取最大空洞的數倍當視窗。
實測案例：16 小時內 9 個空洞、全部 4–14 分鐘，最長連續清醒窗
269／209／131／87／75／59 分鐘——所以 `for: 2h` 在十六小時內只有三次機會被滿足。
取 1h（最大空洞的約 4 倍）。

**代價要講清楚**：`max_over_time` 帶來遲滯，條件消失後最多多燒一個視窗長度。
底層資料更新頻率若遠低於視窗（例如週資料），這個代價趨近於零；
若是秒級資料就要重新權衡。

## 驗收

合成控制必須包含**一段缺失的樣本**（promtool 的 `_` 值），
並斷言在缺口之後、`for` 應已滿足的時點仍然 firing。
無回看窗的版本會在缺口處重數而不燒——那一個斷言就是全部差別。
兩個突變要能殺死它：拿掉回看窗、把視窗縮到小於實測空洞。

## 反例（不要這樣做）

**不要**用「把監控搬到不會睡的機器」當成這一條的替代。
那是對的長期方向，但它是主機決策；在那之前，
上面的修法讓已經成立的訊號**不被空洞抹掉**，兩者解決的不是同一件事。
