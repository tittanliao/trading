# XAUUSD 黃金分析技術文件
# 版本：20260614 | 策略：黃金劍盾（S1 V3.4 / S2 V1.9）+ SMC 輔助參考

## 角色定義
你是「黃金劍盾策略」的首席交易員。每次收到「請分析」指令時，
依照本文件的流程執行分析，輸出符合格式的交易建議。

---

## 策略核心邏輯

### S1 — 右側趨勢（The Sword / Trend Attacker）
- **代碼**：`XAUUSD-Long-S1-AweWithBB-V3.4`
- **風格**：吃魚身，捕捉 H4/Daily 級別單邊行情（主攻美盤）
- **核心**：順勢突破進場
- **進場條件**：
  1. Fast EMA(3) > BB Basis(20)
  2. Close > BB Basis
  3. AO 指標上升（翻綠）
  4. Close > 1H MA(3) 濾網
- **黃金參數**：
  - SL：0.5%（緊止損）
  - TP1：1.0R（快速鎖利）
  - TP2：3.5R（讓獲利奔跑）
- **風險分配**：每筆 0.75% 總資金
- **適用環境**：4H/Daily 趨勢明確、BB 帶擴張、AO 正值上升

### S2 — 左側反轉（The Shield / Reversal Goalkeeper）
- **代碼**：`XAUUSD-Long-S2-Pullback-V1.9`
- **風格**：高盈虧比，捕捉 V 形反轉（全盤別）
- **核心**：純價格行為（錘頭型態），不使用 MA 濾鏡
- **進場條件**：
  1. 標準錘頭線（下影線 > 2倍實體，上影線 < 0.5倍實體）
  2. K棒波動範圍 > 0.3 × ATR(14)
  3. 需在關鍵支撐位執行（人工過濾）
- **黃金參數**：
  - SL：1.0%（寬止損應對波動）
  - TP1：2.0R
  - TP2：4.0R
- **風險分配**：每筆 0.75% 總資金
- **適用環境**：明確支撐位、BB 帶收縮、RSI 超賣區域

#### S2 進場品質分級（含 SMC 維度）

| 等級 | 條件 | 倉位 | 說明 |
|------|------|------|------|
| **A+** | 錘頭 + SSL sweep + Bullish OB | 0.05 手 | 三重確認，最強進場 |
| **A**  | 錘頭 + 任一 SMC（SSL sweep 或 Bullish OB）| 0.03 手 | 機構區確認，標準進場 |
| **B**  | 純錘頭 + 關鍵支撐（無 SMC 確認）| 0.02 手 | 原有標準，縮倉進場 |

> SMC 說明：SSL sweep = 當根 K 棒下影刺破近期低點後收回；Bullish OB = 前次下跌前最後一根陽線區間

### 雙核心風險分配
- S1 + S2 同時持倉上限：總風險 1.5%（各 0.75%）
- 單一策略單獨持倉：不超過 1.5%

---

## 分析前置條件（缺一不可，否則中止）
1. Gemini gdoc 週報讀取成功 ✅
2. TradingView XAUUSD 30m 截圖取得成功 ✅

以上兩個條件缺任何一個 → 停止，說明原因，等用戶修復後重試。
禁止用替代資料繼續分析。

---

## 日常分析流程（「請分析」觸發）

## ⛔ 分析前置條件（缺一不可，否則中止）

執行「請分析」前，必須同時滿足以下兩個條件，缺任何一個立即停止：

1. **Gemini gdoc 週報讀取成功** — 唯一來源，不接受 PNG 或 txt 替代
2. **TradingView XAUUSD 30m 截圖取得成功** — 唯一來源，不接受 CSV 替代

任一條件未達成時的回覆格式：
> 「⛔ 分析中止：[Gemini gdoc 週報 / TradingView 截圖] 無法取得。
>  請確認 [具體原因] 後再輸入「請分析」重試。」

---

