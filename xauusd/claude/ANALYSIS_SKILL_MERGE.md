# XAUUSD 合併週報技術文件
# 版本：20260705-v5 | 觸發指令：「合併週報」（20260705起也會被「週日黃金工作流」自動接續觸發，見 ANALYSIS_SKILL_WEEKLY.md「Step 最終」）
# 20260705-v5：移除交易員C(Dispatch)，交易員A=Gemini／交易員B=Claude固定對應，Combine只產生Style C
# 本文件在「合併週報」觸發時讀取，或於「週日黃金工作流」產出 Claude 版週報後自動接續執行。日常分析請使用 ANALYSIS_SKILL.md。

---

## 合併週報流程（「合併週報」觸發）

### ⚠ 前置條件（執行前必查）

**Step 0：確認 Claude 當週報告存在**
```
路徑：/Users/tittan/googledrive/Github/trading/xauusd/claude/reports/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx
```
- 20260705起若是由「週日黃金工作流」自動接續觸發，此條件在當次對話中天然滿足，可直接跳過此檢查
- 若是使用者手動下「合併週報」指令觸發、且找不到本週 Claude 報告 → 先執行「週日黃金工作流」生成，再合併
- 若存在但日期差 > 7 天（舊週）→ 同上，重新生成當週報告
- ❌ 絕對不能用舊週的 Claude 報告當交易員 A（W24 教訓：用 W23 Wed 導致所有價位過時）

**Step 0.5：讀取 Macro Dashboard（20260705 起改為文字檔記錄，不再依賴使用者手動存 PNG）**

資料夾：`/Users/tittan/googledrive/XAUUSD/weekly report/macro/`

**標準流程（主要方式，20260705 起）：文字檔 `macro-YYYYMMDD.txt`**
```
1. 確認使用者的 Chrome 已開啟 TradingView 圖表（含 Macro Dashboard 面板，
   通常是同一張存有 S1/S2 指標的個人 chart layout，例如 y23HVHHP）。
2. 用 computer-use 的 request_access 取得 Google Chrome 唯讀畫面存取權限。
3. open_application 把 Chrome 帶到前景 → screenshot（必要時 zoom 進 Macro
   Dashboard 面板區域，通常在圖表右下角，欄位為 Asset / Macro / Now / Val / Bias）。

   ⚠️ 重要限制：不可用 Chrome MCP（mcp__claude-in-chrome__* 自己開的分頁）截圖
   讀這個面板 —— 該分頁是背景渲染，canvas 內容（K棒、Pine Script overlay 表格）
   不會畫出來，截圖會是空白。必須用 computer-use 對「使用者已經開啟、正在前景
   顯示」的真實 Chrome 視窗做原生螢幕截圖，才能讀到即時渲染的畫面。
4. 讀出以下欄位數值後，寫成文字檔存入 macro/ 資料夾，檔名
   `macro-YYYYMMDD.txt`（YYYYMMDD 為讀取當天日期）。
5. 內容需包含：截圖時間（Asia/Taipei）、Real Rate、US 10Y、DXY Index、
   VIX Index、GVZ(Vol)、XAU(Now)/XAU(1h)/XAU(4h)、綜合判定
   （STRONG BUY / NEUTRAL / WAIT，若面板只顯示燈號 banner 沒有明確 X/6
   分數方塊，就記錄燈號判定，不強行推算分數）。可參考
   `macro/macro-20260705.txt` 的格式。
```

**備援流程（若使用者仍手動存了截圖，或 computer-use 無法使用）：舊版 PNG 判讀邏輯**
```bash
# 找最新截圖
ls "/Users/tittan/googledrive/XAUUSD/weekly report/macro/" | sort | tail -1
```
→ 用 Read 工具讀取該圖片（Claude 有 vision 能力，直接解讀儀表板）

