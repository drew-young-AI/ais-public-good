---
id: mlx-call-discipline
type: policy
title: 本機 MLX 的呼叫紀律與定位
description: "用 AIS mlx 腳本，不要直接 curl。定位是 contradiction detector。token 預算超過約 6000 會從截斷變成逾時。"
tags: [mlx, local-llm, ais]
source:
  - path: ~/.claude/projects/-Users-drew/memory/mlx_usage_discipline.md
    digest: sha256:2f7bbcadfa1f69ab0795950488cee5e435a2542fb03b42903dcda8faa9cf380c
status: stable
inject: auto
timestamp: '2026-08-24T18:00:00+08:00'
---

# 本機 MLX 呼叫紀律

- 呼叫入口是 `${AIS_ROOT}/capabilities/scripts/mlx`（registry verify：`mlx selftest`）。不要直接 curl 本機 endpoint，也不要直接調 `qwen_local_bridge`。
- 這是本機唯一同時滿足零邊際成本、`temperature=0` 可重現、資料不出機、可離線的推理來源。可識別資料不進外部 API 時，它不是備胎。
- 輸出契約：rc=0 乾淨答案；rc=3 未完成（下游不得當結論）；rc=4 服務不可用。
- 模式：`mlx yesno` 最穩；`mlx ask` 可用；`mlx review` 是 best-effort。
- token 預算反直覺：約 4000 對 yesno 穩定；超過約 6000 後失效從截斷變成逾時。遇 rc=3 應收窄問題（改 yesno），不是加預算。
- 定位是 contradiction detector（找「註解宣稱 vs 實作」落差），不是 reviewer。它的修法建議必須再實測，不可直接採納。
- 本機服務是否在聽是 runtime probe，不在本 record 宣稱。

## 崩潰真因是模型換載，不是連續呼叫（2026-09-01 更正）

**舊結論（2026-08-29）**：「每輪都死在連續第 2–3 次呼叫、與材料無關、
根因在推論服務端、不是 AIS 能修的」，對策是加 25 秒冷卻。
**觀察正確、歸因錯誤，保留不刪——刪掉的話下一個人會用同樣的觀察重新推導出同一個錯。**

**實測**：AIS 請求 `mlx-community/Qwen3.6-35B-A3B-4bit`，而 server 以
`--model ~/models/Qwen3.8-27B-4bit` 啟動。同一句「只回 OK」：

| 請求的模型 | 耗時 |
|---|---|
| server 已載入的那一個 | **3.5 秒** |
| 另一個（觸發換載） | **29.1 秒**（8×），RSS 15.3GB → 5.6GB |

換載完成後，**連續三次同模型呼叫是 1s / 1s / 0s，全部成功**。
連續呼叫本身不會打掛任何東西。

**機制**：server 重啟後回到預設模型 → AIS 下一次呼叫強制換載 10GB+ →
記憶體 churn 打掛服務 → 再重啟 → 再換載。
冷卻之所以「有效」，只是讓換載有時間完成——**等症狀過去，不是修因**。

**已由機制守住**：`contract-pairs` 的 `mlx-model-matches-server`
比對 `capabilities/scripts/mlx` 的預設模型與 `~/ENV/mlx_llm_server.env` 的
`MODEL_PATH`。要改哪一邊由人決定：換模型會改變萃取品質。

**同時發現的第三個數字**：server 的 env 寫 `MAX_TOKENS=4096`，
而 mlx 腳本用 6000、bridge 用 8192。三者互不相同。
（服務端這個值是否會蓋掉請求端的 max_tokens **尚未實測**，標 `UNVERIFIED`。）
