# TX — 台指期（小台 MTX）交易策略分析工具箱 CLAUDE.md

## 專案目的

分析台指期小台（MTX）的交易策略失敗模式，並系統性地測試新策略（多單 + 空單）。
架構完全對應 xauusd 專案，核心差異：**點數制 SL/TP**、**日盤/夜盤分段**、**NQ 取代 DXY 做相關性分析**。

包含四大模組：

1. **Macro Analysis** — 週線月度方向統計，建立宏觀偏向基準（多/空/中性）
2. **Fail-Pattern Analysis** — 分析現有策略的虧損交易，找出失敗根因（含 NQ 相關性）
3. **Long Experiment Engine** — 回測 20 個多單策略，自動生成 TradingView Pine Script
4. **Short Experiment Engine** — 回測 20 個空單策略，自動生成 TradingView Pine Script

---

## 執行方式

```bash
# Windows 環境（Python 3.11）
py -3.11 macro_analysis.py                     # 宏觀分析（週線月度統計 → macro_report.html）
py -3.11 run_experiments.py                    # 執行 20 多單策略實驗
py -3.11 run_short_experiments.py              # 執行 20 空單策略實驗
py -3.11 generate_index.py                     # 更新 index.html
py -3.11 generate_sample_data.py               # 生成合成資料（測試用）

# Mac 環境（Python 3.12）
python3.12 macro_analysis.py

# 自訂 SL/TP
py -3.11 run_experiments.py --sl 40 --tp 80
py -3.11 run_experiments.py --csv "TAIFEX_DLY_MXF1!, 30.csv"
```

---

## 目錄結構

```
tx/
├── analysis/               # Fail-pattern 分析套件
│   ├── config.py           # 策略設定 + 失敗分類門檻 + CSV 路徑
│   ├── loader.py           # TradingView CSV → 正規化 DataFrame（load_price / load_nq）
│   ├── metrics.py          # 統計指標（win_rate, profit_factor, drawdown）
│   ├── fail_patterns.py    # 虧損分類邏輯（核心）
│   ├── pre_entry.py        # 進場前情境分析（交易資料 + K 棒 RSI 特徵）
│   ├── nq_analysis.py      # NQ 相關性分析（對應 xauusd 的 dxy_analysis.py）
│   ├── mtf_analysis.py     # 多時間框架（MTF）共軌分析（60m/4H/1D）
│   ├── bb_analysis.py      # BB 位置分析（%B 分區勝率）
│   ├── session_analysis.py # 日盤/夜盤分段分析（台指期特有）
│   ├── divergence.py       # RSI 背離偵測（bullish/bearish）
│   ├── charts.py           # matplotlib 圖表
│   └── report.py           # 自含式 HTML 報告生成器
│
├── experiments/            # 策略回測引擎（多單 + 空單共用）
│   ├── engine.py           # run_backtest()（多單）+ run_backtest_short()（空單）
│   ├── indicators.py       # 技術指標庫
│   ├── strategies.py       # 20 個多單策略信號（E01–E20）
│   ├── strategies_short.py # 20 個空單策略信號（S01–S20）
│   ├── runner.py           # 執行所有策略 + 複合評分
│   ├── pine_generator.py   # 自動生成多單 Pine Script v6
│   ├── pine_generator_short.py # 自動生成空單 Pine Script v6
│   └── report.py           # HTML 實驗結果儀表板
│
├── csv/                    # 所有 TradingView 匯出資料（統一放這裡）
│   ├── TAIFEX_MXF1!, 30.csv   # MTX 30m（主力資料）
│   ├── TAIFEX_MXF1!, 60.csv   # MTX 60m
│   ├── TAIFEX_MXF1!, 240.csv  # MTX 4H
│   ├── TAIFEX_MXF1!, 1D.csv   # MTX 日線
│   ├── CME_MINI_NQ1!, 30.csv  # NQ 30m
│   ├── CME_MINI_NQ1!, 60.csv  # NQ 60m
│   ├── CME_MINI_NQ1!, 240.csv # NQ 4H
│   └── CME_MINI_NQ1!, 1D.csv  # NQ 日線
│
├── macro_analysis.py       # 宏觀分析入口（週線月度統計 + 季節性）
├── main.py                 # Fail-pattern 分析入口
├── run_experiments.py      # 多單 20 策略實驗入口
├── run_short_experiments.py # 空單 20 策略實驗入口
├── generate_index.py       # 更新 index.html
├── index.html              # 整合報告（含宏觀分析摘要）
├── macro_report.html       # 宏觀分析完整報告（暗色主題，含熱力圖）
├── requirements.txt
└── CLAUDE.md
```