**讀取優先序：** 每次先找 `macro/` 資料夾裡「日期最新」的檔案，不論是 `.txt` 或 `.png`，只要日期最新就用它；`.txt` 與 `.png` 判讀邏輯共用下方同一套欄位定義。

**從截圖或文字檔提取以下欄位：**
| 欄位 | Pine Script 列名 | 說明 |
|------|-----------------|------|
| `real_rate` | Real Rate / Val | 數值（如 2.205）|
| `real_rate_trend` | Real Rate / Macro | Bull ↗ 或 Bear ↘ |
| `us10y` | US 10Y / Val | 數值（如 4.455）|
| `dxy` | DXY Index / Val | 數值（如 100.781）|
| `dxy_trend` | DXY Index / Now | Bull ↗ 或 Bear ↘（本地趨勢）|
| `vix` | VIX Index / Val | 數值（如 16.41）|
| `gvz` | GVZ (Vol) / Val | 數值（如 27.9）|
| `gvz_status` | GVZ Bias 欄 | 🧊 SQZ / 🌊 Normal / 🔥 Extreme |
| `xau_4h_diff` | XAU(4h) 乖離 | 正數 = 價在MA上，負數 = 價在MA下 |
| `macro_score` | 最底列 | STRONG BUY / NEUTRAL / WAIT |

**評分邏輯（Pine Script v3.6 原始算法）：**
| 因子 | 黃金有利條件 | 分數 |
|------|------------|------|
| Real Rate | Macro Bear（實質利率下降）| **+2**（雙倍）|
| US 10Y | Macro Bear（名目利率下降）| +1 |
| DXY Index | Macro Bear（美元走弱）| +1 |
| VIX Index | Macro Bull（恐慌上升，避險需求）| +1 |
| Gold MA趨勢 | Macro Bull（黃金日線 > MA50）| +1 |
| **滿分** | | **6分** |

- 5–6 分 → **STRONG BUY**：宏觀順風，S1 正常執行；S2A 縮倉（見下方）
- 3–4 分 → **NEUTRAL**：**S1 和 S2A 表現最佳的黃金環境**，依技術信號正常執行
- 0–2 分 → **WAIT**：宏觀逆風，S1 完全不做，S2 縮倉

**各策略宏觀最佳環境（2024-01 → 2026-04，真實交易回測，N=504/160/199）：**
| 策略 | STRONG BUY | NEUTRAL | WAIT | 結論 |
|------|-----------|---------|------|------|
| S1-AweWithBB | WR 52.1% PF 1.46 | **WR 58.7% PF 2.08 ★** | WR 51.8% PF 1.39 | NEUTRAL 最佳；WAIT 過濾有效（PF +0.12）|
| S2A-RSI | **WR 34.4% PF 1.26 ⚠️** | **WR 66.7% PF 4.71 ★** | WR 41.3% PF 1.58 | STRONG BUY 最危險；NEUTRAL 最佳 |
| S2B-Hammer | WR 44.4% PF 1.71 | WR 46.2% PF 1.80 | WR 42.0% PF 1.59 | 各環境均穩，宏觀敏感度最低 |

> **S2A-RSI 反直覺發現**：STRONG BUY（黃金宏觀順風）反而是 S2A 最差的進場環境。
> 原因：趨勢強勁上漲時，RSI 逆勢信號頻繁假突破，進場即被洗出。
> **結論：STRONG BUY 環境應縮 S2A 倉位，而非積極執行。**

**GVZ 狀態 → 操作含義：**
| GVZ 狀態 | 門檻 | 含義 | 操作調整 |
|---------|------|------|---------|
| 🧊 SQZ | < 13 | 黃金波動收縮，蓄勢待發 | S1 優先（突破策略有利）|
| 🌊 Normal | 13–20 | 標準波動環境 | S1 / S2 皆可正常執行 |
| 🔥 Extreme | > 20 | 事件驅動高波動 | 縮倉 50%，S2 為主，S1 慎用 |

