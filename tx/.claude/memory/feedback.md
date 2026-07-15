---
name: feedback-preferences
description: 用戶對工作方式的偏好與回饋
metadata:
  type: feedback
---

## 繁體中文溝通
**Why:** 用戶慣用繁體中文。
**How to apply:** 所有回覆和說明預設用繁體中文。

## 記憶存放在專案 .claude/memory/ 資料夾
**Why:** 用戶希望記憶跟著 git 走，不同電腦 git pull 後就有一樣的記憶（xauusd 已驗證此流程有效）。
**How to apply:** 記憶檔寫在 `tx/.claude/memory/`。新電腦需執行 CLAUDE.md 內的 symlink 指令。

## 架構對應 xauusd，差異最小化
**Why:** 用戶已熟悉 xauusd 框架，希望 tx 用相同邏輯方便切換。
**How to apply:** 模組命名、函式簽名、報告格式盡量與 xauusd 一致；差異點（NQ vs DXY、點數制 SL/TP、session 分析）在 CLAUDE.md 明確標示。
