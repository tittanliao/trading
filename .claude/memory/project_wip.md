---
name: project-wip
description: 進行中工作狀態（20260712 更新）：Footprint D模式實測PF 2.2、V4.1發布（含Gemini建議整合）；最優先=索取D模式逐筆CSV做OOS
metadata:
  type: project
---

# 進行中工作（20260712 狀態）

## 🚀 Footprint 主線（20260712 新增，目前最活躍）
- **V4.0 實測**：S2-Hammer Footprint D 模式（POC上半部+低檔買方吸收堆疊）**PF 2.047→2.2**，
  其他模式無明顯變化；`request.footprint(ticks_per_row, va_percent, imbalance_percent)` API 已確認可編譯
- **V4.1 已發布**（S1 + S2-Hammer，皆基於 xlsx 最佳參數版）：
  - S2：fp_mode 預設改 D；新增 G（D+恐慌爆量）/H（trapped sellers）/I（收回價值區）；
    FILTER⑩ Volume Climax、⑪ DXY死亡區間阻擋（數據驅動：阻擋 DXY RSI 30-50，非 Gemini 直覺的強勢區）
  - S1：FILTER⑦ Weekly VWAP、⑧ Volume Surge、⑨ DXY Alignment（Gemini 建議採納，全預設 OFF）
  - Gemini 的 Micro Bounce（1m array）未採納：security_lower_tf 歷史深度限制 + 資訊劣於 footprint
- **✅ V4.1 D 模式逐筆 OOS 已完成（20260712，詳見 `report_v41_oos.html`）**：
  - 全樣本三版階梯 V1.9 PF1.53 → V3.2 2.05 → V4.1 2.27（WR 41.1→47.1→49.7%）
  - **footprint 歷史資料只覆蓋 ~2026年4月起**：被D篩的14筆全在2026Q2/Q3，2024/2025兩版完全相同
    ——改善天然集中在最需要救的近期，無「早期樣本撐數字」幻覺空間
  - D 篩選精度 79%（14筆中11筆原本是輸單）；V1.9-OOS同區間三版階梯 PF 0.90→1.23→**1.64**
  - 驗證A：V4.1 OOS PF1.87 過門檻，勝率落差11.1pp仍超8pp（vs V3.2 的19.9pp，大幅收斂）
  - 判定 🟡 接近通過方向強烈正向；限制=footprint只作用近3個月/被篩僅14筆，統計基礎薄
- **下一步**：①不急升版，每月重匯 V4.1 CSV 追蹤「footprint生效段」PF 是否守住 >1.4
  ②TV 測模式 G（D+恐慌爆量）/H（trapped sellers）與 D 對照 ③D 參數只做粗掃防過擬合
- S1 V4.1 尚未有實測回報（Footprint 順勢模式 + Weekly VWAP/Vol Surge/DXY Align 三個Gemini濾網）
- 20260712 追加：S1 全過濾器時框已開放可調（①HTF MA原寫死60、⑦VWAP錨定原寫死1W、⑨DXY原寫死D）

# 20260711 晚間狀態（保留備查）

## 🟡 S2-Hammer OOS 問題現況：V3.2 有改善但未解決，非阻塞性持續觀察
最新結論（詳見 `report_v32_oos.html` 與 ANALYSIS_SKILL.md「V3.2 逐筆 OOS 驗證結論」）：
- V1.9 原始邏輯 OOS（後30%）WR 27.9%/PF 0.92，低於損益兩平——最早發現的問題
- V3.2（HTF RSI + S2-RSI互斥過濾器）驗證後：自己的 OOS 是 WR 33.3%/PF 1.35（勝率落差-19.9pp仍超標，
  未通過）；在 V1.9-OOS 相同日曆區間（2026-01-22後）WR 30.8%/PF 1.23（比V1.9同期間好，但仍脆弱）
- **結論：真實改善，但不是「解決」**。IS→OOS 勝率大幅衰退的模式在兩版都存在，暗示問題可能不只是
  合流訊號需要過濾，錘頭型態本身在近期市場結構下的辨識力可能也在減弱
- **fail-pattern 對照已補做**（暫切 `config.py` 到 V3.2 重跑 main.py，詳見 `report_v3.2.html`／
  ANALYSIS_SKILL.md「V3.2 fail-pattern 對照」）：印證判斷——過濾器只砍到 immediate_loss
  （16.8%→10.8%），time_bleed 佔比完全沒變（57.8%），因為 V3.2 沒開提早保本。
  `report.html` 已切回 V1.9 現行基準，兩版報告並存（`report.html`=V1.9、`report_v3.2.html`=V3.2）。

## ⚠️ 提早保本已證實無效，推翻 V2.4.1 原假設（20260711 新結論）
用真實30m K棒逐bar重建（非MFE彙總粗估）掃描 0.10%~1.75% 共12個門檻，對 V1.9全樣本／V3.2全樣本／
V1.9-OOS段分別測試，**結論：所有門檻在所有樣本都是淨損**，最佳門檻也只接近打平，不是真優勢。
詳見 `report_early_be_sweep.html` 與 ANALYSIS_SKILL.md「提早保本參數掃描結論」。
- 根本原因：S2-Hammer 靠少數大贏家（TP2=4R，平均持倉90h+）撐獲利，這些「慢贏」單過程常見先小賺
  拉回進場價、之後才反轉大漲；提早保本會把這類單腰斬在打平，砍贏家代價 > 救輸家好處
- **推翻 V2.4.1「83%可攔截且不傷慢贏」的假設**——原估計只算了救回那一半，沒算砍贏家的代價
- V3.2 pine 的 FILTER③ tooltip 已更正（維持預設OFF不變，只是文字說明從「建議開」改成「不建議開」）
- **下一步方向（優先度皆不高）**：
  1. ~~疊加提早保本~~（已證實無效，不再列為選項）
  2. 持續累積更多近期交易，觀察 V3.2（僅HTF+互斥過濾器）是否隨時間推移穩定在改善水準
  3. 重新檢視錘頭型態定義本身是否需要調整（更根本的方向，優先度提升——出場端修法已證明此路不通，
     問題可能真的出在進場辨識邏輯本身）
  4. 或考慮進場品質的其他方向（HTF/互斥已證實有效但不夠），而非出場端修補
- **不建議急著升版確認 V3.2**

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
