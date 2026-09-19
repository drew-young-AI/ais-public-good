---
name: telegram-bot
type: skill
description: "安全且專屬地處理 codex6520_bot 的 Telegram 訊息與截圖發送。"
version: 1.0.0
---

# telegram-bot Skill

此 Skill 用於安全、專屬地處理 `codex6520_bot` 的 Telegram 訊息與截圖發送。

## 原則
1. **唯一性**：僅處理 `codex6520_bot`，嚴禁混用其他機器人。
2. **安全性**：Token 從 `~/.codex/.env` 安全讀取，不存放在臨時腳本中。
3. **身份驗證**：每次呼叫前，強制執行 `getMe` 握手驗證，確保目標為 `codex6520_bot`。

## 呼叫方式
- "使用 telegram bot 送出 [訊息]"
- "使用 telegram bot 發送截圖 [檔案路徑]"

## 執行流程
1. 讀取配置 (`~/.codex/.env`)。
2. 執行 `getMe` 驗證機器人身份 (若發現 API 異常或驗證失敗，應記錄並回報，而非崩潰)。
3. 若身份確認無誤，執行訊息/圖片發送。

## 排錯與注意事項
- **401 Unauthorized**：Token 已過期或無效，請前往 @BotFather 重新產生並更新 `~/.codex/.env`。
- **SSL 警告**：若出現 `NotOpenSSLWarning`，為環境依賴問題，不影響功能發送。
- **驗證機制**：永遠優先執行身份 handshake，若 API 連線失敗，請檢查網路環境與 Token 有效性。
