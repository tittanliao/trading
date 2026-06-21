# Claude Dispatch — 工作流手冊
# 依使用情境選擇對應段落，複製後貼給 Claude。

---

## 快速恢復（日常分析 / context 爆掉用）

```
請依序讀取以下檔案，恢復黃金分析工作流：

1. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL.md
2. /Users/tittan/program/github/trading/xauusd/claude/TRADING_PROFILE.md
3. /Users/tittan/program/github/trading/xauusd/claude/context.md

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

---

## 週日工作流（周報生成用）

```
請依序讀取以下檔案，恢復黃金分析工作流：

1. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL.md
2. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL_WEEKLY.md
3. /Users/tittan/program/github/trading/xauusd/claude/TRADING_PROFILE.md
4. /Users/tittan/program/github/trading/xauusd/claude/context.md

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

---

## 合併週報

```
請依序讀取以下檔案，恢復黃金分析工作流：

1. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL.md
2. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL_WEEKLY.md
3. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL_MERGE.md
4. /Users/tittan/program/github/trading/xauusd/claude/TRADING_PROFILE.md
5. /Users/tittan/program/github/trading/xauusd/claude/context.md

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

---

## 指令速查表

| 指令 | 說明 |
|------|------|
| `請分析` | 即時分析：讀 context → Gemini gdoc 週報 → TV 截圖 → 輸出交易建議 + 更新 context |
| `週日黃金工作流` | 完整周報生成（CFTC + CSV + 周報），需先載入 ANALYSIS_SKILL_WEEKLY.md |
| `合併週報` | 三份週報合併（Claude / Gemini / Dispatch），需先載入 ANALYSIS_SKILL_MERGE.md |
| `請比對周報` | 周報①（Gemini）vs 周報②（Claude），輸出差異 |
| `更新 profile` | 更新 TRADING_PROFILE.md |
| `signal scanner` | 執行 /Users/tittan/program/github/trading/xauusd/signal_scanner.py |

---

## 注意事項

- **Git commit/push**：分析後提醒用戶在 Terminal 手動執行：
  ```bash
  cd /Users/tittan/program/github/trading && git add xauusd/claude/ && git commit -m "daily analysis: $(date +%Y-%m-%d)" && git push
  ```
- **CSV 資料**：存放於 /Users/tittan/googledrive/XAUUSD/weekly report/csv/
- **Gemini 周報**：讀 .gdoc（唯一來源），不接受 PNG 或 txt 替代
- **daily JSON**：歷史存檔用，啟動時不讀，路徑 /Users/tittan/program/github/trading/xauusd/claude/daily/

---

## 版本記錄
- 20260609：初版建立
- 20260619：dispatch_start + dispatch_recovery 合併為本檔
- 20260621：整合三種啟動情境；移除啟動時讀 daily JSON（近5筆已移入 context.md）
