---
name: feedback-index-update
description: 每次更新 index.html 新增功能後，必須同步更新網站地圖與對話記錄，不需用戶提醒
metadata:
  type: feedback
---

每次在 index.html 新增任何分頁、分析報告、或功能區塊後，必須自動同步更新：
1. **網站地圖**（網站地圖 nav → 對應商品的分類條目）
2. **對話記錄**（對話記錄 nav → 新增最新一筆，總計數 +1）

**Why:** 用戶每次都要額外提醒，很累。這是 index.html 維護的標準作業程序，不是選項。

**How to apply:** 完成 HTML 功能更新後，在 commit 之前先找到網站地圖與對話記錄區塊，插入對應條目，一起 commit。

## ⚠️ 20260710 事故記錄：generate_index.py 與 index.html 已經不同步，禁止整份重新生成
`generate_index.py` 缺少「宏觀指標解讀」「Macro 回測」「週報分析」「2026 H1/H2」等區塊
（這些是先前某次直接手改 `index.html` 加進去的，從未同步回 `generate_index.py`）。
20260710 曾經直接跑 `python generate_index.py` 想加一筆對話記錄，結果整份重新生成
把上述區塊全部砍掉（誤刪 2000+ 行），事後用 `git show <上一個commit>:index.html`
復原並改用手動編輯插入新記錄才修復。

**How to apply（重要）**：在 `generate_index.py` 補齊所有缺失的區塊、並確認
`git diff` 只有預期的新增（不是大量刪除）之前，**禁止執行 `python generate_index.py`
整份重新生成 index.html**。需要新增內容時，改用手動編輯 `index.html`（找到對應區塊直接插入
新的 `<div class='log-entry'>...`，格式參照既有條目），跟改 `generate_index.py` 的
`XAUUSD_LOG` 源碼（保留給未來真正修復同步問題時使用）分開處理。
每次要動 index.html 前，先用 `git diff --stat index.html` 確認變動幅度是否合理，
出現大量非預期刪除要立刻停下來，不要繼續 commit。
