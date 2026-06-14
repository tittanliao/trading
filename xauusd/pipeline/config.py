# ══════════════════════════════════════════════════════════════════════════════
#  config.py — XAUUSD M30 資料管線 全域設定
# ══════════════════════════════════════════════════════════════════════════════
from pathlib import Path

# ── 目錄定義 ──────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent          # xauusd/pipeline/
CSV_DIR    = BASE_DIR.parent / "csv"                  # xauusd/csv/
OUTPUT_DIR = BASE_DIR / "output"                      # 週報 CSV 輸出目錄

# ── 冷庫路徑（SQLite） ─────────────────────────────────────────────────────────
# 初始 10 年資料由 TickStory 手動匯出後，透過 init_cold_db.py 建立
DB_PATH  = BASE_DIR / "XAUUSD_M30_Cold.db"
DB_TABLE = "XAUUSD_M30"

# ── 模組 B：TV 手動匯出驗證 CSV ────────────────────────────────────────────────
# SOP：TradingView → OANDA:XAUUSD 30m → 匯出圖表資料 → 存至 xauusd/csv/
# 預設指向現有的 TradingView 匯出檔
TV_EXPORT_PATH          = CSV_DIR / "FX_IDC_XAUUSD, 30.csv"
VALIDATION_FAIL_IF_MISSING = True   # True = 檔案不存在直接終止；False = 跳過驗證

# ── tvDatafeed 帳號（留空 = 匿名模式） ────────────────────────────────────────
TV_USERNAME = "aaasdf691@gmail.com"
TV_PASSWORD = "525629qqQQqq"

# ── Google 登入帳號：用 sessionid 動態取得 auth_token ────────────────────────
# 取得方式：
#   1. Chrome 開啟 tradingview.com 並登入
#   2. F12 → Application → Cookies → .tradingview.com
#   3. 複製 sessionid 和 sessionid_sign 的 Value 貼到下方
#   留空 = 使用 username/password 登入
TV_SESSIONID      = "drnmd2k8k3rh5xtbafzi1d4hkluh5y17"
TV_SESSIONID_SIGN = "v3:eeRT2cRyOmCZgzXB0JSCz9X4wrpDtT0Q2srdImivykA="
TV_DEVICE_T       = "V2E4ejoy.WzwQatjGGQZqRwSUgLbpPcfFXpQCrZsDOjLPr6aHm2s"

# ── 備用：直接填入 auth_token（靜態，不建議） ─────────────────────────────────
TV_AUTH_TOKEN = ""

# ── 抓取商品設定 ───────────────────────────────────────────────────────────────
# with_indicators : 是否計算技術指標（只有 XAUUSD 需要）
# output_csv      : 週報 CSV 檔名
# write_db        : 是否 UPSERT 進冷庫（只有 XAUUSD）
SYMBOLS: dict[str, dict] = {
    "XAUUSD": {
        "exchange":        "OANDA",
        "with_indicators": True,
        "output_csv":      "Weekly_Report_XAUUSD_M30.csv",
        "write_db":        True,
    },
    "DXY": {
        "exchange":        "TVC",
        "with_indicators": False,
        "output_csv":      "Weekly_Report_DXY_M30.csv",
        "write_db":        False,
    },
    "GC1!": {
        "exchange":        "COMEX",
        "with_indicators": False,
        "output_csv":      "Weekly_Report_GC_M30.csv",   # 標準黃金期貨（MGC1! 不可用）
        "write_db":        False,
        "optional":        True,   # 失敗時僅 Warning，不中斷管線
    },
}

# ── 抓取範圍 ───────────────────────────────────────────────────────────────────
LOOKBACK_MONTHS = 3      # 週報涵蓋「今天往回 N 個月」
N_BARS          = 5000   # tvDatafeed 多抓以確保足量（含假日空缺）

# ── 技術指標參數（XAUUSD only） ────────────────────────────────────────────────
BB_LENGTH = 20
BB_STD    = 2.0
EMA_FAST  = 50
EMA_SLOW  = 200

# ── 驗證容忍度 ─────────────────────────────────────────────────────────────────
OHLC_TOLERANCE = 1e-4   # OHLC 嚴格：差值超過此值視為不一致
                         # Volume 寬容：僅 Log，不中斷程式

# ── 時區 ──────────────────────────────────────────────────────────────────────
TIMEZONE = "Asia/Taipei"   # UTC+8，與 Pine Script 時段過濾器對齊
