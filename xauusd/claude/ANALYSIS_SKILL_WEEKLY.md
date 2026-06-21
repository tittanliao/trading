# XAUUSD 周報分析技術文件
# 版本：20260614 | 觸發指令：「週日黃金工作流」
# 本文件在「週日黃金工作流」觸發時讀取。日常分析請使用 ANALYSIS_SKILL.md。

---

## 周報分析流程（「週日黃金工作流」觸發）

### 資料準備

#### Step -1 — 更新 MGC 期貨資料（週報前必做）
```
1. 執行 launch.sh 抓取 MGC 最新資料（自動寫入 Google Drive）：
   /Users/tittan/program/github/trading/xauusd/fetcher/launch.sh

   執行完畢後，5 個 MGC 檔案已直接寫入：
   /Users/tittan/googledrive/XAUUSD/weekly report/csv/

2. XAUUSD 和 DXY 的 CSV 由用戶從 TradingView 手動匯出，確認已是最新版本
```

#### Step 0 — 確認資料即時性（15 個 CSV + CFTC）
```
CSV 路徑：/Users/tittan/googledrive/XAUUSD/weekly report/csv/
預期共 15 個檔案（各 5 個）：

FX_IDC_XAUUSD, 1D.csv     ← TradingView 匯出
FX_IDC_XAUUSD, 1W.csv
FX_IDC_XAUUSD, 240.csv
FX_IDC_XAUUSD, 60.csv
FX_IDC_XAUUSD, 30.csv
TVC_DXY, 1D.csv            ← TradingView 匯出
TVC_DXY, 1W.csv
TVC_DXY, 240.csv
TVC_DXY, 60.csv
TVC_DXY, 30.csv
MGC_1d.csv                 ← launch.sh 產生（yfinance）
MGC_1h.csv
MGC_1wk.csv
MGC_30m.csv
MGC_4h.csv

CFTC 截圖路徑：/Users/tittan/googledrive/XAUUSD/weekly report/cftc/
預期：最新檔名含上週二日期，如 GOLD-CFTC-20260609.png
```

#### 資料有效性確認
```python
# 確認最新資料日期（tail -3 任一 CSV）
tail -3 "FX_IDC_XAUUSD, 1D.csv"
# 若最後一筆距今 > 3 天，提醒用戶重新從 TradingView 匯出
```

#### 分析步驟
1. **抓取 CFTC 資料（必須用此順序）**
   ```
   Step A：先檢查用戶已備好的截圖（優先）
     ls /Users/tittan/googledrive/XAUUSD/weekly\ report/cftc/
     → 找最新 .png（檔名含日期，如 GOLD-CFTC-20260609.png）
     → CFTC 每週五公布前一個週二截止的數據
       範例：週六/日出週報時，應有截至當週週一前兩天（週二）的最新 .png
     → 用 Read 工具讀取圖片（Claude 可直接看圖提取數字）

   Step B：若 GDrive 截圖不是本週最新 → 再用 web_fetch 補抓
     URL：https://www.tradingster.com/cot/futures/disagg/088691
     注意：web_fetch 可能因頁面 JS 渲染失敗，改用 Chrome MCP navigate
   ```

   ⚠️ **絕對不能做**：直接沿用上一份週報（Dispatch/Claude/Gemini）的 CFTC 數字
   → W24 教訓：Dispatch 報告用了 6/2 舊數據，而 GDrive 早已有 6/9 截圖，多滯後 7 天

2. 讀取 CSV 並計算指標（Python / bash）
3. 計算 BB(20)、RSI(14)、ATR(14)、EMA(50/200)

