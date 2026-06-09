# Claude Dispatch 恢復指令
# 當 context 爆掉或清掉對話後，貼這份文件給 Claude 即可恢復

---

## 快速恢復（貼給 Claude 的指令）

```
你好，請依序讀取以下檔案，恢復黃金分析工作流：

1. /Users/tittan/program/github/trading/xauusd/skill/ANALYSIS_SKILL.md
2. /Users/tittan/program/github/trading/xauusd/skill/TRADING_PROFILE.md
3. /Users/tittan/program/github/trading/xauusd/daily_log/xauusd_latest.json

4. 【周報①：Gemini 版】
   在以下路徑找 7 天內最新的 XAUUSD_Weekly_Report_*.gdoc：
   /Users/tittan/googledrive/XAUUSD/weekly report/
   用 Chrome 開啟後讀取內容（需要登入 Google）

5. 【周報②：Claude 版】
   在以下路徑找最新的 weekly_report_*.txt：
   /Users/tittan/program/github/trading/xauusd/daily_log/

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

---

## 工作流指令對照表

| 指令 | 說明 |
|------|------|
| `請分析` | 日常黃金分析（截圖 + 狀態 + 建議） |
| `週日黃金工作流` | 完整周報生成（CFTC + CSV + 周報） |
| `請比對周報` | 周報①（Gemini/Google Drive 最新）vs 周報②（Claude txt 最新），輸出綜合分析 |
| `更新 profile` | 更新 TRADING_PROFILE.md 中的個人設定 |
| `signal scanner` | 執行 xauusd/signal_scanner.py，輸出即時訊號 |

---

## 環境資訊

### 路徑
- Git Repo：`/Users/tittan/program/github/trading/`
- Google Drive CSV：`/Users/tittan/googledrive/XAUUSD/weekly report/csv/`
- Google Drive 周報：`/Users/tittan/googledrive/XAUUSD/weekly report/`
- CFTC 資料來源：`https://www.tradingster.com/cot/futures/disagg/088691`

### Python 版本
- Mac：`python3.12`
- 主要套件：pandas 3.x, numpy, matplotlib

### CSV 檔案（三份 30m 即可）
- `FX_IDC_XAUUSD, 30.csv`
- `TVC_DXY, 30.csv`
- `MGC_30m.csv`

### Git Remote
- `git@github.com:tittanliao/trading.git`（SSH）

---

## 完成清單（Completion Checklist）

每次任務結束前確認：
- [ ] `xauusd_latest.json` 已更新
- [ ] 重要分析已存到 `daily_log/`
- [ ] TRADING_PROFILE 若有新發現已更新
- [ ] git commit + push

---

## xauusd_latest.json 初始化 Prompt

第一次啟動 dispatch，或 xauusd_latest.json 不存在時，貼以下內容給 dispatch：

```
請初始化 xauusd_latest.json 並開始使用。

檔案路徑：/Users/tittan/program/github/trading/xauusd/daily_log/xauusd_latest.json

【用途】
每次「請分析」結束後，把本次分析重點寫入這個檔案。
下次分析時，先讀這個檔案，了解最近的市場基準再開始。

【每筆記錄格式】
{
  "ts": "2026-06-09T09:00",
  "session": "Asia",
  "price": 4328.78,
  "rsi_30m": 52.3,
  "rsi_4h": 45.1,
  "bb_pct_b_4h": -0.06,
  "dxy": 100.07,
  "dxy_rsi": 70.6,
  "s1_status": "距突破 5.8 點，AO 下降",
  "s2_status": "無錘頭，4311 支撐觀察中",
  "key_levels": {"support": 4311, "resistance": 4446},
  "claude_view": "偏空，4H BB Lower 以下，不做 S1，等 S2 A+ 機會",
  "action": "觀望"
}

【規則】
- 保留最近 20 筆，超過自動刪除最舊的
- 每次「請分析」結束後必須寫入
- 格式為 JSON array，最新的在最後
- 寫入後執行 git commit + push
```

---

## 版本記錄
- 20260609：初版建立
- 20260609：新增 xauusd_latest.json 初始化 prompt
