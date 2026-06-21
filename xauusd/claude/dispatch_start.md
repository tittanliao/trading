# Claude Dispatch 啟動指令
# 新對話開始時，把下方「貼給 Claude 的指令」整段貼給 Claude，即可恢復完整黃金分析工作流。

---

## 貼給 Claude 的指令（直接複製整段）

```
請依序讀取以下檔案，恢復黃金分析工作流：

1. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL.md
2. /Users/tittan/program/github/trading/xauusd/claude/TRADING_PROFILE.md
3. /Users/tittan/program/github/trading/xauusd/claude/daily/（讀最新的 YYYY-MM-DD.json）

4. 【周報①：Gemini 版】
   在以下路徑找 7 天內最新的 XAUUSD_Weekly_Report_*.gdoc：
   /Users/tittan/googledrive/XAUUSD/weekly report/
   用 Chrome 開啟後讀取內容

5. 【周報②：Claude 版】
   在以下路徑找最新的 weekly_report_*.txt：
   /Users/tittan/program/github/trading/xauusd/daily_log/

6. 讀取指令手冊：
   /Users/tittan/program/github/trading/xauusd/claude/dispatch_recovery.md

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

---

## 工作流指令對照表

| 指令 | 說明 |
|------|------|
| `請分析` | ① 讀 xauusd_latest.json 最後一筆 → ② 從 `/Users/tittan/googledrive/XAUUSD/weekly report/` 找最新 Gemini 週報（.png/.gdoc/.txt）並讀取 → ③ 用 computer use 截取 Chrome TradingView XAUUSD 30m 即時截圖（不用 API/Yahoo Finance）→ ④ 結合 json + 週報 + 截圖做分析 → ⑤ 輸出標準格式結果 → ⑥ 自動 append 結果到 xauusd_latest.json（不問用戶）→ ⑦ 提醒 git commit/push |
| `週日黃金工作流` | 完整周報生成（CFTC + CSV + 周報） |
| `請比對周報` | 周報①（Gemini）vs 周報②（Claude）輸出差異報告 |
| `更新 profile` | 更新 TRADING_PROFILE.md |
| `signal scanner` | 執行 xauusd/signal_scanner.py |
| `工作流已恢復` | 確認 context 載入完成，等待指令 |

---

## 注意事項

- **Git commit/push**：沙盒無 .git 寫入權限，分析後提醒用戶在 Terminal 手動執行：
  ```bash
  cd /Users/tittan/program/github/trading && git add xauusd/claude/ && git commit -m "daily analysis: $(date +%Y-%m-%d)" && git push
  ```
- **CSV 資料**：目前最新至 2026-04-27，截圖分析為主
- **Gemini 周報**：若 Chrome 無法開啟 .gdoc，改讀同路徑的 .txt 備份
- **xauusd_latest.json**：若不存在，執行「請分析」時自動初始化

---

## 版本記錄
- 20260609：初版建立（整合 recovery.md + 本次對話流程）
