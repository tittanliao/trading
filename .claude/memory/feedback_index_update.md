---
name: feedback-index-update
description: 網站更新流程（20260711 拆頁後）：手寫改 content/、記錄改 data/logs.json、重跑 generate_site.py，生成頁禁止手改
metadata:
  type: feedback
---

## 網站架構（20260711 拆頁重構後）
網站拆成 6 頁（index/xauusd/tx/shared/history/sitemap.html），全部由根目錄
`generate_site.py` 生成。**生成的 6 個 .html 一律禁止手改**（頁首有 DO NOT EDIT banner）。

**Why:** 20260710 曾因舊 generate_index.py 與手改過的 index.html 脫節，整份重新生成時
誤刪 2000+ 行內容。20260711 重構後手寫內容全部隔離到 content/ fragment，
生成器可以安全地隨時重跑，此問題已根治。舊 generate_index.py 已刪除（git 歷史保留）。

**How to apply:**
- 手寫內容（策略說明、H2 複盤、正二、sitemap）→ 改 `content/` 下對應 fragment
- 對話記錄 → append `data/logs.json`（「共 N 筆」自動計算，永遠不用手動 +1）
- 動態數據 → 改對應 data 檔（results.json 等）
- 改完重跑 `python3.12 generate_site.py`（可 `--page xxx` 只生成單頁）
- commit 前 `git diff --stat` 檢查：大量非預期刪除 → 停下來查
- 完整規則與四種任務 checklist 見根目錄 `DEVELOPMENT.md`（每次動網站前先讀）

## 每次新增功能後必須同步（沿用舊規則，不需用戶提醒）
1. `data/logs.json` append 一筆對話記錄
2. `content/sitemap.html` 登記新頁面/報告連結
3. 重跑 generate_site.py，一起 commit