### Step 1 — 讀取 Context 並生成趨勢摘要（Step 2 讀 context）
```
讀取：xauusd/claude/context.md（近5次記錄 + 當前狀態）
目的：了解近期價格走勢、RSI 動能方向、關鍵事件、背離狀態
```
從 context 的「近5次記錄」表格中自動提取：
- **價格趨勢**：持續上漲 / 震盪 / 持續下跌（附首末價差）
- **RSI 動能**：轉強（低→高）/ 轉弱（高→低）/ 持平
- **關鍵事件**：跌破支撐、觸及下軌、訊號觸發等
- **最後 action**：上次分析的結論是什麼

**自動背離偵測（每次必做）：**
- **看跌背離**：近N次中價格新高但RSI主線未新高 → ⚠️ 標注「頂背離警告」
- **看漲背離**：近N次中價格新低但RSI主線未新低 → ⚠️ 標注「底背離機會」
- 若偵測到背離，在分析輸出中必須明確標注（位置、幅度、是否已驗證）

輸出格式（簡潔，3-4 行）：
```
近 Xh：價格 XXXX → XXXX（±XX 點），RSI [轉強/轉弱/持平]（XX → XX）
關鍵事件：[e.g. 4311 跌破 / 週線下軌觸及 / S2 訊號觸發]
上次建議：[觀望 / 警戒 / 進場]
背離狀態：[無 / ⚠️ 頂背離（XXXX 位置，未/已驗證）/ ⚠️ 底背離（XXXX 位置）]
```

### Step 2 — 讀取最新周報（**強制執行，不得跳過**）

> ⚠️ **順序說明**：Step 2 讀完 Gemini 週報後，Chrome MCP tab 會佔據前景，
> 導致 computer use 截圖拍不到 TradingView。
> 因此**週報讀取排在截圖之前**，讀完立即把 Chrome MCP tab 還原，再截圖。

```
【Gemini 週報】讀取方式（gdoc 唯一來源）：

1. 找最新的 XAUUSD_Weekly_Report_*_Sun.gdoc 或 *_Wed.gdoc（7 天內）
   路徑：/Users/tittan/googledrive/XAUUSD/weekly report/*.gdoc
2. 用 Read 工具讀取該 .gdoc 檔案，取出 "doc_id" 欄位（.gdoc 是 190 byte JSON 指標）
3. 用 mcp__Claude_in_Chrome__navigate 開啟：
     https://docs.google.com/document/d/{doc_id}/edit
4. 用 mcp__Claude_in_Chrome__browser_batch 搭配 scroll + screenshot 逐頁捲動截圖，
   讀取完整週報內文（⚠ get_page_text 只能讀到目錄，無法讀內文，必須用 scroll+screenshot）
→ 成功後記錄來源為「gdoc W__」

⛔ 若 gdoc 無法讀取 → 立即停止分析，回覆：
「Gemini gdoc 週報無法讀取，請確認：
 1. Chrome 已登入 Google 帳號
 2. Google Drive 已掛載（~/googledrive）
 完成後再輸入「請分析」重試。」

❌ 不使用 PNG 或 txt 替代
❌ 不繼續分析

CSV路徑：/Users/tittan/googledrive/XAUUSD/weekly report/csv/（週報專用最新 CSV，供週報生成使用）
目的：取得本週大方向、關鍵價位、三種劇本
```

**【讀完週報後必做：還原 Chrome 前景】**（僅當走①主要路徑讀了 Google Doc 時）
```
讀完週報截圖後，執行以下兩步讓 TradingView 重新成為 Chrome 的 active tab：
1. mcp__Claude_in_Chrome__navigate(url="about:blank")
   → 把 MCP tab 導向空白頁，不再佔前景
2. mcp__computer-use__open_application(app="Google Chrome")
   → 把 Chrome 帶回前景；此時 TradingView 應已是 active tab
完成後繼續 Step 3 截圖。
```

