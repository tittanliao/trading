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

## XAUUSD 現況（2026-06-14）
- 三個已開發策略（S1-AweWithBB / S2A-RSI / S2B-Hammer），均在測試新版本
- S1 V3.6.2：修正 lookahead 重繪 + BB %B 過濾 + 4H HTF 過濾
- S2A V2.3 / S2B V2.2：時間止損修正（strategy.close()）+ 4H HTF 過濾
- 20 多單實驗：E03 MACD Signal 最佳（PF 1.643, +9.0%）
- 20 空單實驗：S19 Bearish Engulf 最佳（PF 1.507, +12.4%）
- 關鍵發現：DXY RSI < 30 → 三策略勝率 60–75%；HTF alignment=3/3 → S1 WR ~69%

## SMC 回測實驗（2026-06-14 新增）
- 新增 SMC 回測引擎：`smc_indicators.py` / `strategies_smc.py` / `run_smc_experiments.py`
- 資料期：2026-01-21 → 04-27（3058 × 30m bars）
- **核心結論：SMC 不替換 S1/S2，只作為週報輔助參考與 S2 進場分級依據**

### SMC 回測關鍵結果
- 最強空單：M12 Bearish FVG + RSI 35-70（WR 43.0%、PF 1.470、158 筆）★ 統計最可信
- 最高品質空單：M17 BSL sweep + FVG（WR 50.0%、PF 2.000，但僅 20 筆）
- 最強多單：M09 FVG + OB（WR 34.0%、PF 1.045、100 筆）— 勉強轉正
- 多單偏弱原因：SL 0.5% 太緊，FVG 自然 SL 應為 0.8-1.0%

### SMC 整合到週報的方式
- ANALYSIS_SKILL.md 新增 Module B+（SMC Context）和週報第 6 項輸出格式
- 週報 Python 模板加入自包含 SMC 掃描程式碼（scan_fvg / scan_liquidity / check_ssl_sweep）
- S2 進場品質分級更新：A+（錘頭+SSL sweep+OB）/ A（錘頭+任一SMC）/ B（純錘頭）
- 對應倉位：A+ 0.05手 / A 0.03手 / B 0.02手

### 週報分析體系（2026-06-14 確立）
- **三個來源**：Gemini 週報（基本面）/ Dispatch txt（技術面）/ Claude 週報（技術面）
- **分工原則**：Gemini 主攻宏觀/基本面；Claude/Dispatch 主攻技術分析
- **合併週報**：三份差距 < 7 天才合併，輸出 Style A/B/C 三份 .docx
- 用戶已使用 Gemini 寫週報 6 個月，後續可與 Claude 週報做回測比較

## TX 現況（2026-05-13）
- SL 敏感度分析完成，**確認 SL=120pts 為新基準（原 30pts 過緊）**
- SL=120, TP=240（R:R 2:1）：E09/E07/E12 均 WR>50%、PF>2.0
  - E07 RSI 50 Crossover: WR=52.1%, PF=2.041
  - E09 EMA55 Pullback:   WR=50.8%, PF=1.801
  - E12 BB Squeeze Break: WR=51.8%, PF=2.002
- 空單全虧（此期間大多頭，屬預期結果）
- 宏觀分析：月勝率 63.9%，九月唯一偏空月，四月期望值最大（+518pts avg）
- 下一步：NQ 相關性過濾 + MTF 4H 過濾；在 TradingView 驗證 E07/E09/E12

## 對話記錄架構（2026-05-15）
- **統一對話記錄**：所有 XAUUSD / TX / 跨商品 的 log 集中在「📋 對話記錄」Top-Level Tab
- Log 資料結構：`XAUUSD_LOG` / `TX_LOG` / `CROSS_LOG`（在 generate_index.py）
- 每筆 entry 有商品 tag（🟡 XAUUSD / 🔵 TX / 📊 跨商品），按日期降序顯示
- 個別商品的「對話記錄」子 tab 已移除，不再有重複內容
- 新增對話記錄時：在對應 LOG 清單加一個 dict（date, title, items）即可，重跑 generate_index.py 生效

## 跨商品共同分析（2026-05-15）
- 新增 `shared/run_shared_analysis.py`，對 XAUUSD + TX 共同執行：
  1. **整點熱力圖**：每整點進場 → 下一整點出場，計算星期×小時的勝率和損益
  2. **30m RSI 濾鏡**：在整點進場時，30m RSI 金叉/死叉/位置對勝率的影響
- TX 關鍵發現：
  - 最佳時段：週二 23:00 WR=73.7%, avg +40.9pts（夜盤）
  - 最差時段：週四 08:00 WR=33.3%, avg -89.5pts（日盤開盤前）
  - RSI<MA 時略優（WR 53.7%, avg+8.0pts）vs RSI>MA（WR 53.1%, avg+1.8pts）
- XAUUSD 關鍵發現：
  - 最佳時段：週三 06:00 WR=88.9%（n=9，小樣本）
  - 最差時段：週一 06:00 WR=10.0%（n=10）
- 背離訊號（Regular Bullish/Bearish）CSV 欄位目前無資料，需重新從 TV 匯出
- 結果存於 `shared/shared_results.json`（含 base64 heatmap 圖）
- index.html 新增「📊 跨商品分析」Nav Tab（整點熱力圖 + RSI 濾鏡）

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
