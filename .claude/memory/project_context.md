---
name: project-context
description: trading hub 多商品策略分析工具箱的目標、架構、各商品現況
metadata:
  type: project
---

## 專案目標
統一管理多個商品的量化策略分析：XAUUSD 黃金 + TX 台指期，後續可擴展至更多商品。
前身是兩個獨立的 git 專案（xauusd / tx），於 2026-05-13 整併為 trading。

**Why:** 兩個專案架構相似，統一管理可共享記憶、方便跨商品比較、新增商品只需加一個子目錄。
**How to apply:** 商品代碼分別在 `xauusd/` 和 `tx/` 子目錄；master index.html 在根目錄。

## 目錄規則
- `trading/` — 根目錄，含 index.html + generate_index.py + CLAUDE.md
- `trading/xauusd/` — XAUUSD 所有程式碼和資料
- `trading/tx/` — TX 所有程式碼和資料
- `trading/.claude/memory/` — **git 追蹤的記憶**，新電腦 clone 後需執行 symlink（見 CLAUDE.md）

## XAUUSD 現況（2026-05-02）
- 三個已開發策略（S1-AweWithBB / S2A-RSI / S2B-Hammer），均在測試新版本
- S1 V3.6.2：修正 lookahead 重繪 + BB %B 過濾 + 4H HTF 過濾
- S2A V2.3 / S2B V2.2：時間止損修正（strategy.close()）+ 4H HTF 過濾
- 20 多單實驗：E03 MACD Signal 最佳（PF 1.643, +9.0%）
- 20 空單實驗：S19 Bearish Engulf 最佳（PF 1.507, +12.4%）
- 關鍵發現：DXY RSI < 30 → 三策略勝率 60–75%；HTF alignment=3/3 → S1 WR ~69%

## TX 現況（2026-05-13）
- 第一版回測引擎完成，20 多單 + 20 空單
- 多單 E12 BB Squeeze Break 唯一獲利（PF=1.132, WR=36.1%）
- 空單全虧（此期間大多頭，屬預期結果）
- 宏觀分析：月勝率 63.9%，九月唯一偏空月，四月期望值最大（+518pts avg）
- 下一步：NQ 相關性過濾 + MTF 4H 過濾 + 分析 SL 30pts 是否過緊

## 新增商品流程
1. 建立 `trading/<商品>/` 子目錄
2. 在 `generate_index.py` 的 `COMMODITIES` 清單新增一筆
3. 視需要新增對應的 HTML 生成函式
4. 執行 `python generate_index.py` 更新 index.html
