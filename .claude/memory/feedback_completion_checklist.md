---
name: feedback-completion-checklist
description: 每次完成任務前必須達到的標準清單，缺一不可才能 commit and push
metadata:
  type: feedback
---

每次完成任何分析或功能任務，必須按順序完成以下所有步驟，才能 commit and push：

1. **更新 index.html** — 執行 `python generate_index.py` 重新生成，確認新分析有出現在網頁
2. **更新網站地圖（sitemap）** — index.html 內的 sitemap 區塊也要反映新增的頁面/分析
3. **更新 Claude 記憶相關檔案** — `.claude/memory/` 底下的 MEMORY.md 和相關 md 檔要記錄新的分析成果
4. **跨商品共同分析放同一個 sheet** — 黃金和台指都有的分析（e.g., 整點熱力圖、RSI 過濾），要放在同一個頁籤/區塊，方便跨商品比較，不要分開放
5. **驗證需求達成** — 實際跑腳本確認輸出正確，瀏覽 HTML 確認顯示正常
6. **最後才 commit and push**

**Why:** 用戶不想每次都重複叮嚀這些步驟，要內化成標準流程。
**How to apply:** 每次任務結束前，逐一確認這 6 點都完成了再說「完成」。