---

## CSV 欄位格式（TradingView 匯出）

所有 csv/ 下的 K 棒檔案格式相同（與 xauusd 完全一致）：
```
time, open, high, low, close, RSI, RSI-based MA,
Regular Bullish, Regular Bullish Label, Regular Bearish, Regular Bearish Label
```
- `time`：帶時區的 ISO 字串（`+08:00`），loader 自動轉為 Asia/Taipei 無時區
- `RSI`：RSI(14)
- `RSI-based MA`：RSI 移動平均線（趨勢確認）
- `Regular Bullish/Bearish`：RSI 背離信號

**TradingView 匯出設定**：
- 小台指連續合約：`TAIFEX:MXF1!`
- NQ 連續合約：`CME_MINI:NQ1!`（可切換為 `NASDAQ:NDX` 現貨指數）

---

## 核心設計決策

### xauusd 到 tx 的關鍵差異

| 面向 | xauusd | tx（台指期） |
|------|--------|------------|
| 商品 | XAUUSD（黃金/美元） | MTX（小台指期）|
| 相關性指標 | DXY（反向） | NQ（同向） |
| SL/TP 單位 | 百分比（0.5%/1.0%） | 固定點數（30pts/60pts） |
| 每點價值 | N/A | NT$50 |
| 交易時段 | 24/5 | 日盤 08:45–13:45 + 夜盤 15:00–05:00 |
| 時間止損 | 48 bars（24h） | 48 bars（24h，可跨日夜盤） |

### 失敗分類邏輯（analysis/fail_patterns.py）

虧損交易分為 4 類（依序判斷）：
- `immediate_loss`：MFE（最大有利浮動，點數）< 3 pts（進場就錯）
- `false_breakout`：MFE ≥ 3 pts 且 MAE/MFE > 2.0（曾有利潤但完全逆轉）
- `time_bleed`：持倉 ≥ 48 bars（30 分鐘 K 棒，跨日盤/夜盤）
- `normal_sl`：其他（正常止損）

### 回測引擎規則（experiments/engine.py）

| 參數 | 多單 | 空單 |
|------|------|------|
| 進場 | bar[i+1] open | bar[i+1] open |
| 止損（預設） | entry - 30 pts | entry + 30 pts |
| 止盈（預設） | entry + 60 pts | entry - 60 pts |
| 時間止損 | 48 bars（24h，30m K） | 48 bars（24h，30m K） |
| R:R | 2:1 | 2:1 |
| 每點價值 | NT$50（小台） | NT$50（小台） |

`sl_points` 與 `tp_points` 為可調參數，每個策略可個別設定。

### 交易時段定義（UTC+8，台指期）

- `day`（日盤）：08:45–13:45
- `night`（夜盤）：15:00–05:00（跨午夜）
- `closed`（收盤空窗）：05:00–08:44（不進場）

### NQ 相關性分析（analysis/nq_analysis.py）

NQ 與台指期為**同向連動**（NQ 強 → 台指期傾向跟漲）。
分析欄位（對應 xauusd 的 dxy_* 欄位）：
- `nq_rsi_1d`、`nq_trend_1d`、`nq_rsi_vs_ma`、`nq_rsi_bucket`

NQ RSI bucket 解讀（與 DXY 相反）：
- `超買 > 70`（NQ 強，台指期有利多）→ 多單勝率應較高
- `超賣 < 30`（NQ 弱，台指期承壓）→ 空單勝率應較高

支援切換至其他相關指標（SOX、SPX、VIX）：在 `config.py` 修改 `CORR_SYMBOL`。

### 多時間框架分析（analysis/mtf_analysis.py）

