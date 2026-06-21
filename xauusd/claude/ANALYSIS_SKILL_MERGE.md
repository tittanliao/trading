# XAUUSD 合併週報技術文件
# 版本：20260614 | 觸發指令：「合併週報」
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
   讀取：Read .gdoc 取 doc_id → Chrome MCP navigate → scroll+screenshot
   ⚠ 格式是 .gdoc，不是 .txt

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

```
// Gemini .gdoc（Read .gdoc → Chrome MCP navigate → scroll+screenshot）
// Step 1: Read .gdoc 檔案，取出 "doc_id" 欄位（.gdoc 是 190 byte JSON 指標）
// Step 2: mcp__Claude_in_Chrome__navigate 開啟：
//           https://docs.google.com/document/d/{doc_id}/edit
// Step 3: mcp__Claude_in_Chrome__browser_batch 搭配 scroll + screenshot 逐頁捲動截圖
// ⚠ 注意：
//   - get_page_text 只能讀到目錄，無法讀到內文，必須用 scroll+screenshot
//   - 需用戶 Chrome 已登入 Google 帳號
//   - export?format=txt 方式已廢棄（無法讀到正文內容）
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

### 參考提示詞位置
```
週報提示詞與生成 SOP 詳見 ANALYSIS_SKILL_WEEKLY.md「參考提示詞」段落。
若需重新生成 Claude 週報，先執行「週日黃金工作流」，再回來執行合併。
```
