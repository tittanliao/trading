# XAUUSD 合併週報技術文件
# 版本：20260622 | 觸發指令：「合併週報」
# 本文件在「合併週報」觸發時讀取。日常分析請使用 ANALYSIS_SKILL.md。

---

## 合併週報流程（「合併週報」觸發）

### ⚠ 前置條件（執行前必查）

**Step 0：確認 Claude 當週報告存在**
```
路徑：/Users/tittan/program/github/trading/xauusd/claude/reports/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx
```
- 若不存在 → 先執行「週日黃金工作流」生成 Claude 版本，再合併
- 若存在但日期差 > 7 天（舊週）→ 同上，重新生成當週報告
- ❌ 絕對不能用舊週的 Claude 報告當交易員 A（W24 教訓：用 W23 Wed 導致所有價位過時）

**Step 0.5：讀取宏觀截圖（Macro v3.6 Dashboard）**

資料夾：`/Users/tittan/googledrive/XAUUSD/weekly report/macro/`
命名格式：`macro-YYYYMMDD.png`（取最新日期那張）

```bash
# 找最新截圖
ls "/Users/tittan/googledrive/XAUUSD/weekly report/macro/" | sort | tail -1
```

→ 用 Read 工具讀取該圖片（Claude 有 vision 能力，直接解讀儀表板）

**從截圖提取以下欄位：**
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

- 5–6 分 → **STRONG BUY**：宏觀順風，全力執行技術信號
- 3–4 分 → **NEUTRAL**：宏觀混合，依技術信號正常執行
- 0–2 分 → **WAIT**：宏觀逆風，縮倉或暫停

**GVZ 狀態 → 操作含義：**
| GVZ 狀態 | 門檻 | 含義 | 操作調整 |
|---------|------|------|---------|
| 🧊 SQZ | < 13 | 黃金波動收縮，蓄勢待發 | S1 優先（突破策略有利）|
| 🌊 Normal | 13–20 | 標準波動環境 | S1 / S2 皆可正常執行 |
| 🔥 Extreme | > 20 | 事件驅動高波動 | 縮倉 50%，S2 為主，S1 慎用 |

**宏觀 × 技術面衝突裁決：**
| 宏觀 | 技術面 | 裁決 |
|------|--------|------|
| WAIT | 技術看多 | S2 只用 0.02 手（極限縮倉），完全不做 S1 |
| WAIT | 技術看空 | 確認不做多，等宏觀好轉 |
| NEUTRAL | 技術看多 | 正常執行，S2 A+ 0.05手，S2 A 0.03手 |
| STRONG BUY | 技術看多 | 積極執行，S1 也可參與 |
| STRONG BUY | 技術看空 | 等技術面確認，偏向做多但不強搶 |

**Real Rate 是核心驅動（雙倍權重的意義）：**
- Real Rate Bear + DXY Bear = 最強多頭組合（即使 VIX 低也有支撐）
- Real Rate Bull（上升）= 黃金最大逆風，此時其他因子即使全綠也要謹慎
- Real Rate 目前 2.205（高位）且 Macro Bull = 黃金長期壓制

**「宏觀結論一句話」寫法：**
格式：`宏觀 {N}/6（{WAIT/NEUTRAL/STRONG BUY}）：{最關鍵因子} → 本週 {操作調整}`

範例：
- `宏觀 2/6（WAIT）：實質利率2.2高位+DXY未見回落 → 本週S2縮0.02手，不追S1`
- `宏觀 5/6（STRONG BUY）：實質利率轉跌+DXY破支撐 → 全倉位執行，S1 S2 皆有效`
- `宏觀 3/6（NEUTRAL）：VIX低+DXY混沌，GVZ Extreme → 縮倉50%，等事件落地`

**若找不到截圖：**
- 在 Combine 報告中標注「宏觀截圖未提供，跳過 Macro 段落」
- 繼續執行後續步驟，不強制中斷

### 三份週報來源
```
① Claude 週報（本次生成）
   路徑：/Users/tittan/program/github/trading/xauusd/claude/reports/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx
   讀取：python-docx（見下方）

② Gemini 週報（用戶手動生成，Google Drive 存為 .gdoc）
   路徑：/Users/tittan/googledrive/XAUUSD/weekly report/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}.gdoc
   讀取：browser-cookie3（見下方，已驗證 HTTP 200，不需用戶介入）
   ⚠ 格式是 .gdoc（190 bytes JSON 指標），不是真正文件

③ Dispatch 週報（分析生成）
   路徑：/Users/tittan/program/github/trading/xauusd/daily_log/weekly_report_W{週次}_{YYYYMMDD}.txt
   讀取：Read 工具或 bash cat
```

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
- 三份報告日期差距 < 7 天 → 可合併
- 若有時間差 → 在報告中標注，以較新的 Gemini/Dispatch 為現況基準
- 若缺少某份報告 → 提示用戶，不強行合併

### 執行步驟
1. **確認 Claude 當週報告存在**（見 Step 0）
2. **讀取宏觀截圖**（見 Step 0.5）→ 記錄 Macro Score + 各指標值
3. **讀取三份報告**，各自提取：主劇本 + 機率、關鍵支撐/阻力、S1/S2 條件、本週最大風險
4. **製作共識/分歧對照表**（3 欄：Claude / Gemini / Dispatch）
5. **生成三個 Style Combine .docx**（格式見下方，含宏觀段落）
6. **⚡ 自動更新 index.html**（見下方「Step 6」段落，必跑）

### Combine 輸出格式（三個 Style，各一份）
```
輸出路徑：/Users/tittan/program/github/trading/xauusd/claude/reports/
命名：XAUUSD_W{週次}_Combine_Style{A/B/C}.docx

每份檔案結構：
1. 標題：【黃金劍盾週報 Combine】W{N} — 三交易員觀點整合
2. Style 標識 + 審核日期
3. 宏觀環境摘要（Macro v3.6 Dashboard）← 新增
   - Macro Score：STRONG BUY / NEUTRAL / WAIT
   - 關鍵數值：Real Rate {值}（{Bull/Bear}）/ US10Y {值} / DXY {值}（{Now趨勢}）
   - VIX {值} / GVZ {值}（{🧊/🌊/🔥}）/ XAU 4H 乖離 {值}
   - 宏觀結論一句話（對本週操作的影響）
4. 三份報告概覽表（交易員 / 日期 / 主情境）
5. 交易員 A（Claude）核心觀點
6. 交易員 B（Gemini）核心觀點
7. 交易員 C（Dispatch）核心觀點
8. 共識與分歧對照表（含仲裁結論）
9. 主管審核意見（各 Style 風格）
```

### 三個 Style 風格定義
```
Style A — 量化風控主管審核版
  輸出：共識確認 → 分歧量化仲裁（數字/機率）→ 收斂操作建議 + 倉位上限
  語氣：精確、量化、冷靜

Style B — 資深老鳥主管拍板版
  輸出：【好消息】共識 → 【關於分歧】分析 → 【這週怎麼做】執行 → 【最重要一件事】
  語氣：口語化、大白話、有人情味

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

reports_dir = "/Users/tittan/program/github/trading/xauusd/claude/reports"
json_path = f"{reports_dir}/weekly_consensus_{consensus['week']}_{consensus['day']}.json"
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(consensus, f, ensure_ascii=False, indent=2)
print(f"✅ 儲存 {json_path}")

result = subprocess.run(
    ['python3.12', 'xauusd/claude/generate_weekly_html.py', '--from-json', json_path],
    cwd='/Users/tittan/program/github/trading',
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
