---
id: agent-skills-open-standard
type: reference
title: Agent Skills 是開放標準，不合規等於不存在
description: "SKILL.md 需 name/description/version、小寫連字號、name 與目錄名一致；description 是檢索鍵不是說明文；分隔線帶尾隨空白會讓 skill 對所有標準客戶端隱形。"
tags: [skills, standards, interoperability, ais, capabilities]
source:
  - path: ${AIS_ROOT}/docs/research-2026-08-29-agent-memory-and-skills.md
    digest: sha256:4f3622f9fcfdbede98a50f490bafd2920567465dd8da83a56119d9a84d96e2e6
status: stable
inject: auto
timestamp: '2026-08-29T10:30:00+08:00'
---

# Agent Skills 標準

- Agent Skills 由 Anthropic 於 2025 年底釋出為**開放標準**，已被 40+ 客戶端採用（Claude Code、Codex、Cursor、Copilot、VS Code、Gemini CLI、Goose、Databricks、Snowflake）。它不是某一家的私有格式。
- 結構：`skills/<skill-name>/SKILL.md` 為必要進入點；附帶 scripts / templates / examples 放在兄弟目錄。frontmatter 欄位為 `name`、`description`、`version`。
- 命名一律小寫連字號式，且 `name` 應與目錄名一致——不一致時各家客戶端的定位行為分歧。
- **`description` 是檢索鍵，不是說明文字。** 客戶端先用它與當下 context 比對，才決定要不要載入完整內文（漸進式揭露）。寫得含糊 → 永遠不會被選中 → 這個 skill 實質不存在，而且不會有任何錯誤訊息。
- **不合規不是品質差一點，是對所有標準客戶端不存在。** 實測：frontmatter 分隔線寫成 `--- `（尾隨一個空白）時，內容完全正確、`yaml.safe_load` 也讀得過，但嚴格的 frontmatter 解析器讀不到，該 skill 對外隱形。一個空白字元讓資產從共用層消失。
- 檢查工具：`capabilities/scripts/skills-audit`（registry verify：`skills-audit --selftest`），已列入 `ais gate`。
- 公開 registry（skills.sh / ClawHub / SkillsDirectory / LobeHub）缺的是「這個 skill 還活著嗎、它真的做它宣稱的事嗎」的機制；arXiv 已有針對 skill registry 的供應鏈攻擊與生命週期治理研究。**消費外部 skill 前必須自行驗證**，不可因為它在 registry 上就當作可信。