**宏觀 × 技術面衝突裁決（依 2024-2026 真實回測更新）：**
| 宏觀 | 技術面 | S1-AweWithBB | S2A-RSI | S2B-Hammer |
|------|--------|-------------|---------|-----------|
| WAIT | 技術看多 | ⛔ 不執行 | 0.02 手（極限縮倉）| 0.02 手（縮倉）|
| WAIT | 技術看空 | — | 確認不做多，等宏觀好轉 | — |
| NEUTRAL | 技術看多 | ✅ 正常執行（最佳）| ✅ 0.05 手正常執行（最佳）| ✅ 正常執行 |
| STRONG BUY | 技術看多 | 正常執行（略遜 NEUTRAL）| ⚠️ 縮倉 0.01 手（回測最差）| ✅ 正常執行 |
| STRONG BUY | 技術看空 | 等確認，偏向看多不強搶 | 同上 | 同上 |

**Real Rate 是核心驅動（雙倍權重的意義）：**
- Real Rate Bear + DXY Bear = 最強多頭組合（即使 VIX 低也有支撐）
- Real Rate Bull（上升）= 黃金最大逆風，此時其他因子即使全綠也要謹慎
- Real Rate 目前 2.205（高位）且 Macro Bull = 黃金長期壓制

**「宏觀結論一句話」寫法：**
格式：`宏觀 {N}/6（{WAIT/NEUTRAL/STRONG BUY}）：{最關鍵因子} → 本週 {操作調整}`

範例：
- `宏觀 2/6（WAIT）：實質利率2.2高位+DXY未見回落 → 本週S2縮0.02手，不追S1`
- `宏觀 5/6（STRONG BUY）：實質利率轉跌+DXY破支撐 → S1正常執行，S2A縮0.01手（STRONG BUY期S2A回測最差）`
- `宏觀 3/6（NEUTRAL）：VIX低+DXY混沌，GVZ Extreme → S1/S2A黃金環境，縮倉50%（GVZ）但信號品質高`

**若找不到任何記錄（.txt 或 .png 皆無）：**
- 先嘗試 Step 0.5 標準流程（computer-use 讀取使用者 Chrome 現有畫面並寫成 .txt）
- 仍無法取得時，在 Combine 報告中標注「宏觀資料未提供，跳過 Macro 段落」
- 繼續執行後續步驟，不強制中斷

### 兩份週報來源（20260705 起：移除 Dispatch，只比對 Gemini × Claude）

**交易員 A = Gemini　交易員 B = Claude**（20260705 起固定這個對應，不再對調）

```
① 交易員 A — Gemini 週報（用戶手動生成，Google Drive 存為 .gdoc，6個月track record，主要信任來源）
   路徑：/Users/tittan/googledrive/XAUUSD/weekly report/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}.gdoc
   讀取：browser-cookie3（見下方，已驗證 HTTP 200，不需用戶介入）或 mobilebasic 網頁版
   ⚠ 格式是 .gdoc（190 bytes JSON 指標），不是真正文件

② 交易員 B — Claude 週報（本次「週日黃金工作流」生成的獨立版）
   路徑：/Users/tittan/googledrive/Github/trading/xauusd/claude/reports/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx
   讀取：python-docx（見下方）
```

> 20260705 之前的舊版流程還有「交易員 C（Dispatch）」，讀取
> `xauusd/daily_log/weekly_report_W{週次}_*.txt`。使用者已確認移除，
> Combine 報告不再產生 Dispatch 相關段落，本節與下方結構皆已同步移除。

### 讀取技巧
```python
# Claude .docx（python-docx）
pip install python-docx --break-system-packages -q
from docx import Document
text = '\n'.join([p.text for p in Document('/path/file.docx').paragraphs if p.text.strip()])
```