#### Python 分析模板（每次週報使用）
```python
import pandas as pd, numpy as np
CSV_DIR = "/Users/tittan/googledrive/XAUUSD/weekly report/csv/"

def load_csv(fname):
    for enc in ['utf-8', 'utf-8-sig', 'big5', 'cp950']:
        try:
            df = pd.read_csv(CSV_DIR + fname, encoding=enc, encoding_errors='ignore')
            df['time'] = pd.to_datetime(df['time'])
            return df.sort_values('time').reset_index(drop=True)
        except: continue
    return None

xau_1d = load_csv("FX_IDC_XAUUSD, 1D.csv")
xau_1w = load_csv("FX_IDC_XAUUSD, 1W.csv")
xau_4h = load_csv("FX_IDC_XAUUSD, 240.csv")
dxy_1d = load_csv("TVC_DXY, 1D.csv")
dxy_1w = load_csv("TVC_DXY, 1W.csv")

# EMA
for df in [xau_1d, xau_4h]:
    df['ema50']  = df['close'].ewm(span=50).mean()
    df['ema200'] = df['close'].ewm(span=200).mean()

# ATR
def calc_atr(df, n=14):
    tr = pd.concat([df['high']-df['low'],
                    (df['high']-df['close'].shift()).abs(),
                    (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean().iloc[-1]

atr_4h = calc_atr(xau_4h)

# ── SMC Context 掃描（接在上方模板後執行）────────────────────────────────────

def scan_fvg(df, lookback_bars=50):
    """掃描最近 N 根 K 棒內未填補的 FVG。"""
    h, l, c = df['high'].values, df['low'].values, df['close'].values
    n = len(df)
    bull_fvgs, bear_fvgs = [], []
    for j in range(2, n):
        if h[j-2] < l[j]:   # Bullish FVG（上行衝動留下的缺口）
            bull_fvgs.append({'bar': j, 'bottom': round(h[j-2], 2), 'top': round(l[j], 2)})
        if l[j-2] > h[j]:   # Bearish FVG（下行衝動留下的缺口）
            bear_fvgs.append({'bar': j, 'bottom': round(h[j], 2), 'top': round(l[j-2], 2)})
    active_bull = [z for z in bull_fvgs if z['bar'] >= n - lookback_bars
                   and not any(l[k] <= z['bottom'] for k in range(z['bar'], n))]
    active_bear = [z for z in bear_fvgs if z['bar'] >= n - lookback_bars
                   and not any(h[k] >= z['top'] for k in range(z['bar'], n))]
    return active_bull[-3:], active_bear[-3:]

def scan_liquidity(df, lookback_bars=30):
    """找出 BSL（擺動高點 / 買方流動性）和 SSL（擺動低點 / 賣方流動性）。"""
    h, l = df['high'].values, df['low'].values
    n = len(df)
    bsl, ssl = [], []
    for i in range(2, min(lookback_bars, n - 2)):
        idx = n - 1 - i
        if idx < 2: break
        if h[idx] > h[idx-1] and h[idx] > h[idx-2] and h[idx] > h[idx+1] and h[idx] > h[idx+2]:
            bsl.append(round(h[idx], 2))
        if l[idx] < l[idx-1] and l[idx] < l[idx-2] and l[idx] < l[idx+1] and l[idx] < l[idx+2]:
            ssl.append(round(l[idx], 2))
    return sorted(set(bsl), reverse=True)[:3], sorted(set(ssl))[:3]

def check_ssl_sweep(df, lookback_bars=5):
    """最近 N 根是否有 SSL sweep（下影刺破近期低點後收回 → S2 信心+1）。"""
    l, c = df['low'].values, df['close'].values
    n = len(df)
    for i in range(n - lookback_bars, n):
        if i < 31: continue
        prior_low = l[i-30:i].min()
        if l[i] < prior_low and c[i] > prior_low:
            return True, round(prior_low, 2)
    return False, None

# 執行（用 4H 資料）
bull_fvg_4h, bear_fvg_4h = scan_fvg(xau_4h, lookback_bars=50)
bsl_4h, ssl_4h             = scan_liquidity(xau_4h, lookback_bars=30)
ssl_swept, ssl_level        = check_ssl_sweep(xau_4h, lookback_bars=5)

print("=== SMC Context（4H）===")
print(f"Bearish FVG 阻力：{[(z['bottom'], z['top']) for z in bear_fvg_4h] or '無'}")
print(f"Bullish FVG 支撐：{[(z['bottom'], z['top']) for z in bull_fvg_4h] or '無'}")
print(f"BSL（買方流動性）：{bsl_4h or '無'}")
print(f"SSL（賣方流動性）：{ssl_4h or '無'}")
print(f"SSL Sweep：{'✅ 有！位於 ' + str(ssl_level) + '  ← S2 A+ 信心+1' if ssl_swept else '❌ 無'}")
```

### 周報四模組架構

