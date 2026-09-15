---
id: parser-silent-drop
type: policy
title: 解析器的靜默丟棄比解析失敗危險得多
description: "不認得的資料形狀被跳過而不報錯，會產生看起來合理的殘缺資料集。實測：gemini 441 則使用者訊息消失，DB 顯示 user=0 assistant=693，像「這家很少提問」。"
tags: [parser, false-success, data-integrity, ais]
source:
  - path: ${AIS_ROOT}/capabilities/scripts/session-ingest
    digest: sha256:ef8e532816f241776bf11c80988ba8d5f76bed9ddf3227465caeab08030bc087
  - path: ${AIS_ROOT}/adapters/test_dispatcher_smoke.py
    digest: sha256:9330172b1fc01d72bec550bba0683ba4a404a061d0502893213c43b398526cbc
status: stable
inject: auto
timestamp: '2026-09-02T19:00:00+08:00'
---

# 解析器的靜默丟棄

## 樣態（2026-08-31 實測）

gemini CLI 的 content block 是 `{"text": ...}`，**沒有 `type` 欄位**。
餵給以 Anthropic block 形狀寫的解析函式，會在每個 `b.get("type")` 分支上
落空——**一筆都不寫、不拋例外、不留紀錄**。

後果：DB 裡 gemini-cli 的 `user=0`、`assistant=693`。
那看起來像「這家很少被提問」，而不是「解析器吃掉了一半」。

## 為什麼實跑測不出來

實跑只會看到「收了 693 筆」。**數字不為零就像成功。**
沒有基準可比對時，殘缺與完整長得一模一樣。
抓到它的是合成樣本——已知輸入有 2 則使用者訊息，輸出必須有 2 則。

## 規則

1. **不認得的形狀要寫進去，不要跳過。** 讓未知變成可見的雜訊，
   而不是不可見的缺口。雜訊會被人發現，缺口不會。
2. **每個 adapter 的測試斷言要指向該格式特有的陷阱**，不是「有沒有解出東西」——
   空檔也解得出零筆而不報錯，那種斷言等於沒有。
3. **重置型的迴圈變數要先確認來源不會出現第二個標頭。** 同一實測中，
   24 個 gemini 檔有 1 個含兩個 session 標頭，舊程式一遇標頭就重置累加器，
   前一段整個消失——同樣不報錯。

## 反面：跳過 ≠ 丟掉（2026-09-02 補）

規則 1 有一個危險的讀法：「把所有跳過的都收進來」。**那會換成另一種錯**。

三次實測，看起來像漏收的有兩次不是：

| 事件 | 判定 | 依據 |
|---|---|---|
| codex `event_msg/agent_message` | 重複 | 36 檔與 `response_item/message` 內容 100% 重疊 |
| qoder `last-prompt` | 重複 | 與同檔 `type:user` 同內容 |
| copilot `skill.invoked` | 重複＋樣板 | skill 名在同檔另 6 處出現；事件只多帶 SKILL.md 全文 |
| copilot `permission.completed` | **真漏收** | `result.kind` 全庫唯一 |

**分辨的方法是比對內容，不是看數量。** 數量只能告訴你「有東西被跳過」，
不能告訴你那東西別處有沒有。收進重複資料不會報錯，
但會讓所有基於次數的統計（呼叫頻率、共現）失真——
而那些統計**沒有任何機制會發現自己被灌水了**。

## 同族

與 rc=0 假成功同構：**失敗必須產生訊號**。
差別在於 rc=0 至少還有一個可檢查的欄位，靜默丟棄連欄位都沒有，
只能靠「已知答案的輸入」來揭露。見 [[copilot-headless-write-false-success]]、
[[launchd-service-false-success]]。