```python
# Gemini .gdoc（browser-cookie3 直接讀取，不需 Chrome MCP，不需用戶介入）
# 前提：Chrome 已登入 Google 帳號（.gdoc 掛載即代表已登入）
# 驗證：2026-06-21 測試成功（HTTP 200，內容完整）

import browser_cookie3, requests

# Step 1: Read .gdoc 取出 doc_id
# doc_id = json.loads(open(gdoc_path).read())["doc_id"]

# Step 2: 用 Chrome cookies 直接 export 純文字
cj = browser_cookie3.chrome(domain_name='.google.com')
url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
r = requests.get(url, cookies=cj, allow_redirects=True, timeout=15,
                 headers={"User-Agent": "Mozilla/5.0"})
# r.status_code == 200 → r.text 即為完整週報內文

# 安裝（若缺）：pip3.12 install browser-cookie3 --break-system-packages -q
# ⚠ 若 401：Chrome 尚未登入 Google，讓用戶登入後重試
# ❌ WebFetch export?format=txt → 401（未授權，不可用）
# ❌ DriveFS server_token → 401（僅供 DriveFS 內部使用，不可用）
```

### 有效性判斷
- 兩份報告日期差距 < 7 天 → 可合併
- 若有時間差 → 在報告中標注，以較新的 Gemini 為現況基準
- 若缺少某份報告 → 提示用戶，不強行合併

### 執行步驟
1. **確認 Claude 當週報告存在**（見 Step 0）
2. **讀取宏觀截圖**（見 Step 0.5）→ 記錄 Macro Score + 各指標值
3. **讀取兩份報告**，各自提取：主劇本 + 機率、關鍵支撐/阻力、S1/S2 條件、本週最大風險
4. **製作共識/分歧對照表**（2 欄：交易員A/Gemini vs 交易員B/Claude）
5. **只生成 Style C 一份 Combine .docx**（20260705 起簡化，格式見下方，含宏觀段落）
6. **⚡ 自動更新 index.html**（見下方「Step 6」段落，必跑）

### Combine 輸出格式（20260705 起只產生 Style C 一份）
```
輸出路徑：/Users/tittan/googledrive/Github/trading/xauusd/claude/reports/
命名：XAUUSD_W{週次}_Combine_StyleC.docx
（不再產生 StyleA / StyleB，舊週次留存的 A/B 檔案可忽略或手動清除）

檔案結構：
1. 標題：【黃金劍盾週報 Combine】W{N} — 雙交易員觀點整合
2. 審核日期
3. 宏觀環境摘要（Macro Dashboard）
   - Macro Score：STRONG BUY / NEUTRAL / WAIT
   - 關鍵數值：Real Rate {值}（{Bull/Bear}）/ US10Y {值} / DXY {值}（{Now趨勢}）
   - VIX {值} / GVZ {值}（{🧊/🌊/🔥}）/ XAU 4H 乖離 {值}
   - 宏觀結論一句話（對本週操作的影響）
4. 兩份報告概覽表（交易員 / 日期 / 主情境）
5. 交易員 A（Gemini）核心觀點
6. 交易員 B（Claude）核心觀點
7. 共識與分歧對照表（含仲裁結論）
8. 主管審核意見（Style C 風格，投資委員會正式審核版）
```

### Style 風格定義（20260705 起只保留 Style C）
```
Style C — 投資委員會正式審核版
  輸出：一、報告說明 / 二、共識事項 / 三、分歧與決議 / 四、操作決議表格 / 五、下次審核
  語氣：正式會議紀錄，逐條決議
```

### Step 6：自動更新 index.html（Merge 完成後必跑）

Combine 生成完成後，從仲裁結論中提取共識欄位，儲存 JSON 並呼叫 Python。

