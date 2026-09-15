---
id: bsd-gnu-portability-traps
type: reference
title: BSD 與 GNU 的介面差異：在 macOS 上綠、在 Linux 上靜默失敗的四種寫法
description: "stat -f / sed -i '' / dd bs=1m / 直接呼叫 docker：四種都在 macOS 通過、在 Linux 靜默失敗或變成假缺陷；三種的錯誤訊息會去到被重導掉的 stderr。"
tags: [portability, macos, linux, bash, false-success, ci]
source:
  - agent: claude
    path: ~/ENV/Devops/docs/Backlog.md
    locator: "§24 ADR-0008 訂了三天，沒有人檢查另一邊"
    digest: sha256:049967bebe4374ac26281bf9277287eeb74d6427bf91b85373dd0e0f894f222f
    note: "digest 於 2026-09-08 重釘：§24 被加入 ubu 休眠／闔蓋的實測（與本記錄無關），本記錄的主張逐條複查後不變。2026-09-03/04 第二台機器（Ubuntu amd64）開機當天實測找到；CI 曾因此連紅四次"
status: stable
inject: auto
timestamp: '2026-09-04T00:00:00+08:00'
---

# BSD／GNU 的四個陷阱

**適用範圍**：任何在 macOS 開發、在 Linux（CI／容器／伺服器）執行的 shell 程式碼。
與專案無關。

## 四種寫法

| 寫法 | macOS | Linux（GNU） | 為什麼會被漏掉 |
|---|---|---|---|
| `stat -f '%z'` | 可 | **不存在** | 錯誤訊息明顯，最容易被發現的一個 |
| `sed -i '' 's/a/b/' f` | 可 | **把 `''` 當腳本、把腳本當檔名** | `sed: can't read s/a/b/`，而測試常把 stderr 重導掉 |
| `dd bs=1m` | 可 | **`invalid number '1m'`**，檔案不會被建立 | 同上；呼叫端看到的是空檔案不是錯誤 |
| 直接呼叫 `docker` | 通常可 | 常常不存在 | 未捕捉的 `FileNotFoundError` 讓「這裡沒有 docker」變成「這個檢查壞了」 |

## 可攜寫法

```bash
stat -c %s "$f" 2>/dev/null || stat -f %z "$f" 2>/dev/null   # GNU 先試
sed --version >/dev/null 2>&1 && sed -i -e "$s" "$f" || sed -i '' -e "$s" "$f"
dd bs=1024k   # 或 1M；小寫 m 只有 BSD 接受
try: subprocess.run(["docker", ...])
except FileNotFoundError: return None    # 「這裡沒有」不是缺陷
```

## 真正的教訓不是這四條

**這四條的共同點是：錯誤訊息去了一個沒有人在看的 stderr，
於是呼叫端看到的是「什麼都沒發生」而不是「失敗了」。**

在 `sed -i ''` 那個案例裡，突變測試的每一次編輯都靜默地什麼都沒改，
輸出卻寫「mutant survived」——**那是一句關於受測程式的宣稱，
實際上是一句關於測試本身的宣稱**。兩者在輸出上分不出來。

所以：**做就地編輯或寫檔的動作，要驗證它真的發生了**（比對 checksum、
檢查檔案大小），不要只看指令的回傳碼——尤其在錯誤輸出被丟棄的地方。

## 制度性的修法

不要靠記憶。這四條都應該變成**靜態規則 ＋ 一個能紅的合成控制**：
一個必須被抓的 fixture、一個必須不被抓的 fixture。
`shellcheck` 的 SC2xxx 認得其中多數，是最省力的入口。