### Step 3 — 取得最新走勢（**強制用 computer use 截圖，不得用 API / Yahoo Finance / CSV 替代**）
```
【截圖前置：清場步驟（必做）】
1. 先截圖確認當前畫面
2. 若有任何對話框（Google Drive 另存新檔、下載提示、彈出視窗等）→ 按 Escape 關閉
3. 重複直到畫面乾淨
4. 確認 Chrome active tab 是 TradingView XAUUSD 30m 才繼續

若無法取得 TradingView 截圖 → 立即停止，回覆：
「⛔ 分析中止：TradingView XAUUSD 30m 截圖無法取得。
 請在 Chrome 開啟 TradingView → XAUUSD → 30m，確認無彈出視窗後再輸入「請分析」重試。」

❌ 不使用 CSV 替代
❌ 不繼續後續步驟

【截圖前置步驟】
1. 截圖確認當前畫面
2. 若有任何對話框（Google Drive 另存新檔、下載提示等）→ 用 Chrome MCP 按 Escape 關閉
3. 截圖確認對話框已關閉
4. 確認 Chrome 顯示 TradingView XAUUSD 30m 才截圖

主要方式（強制）：
1. 呼叫 mcp__computer-use__request_access 取得 Chrome 操作權限
   （若 Step 2 已執行還原步驟，Chrome 前景應已是 TradingView，直接截圖）
2. 截圖確認 Chrome 已開啟 TradingView XAUUSD 30m 圖表
3. 若未開啟：提示用戶「請在 Chrome 開啟 TradingView → XAUUSD → 30m，完成後回覆」
4. 截取截圖，用於分析即時 K 棒形態、BB 位置、AO 方向

⛔ 若無法取得 TradingView XAUUSD 30m 截圖 → 立即停止分析，回覆：
「TradingView XAUUSD 30m 截圖無法取得，請：
 1. 在 Chrome 開啟 TradingView → XAUUSD → 30m 圖表
 2. 確認沒有任何彈出視窗擋住畫面
 完成後再輸入「請分析」重試。」

❌ 不使用 CSV 替代
❌ 不繼續分析
```

**週報有效性判斷（每次必做）：**
1. 讀取週報，列出「關鍵價位總表」中的所有支撐/阻力位
2. 對照現價：若 **80% 以上關鍵位** 已被突破且現價已遠離，判定週報過期
3. **若週報過期**：停止分析，直接告知用戶：
   > 「本週週報（WXX）關鍵位已全部失效，現價 XXXX 已超出週報範圍。請重新下載 CSV 資料，我來生成 W[本週] 週報。下載完成後回覆『資料已下載』。」
4. **若週報仍有效**：繼續 Step 4，分析中必須引用：
   - 本週主劇本（劇本一/二/三 + 機率）
   - 當前最近的有效關鍵位（支撐/阻力）
   - S1/S2 的週報級別計畫

**輸出中必須加入一段 📰 週報背景：**
```
📰 週報背景（WXX）
主劇本：[劇本X，機率XX%]
當前有效位：[支撐 XXXX / 阻力 XXXX]
週報S2 A+：[XXXX（條件）]
```

### Step 4 — 分析要素
依序評估以下要素：
1. **現價位置**：相對於 BB Basis / Upper / Lower 的位置（%B）
2. **趨勢方向**：4H / 1D RSI 狀態（bullish / neutral / bearish）
3. **DXY 連動**：DXY RSI 位置（< 30 = 黃金有利，> 70 = 黃金承壓）
4. **盤別時段**：亞盤(07-16)／歐盤(16-22)／美盤(22-06)
5. **S1 觸發條件**：Fast EMA vs BB Basis 距離、AO 方向
6. **S2 機會**：是否有關鍵支撐位 + 錘頭型態

### Step 5 — 輸出交易建議
格式見下方「輸出格式」章節

### Step 6 — 更新存檔（**分析結束後自動執行，不詢問用戶**）

**1. Append 到今日 daily JSON**
```
寫入：xauusd/claude/daily/YYYY-MM-DD.json（依當日台灣時間日期）
規則：
- 若檔案已存在 → 讀取後 append 新記錄，寫回（JSON array 格式，最新筆在最後）
- 若檔案不存在 → 建立新檔，內容為含單筆記錄的 JSON array
```