**Module A：大格局（Context）**
- 週線/日線結構（多頭/空頭/盤整）
- DXY 相關性（反向標準）
- Daily ATR(14) 波動警示

**Module B：關鍵價位（Key Levels）**
- Python 計算 BB + EMA(50/200) for 1D / 4H / 1H
- 找出「匯聚區」（Confluence Zone）：例如日線 Basis + 4H Lower Band 重疊
- S2 支撐區分三級：
  - Zone 1（積極）：1H/4H BB Lower
  - Zone 2（標準）：Daily BB Basis
  - Zone 3（極限）：Weekly/Daily BB Lower + 整數關口

**Module B+：SMC Context（FVG / OB / 流動性）**
- 執行上方 SMC Python 掃描，輸出 4H 級別結果
- **Bearish FVG**（阻力）：S1 突破須清掉此區才算有效，否則縮倉
- **Bullish FVG**（支撐）：S2 進場若落在此區，等級自動升一格（B→A）
- **BSL 位置**（買方流動性 / 前擺動高點）：S1 TP 目標參考；BSL 被清掉後反轉 = 做空信號
- **SSL 位置**（賣方流動性 / 前擺動低點）：S2 候選進場區；若本週已出現 SSL sweep → S2 信心升 A+
- **S1 SMC 品質輔助判斷**：
  - ✅ 加分：突破位同時清掉 BSL（機構掃停損後繼續推）
  - ⚠️ 注意：突破位處於 Bearish FVG 內（遇阻力，考慮分批或縮倉）
  - ❌ 警示：突破後仍在大 Bearish FVG 陰影下（假突破風險高）

**Module C：作戰劇本（Battle Plan）**
- S1 計畫：定義具體「突破位」（1H EMA 50）
- S2 計畫：定義 A+ 支撐區
- 三種劇本（多頭/震盪/空頭）+ 機率

**Module D：輸出格式**
- 嚴格 Markdown 結構 + emoji（🚀 S1, 🛡️ S2）
- 必含「紀律提醒」段落

### 周報輸出格式
1. 標題：`【黃金劍盾週報】W[週數] [副標題]`
2. 四週大格局全覽（表格）
3. 交易員備忘錄（5點）
4. CFTC 籌碼數據事實（表格 + 解讀）
5. 關鍵價位總表（5-10個，表格）
6. SMC Context（4H 掃描結果，格式如下）
7. 下週三種劇本（多頭/震盪/空頭 + 機率）
8. 策略執行劇本（S1 A+/A/B，S2 A+/A/B 含 SMC 等級）
9. 結語（心理建設 + 風控提醒）

**SMC Context 輸出格式（第 6 項）：**
```
🔍 SMC Context（4H 掃描）
Bearish FVG（阻力）：XXXX–XXXX / XXXX–XXXX
Bullish FVG（支撐）：XXXX–XXXX（若無則標「本週無未填 FVG」）
BSL 位置（前高 / 買方流動性）：XXXX, XXXX → S1 突破參考
SSL 位置（前低 / 賣方流動性）：XXXX, XXXX → S2 進場候選
本週 SSL Sweep：[✅ 有，位於 XXXX → S2 信心升 A+] / [❌ 無]
S1 品質：[✅ 突破清掉 BSL / ⚠️ 在 FVG 內突破 / ❌ FVG 阻力未清]
```

### 週報頻率
- **週末週報**：週六或週日
- **週間週報**：通常週三晚上
- **緊急週報**：超大波動時加開，加入本週收盤預測 + 下週三種劇本

### 週報輸出路徑
```
/Users/tittan/program/github/trading/xauusd/claude/reports/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx
```

### 參考提示詞（生成週報前必讀）
```
提示詞（Google Doc）：
Doc ID：1gKMZbIKcKTT3BWk2r0_BQQrWBfTEPyGps0qQzfhYj8w
讀取：mcp__Claude_in_Chrome__navigate 開啟
      https://docs.google.com/document/d/1gKMZbIKcKTT3BWk2r0_BQQrWBfTEPyGps0qQzfhYj8w/edit
      → scroll+screenshot 讀取完整內文

完整 SOP：已整合進本文件（ANALYSIS_SKILL_WEEKLY.md）Step -1 至週報輸出格式
```