與 xauusd 相同邏輯，使用 `pd.merge_asof` O(n log n) 查找：
- `htf_60m_rsi_state`、`htf_4h_rsi_state`、`htf_1d_rsi_state`
- `htf_alignment`（0–3）、`htf_alignment_label`
- `htf_conflict`、`htf_high_vol`

### 日盤/夜盤分析（analysis/session_analysis.py）—台指期特有

每筆交易新增 `session` 欄位（`day` / `night`）：
- 分析日盤 vs 夜盤的勝率差異
- 夜盤受美股直接影響，NQ 相關性更強
- 可分析特定策略適合哪個時段

### Pre-Entry K 棒特徵（analysis/pre_entry.py）

使用 RSI 相關特徵（與 xauusd 相同）：
- `rsi`、`rsi_vs_ma`、`rsi_slope_3`
- `prev_1_dir`、`prev_3_green`、`prev_3_range`、`momentum_3`

---

## 策略命名系統

| 家族 | 類型 | Pine Entry |
|------|------|-----------|
| S1 | 右側突破 | `S1_LE` |
| S2A | 左側回測（指標） | `S2A_LE` |
| S2B | 左側回測（型態） | `S2B_LE` |
| S3 | 空單系列 | `S3_SE` |

**版本命名規則**：`VX.Y`（確認版）→ `VX.Y+1.1`（測試版）→ `VX.Y+1`（確認後升版）

---

## Pine Script 使用方式

| 檔案 | 說明 |
|------|------|
| `TX-Long-Experiments/pine/ALL_Long_Strategies.pine` | E01–E20 合併版（下拉選單）|
| `TX-Short-Experiments/pine/ALL_Short_Strategies.pine` | S01–S20 合併版（下拉選單）|

### 設定說明（Pine Script 右側面板）

| 設定 | 說明 |
|------|------|
| **Strategy** | 下拉選擇策略（E01–E20 / S01–S20） |
| **Enable Signals** | 開啟進場；關閉後只顯示灰色參考箭頭 |
| **Stop Loss (pts)** | 止損點數（預設 30pts = NT$1,500/口） |
| **R:R Ratio** | 風報比（TP = SL × R:R，預設 2.0 → TP 60pts） |
| **Session** | 日盤/夜盤個別開關 |

---

## 輸出產物

- **`macro_report.html`** — 宏觀分析（月度統計、季節性、週內結構、熱力圖、近12月回顧）
- **`{策略資料夾}/report.html`** — 自含式 HTML，含 NQ + MTF + Session 分析段落
- **`TX-Long-Experiments/report.html`** — 多單 20 策略排名儀表板
- **`TX-Long-Experiments/pine/*.pine`** — 20 個多單 Pine Script v6
- **`TX-Long-Experiments/pine/ALL_Long_Strategies.pine`** — 合併下拉選單版
- **`TX-Short-Experiments/report.html`** — 空單 20 策略排名儀表板
- **`TX-Short-Experiments/pine/ALL_Short_Strategies.pine`** — 合併下拉選單版
- **`index.html`** — 根目錄整合報告

---

## 換新電腦後的記憶設定

Claude 的專案記憶存在 `.claude/memory/`（git 追蹤）。新電腦 `git clone` 後需執行一次下列指令，把系統記憶路徑指向專案資料夾。

### Mac / Linux（在專案根目錄執行）

```bash
PROJ=$(pwd)
SYSTEM_KEY=$(echo "$PROJ" | sed 's|^/||' | sed 's|/|-|g')
rm -rf ~/.claude/projects/${SYSTEM_KEY}/memory
ln -s "${PROJ}/.claude/memory" ~/.claude/projects/${SYSTEM_KEY}/memory
```

### Windows（PowerShell，在專案根目錄執行）

```powershell
$proj = (Get-Location).Path
$key  = $proj -replace '\\', '-' -replace ':', ''
$src  = "$proj\.claude\memory"
$dst  = "$env:USERPROFILE\.claude\projects\-$key\memory"
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
New-Item -ItemType Junction -Path $dst -Target $src
```

---

## 技術環境

- Python 3.11（Windows 使用 `py -3.11`，Mac 使用 `python3`）
- 套件：pandas, numpy, matplotlib（見 requirements.txt）
- Pine Script v6（TradingView 使用）
- 無外部 API、無環境變數需求