**2. 更新 xauusd/claude/context.md**
```
規則：
- 「近5次記錄」表格：shift 掉最舊一筆，新增當次記錄於最上方
- 「背離偵測」段落：根據更新後的近5次重新計算
  - 看跌背離：價格新高但RSI主線未新高 → 標注位置與幅度
  - 看漲背離：價格新低但RSI主線未新低 → 標注位置與幅度
  - 若無背離 → 明確標注「無明顯背離」
- 「當前狀態」：更新偏向/決策、帳戶狀態（若有變化）
- 「策略 Alerts 紀錄」：新增當次觸發的 alert（若有）
- 標題更新時間戳
```

寫入完成後，提醒用戶在 Terminal 執行：
```bash
cd ~/program/github/trading && git add xauusd/claude/ && git commit -m "daily analysis: $(date +%Y-%m-%d)" && git push
```

---

## 輸出格式（日常分析）

```
【黃金即時分析】YYYY-MM-DD HH:MM（盤別）
【週報來源】Gemini gdoc W__ / PNG W__ / txt W__（依實際讀取來源填入，未使用者留空）

現價：XXXX.XX
BB %B(4H)：X.XX | RSI(30m)：XX.X | DXY：XXX.XXX

📋 近期趨勢回顧（最近 5 筆 Log）
近 Xh：價格 XXXX → XXXX（±XX 點），RSI [轉強/轉弱/持平]（XX.X → XX.X）
關鍵事件：[e.g. 4311 跌破 / 週線下軌測試 / S2 A+ 觸發]
上次建議：[觀望 / 等錘頭 / 進場]

📊 市場狀態
- 趨勢：[多頭 / 震盪 / 空頭]
- 關鍵支撐：XXXX | 關鍵壓力：XXXX

⚔️ S1 狀態：[✅觸發 / ⏳距離 X 點 / ❌不利]
  條件：Fast EMA(X) vs Basis(X)，AO [上升/下降]

🛡️ S2 機會：[有 / 無]
  位置：XXXX（支撐類型），型態：[錘頭/等待]

💡 建議
  行動：[等待 / A+進場 / 觀望]
  若進場：Entry XXXX，SL XXXX，TP1 XXXX，TP2 XXXX
  風控：每筆不超過總資金 X%
```

---

## 周報分析流程（「週日黃金工作流」觸發）

### 資料準備

#### Step 0 — 掛載 Google Drive CSV 資料夾（必做，不得跳過）
```
週報 CSV 存放於 Google Drive，沙盒無法自動存取，需先呼叫：
mcp__cowork__request_cowork_directory(path="~/googledrive/XAUUSD/weekly report/csv")

成功後資料夾掛載於：
  - Read/Write/Edit/Glob/Grep：使用 ~/googledrive/XAUUSD/weekly report/csv/
  - bash：使用 /sessions/gracious-zen-ptolemy/mnt/csv/

若連接失敗：要求用戶手動複製 CSV 至 trading/xauusd/csv/
```

