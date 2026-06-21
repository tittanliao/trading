# Claude Dispatch 恢復指令
# 當 context 爆掉或清掉對話後使用

---

## 快速恢復步驟

**方案①**：若只是 context 滿了，想快速回血
```
1. 用瀏覽器開啟本檔案位置：
   /Users/tittan/program/github/trading/xauusd/claude/dispatch_recovery.md
2. 把「👇 貼下方文字給 Claude」那段複製出來
3. 新對話中貼給 Claude，自動恢復工作流
```

**方案②**：完整恢復（推薦）
```
直接貼 dispatch_start.md 的「貼給 Claude 的指令」段落給 Claude
路徑：/Users/tittan/program/github/trading/xauusd/claude/dispatch_start.md
```

---

## 👇 貼下方文字給 Claude

```
你好，請依序讀取以下檔案，恢復黃金分析工作流：

1. /Users/tittan/program/github/trading/xauusd/claude/ANALYSIS_SKILL.md
2. /Users/tittan/program/github/trading/xauusd/claude/TRADING_PROFILE.md
3. /Users/tittan/program/github/trading/xauusd/claude/daily/（讀最新的 YYYY-MM-DD.json）
4. /Users/tittan/program/github/trading/xauusd/claude/context.md

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

---

## 工作流指令速查表

| 指令 | 說明 |
|------|------|
| `請分析` | 即時分析：讀 daily JSON → 最新周報 → TV 截圖 → 輸出交易建議 + 更新 context |
| `週日黃金工作流` | 完整周報生成（CFTC + CSV + 周報） |
| `請比對周報` | 周報①（Gemini）vs 周報②（Claude），輸出差異 |
| `更新 profile` | 更新 TRADING_PROFILE.md |
| `signal scanner` | 執行 signal_scanner.py |

---

## 版本記錄
- 20260609：初版建立
- 20260619：簡化版本，指向 dispatch_start.md 做完整恢復
