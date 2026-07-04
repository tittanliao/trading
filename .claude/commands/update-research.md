# /update-research — 研究成果更新完整流程

執行此 skill 時，根據下方清單逐步完成所有更新，不需要用戶額外提醒每個步驟。
每完成一個大項目後詢問用戶是否繼續，或直接依序執行到最後再 commit & push。

---

## 使用場景

用戶說以下任何一個時觸發此清單：
- 「幫我跑 S1 分析」/ 「新增 V3.x Pine Script」/ 「回測結果出來了」
- 「commit and push」（在新分析完成之後）
- 明確說「/update-research」

---

## 完整步驟清單

### A. Python 分析腳本

若有新分析腳本（e.g., `run_s1_deep_analysis.py`, `run_s1_fail_short.py`）：

```bash
# 在 trading/ 根目錄執行
python3.12 xauusd/run_s1_deep_analysis.py
python3.12 xauusd/run_s1_fail_short.py
```

確認輸出 HTML 成功生成（沒有 exit code 1）。
CJK 字體 UserWarning 可忽略，不影響輸出。

---

### B. Pine Script 新版本

若用戶提供新 .pine 檔（e.g., 從 Downloads 複製）：
1. 複製到對應資料夾：
   - S1: `xauusd/XAUUSD-Long-S1-AweWithBB/`
   - S2A: `xauusd/XAUUSD-Long-S2A-RSI/`
   - S2B: `xauusd/XAUUSD-Long-S2B-Hammer/`
2. 確認檔名格式：`{策略ID}-V{版本}.pine`

---

### C. 更新 index.html（每次都要做）

**C1. 綜合對比 Tab（xauusd-opt-overview）中的策略卡片**

找到對應策略的 card，同時更新：
- `badge` 版本號 → 最新版本
- 4 個 `metric-val`：WR、PF、PnL、MDD
- `report-links`：加入所有新生成的 HTML 報告連結
  - 格式：`<a class="report-link" href="...">📄 報告名稱</a>`
  - 深度報告（report_v2.html）用藍色：`style="border-color:#38bdf8;color:#38bdf8"`
  - Fail 測試報告用橙色：`style="border-color:#f97316;color:#f97316"`
  - V3.4 vs V3.7 同時存在時，保留雙版本對比區塊
- 底部說明文字：更新回測期間、過濾器配置

**C2. 版本歷程表格（xauusd-opt-overview 下方 `<table>`）**

找到版本歷程表（行含 `ver-confirmed` / `ver-test` class），在最上方新增一行：
```html
<tr style="background:rgba(34,197,94,.06)">
  <td>{策略ID}</td>
  <td class="ver-test">{版本} ★</td>
  <td><span class="badge badge-green">測試中</span></td>
  <td>{本版新增功能的一句話說明} ｜ <strong>TV 回測 {期間}：WR {x}%（{n}/{total}）· PF {x} · +${x}（+{x}%）· MDD ${x}（{x}%）</strong></td>
</tr>
```

**C3. 下載連結區塊（xauusd-opt-overview 底部的 download section）**

找到 Pine Script 下載按鈕區，加入新版本：
- 最新版（★）：綠色漸層 `background:linear-gradient(135deg,#14532d,#16a34a);border-color:#22c55e`
- 舊版：藍色漸層或預設樣式

**C4. 策略個別 Tab（e.g., xauusd-opt-s1）**

找到該策略 Tab 的 `report-links`，加入所有新報告連結：
```html
<a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/report_v2.html" style="border-color:#38bdf8;color:#38bdf8">📊 深度分析 V2</a>
<a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/report_s1_fail_short.html" style="border-color:#f97316;color:#f97316">🔴 Fail 空單測試</a>
```

若有新 TradingView 回測結果，也更新 PART 1 的 metric-card 數值。

**C5. 對話紀錄（最底部 conversation-log）**

找到最近的日期區塊，或新增一個 `<div class="session">` 加入本次重點：
```html
<div class="session">
  <div class="session-date">{YYYY-MM-DD}</div>
  <div class="log-item {green|blue|orange}">📊 {一句話說明本次更新}</div>
</div>
```

---

### D. Commit & Push 順序

**第一次 commit**（腳本 + 生成的 HTML 報告 + Pine Script）：
```bash
git add xauusd/run_s1_deep_analysis.py \
        xauusd/run_s1_fail_short.py \
        xauusd/XAUUSD-Long-S1-AweWithBB/report_v2.html \
        xauusd/XAUUSD-Long-S1-AweWithBB/report_s1_fail_short.html
git commit -m "feat: {說明}"
git push origin main
```

**第二次 commit**（index.html 更新）：
```bash
git add index.html
git commit -m "docs: index.html 補充 {版本} 報告連結與對比數據"
git push origin main
```

若兩者一起完成可合併為一次 commit。

---

## 常見遺漏項目（過去對話中反覆被提醒的）

| 遺漏點 | 解決方式 |
|--------|---------|
| 新 HTML 報告沒加到 index | 每次生成後立刻在 C4 加連結 |
| 綜合對比卡片版本號沒更新 | 每次新版本後同步 C1 badge |
| 版本歷程表沒有新行 | 每次新版本後同步 C2 |
| 舊版數值被蓋掉沒有對比 | 保留 V3.4 vs V3.7 對比區塊 |
| download 區沒有新 Pine | 每次新 Pine 後同步 C3 |
| 對話紀錄沒更新 | 每次 push 前同步 C5 |

---

## 報告 HTML 命名規則

| 報告 | 路徑 | 顏色 |
|------|------|------|
| V1 基礎報告 | `{策略資料夾}/report.html` | 預設藍 |
| V2 深度報告 | `{策略資料夾}/report_v2.html` | 藍 `#38bdf8` |
| Fail 空單測試 | `{策略資料夾}/report_s1_fail_short.html` | 橙 `#f97316` |
| 宏觀回測報告 | `xauusd/XAUUSD-Macro/real_macro_backtest_report.html` | 紫 |

---

## 頁面拆分建議（當 index.html > 4000 行時）

若 token 消耗過大，可將以下大 section 拆為獨立 HTML：
- `xauusd-opt-s1` Tab → `xauusd/XAUUSD-Long-S1-AweWithBB/strategy.html`
- `xauusd-opt-s2a` + `xauusd-opt-s2b` → `xauusd/s2_strategies.html`
- 操作手冊（Handbook）→ `xauusd/XAUUSD-Long-S1-AweWithBB/handbook_v3.7.html`

index.html 保留卡片摘要 + report-links，長文內容移到子頁面。
