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
- SL 敏感度分析完成，**確認 SL=120pts 為新基準（原 30pts 過緊）**
- SL=120, TP=240（R:R 2:1）：E09/E07/E12 均 WR>50%、PF>2.0
  - E07 RSI 50 Crossover: WR=52.1%, PF=2.041
  - E09 EMA55 Pullback:   WR=50.8%, PF=1.801
  - E12 BB Squeeze Break: WR=51.8%, PF=2.002
- 空單全虧（此期間大多頭，屬預期結果）
- 宏觀分析：月勝率 63.9%，九月唯一偏空月，四月期望值最大（+518pts avg）
- 下一步：NQ 相關性過濾 + MTF 4H 過濾；在 TradingView 驗證 E07/E09/E12

## 筆記驗證結果（2026-05-13，validate_notes.py）
結果存於 `doc/validation_results.json`；index.html 各商品均有「筆記驗證」頁。

### XAUUSD（黃金秘笈 vs 日線 2014–2026）
- 符合：一月✅強、七月✅強、九月✅弱、十月✅強、十一月✅弱、十二月✅強（6/12）
- **不符重要差異**：四月(筆記弱/資料WR=77%強)、五月(筆記弱/資料WR=58%強)、六月(筆記強/資料WR=42%弱)
- 時段：早上9-10趨勢K=60%（筆記說90%震盪 → 資料偏離），下午14-15趨勢K=46%（較一致）
- 結論：約半數月份筆記方向正確；六月/四月/五月需重新評估

### TX（指數密技 vs 日線 2012–2026）
- 符合：一月✅強、四月✅強、十一月✅強、十二月✅強（4/12）
- **主要問題**：五月筆記說弱但資料WR=71%強；整體台指期資料顯示多數月份都偏強（牛市期）
- Q4 avg_ret=1.7%，WR=64%，支持「Q4必有多單機會」結論
- 選舉年效應存在，選舉年Q1勝率高於非選舉年
- 結論：TX多個月份資料都WR>65%，可能受2012-2026大多頭期偏差影響；五月弱的結論需更長週期驗證

## 新增商品流程
1. 建立 `trading/<商品>/` 子目錄
2. 在 `generate_index.py` 的 `COMMODITIES` 清單新增一筆
3. 視需要新增對應的 HTML 生成函式
4. 執行 `python generate_index.py` 更新 index.html
