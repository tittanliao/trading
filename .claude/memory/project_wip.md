---
name: project-wip
description: 進行中工作狀態（20260711 晚間，第四次更新）：S2-Hammer V3.2逐筆OOS已驗證——真實改善但未解決，非緊急持續觀察
metadata:
  type: project
---

# 進行中工作（20260711 晚間狀態）

## 🟡 S2-Hammer OOS 問題現況：V3.2 有改善但未解決，非阻塞性持續觀察
最新結論（詳見 `report_v32_oos.html` 與 ANALYSIS_SKILL.md「V3.2 逐筆 OOS 驗證結論」）：
- V1.9 原始邏輯 OOS（後30%）WR 27.9%/PF 0.92，低於損益兩平——最早發現的問題
- V3.2（HTF RSI + S2-RSI互斥過濾器）驗證後：自己的 OOS 是 WR 33.3%/PF 1.35（勝率落差-19.9pp仍超標，
  未通過）；在 V1.9-OOS 相同日曆區間（2026-01-22後）WR 30.8%/PF 1.23（比V1.9同期間好，但仍脆弱）
- **結論：真實改善，但不是「解決」**。IS→OOS 勝率大幅衰退的模式在兩版都存在，暗示問題可能不只是
  合流訊號需要過濾，錘頭型態本身在近期市場結構下的辨識力可能也在減弱
- **不建議急著升版確認**。下一步方向（優先度皆不高，可視使用者意願推進）：
  1. 疊加提早保本規則（V3.2 目前未開）看能否進一步救回
  2. 持續累積更多近期交易，觀察 V3.2 是否隨時間推移穩定在改善水準
  3. 重新檢視錘頭型態定義本身是否需要調整（更根本的方向）

## S1-AweWithBB 現況：V3.9 初步雙重驗證正向，未完整驗證
- V3.9（BB Source close→ohlc4）在 TradingView 全樣本（xlsx記錄）與 Python 共同期間分析兩邊
  都顯示優於 V3.7（PF 1.743→1.869~1.888），方向一致，互相印證
- TP2=3.5R 優於 TP2=2R 已在 v3.4/v3.7/v3.8.1/v3.9 四代穩定驗證，視為定論不需再測
- 逐筆 CSV 已有（`S1-Awe-V3.9_FX_IDC_XAUUSD_2026-07-11.csv`，已用於`report_v3.9_real.html`），
  但尚未做像 S2-Hammer 那樣的 70/30 OOS 切分驗證——non-blocking，優先度低，有空可補做
- 現行確認版仍是 V3.7，V3.9 待驗證後再決定是否升版

## 已建立的分析工具（可重用的方法論腳本）
- `run_s1_v37_real_attribution.py`：兩版真實逐筆對比（V3.4 vs V3.7 模式）
- `run_s1_v39_real_attribution.py`：同上，V3.7 vs V3.9（共同期間對照）
- `run_s2_attribution.py`：S2-RSI/S2-Hammer 歸因 + OOS 70/30 + 濾網重疊 + time_bleed 解剖
- `run_s2_hammer_v32_oos.py`：雙重OOS驗證（自己的70/30切分 + 相同日曆區間直接對照），
  這個「相同日曆區間對照」手法比單純各自切分更嚴謹，之後其他版本比較可以沿用這個模式

## 等待使用者提供（TradingView 匯出，CSV 放對應策略資料夾，皆非緊急）
1. S2-Hammer V2.4.1 的 2×2 對照（4 份 CSV，檔名帶 A/B/C/D）：
   - A=互斥OFF/保本OFF（≈V2.3基準）、B=互斥ON、C=保本ON、D=全ON
   - 放 `xauusd/XAUUSD-Long-S2-Hammer/`
2. S1 V3.8.1：BBW高檔回看20 一份、BBW低檔ON+回看90 一份
3. S1 ABCD 診斷（V3.7-ABCD-Diagnostic.pine）四種組合各一份
   - ⚠️ 此 pine 寫於語法修復之前，可能有 V2.3 同款壞語法（行接續/plotshape參數順序），使用者回報編譯錯誤就照 V2.4.1 的修法處理
4. S2-RSI V2.0 基準版重匯到最新日期（S2-Hammer 已完成，S2-RSI 尚未）
5. xlsx row 8（S2-Hammer TP1/TP2=1R/2R 高勝率版）的逐筆CSV，看是否在OOS段更穩定（加分項）

## 價格 CSV 基礎設施（20260711 已完成，記錄備查）
- 30/60/240/1D/1W × XAUUSD+DXY 重匯到 2026-07-11，舊版存 `csv/20260705/`，新版 `csv/20260711/`，
  `analysis/config.py` 的 `CSV_DIR` 已指向新資料夾
- ⚠️ 新匯出是純 OHLC（無 RSI/RSI-based MA/背離欄位）。已在 `loader.py` 加自動 fallback：
  缺欄位時用 close 本地計算 Wilder RSI(14)+SMA(14)（公式取自 `XAUUSD-Macro-v3.7.pine`），
  永久性修復，之後匯出新CSV不用特別注意這件事
- ⚠️ **尚未修復**：`scripts/macro_analysis.py`、`run_macro_backtest.py`、
  `run_real_strategy_macro_backtest.py`、`analyze_h1_regime.py`、`run_fvg_experiments.py`
  這幾支腳本各自寫死 `xauusd/csv/`（不走 config.py），舊檔案已被搬走，**目前會
  FileNotFoundError**。非本輪常跑清單，之後要跑要記得先改路徑（部分還讀取 GVZ/VIX/T10Y，
  這些檔案沒被搬動，改路徑前要逐一確認別break）

## 重要背景（詳見 data/logs.json 20260710-11 條目）
- S2 優化主線：合流分析→歸因→V2.4.1（互斥過濾器+提早保本，已修完語法可編譯）→V3.2（功能對等，
  已做完OOS驗證，見上方）
- ⚠️ repo 內 V2.2/V2.3 系 pine 是被壓扁的壞源碼（逗號if/壓扁縮排/plotshape參數順序錯），
  以 repo pine 為基礎開發前先確認能編譯；V2.4.1 與 S2-RSI V2.4 已修復
- 網站已拆頁重構（DEVELOPMENT.md 為開發規範）；策略更名 S2-RSI / S2-Hammer
- TradingView 訂閱決策：留 Premium 90 天觀察期，footprint 實驗（request.footprint()
  Premium限定）排在 S2/S1 驗證之後
