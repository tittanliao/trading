---
name: feedback-preferences
description: 用戶對工作方式的偏好與回饋
metadata:
  type: feedback
---

## 繁體中文溝通
**Why:** 用戶慣用繁體中文。
**How to apply:** 所有回覆和說明預設用繁體中文。

## 記憶存放在專案 .claude/memory/ 資料夾（git 追蹤）
**Why:** 用戶希望記憶跟著 git 走，不同電腦 git clone/pull 後就有一樣的記憶。
**How to apply:** 記憶檔寫在 `trading/.claude/memory/`。新電腦需執行 CLAUDE.md 內的 symlink 指令。

## 架構最小差異原則
**Why:** 用戶已熟悉 xauusd 框架，希望新商品（tx、未來商品）用相同邏輯方便切換。
**How to apply:** 模組命名、函式簽名、報告格式盡量與 xauusd 一致；差異點在各商品 CLAUDE.md 明確標示。

## 分析 → Pine Script → TradingView 驗證的工作流程
**Why:** 用戶的最終目標是在 TradingView 上跑策略，Python 分析只是前期篩選。
**How to apply:** 每次分析完找到 insight，優先提供可在 TradingView 測試的 Pine Script 版本。

## generate_index.py 是 index.html 的唯一來源
**Why:** index.html 有動態部分（實驗結果），直接手改 HTML 不如改 generate_index.py 後重跑。
**How to apply:** 需更新 index.html 的靜態文字（策略備忘、對話記錄）時，改 generate_index.py 的對應字串再執行。
