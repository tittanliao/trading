---
name: project-wip
description: 進行中工作狀態（20260711 更新）：等待使用者 TradingView 匯出 CSV，收到後的分析步驟
metadata:
  type: project
---

# 進行中工作（20260711 晚間狀態）

## 等待使用者提供（TradingView 匯出，CSV 放對應策略資料夾）

1. **最優先：S2-Hammer V2.4.1 的 2×2 對照**（4 份 CSV，檔名帶 A/B/C/D）：
   - A=互斥OFF/保本OFF（≈V2.3基準）、B=互斥ON、C=保本ON、D=全ON
   - 放 `xauusd/XAUUSD-Long-S2-Hammer/`
2. S1 V3.8.1：BBW高檔回看20 一份、BBW低檔ON+回看90 一份
3. S1 ABCD 診斷（V3.7-ABCD-Diagnostic.pine）四種組合各一份
   - ⚠️ 此 pine 寫於語法修復之前，可能有 V2.3 同款壞語法（行接續/plotshape參數順序），使用者回報編譯錯誤就照 V2.4.1 的修法處理
4. 加分：S2-RSI V2.0 / S2-Hammer V1.9 基準版重匯到最新日期

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
