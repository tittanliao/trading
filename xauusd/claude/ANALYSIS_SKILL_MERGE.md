# XAUUSD 合併週報技術文件
# 版本：20260621 | 觸發指令：「合併週報」
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
1. **確認 Claude 當週報告存在**（見前置條件）
2. **讀取三份報告**，各自提取：主劇本 + 機率、關鍵支撐/阻力、S1/S2 條件、本週最大風險
3. **製作共識/分歧對照表**（3 欄：Claude / Gemini / Dispatch）
4. **生成三個 Style Combine .docx**
5. **⚡ 自動更新 index.html**（見下方「Step 5」段落，必跑）

### Combine 輸出格式（三個 Style，各一份）
```
輸出路徑：/Users/tittan/program/github/trading/xauusd/claude/reports/
命名：XAUUSD_W{週次}_Combine_Style{A/B/C}.docx

每份檔案結構：
1. 標題：【黃金劍盾週報 Combine】W{N} — 三交易員觀點整合
2. Style 標識 + 審核日期
3. 三份報告概覽表（交易員 / 日期 / 主情境）
4. 交易員 A（Claude）核心觀點
5. 交易員 B（Gemini）核心觀點
6. 交易員 C（Dispatch）核心觀點
7. 共識與分歧對照表（含仲裁結論）
8. 主管審核意見（各 Style 風格）
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

### Step 5：自動更新 index.html（Merge 完成後必跑）

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
    "source": "Combine（Claude × Gemini × Dispatch 仲裁）"
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
- `xauusd/index.html` 週報分析 tab 已更新
- `xauusd/claude/reports/weekly_consensus_W{N}_{day}.json` 已儲存
- 報告歸檔 tab 自動掃 reports/ 目錄，新 Combine .docx 自動出現

---

### 參考提示詞位置
```
週報提示詞與生成 SOP 詳見 ANALYSIS_SKILL_WEEKLY.md「參考提示詞」段落。
若需重新生成 Claude 週報，先執行「週日黃金工作流」，再回來執行合併。
```
