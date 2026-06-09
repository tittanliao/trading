# Claude Dispatch 恢復指令
# 當 context 爆掉或清掉對話後，貼這份文件給 Claude 即可恢復

---

## 快速恢復（貼給 Claude 的指令）

```
你好，請依序讀取以下檔案，恢復黃金分析工作流：

1. trading/xauusd/skill/ANALYSIS_SKILL.md     ← 分析技術與流程
2. trading/xauusd/skill/TRADING_PROFILE.md    ← 我的交易習慣
3. trading/xauusd/daily_log/xauusd_latest.json ← 最近分析狀態
4. trading/xauusd/daily_log/[最新的 weekly_report_*.txt] ← 最新周報

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

---

## 工作流指令對照表

| 指令 | 說明 |
|------|------|
| `請分析` | 日常黃金分析（截圖 + 狀態 + 建議） |
| `週日黃金工作流` | 完整周報生成（CFTC + CSV + 周報） |
| `請比對周報` | Claude 周報 vs Gemini 周報，輸出綜合分析 |
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

## 版本記錄
- 20260609：初版建立