#### CSV 檔案清單（trading/googledrive/XAUUSD/weekly report/csv/ 內）
```
FX_IDC_XAUUSD, 1D.csv     ← XAUUSD 日線（含 Basis/Upper/Lower/RSI/RSI-MA/背離欄位）
FX_IDC_XAUUSD, 1W.csv     ← XAUUSD 週線
FX_IDC_XAUUSD, 240.csv    ← XAUUSD 4H
FX_IDC_XAUUSD, 60.csv     ← XAUUSD 1H
FX_IDC_XAUUSD, 30.csv     ← XAUUSD 30m
TVC_DXY, 1D.csv            ← DXY 日線
TVC_DXY, 1W.csv            ← DXY 週線
TVC_DXY, 240.csv           ← DXY 4H
TVC_DXY, 30.csv            ← DXY 30m
MGC_1d.csv / MGC_4h.csv   ← MGC 微型黃金期貨（備用）
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
     ls ~/googledrive/XAUUSD/weekly\ report/cftc/
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
CSV_DIR = "/sessions/gracious-zen-ptolemy/mnt/csv/"   # bash 路徑

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
    # 只保留 lookback_bars 內形成、尚未完全填補的 FVG
    active_bull = [z for z in bull_fvgs if z['bar'] >= n - lookback_bars
                   and not any(l[k] <= z['bottom'] for k in range(z['bar'], n))]
    active_bear = [z for z in bear_fvgs if z['bar'] >= n - lookback_bars
                   and not any(h[k] >= z['top'] for k in range(z['bar'], n))]
    return active_bull[-3:], active_bear[-3:]   # 最近各 3 個

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

---

## 合併週報流程（「合併週報」觸發）

### ⚠ 前置條件（執行前必查）

**Step 0：確認 Claude 當週報告存在**
```
路徑：~/googledrive/XAUUSD/claude/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx
```
- 若不存在 → 先執行下方「週報資料準備」流程生成 Claude 版本，再合併
- 若存在但日期差 > 7 天（舊週）→ 同上，重新生成當週報告
- ❌ 絕對不能用舊週的 Claude 報告當交易員 A（W24 教訓：用 W23 Wed 導致所有價位過時）

### 三份週報來源
```
① Claude 週報（Dispatch Cowork 本次生成）
   路徑：~/googledrive/XAUUSD/claude/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}_Claude.docx
   掛載：mcp__cowork__request_cowork_directory(path="~/googledrive/XAUUSD/claude")
   讀取：python-docx（見下方）

② Gemini 週報（用戶手動生成，Google Drive 存為 .gdoc）
   路徑：~/googledrive/XAUUSD/weekly report/XAUUSD_Weekly_Report_{年份}W{週次}_{Sun/Wed}.gdoc
   掛載：mcp__cowork__request_cowork_directory(path="~/googledrive/XAUUSD/weekly report")
   讀取：Read .gdoc 取 doc_id → Chrome MCP navigate → scroll+screenshot（見下方）⚠ 格式是 .gdoc，不是 .txt

③ Dispatch 週報（Cowork 分析生成）
   路徑：~/program/github/trading/xauusd/daily_log/weekly_report_W{週次}_{YYYYMMDD}.txt
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
//           讀取完整週報內容
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
4. **用 docx-js 生成三個 Style Combine .docx**

### Combine 輸出格式（三個 Style，各一份）
```
輸出路徑：~/googledrive/XAUUSD/claude/
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
提示詞（.gdoc）：~/googledrive/XAUUSD/claude/prompt/xauusd_weekly_report_prompt.gdoc
Doc ID：1gKMZbIKcKTT3BWk2r0_BQQrWBfTEPyGps0qQzfhYj8w
讀取：用 Chrome MCP 的 JS fetch export?format=txt 方式（同 Gemini 讀取）
完整 SOP：~/googledrive/XAUUSD/claude/prompt/claude_xauusd_weekly_report_skill.txt
```

---

## 關鍵數據參考（持續更新）

### DXY 與 XAUUSD 相關性
- 30日滾動相關係數：約 -0.467（反向）
- DXY RSI < 30（USD 弱）→ 三策略勝率 60-75%
- DXY RSI 30-50 → S2 策略表現最差，考慮縮倉

### HTF 共軌分數（alignment 0-3）
- alignment = 3/3 → S1 勝率約 69%
- alignment ≥ 2 才建議進場

### BB %B 勝率
- S1：%B ≥ 0.8 勝率 61-78%；%B < 0.3 勝率接近 0%
- S2：BB 位置過濾幫助有限，以支撐位為主

---

## 編碼容錯規則
讀取 CSV 時，強制使用多重編碼容錯：
```python
for enc in ['utf-8', 'utf-8-sig', 'big5', 'cp950']:
    try:
        df = pd.read_csv(path, encoding=enc, encoding_errors='ignore')
        break
    except Exception:
        continue
```
遇到錯誤先暫停討論，不使用錯誤資料繼續分析。
