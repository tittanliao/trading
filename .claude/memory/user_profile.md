---
name: user-profile
description: 量化交易者，同時操作 XAUUSD 和台指期小台（MTX），使用 TradingView + Python 回測，跨 Mac/Windows
metadata:
  type: user
---

- 量化交易者，同時操作 **XAUUSD 黃金**（xauusd 專案）與**台指期小台 MTX**（tx 專案）
- 使用 TradingView 看盤 + 匯出 CSV，用 Python 3.11 做回測與分析
- 慣用 Windows 環境（py -3.11 執行），但也用 Mac（python3）
- **跨電腦工作（Mac + Windows）**，用 git 同步程式碼與記憶
- 能看懂 pandas / matplotlib 程式碼，熟悉 Pine Script v6
- 偏好**繁體中文**溝通
- 工作方式：分析 → 找到 insight → 落地到 Pine Script → TradingView 驗證

## XAUUSD 交易習慣（20260609 更新）
- 三個盤別（亞/歐/美）都操作，以各盤別歷史勝率決定優先順序
- 進場等級：S1/S2 均只做 A+ 和 A，不做 B 級
- 風控：每筆 1.0~1.5% 總資金，同時只持 1 倉，不加碼攤平
- 看盤方式：被動觸發，TradingView 跳訊號才查看，不固定時間盯盤
- 觸發流程：手機收到 TV 通知 → Claude co-work 請分析 → 決定進場
