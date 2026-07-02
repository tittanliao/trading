"""
analyze_ma_bounce.py
台指日線 × 四條均線 收盤跌破 → 買入正二績效分析

均線定義：
  MA5   = 5日均線（週線/日線）
  MA20  = 20日均線（月線）
  MA60  = 60日均線（季線）
  MA120 = 120日均線（半年線）

信號：前一日收盤在均線上方，當日收盤跌破（crossover，不含持續跌破）
進場：信號日隔天（next bar），以收盤價近似
正二：每日報酬 × 2 複利（proxy，未含管理費/追蹤誤差）
基準：每次信號投入 100萬 TWD，可多次觸發
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import timedelta

ROOT      = Path(__file__).parent.parent
DAILY_CSV = ROOT / "tx" / "csv" / "TAIFEX_DLY_MXF1!, 1D.csv"
OUT_CSV   = ROOT / "tx" / "ma_bounce_signals.csv"

INVEST = 1_000_000

MA_DEFS = {
    "MA5（週線）":    5,
    "MA20（月線）":  20,
    "MA60（季線）":  60,
    "MA120（半年線）": 120,
}

HOLD_DAYS = {"1M": 30, "3M": 90, "6M": 180, "12M": 365}


# ── 1. 載入資料 ────────────────────────────────────────────────────
def load_daily():
    df = pd.read_csv(DAILY_CSV)
    df.columns = df.columns.str.strip()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time").reset_index(drop=True)
    df["daily_ret"] = df["close"].pct_change()
    for label, p in MA_DEFS.items():
        df[f"ma{p}"] = df["close"].rolling(p).mean()
    return df


# ── 2. 找 crossover 信號 ───────────────────────────────────────────
def find_signals(df, ma_col):
    prev_above = df["close"].shift(1) >= df[ma_col].shift(1)
    curr_below  = df["close"] < df[ma_col]
    valid       = df[ma_col].notna() & df[ma_col].shift(1).notna()
    return df.index[prev_above & curr_below & valid].tolist()


# ── 3. 計算單次信號績效 ────────────────────────────────────────────
def calc_perf(df, signal_idx, hold_days):
    # 進場：信號日 +1（下一交易日）
    entry_idx = signal_idx + 1
    if entry_idx >= len(df):
        return None

    entry_date  = df.loc[entry_idx, "time"]
    entry_price = df.loc[entry_idx, "close"]
    exit_date   = entry_date + timedelta(days=hold_days)

    # 持有期間 bars
    period = df[(df["time"] >= entry_date) & (df["time"] <= exit_date)].copy()
    if len(period) < 2:
        return None

    # TX 報酬
    tx_ret = (period.iloc[-1]["close"] - entry_price) / entry_price

    # 正二：複利每日 ret × 2
    daily_rets = period["daily_ret"].fillna(0).values
    z2_equity  = np.cumprod(1 + daily_rets * 2)
    z2_ret     = float(z2_equity[-1] - 1)

    # MDD（正二等值）
    eq          = np.insert(z2_equity, 0, 1.0)
    running_max = np.maximum.accumulate(eq)
    mdd         = float(((eq - running_max) / running_max).min())

    return {
        "signal_date":  df.loc[signal_idx, "time"].date(),
        "entry_date":   entry_date.date(),
        "entry_price":  entry_price,
        "hold":         hold_days,
        "tx_ret":       tx_ret,
        "z2_ret":       z2_ret,
        "mdd":          mdd,
        "profit_twD":   INVEST * z2_ret,
    }


# ── 4. 輸出格式工具 ────────────────────────────────────────────────
def pct(v):  return f"{v*100:+.1f}%"
def twd(v):  return f"{v:+,.0f}"
def sep(n=62): print("─" * n)


# ── 5. 主程式 ─────────────────────────────────────────────────────
def run():
    df = load_daily()
    print(f"\n台指日線：{df['time'].iloc[0].date()} → {df['time'].iloc[-1].date()}  ({len(df)} bars)")

    all_rows = []

    for ma_label, ma_period in MA_DEFS.items():
        ma_col  = f"ma{ma_period}"
        signals = find_signals(df, ma_col)

        print(f"\n{'='*62}")
        print(f"  {ma_label}  ｜  crossdown 信號次數：{len(signals)}")
        print(f"{'='*62}")

        # 信號日期
        print("  信號日期：", end="")
        for i, idx in enumerate(signals):
            sep_ch = "  " if (i+1) % 6 else "\n          "
            print(f"{df.loc[idx,'time'].date()}{sep_ch}", end="")
        print()

        # 每個持有期統計
        print(f"\n  {'持有':^5}  {'次數':^4}  {'TX勝率':^7}  {'TX均報':^8}  {'正二均報':^9}  {'avg MDD':^8}  {'100萬均獲利':^12}  {'最差單次':^10}")
        sep()

        for hp_label, hp_days in HOLD_DAYS.items():
            rows = [r for idx in signals if (r := calc_perf(df, idx, hp_days))]
            if not rows:
                print(f"  {hp_label:<5}  —（資料不足）")
                continue

            tx_wr  = np.mean([r["tx_ret"] > 0 for r in rows])
            tx_avg = np.mean([r["tx_ret"] for r in rows])
            z2_avg = np.mean([r["z2_ret"] for r in rows])
            mdd_avg= np.mean([r["mdd"] for r in rows])
            pr_avg = np.mean([r["profit_twD"] for r in rows])
            worst  = min(r["profit_twD"] for r in rows)
            n      = len(rows)

            print(f"  {hp_label:<5}  {n:>4}  {tx_wr*100:>6.0f}%  {pct(tx_avg):>8}  {pct(z2_avg):>9}  {pct(mdd_avg):>8}  {twd(pr_avg):>12}  {twd(worst):>10}")

            for r in rows:
                r["ma"] = ma_label
                r["hp"] = hp_label
                all_rows.append(r)

        # 累計：若每次信號都投 100萬，不同持有期的總成果
        print(f"\n  ── 若每次信號各投 100萬（每次獨立，可重疊）──")
        for hp_label, hp_days in HOLD_DAYS.items():
            rows = [r for idx in signals if (r := calc_perf(df, idx, hp_days))]
            if not rows:
                continue
            total_in  = len(rows) * INVEST
            total_out = sum(r["profit_twD"] for r in rows)
            worst_mdd = min(r["mdd"] for r in rows)
            print(f"  {hp_label}: 投入 {total_in/1e6:.0f}M → 累計獲利 {twd(total_out)}  最大單次MDD {pct(worst_mdd)}")

    # CSV
    if all_rows:
        pd.DataFrame(all_rows).to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
        print(f"\n✅ 詳細資料輸出：{OUT_CSV}")


if __name__ == "__main__":
    run()
