---
name: feedback-completion-checklist
description: 每次完成任務前必須達到的標準清單，缺一不可才能 commit and push
metadata:
  type: feedback
---

每次完成任何分析或功能任務，必須按順序完成以下所有步驟，才能 commit and push：

1. **更新 index.html** — 執行 `python generate_index.py` 重新生成，確認新分析有出現在網頁
2. **更新網站地圖（sitemap）** — index.html 內的 sitemap 區塊也要反映新增的頁面/分析
3. **更新 Claude 記憶相關檔案** — `.claude/memory/` 底下的 MEMORY.md 和相關 md 檔要記錄新的分析成果（**必做**，用戶每次都要求多記錄）
4. **跨商品共同分析放同一個 sheet** — 黃金和台指都有的分析（e.g., 整點熱力圖、RSI 過濾），要放在同一個頁籤/區塊，方便跨商品比較，不要分開放
5. **更新對話記錄** — 在 CROSS_LOG / TX_LOG / XAUUSD_LOG 加入本次對話的重點，帶 tag 出現在「📋 對話記錄」頁
6. **驗證需求達成** — 實際跑腳本確認輸出正確，瀏覽 HTML 確認顯示正常
7. **最後才 commit and push**

**強化記憶要求（2026-05-15 新增）：**
- 每次對話開始，主動讀取 `.claude/memory/` 內的 project_context.md 掌握現況
- 每次對話結束，無論任務大小，都要在 project_context.md 記錄這次做了什麼、發現什麼
- 新的重要決策或發現，單獨建立 memory 檔案（不要全塞進 project_context）
- 對話記錄（CROSS_LOG / TX_LOG / XAUUSD_LOG）也是 memory 的一部分，每次要新增一筆

**Why:** 用戶不想每次都重複叮嚀這些步驟，要內化成標準流程。記憶是跨電腦協作的基礎。
**How to apply:** 每次任務結束前，逐一確認這 7 點都完成了再說「完成」。
