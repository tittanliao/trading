---
name: project-context
description: tx 台指期分析工具箱的目標、架構設計、與 xauusd 的關鍵差異
metadata:
  type: project
---

## 目標
分析台指期小台（MTX）的多/空策略失敗模式，系統性測試新策略。
架構完全對應 xauusd 專案，可共用大部分邏輯。

**Why:** 用戶已有 xauusd 完整框架（Fail-Pattern + 20多單 + 20空單實驗），要把同套方法論擴展到台指期。
**How to apply:** 有 xauusd 現成程式碼時，優先改寫而非從頭寫。差異點見下表。

## 與 xauusd 的關鍵差異

| 面向 | xauusd | tx（台指期） |
|------|--------|------------|
| 商品 | XAUUSD | MTX 小台（每點 NT$50） |
| 相關性指標 | DXY（反向相關） | NQ（同向相關） |
| SL/TP 單位 | 百分比 0.5%/1.0% | 固定點數 30pts/60pts |
| 交易時段 | 24/5 | 日盤 08:45–13:45 + 夜盤 15:00–05:00 |
| 特有分析模組 | — | session_analysis.py（日盤/夜盤分段） |

## NQ 相關性（同向）
- NQ 強（RSI 超買 > 70）→ 台指期多單有利
- NQ 弱（RSI 超賣 < 30）→ 台指期空單有利
- 與 xauusd 的 DXY 分析邏輯相反，讀報告時注意方向

## 回測參數（第一版預設）
- SL: 30 pts，TP: 60 pts，R:R = 2:1
- 時間止損：48 bars（30m K = 24 小時）
- 日盤 + 夜盤都納入回測

## TradingView 符號 / CSV 檔名
- 小台連續：`TAIFEX:MXF1!` → 匯出檔名 `TAIFEX_DLY_MXF1!, 30.csv`（含 `DLY` 前綴）
- NQ 連續：`CME_MINI:NQ1!` → 匯出檔名 `CME_MINI_DL_NQ1!, 30.csv`
- TradingView CSV 欄位包含 `Basis/Upper/Lower`（BB），loader 已容許此格式

## 第一版實驗結果（2026-05-13，真實資料 2025-06 起，8585 bars）
多單：E12 BB Squeeze Break 唯一 PF > 1（PF=1.132, WR=36.1%）
空單：全部虧損（此期間大多頭，做空困難）

## Pine Script（2026-05-13）
- `TX-Long-Experiments/pine/ALL_Long_Strategies.pine`：E01–E20 合併，下拉選單
- `TX-Short-Experiments/pine/ALL_Short_Strategies.pine`：S01–S20 合併，下拉選單
- 功能：Enable 開關、SL 點數、R:R Ratio（TP 自動計算）、日盤/夜盤 Session 過關
- 視覺化：進場箭頭、SL/TP 虛線、右側資訊標籤
- Alert：有設定 alertcondition 可連通知

## 宏觀分析（macro_analysis.py，2026-05-13）
週線資料（2012–2026，169 個月）統計月初買入、月底賣出的歷史勝率。
- 整體月勝率：63.9%，平均月漲跌 +199 pts
- 季節性：九月唯一偏空月（42.9%）；十二月最穩（78.6%）；四月期望值最大（+518 pts avg）
- 週內結構：第1、4、5週勝率較高（58–61%）；第3週最弱（55.4%）
- 操作框架：先看月度季節性偏向（宏觀基準）→ 再用週線 RSI/BB 挑選進場時機
- 輸出：macro_report.html（暗色主題，含熱力圖），摘要整合到 index.html

## 下一步
- 用週線 RSI + BB 位置做月內進場時機分析
- 加入 NQ 相關性過濾（NQ RSI 同向確認）
- 加入 MTF 過濾（4H RSI 狀態）提升勝率
- 分析為何大多頭期間多單策略仍大多虧損（可能 SL 太緊、30pts ≈ 0.15%）
