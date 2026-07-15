# Claude Dispatch 啟動指令（已併入 DISPATCH.md，本檔為相容重導向頁）

⚠️ 本檔內容已於 20260619 併入 `DISPATCH.md`。過去這裡寫的「讀 xauusd_latest.json」「讀 daily_log/*.txt 週報」流程都已被取代（現行是 context.md + daily/YYYY-MM-DD.json + Gemini gdoc 唯一來源），為避免與 ANALYSIS_SKILL.md 現行規則衝突，本檔已簡化為重導向頁。**請改用 `DISPATCH.md`**，若兩者不一致以 `DISPATCH.md` 為準。

---

## 貼給 Claude 的指令（與 DISPATCH.md「快速恢復」一致）

```
請依序讀取以下檔案，恢復黃金分析工作流：

1. /Users/tittan/googledrive/Github/trading/xauusd/claude/ANALYSIS_SKILL.md
2. /Users/tittan/googledrive/Github/trading/xauusd/claude/TRADING_PROFILE.md
3. /Users/tittan/googledrive/Github/trading/xauusd/claude/context.md

讀完後回覆「工作流已恢復，等待指令」，不需要額外說明。
```

完整的工作流指令對照表、注意事項、版本記錄請見 `/Users/tittan/googledrive/Github/trading/xauusd/claude/DISPATCH.md`。

---

## 版本記錄
- 20260609：初版建立（整合 recovery.md + 本次對話流程）
- 20260705：改為 DISPATCH.md 的相容重導向頁，移除過期內容（xauusd_latest.json、daily_log txt 流程、啟動時讀 daily JSON）
