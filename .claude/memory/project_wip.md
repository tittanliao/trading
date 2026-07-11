---
name: project-wip
description: 進行中工作狀態（20260711 晚間更新）：S2-Hammer OOS未過為最高優先，等待更多TV匯出CSV
metadata:
  type: project
---

# 進行中工作（20260711 晚間狀態，第二次更新）

## 本輪已完成（20260711 晚間）
- ✅ S2-Hammer V1.9 基準版重匯到 2026-07-11（200→225筆），`run_s2_attribution.py` 用新 CSV
  重跑，**發現 OOS 未通過**（後30%WR 27.9%/PF 0.92）——見下方「新的最高優先」
- ✅ S1 V3.9（測試版：Filter編號化＋BB Source改ohlc4＋持倉中提示等 UI 改動）真實回測 CSV
  已匯入，新增 `run_s1_v39_real_attribution.py` 對照 V3.7（共同期間內 V3.9 全面小幅優於 V3.7）
- ✅ 兩份報告與 xauusd.html / sitemap.html / ANALYSIS_SKILL.md 已同步更新
- ✅ **價格 CSV 重匯到 20260711**（30/60/240/1D/1W × XAUUSD+DXY），舊版移到 `csv/20260705/`，
  新版放 `csv/20260711/`；`analysis/config.py` 的 `CSV_DIR` 已指向新資料夾
  - ⚠️ **重要發現**：新匯出是純 OHLC，**沒有 RSI/RSI-based MA/背離欄位**（舊版有）。
    已在 `loader.py` 加上自動 fallback：偵測到缺欄位時本地計算 Wilder RSI(14)+SMA(14)
    （公式取自 `XAUUSD-Macro-v3.7.pine` 的指標定義），下次「請分析」或匯出新CSV前不用特別注意，
    這是永久性修復——但若之後想要更精確的背離訊號，仍建議請 TradingView 匯出時帶上 RSI 指標疊加
  - main.py 全策略 + run_s2_attribution.py 已用新資料重跑，K-bar/MTF/DXY 覆蓋率從 April 27
    延伸到 July 11（S2-Hammer K-bar coverage 19%→52%、60m MTF 覆蓋率大幅提升），
    OOS/勝率/PF等頭條數字不受影響（交易CSV本身沒變，只是進場前情境補完整）
  - ⚠️ **尚未修復**：`scripts/macro_analysis.py`、`run_macro_backtest.py`、
    `run_real_strategy_macro_backtest.py`、`analyze_h1_regime.py`、`run_fvg_experiments.py`
    這幾支腳本各自寫死 `xauusd/csv/`（不走 config.py），舊檔案已被搬走，**目前會
    FileNotFoundError**。這幾支不在本輪常跑清單內所以沒動，若之後要跑要記得先改路徑
    （部分還讀取 GVZ/VIX/T10Y，這些檔案沒被搬動，改路徑前要逐一確認別break）

## 🔴 新的最高優先：S2-Hammer OOS 失敗待處理
V1.9 原始邏輯（未開任何 V2.x 過濾器）在新樣本外資料（近 2.5 個月）勝率僅 27.9%、PF 0.92，
低於損益兩平。下一步：
1. 驗證 V2.4.1（互斥過濾器 ON + 提早保本 ON，預設值）套用後能否挽回 OOS 表現
   ——需要使用者在 TradingView 用 V2.4.1（或功能對等的 V3.2）重新匯出同期間 CSV
2. 若 V2.4.1/V3.2 仍未過 OOS，需重新檢視 S2-Hammer 錘頭型態本身在近期市場結構下是否失效
   （例如：近期波動度/趨勢特徵改變，型態辨識邏輯可能需要調整，不只是加過濾器）

## 仍等待使用者提供（TradingView 匯出，CSV 放對應策略資料夾）

1. S2-Hammer V2.4.1 或 V3.2（功能對等）用最新資料期間重新回測匯出，驗證 OOS 是否轉正
   （見上方「新的最高優先」）
2. S2-Hammer V2.4.1 的 2×2 對照（4 份 CSV，檔名帶 A/B/C/D）：
   - A=互斥OFF/保本OFF（≈V2.3基準）、B=互斥ON、C=保本ON、D=全ON
   - 放 `xauusd/XAUUSD-Long-S2-Hammer/`
3. S1 V3.8.1：BBW高檔回看20 一份、BBW低檔ON+回看90 一份
4. S1 ABCD 診斷（V3.7-ABCD-Diagnostic.pine）四種組合各一份
   - ⚠️ 此 pine 寫於語法修復之前，可能有 V2.3 同款壞語法（行接續/plotshape參數順序），使用者回報編譯錯誤就照 V2.4.1 的修法處理
5. S2-RSI V2.0 基準版重匯到最新日期（S2-Hammer 已完成，S2-RSI 尚未）

## CSV 到手後的分析步驟

- S2 2×2：仿 `xauusd/scripts/run_s1_v37_real_attribution.py` 做四組對照歸因，
  重點驗證：①互斥/保本各自貢獻與交互作用 ②S2B_BE 出場是否如 Python 估計攔截 time_bleed
  （估計值：83% 拖≥12h 虧損單可攔，見 report_s2_attribution.html）
- S1 V3.8.1：對照 report_v3.8_regime_sweep.html 的 Python 相對排名是否被真實回測支持
- ABCD：拆解 V3.4→V3.7 改善中 lookahead bug 修正 vs BBW 過濾器各自貢獻

## 重要背景（本輪已完成，詳見 data/logs.json 20260710-11 條目）

- S2 優化主線：合流分析→歸因→V2.4.1（互斥過濾器+提早保本，已修完語法可編譯）
- ⚠️ repo 內 V2.2/V2.3 系 pine 是被壓扁的壞源碼（逗號if/壓扁縮排/plotshape參數順序錯），
  以 repo pine 為基礎開發前先確認能編譯；V2.4.1 與 S2-RSI V2.4 已修復
- 網站已拆頁重構（DEVELOPMENT.md 為開發規範）；策略更名 S2-RSI / S2-Hammer
- TradingView 訂閱決策：留 Premium 90 天觀察期，footprint 實驗（request.footprint()
  Premium限定）排在 S2/S1 驗證之後
