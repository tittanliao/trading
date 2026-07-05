---
name: reference_gdoc_read
description: 用 browser-cookie3 從 Chrome cookies 讀取 Google Doc 純文字，不需用戶介入、不需 Chrome MCP
metadata: 
  node_type: memory
  type: reference
  originSessionId: bb0c5637-7e16-4d56-8fa0-1f184c485a39
---

## Google Doc 自動讀取方法（已驗證）

**驗證日期**：2026-06-21  
**使用場景**：週報合併時讀取 Gemini .gdoc 週報

### 方法：browser-cookie3 + requests

```python
import browser_cookie3, requests, json

# 1. 從 .gdoc 指標檔取出 doc_id
gdoc_path = "/Users/tittan/googledrive/XAUUSD/weekly report/XAUUSD_Weekly_Report_2026W25_Sun.gdoc"
doc_id = json.loads(open(gdoc_path).read())["doc_id"]

# 2. 用 Chrome cookies 匯出純文字
cj = browser_cookie3.chrome(domain_name='.google.com')
url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
r = requests.get(url, cookies=cj, allow_redirects=True, timeout=15,
                 headers={"User-Agent": "Mozilla/5.0"})

if r.status_code == 200:
    text = r.text  # 完整週報內文
```

**安裝（若缺）**：`pip3.12 install browser-cookie3 --break-system-packages -q`

### 前提
- Chrome 已登入 Google 帳號（Google Drive 有掛載即代表已登入）
- Python 3.12 可用

### 已確認無效的方法
- `WebFetch export?format=txt` → HTTP 401（未授權）
- `DriveFS server_token` → HTTP 401（僅供 DriveFS 內部，無 Docs API 權限）
- `Chrome MCP scroll+screenshot` → 可用但需 Chrome MCP，Claude Code 無此工具
- `export?format=txt` 直接瀏覽器開 → 會觸發下載，不回傳 HTML

### 已更新的 Skill 檔案
`/Users/tittan/googledrive/Github/trading/xauusd/claude/ANALYSIS_SKILL_MERGE.md`（Gemini 讀取段落）