**共識欄位說明：**
| 欄位 | 來源 | 說明 |
|------|------|------|
| `week` | 本週週次（如 W26） | 命名用 |
| `day` | Sun / Wed | 命名用 |
| `price` | 最新收盤（從 CSV 也可自動取） | 現價 |
| `bias` | 仲裁結論 | 本週方向偏向（簡短） |
| `account` | context.md 帳戶餘額 | 顯示用 |
| `scenario2` | 仲裁主情境 + 機率 | 主劇本描述 |
| `s2` | 仲裁 S2 A+ 進場區 | 關鍵支撐數字 |
| `s1` | 仲裁 S1 觸發條件 | 突破確認條件 |
| `cftc_note` | CFTC 籌碼摘要（一句話） | 籌碼方向 |
| `scenario1_pct` / `scenario2_pct` / `scenario3_pct` | 仲裁機率分配 | 劇本機率 |
| `macro_score` | Step 0.5 截圖 | STRONG BUY / NEUTRAL / WAIT |
| `macro_real_rate` | Step 0.5 截圖 | 實質利率數值（如 2.205）|
| `macro_dxy` | Step 0.5 截圖 | DXY 數值（如 100.781）|
| `macro_vix` | Step 0.5 截圖 | VIX 數值（如 16.41）|
| `macro_gvz` | Step 0.5 截圖 | GVZ 數值 + 狀態（如 "27.9 🔥"）|
| `macro_date` | 截圖檔名 | 截圖日期（如 "2026-06-20"）|

**Python 執行碼（在 Bash tool 執行）：**
```python
import json, subprocess, os

# 從仲裁結論填入以下欄位
consensus = {
    "week": "W26",        # ← 填當週週次
    "day": "Sun",          # ← Sun 或 Wed
    "price": 4155.57,      # ← 最新收盤價
    "bias": "觀望，等S2 A+",    # ← 仲裁偏向（簡短）
    "account": 21649,      # ← context.md 帳戶餘額
    "scenario2": "震盪尋底 60%，等 4118 SSL Sweep + 錘頭",  # ← 主情境
    "s2": "4082-4118（日線/4H BB下軌）",   # ← S2 A+ 進場區
    "s1": "站回 1H 中軌 4165 + AO 翻正",  # ← S1 觸發條件
    "cftc_note": "MM 淨多微降，散戶追空；技術底部需確認",  # ← CFTC 一句話
    "scenario1_pct": 25,   # ← 劇本一機率
    "scenario2_pct": 60,   # ← 劇本二機率（主情境）
    "scenario3_pct": 15,   # ← 劇本三機率
    "source": "Combine（Claude × Gemini × Dispatch 仲裁）",
    "macro_score": "WAIT",          # ← 從截圖提取
    "macro_real_rate": 2.205,       # ← 從截圖提取
    "macro_dxy": 100.781,           # ← 從截圖提取
    "macro_vix": 16.41,             # ← 從截圖提取
    "macro_gvz": "27.9 🔥",        # ← 從截圖提取（含狀態符號）
    "macro_date": "2026-06-20"      # ← 從截圖檔名提取
}

reports_dir = "/Users/tittan/googledrive/Github/trading/xauusd/claude/reports"
json_path = f"{reports_dir}/weekly_consensus_{consensus['week']}_{consensus['day']}.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(consensus, f, ensure_ascii=False, indent=2)
print(f"✅ 儲存 {json_path}")

result = subprocess.run(
    ['python3.12', 'xauusd/claude/generate_weekly_html.py', '--from-json', json_path],
    cwd='/Users/tittan/googledrive/Github/trading',
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("❌ 錯誤:", result.stderr)
```

**執行後確認：**
- `trading/index.html` 週報分析 tab 已更新（含宏觀摘要欄位）
- `xauusd/claude/reports/weekly_consensus_W{N}_{day}.json` 已儲存（含 macro_* 欄位）
- 報告歸檔 tab 自動掃 reports/ 目錄，新 Combine .docx 自動出現

---

### 參考提示詞位置
```
週報提示詞與生成 SOP 詳見 ANALYSIS_SKILL_WEEKLY.md「參考提示詞」段落。
若需重新生成 Claude 週報，先執行「週日黃金工作流」，再回來執行合併。
```
