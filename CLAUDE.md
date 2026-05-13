# Trading Strategy Hub — CLAUDE.md

## 專案目的

多商品量化交易策略分析工具箱。目前涵蓋 **XAUUSD 黃金** 和 **TX 台指期小台（MTX）**，未來可擴展至其他商品。

每個商品包含：
1. **Fail-Pattern Analysis** — 分析現有策略虧損根因
2. **Long Experiment Engine** — 回測 20 個多單策略，自動生成 Pine Script
3. **Short Experiment Engine** — 回測 20 個空單策略，自動生成 Pine Script

TX 額外包含：
4. **Macro Analysis** — 週線月度方向統計，建立宏觀偏向基準

---

## 目錄結構

```
trading/
├── CLAUDE.md                    # 本檔（統一說明文件）
├── .claude/memory/              # Claude 記憶（git 追蹤，跨電腦同步）
│   ├── MEMORY.md
│   ├── user_profile.md
│   ├── project_context.md
│   └── feedback.md
├── index.html                   # 多商品 Hub（主入口）
├── generate_index.py            # 重新生成 index.html（更新實驗結果後執行）
├── requirements.txt
│
├── xauusd/                      # XAUUSD 黃金策略分析
│   ├── csv/                     # TradingView 匯出 CSV（XAUUSD + DXY 多時間框架）
│   ├── analysis/                # Fail-pattern 分析套件（含 DXY、MTF、BB、背離）
│   ├── experiments/             # 策略回測引擎（多單 + 空單共用）
│   ├── main.py                  # Fail-pattern 分析入口
│   ├── run_experiments.py       # 多單 20 策略實驗入口
│   ├── run_short_experiments.py # 空單 20 策略實驗入口
│   ├── XAUUSD-Long-S1-AweWithBB/   # S1 右側突破：交易 CSV + report.html + Pine
│   ├── XAUUSD-Long-S2A-RSI/        # S2A 左側（指標）：原 S2-Hybrid
│   ├── XAUUSD-Long-S2B-Hammer/     # S2B 左側（型態）：原 S2-Pullback
│   ├── XAUUSD-Long-Experiments/    # 多單實驗：report.html + pine/ × 20
│   └── XAUUSD-Short-Experiments/   # 空單實驗：report.html + pine/ × 20
│
└── tx/                          # TX 台指期策略分析
    ├── csv/                     # TradingView 匯出 CSV（MTX + NQ 多時間框架）
    ├── experiments/             # 策略回測引擎（多單 + 空單共用）
    ├── macro_analysis.py        # 宏觀分析入口（週線月度統計）
    ├── run_experiments.py       # 多單 20 策略實驗入口
    ├── run_short_experiments.py # 空單 20 策略實驗入口
    ├── generate_index.py        # TX 獨立 index 生成（備用，主要用根目錄版）
    ├── macro_report.html        # 宏觀分析完整報告（暗色主題）
    ├── TX-Long-Experiments/     # 多單實驗：report.html + pine/ × 20 + results.json
    └── TX-Short-Experiments/    # 空單實驗：report.html + pine/ × 20 + results.json
```

---

## 執行方式

### 更新 index.html（更新任一商品實驗結果後）

```bash
python generate_index.py
```

### XAUUSD（在 trading/ 根目錄執行）

```bash
# Windows
py -3.11 xauusd/run_experiments.py
py -3.11 xauusd/run_short_experiments.py
py -3.11 xauusd/main.py S1-AweWithBB

# Mac
python3 xauusd/run_experiments.py
```

### TX（在 trading/ 根目錄執行）

```bash
# Windows
py -3.11 tx/macro_analysis.py
py -3.11 tx/run_experiments.py
py -3.11 tx/run_short_experiments.py

# Mac
python3 tx/macro_analysis.py
python3 tx/run_experiments.py --sl 40 --tp 80   # 自訂 SL/TP
```

---

## 新增商品流程

1. 在 `trading/` 下建立新商品資料夾（e.g., `nq/`）
2. 複製 `tx/experiments/` 架構，調整 SL/TP 單位和相關性指標
3. 在 `generate_index.py` 的 `COMMODITIES` 清單中新增一筆
4. 在 `SESSION_LOGS` 中新增對應的 key
5. 視需要新增 `_<商品>_exp_html()` 函式或共用現有的
6. 執行 `python generate_index.py` 更新 index.html

---

## 商品特性對照

| 面向 | XAUUSD 黃金 | TX 台指期 |
|------|------------|---------|
| 相關性指標 | DXY（反向） | NQ（同向） |
| SL/TP 單位 | 百分比（0.5%/1.0%） | 固定點數（30pts/60pts） |
| 每點價值 | N/A | NT$50（小台） |
| 交易時段 | 24/5 | 日盤 08:45–13:45 + 夜盤 15:00–05:00 |
| 時間止損 | 48 bars（24h） | 48 bars（24h，跨日夜盤） |
| 特有分析 | DXY 相關性 | session_analysis.py + macro_analysis.py |
| 已開發策略 | S1-AweWithBB / S2A-RSI / S2B-Hammer | 無（實驗階段） |

---

## CSV 欄位格式（TradingView 匯出，兩商品相同）

```
time, open, high, low, close, RSI, RSI-based MA,
Regular Bullish, Regular Bullish Label, Regular Bearish, Regular Bearish Label
```

- `time`：帶時區 ISO 字串（`+08:00`），loader 自動轉 Asia/Taipei
- `RSI`：RSI(14)；`RSI-based MA`：RSI 移動平均線
- `Regular Bullish/Bearish`：RSI 背離信號

---

## 換電腦後的記憶設定

Claude 的專案記憶存在 `.claude/memory/`（**git 追蹤**）。
新電腦 `git clone` 後執行一次下列指令，把系統記憶路徑指向專案資料夾。

### Mac / Linux（在 trading/ 目錄執行）

```bash
PROJ=$(pwd)
SYSTEM_KEY=$(echo "$PROJ" | sed 's|^/||' | sed 's|/|-|g')
rm -rf ~/.claude/projects/${SYSTEM_KEY}/memory
ln -s "${PROJ}/.claude/memory" ~/.claude/projects/${SYSTEM_KEY}/memory
```

### Windows（PowerShell，在 trading/ 目錄執行）

```powershell
$proj = (Get-Location).Path
$key  = $proj -replace '\\', '-' -replace ':', ''
$src  = "$proj\.claude\memory"
$dst  = "$env:USERPROFILE\.claude\projects\-$key\memory"
if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
New-Item -ItemType Junction -Path $dst -Target $src
```

> Windows 使用 Junction（不需管理員權限），Mac/Linux 使用 symlink。

---

## 技術環境

- Python 3.11（Windows `py -3.11`，Mac `python3`）
- 套件：pandas, numpy, matplotlib（見 requirements.txt）
- Pine Script v6（TradingView）
- 無外部 API、無環境變數需求
