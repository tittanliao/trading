# /update-research — 研究成果更新完整流程

> 20260711 全面改寫：網站已拆頁重構（見根目錄 `DEVELOPMENT.md`），
> 舊版此 skill 的「直接手改 index.html」流程已全部作廢。
> **鐵律：6 個生成頁（index/xauusd/tx/shared/history/sitemap.html）禁止手改。**

執行此 skill 時，根據下方清單逐步完成所有更新，不需要用戶額外提醒每個步驟。
依序執行到最後，commit 前向用戶確認。

---

## 使用場景

用戶說以下任何一個時觸發此清單：
- 「幫我跑 S1 分析」/「新增 V3.x Pine Script」/「回測結果出來了」
- 「更新 index」/「更新網站」（在新分析完成之後）
- 明確說「/update-research」

---

## 完整步驟清單

### A. Python 分析腳本

若有新分析腳本（放 `xauusd/scripts/`，在 trading/ 根目錄執行）：

```bash
python3.12 xauusd/scripts/run_xxx.py
```

確認輸出 HTML 成功生成（沒有 exit code 1）。CJK 字體 UserWarning 可忽略。
報告輸出到對應策略資料夾，命名 `report_<主題>.html`。

### B. Pine Script 新版本

若用戶提供新 .pine 檔：
1. 複製到對應資料夾（S1: `XAUUSD-Long-S1-AweWithBB/`、S2A: `XAUUSD-Long-S2A-RSI/`、S2B: `XAUUSD-Long-S2B-Hammer/`）
2. 檔名格式：`{策略ID}-V{版本}.pine`（`VX.Y` 確認版 / `VX.Y+1.1` 測試版）

### C. 策略數字更新（僅在版本/績效有變時）

依 DEVELOPMENT.md §3 單一事實來源順序，**先改法定來源，再抄到抄本**：
1. `xauusd/claude/ANALYSIS_SKILL.md` — 法定來源，先改這裡
2. 從 ANALYSIS_SKILL.md 抄到：
   - `xauusd/CLAUDE.md` 的「現有策略最新績效」表
   - `content/xauusd/opt.html` — 策略卡片 badge/metrics、版本歷程表新增一行、Pine 下載連結
     （這是 fragment，可以手改；樣式慣例：最新版★綠色漸層、深度報告藍 `#38bdf8`、Fail 測試橙 `#f97316`）

### D. 網站更新（每次都要做）

1. **`data/logs.json`** append 一筆記錄（date / tag: xauusd|tx|cross / title / items[]，
   items 內可放 HTML，新報告要附 `<a href='...'>報告 →</a>` 連結）
2. **`content/sitemap.html`** 登記新報告連結
3. 重新生成：
   ```bash
   python3.12 generate_site.py            # 全部 6 頁
   python3.12 generate_site.py --page xauusd  # 或只生成受影響的頁
   ```
4. **檢查**：`git diff --stat` — 變動幅度要符合預期，出現大量非預期刪除立即停下

### E. Commit & Push

```bash
git add <分析腳本> <報告html> <pine> <ANALYSIS_SKILL等來源檔> \
        content/ data/logs.json <生成的頁面.html>
git commit -m "feat: {說明}"
git push
```

來源檔與生成頁一起 commit（不要分開，避免 repo 內兩者不同步）。

---

## 常見遺漏項目（過去反覆踩坑）

| 遺漏點 | 解決方式 |
|--------|---------|
| 新報告沒進網站 | D1 logs.json + D2 sitemap 兩處都要 |
| 改了 fragment / logs.json 忘記重新生成 | D3 每次必跑，生成頁和來源一起 commit |
| 直接手改了生成頁 | ⛔ 禁止——內容會在下次生成時消失；改 content/ 或 data/ |
| 策略數字只改了一處 | C 節順序：ANALYSIS_SKILL.md → 抄本，全部過一遍 |
| 版本歷程表沒有新行 | C2 的 content/xauusd/opt.html 內 |
| 手動計數（共 N 筆等） | 已廢除，logs.json 自動計算，不需要動 |

---

## 報告 HTML 命名與顏色慣例

| 報告 | 路徑 | 顏色 |
|------|------|------|
| V1 基礎報告 | `{策略資料夾}/report.html` | 預設藍 |
| V2 深度報告 | `{策略資料夾}/report_v2.html` | 藍 `#38bdf8` |
| Fail 空單測試 | `{策略資料夾}/report_s1_fail_short.html` | 橙 `#f97316` |
| OOS / 敏感度等驗證報告 | `{策略資料夾}/report_<主題>.html` | 預設 |
| 宏觀回測報告 | `xauusd/XAUUSD-Macro/...` | 紫 |
