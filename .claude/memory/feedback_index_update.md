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
