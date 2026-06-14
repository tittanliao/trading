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

## 週報 CSV 放在 Google Drive，非 trading/xauusd/csv/
**Why:** 用戶的週報分析用 CSV 存放在 Google Drive，與日常分析 CSV 分開管理。
**How to apply:**
- 週報生成時優先讀：`~/googledrive/XAUUSD/weekly report/csv/`
- 若 Google Drive 未掛載到 session，請用戶手動複製到 `trading/xauusd/csv/` 或連接該資料夾
- 備用路徑（舊版）：`trading/xauusd/csv/`（可能過時）

## 週報生成流程（確立於 2026-06-13 W24）
**Why:** 完整跑過一次 W24 週報後，確立正確的 SOP，避免下次重複找路徑。
**How to apply:**
1. 先呼叫 `mcp__cowork__request_cowork_directory(path="~/googledrive/XAUUSD/weekly report/csv")`
2. 掛載後 bash 路徑為 `/sessions/.../mnt/csv/`，Read 工具用 `~/googledrive/XAUUSD/weekly report/csv/`
3. 用 Python 讀取 CSV → 計算 BB/RSI/EMA/ATR → 生成分析數據
4. 抓 CFTC：`https://www.tradingster.com/cot/futures/disagg/088691`
5. 輸出週報存至 `trading/xauusd/daily_log/weekly_report_W{週次}_{日期}.txt`
6. 完成後提醒用戶 git add + commit + push

## 合併週報（三交易員 Combine）觸發詞與 SOP
**Why:** 用戶說「合併週報」時，需比對 Claude/Gemini/Dispatch 三份週報，產出 3 種 Style 的 Combine .docx。
**How to apply:**
- 觸發詞：「合併週報」
- 三份週報路徑：
  - Claude：`~/googledrive/XAUUSD/claude/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx`
  - Gemini：`~/googledrive/XAUUSD/weekly report/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}.txt`
  - Dispatch：`~/program/github/trading/xauusd/daily_log/weekly_report_W{週次}_{YYYYMMDD}.txt`
- 三份差距 < 7 天才合併，否則提示用戶等齊
- 輸出：3 個 .docx → `~/googledrive/XAUUSD/claude/XAUUSD_W{N}_Combine_Style{A/B/C}.docx`
- 詳細格式見 ANALYSIS_SKILL.md「合併週報流程」章節
- 提示詞位置：Google Doc 1gKMZbIKcKTT3BWk2r0_BQQrWBfTEPyGps0qQzfhYj8w（需瀏覽器開啟）

7. 合併週報前必須先生成 Claude 當週報告（W24 教訓：用了 W23 Wed 舊報告當交易員 A，所有價位過時）
   流程：先生成 Claude W{N} .docx → 再讀取 Gemini .gdoc + Dispatch .txt → 才能執行合併
   
8. Gemini 週報格式是 .gdoc（非 .txt），需用 Chrome MCP + JS fetch export?format=txt 讀取
   路徑：~/googledrive/XAUUSD/weekly report/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}.gdoc

9. 週報 CFTC 數據必須主動抓最新截圖（W24 教訓：直接複製 Dispatch 報告的 6/2 數據，漏抓 6/9 版本）
   正確步驟：ls ~/googledrive/XAUUSD/weekly\ report/cftc/ → 找最新 .png → Read 讀取圖片 → 提取數字
   CFTC 每週五公布（前一週二截止），週報日期是週六/日時應有當週最新數據
