---
name: project-wip
description: 進行中工作狀態（20260711 晚間更新，第三次）：S2-Hammer V3.2全樣本轉正但OOS未驗證，最高優先是索取V3.2逐筆CSV
metadata:
  type: project
---

# 進行中工作（20260711 晚間狀態，第三次更新）

## 本輪已完成（20260711 晚間，第三次）
- ✅ 使用者提供 `xauusd/csv/Strategy_analysis_by_tittan.xlsx`（TradingView Strategy Tester
  手動記錄，8組S1/S2測試），已解析並整理成對照表，寫入 ANALYSIS_SKILL.md 對應章節
- ✅ **交叉驗證成功**：xlsx記錄的S2-Hammer V1.9數字（WR41.1%/PF1.535/淨利$7216/MDD$2424）
  跟 Python 算出的幾乎一致（$7216.29/MDD$2413.91）——互相驗證兩邊方法論正確
- ✅ **S2-Hammer V3.2 全樣本大幅改善**：PF 1.535→2.047、MDD 12.7%→7.0%（腰斬），
  但這是全樣本Strategy Tester彙總，不是逐筆CSV，**還不能證明OOS問題已解決**——
  下方「最高優先」已更新為明確索取V3.2逐筆CSV

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

## 🔴 最高優先：S2-Hammer V3.2 全樣本轉正，但 OOS 仍待驗證
V3.2（HTF 1H RSI bearish阻擋 + S2-RSI互斥30m RSI上穿20）全樣本 PF 1.535→2.047、MDD腰斬，
但這只是 Strategy Tester 彙總數字，無法拆分IS/OOS。下一步：
1. **向使用者索取 V3.2 的 List of Trades CSV**（TP1/TP2=2R/4R 那組，即 xlsx row 7 的設定），
   放到 `xauusd/XAUUSD-Long-S2-Hammer/`，命名建議 `S2-Hammer-V3.2_FX_IDC_XAUUSD_2026-07-11.csv`
2. 拿到後仿 `run_s2_attribution.py`／`run_s1_v37_real_attribution.py` 的方法論，對 V3.2 做
   70/30 時間切分 OOS 驗證，確認過濾器是否真的救回近2.5個月的樣本外表現
3. 若 OOS 通過，可考慮升級為確認版；若仍未過，代表問題比預期更根本
   （可能是錘頭型態本身在近期市場結構下失效，不只是缺過濾器）
4. 也可順便索取 xlsx row 8（TP1/TP2=1R/2R 高勝率版）的逐筆CSV對照，看是否在OOS段更穩定

## 仍等待使用者提供（TradingView 匯出，CSV 放對應策略資料夾）

1. **S2-Hammer V3.2 逐筆 CSV**（見上方「最高優先」，最急迫）
2. S2-Hammer V2.4.1 的 2×2 對照（4 份 CSV，檔名帶 A/B/C/D）：
   - A=互斥OFF/保本OFF（≈V2.3基準）、B=互斥ON、C=保本ON、D=全ON
   - 放 `xauusd/XAUUSD-Long-S2-Hammer/`
3. S1 V3.8.1：BBW高檔回看20 一份、BBW低檔ON+回看90 一份
4. S1 ABCD 診斷（V3.7-ABCD-Diagnostic.pine）四種組合各一份
   - ⚠️ 此 pine 寫於語法修復之前，可能有 V2.3 同款壞語法（行接續/plotshape參數順序），使用者回報編譯錯誤就照 V2.4.1 的修法處理
5. S2-RSI V2.0 基準版重匯到最新日期（S2-Hammer 已完成，S2-RSI 尚未）

**注意**：S1 V3.9 逐筆 CSV 已經有了（`S1-Awe-V3.9_FX_IDC_XAUUSD_2026-07-11.csv`，450筆，
對應 xlsx row 4 TP2=3.5R 那組，已用於 `report_v3.9_real.html`）——不需要再要，
但目前只做了「共同期間對V3.7」比較，還沒做像 S2-Hammer 那樣的 70/30 OOS 切分，
之後有空可以補做（non-blocking，優先度低於S2-Hammer）。

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
