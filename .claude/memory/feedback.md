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

## 每次「請分析」必須讀取週報（不得跳過）
**Why:** 曾多次跳過週報導致大格局背景缺失。即使部分關鍵位過期，仍有劇本、CFTC、DXY 等有效資訊。
**How to apply:** 讀最新 weekly_report_*.txt → 判斷有效性 → 若 80% 以上支撐位失效則停止並要求用戶重新下載 CSV。每次分析輸出必須含「📰 週報背景」段落。

## 需要記憶時先詢問用戶
**Why:** 用戶希望控制哪些內容進入 skill 或記憶，避免不必要的記錄。
**How to apply:** 判斷有值得長期保留的內容時，先問「要把 [xxx] 記到 [路徑] 嗎？」等確認後再寫入。

## 任何 trading repo 檔案修改後，都必須提醒 git commit+push
**Why:** 用戶明確要求「只要有紀錄的動作，一併更新到 git」，避免 skill/memory/daily_log 改動丟失。
**How to apply:** 凡是修改了 trading repo 內任何檔案（skill/、.claude/memory/、xauusd/、tx/ 等），完成後提醒用戶執行：
```bash
cd ~/program/github/trading && git add -A && git commit -m "update: [描述]" && git push
```
