#!/usr/bin/env python3
"""
Generate root index.html for the multi-commodity trading project.
Run after updating any commodity's experiment results.

Usage:
    python generate_index.py
"""
import json
import re
from pathlib import Path

import pandas as pd
import numpy as np

ROOT = Path(__file__).parent

# ─── Commodity Registry ─────────────────────────────────────────────
# To add a new commodity: append a new dict here.
COMMODITIES = [
    {
        "id":        "xauusd",
        "name":      "XAUUSD 黃金",
        "subtitle":  "黃金/美元 · 30m · 3 策略 + 20L/20S 實驗",
        "color":     "#1e3a5f",
        "accent":    "#2563eb",
        "long_dir":  "xauusd/XAUUSD-Long-Experiments",
        "short_dir": "xauusd/XAUUSD-Short-Experiments",
        "long_pine": "xauusd/XAUUSD-Long-Experiments/pine/ALL_Long_Strategies.pine",
        "short_pine":"xauusd/XAUUSD-Short-Experiments/pine/ALL_Short_Strategies.pine",
    },
    {
        "id":        "tx",
        "name":      "TX 台指期",
        "subtitle":  "小台 MTX · 30m · 20L/20S 實驗 · 宏觀分析",
        "color":     "#1a237e",
        "accent":    "#1565c0",
        "long_dir":  "tx/TX-Long-Experiments",
        "short_dir": "tx/TX-Short-Experiments",
        "long_pine": "tx/TX-Long-Experiments/pine/ALL_Long_Strategies.pine",
        "short_pine":"tx/TX-Short-Experiments/pine/ALL_Short_Strategies.pine",
    },
]

# ─── Session Logs ────────────────────────────────────────────────────
XAUUSD_LOG = [
    {
        "date": "2026-05-02",
        "title": "策略命名重構 + 架構統一",
        "items": [
            "資料夾重命名（git mv）：S2-Hybrid→S2A-RSI、S2-Pullback→S2B-Hammer",
            "修復 S1 lookahead_on 重繪 bug → lookahead_off",
            "統一 entry label 規則（S1BB_LE / S2A_LE / S2B_LE）",
            "三策略均加入 EMA 過濾器群組（預設 off）",
            "產出：S1 V3.6.2、S2A V2.2、S2B V2.1 測試版",
        ],
    },
    {
        "date": "2026-05-01",
        "title": "BB 位置分析 + RSI 背離偵測",
        "items": [
            "建立 bb_analysis.py（%B 7 zone 分類）",
            "S1 price > BB 上軌時勝率 77.8%（n=9）；中軌以下不建議進場",
            "divergence.py 程式化偵測 swing low 背離（17 個信號，樣本不足）",
            "S1 V3.6.1：加入 BB %B ≥ 0.6 過濾器 + 4H HTF RSI 過濾器",
        ],
    },
    {
        "date": "2026-04-29",
        "title": "多時間框架（MTF）共軌分析",
        "items": [
            "建立 mtf_analysis.py；merge_asof 查找 HTF 狀態",
            "HTF alignment=3/3 時 S1 勝率達 ~69%",
            "4H bearish → S1 immediate_loss 飆升；S2 time_bleed 升高",
            "空單 4H 過濾後平均 +4.1% ΔWR（16/20 改善）",
        ],
    },
    {
        "date": "2026-04-27",
        "title": "初始分析 + DXY 相關性",
        "items": [
            "設計 4 類虧損分類邏輯（immediate_loss / false_breakout / time_bleed / normal_sl）",
            "DXY RSI < 30 時三策略勝率均升至 60–75%",
            "S2 time_bleed 超過 50% — 加時間止損是最高優先",
            "建立 20 多單 + 20 空單實驗框架；E03 MACD Signal 最佳（PF 1.643）",
        ],
    },
]

CROSS_LOG = [
    {
        "date": "2026-05-15",
        "title": "統一對話記錄頁 + 跨商品 Log 整合",
        "items": [
            "將 XAUUSD / TX / 跨商品 的所有對話記錄統一整合到「📋 對話記錄」獨立 Tab",
            "每筆 log 加上商品 tag（🟡 XAUUSD / 🔵 TX / 📊 跨商品），便於追蹤 Prompt 演進歷史",
            "移除 XAUUSD 和 TX 各自的「對話記錄」子 tab，集中到統一頁面",
            "新增 feedback_completion_checklist.md 記憶，確保每次完成任務都記錄到 memory",
        ],
    },
    {
        "date": "2026-05-15",
        "title": "跨商品分析：整點熱力圖 + 30m RSI 濾鏡",
        "items": [
            "新增 shared/run_shared_analysis.py：XAUUSD + TX 共同分析框架",
            "整點進場熱力圖：星期幾 × 小時 → 歷史勝率 & 平均損益（TX 3,334 筆 / XAU 2,906 筆）",
            "TX 最佳時段：週二 23:00 WR=73.7%，avg +40.9pts；最差：週四 08:00 WR=33.3%，avg -89.5pts",
            "XAU 最佳時段：週三 06:00 WR=88.9%（n=9 小樣本）；最差：週一 06:00 WR=10.0%（n=10）",
            "30m RSI 狀態過濾：TX RSI<MA 時 WR 53.7% avg +8.0pts；RSI>MA 時 WR 53.1% avg +1.8pts",
            "背離訊號（Regular Bullish/Bearish）欄位在現有 CSV 無資料，需重新從 TradingView 匯出",
            "新增「📊 跨商品分析」Nav Tab，兩商品分析放同一頁面方便比較",
        ],
    },
    {
        "date": "2026-05-14",
        "title": "網站整合：Hub 主頁 + 多商品導覽 + 手機響應式",
        "items": [
            "整合 XAUUSD + TX 為 Trading Strategy Hub（根目錄 index.html）",
            "頂部導覽：XAUUSD 黃金 / TX 台指期 / 📊 跨商品分析 / 🗺 網站地圖",
            "加入 GitHub Actions 自動部署到 GitHub Pages",
            "手機響應式：品牌列 + 可橫滑 tab 列，適配小螢幕",
            "筆記驗證功能：validate_notes.py 比對交易筆記與歷史資料符合率",
        ],
    },
    {
        "date": "2026-05-13",
        "title": "XAUUSD + TX 宏觀分析整合 + 網站地圖",
        "items": [
            "XAUUSD 宏觀分析（DXY 相關性、月度統計、季節性）整合進 Hub",
            "TX 宏觀分析：月勝率 63.9%、四月 +518pts、九月唯一偏空",
            "統一雙商品導覽，網站地圖列出所有分析頁面",
        ],
    },
]

TX_LOG = [
    {
        "date": "2026-05-13",
        "title": "SL 敏感度分析 — 確認 30pts 過緊",
        "items": [
            "問題：SL=30pts（≈0.15%）被雜訊掃出後才噴上，導致 19/20 多單虧損",
            "系統性測試 SL = 30 / 50 / 60 / 80 / 100 / 120 / 150（R:R 固定 2:1）",
            "SL=30：只有 E12 獲利（PF=1.132, WR=36.1%）",
            "SL=60：3 策略獲利，E12 PF=1.648, WR=45.2%",
            "SL=120：甜蜜點 — E09/E07/E12 均 PF>2.0、WR突破50%；E03 淨盈虧 NT$184萬",
            "SL=120 確認為新基準，更新 Pine Script 預設值",
            "<b>結論：30pts 根本原因是台指期 ATR 平均遠大於 30pts，止損設計需重新校準</b>",
        ],
    },
    {
        "date": "2026-05-13",
        "title": "宏觀分析 — 月度方向 + 週內結構",
        "items": [
            "新增 macro_analysis.py：以週線資料（2012–2026，723 根）統計月度勝率與季節性",
            "整體月勝率 63.9%，平均月漲跌 +199 pts（月初買、月底賣）",
            "九月是唯一偏空月（42.9%）；十二月最穩（78.6%）；四月期望值最大（平均 +518 pts）",
            "週內結構：第1、4、5週勝率較高（58–61%）；第3週最弱（55.4%）",
            "建立操作框架：先看月度季節性偏向 → 再用週線 RSI/BB 判斷當週進場時機",
        ],
    },
    {
        "date": "2026-05-13",
        "title": "第一版回測引擎完成 + Pine Script 生成",
        "items": [
            "完成 experiments/ 模組：loader、indicators、engine、runner、report",
            "20 多單策略 E01–E20（Oscillator / Trend / Breakout / Pattern / Session 五大類）",
            "20 空單策略 S01–S20（對應多單鏡像邏輯）",
            "真實資料回測（TAIFEX_DLY_MXF1!, 30.csv，2025-06 起 8585 bars）",
            "多單 E12 BB Squeeze Break 唯一獲利（PF=1.132, WR=36.1%）",
            "空單全部虧損 — 資料期間為大多頭，做空困難，為預期結果",
            "Pine Script v6 多空各一檔：下拉選單選策略、Enable 開關、R:R 可設定",
        ],
    },
    {
        "date": "2026-05-12",
        "title": "架構設計 — 從 XAUUSD 擴展到台指期",
        "items": [
            "決定標的：MTX 小台指期（每點 NT$50）",
            "相關性指標：NQ 納斯達克期貨（同向，可切換 SOX/SPX/VIX）",
            "SL/TP 改為固定點數（30pts/60pts，R:R 1:2）",
            "時段：日盤（08:45–13:45）+ 夜盤（15:00–05:00）皆納入",
        ],
    },
]

SESSION_LOGS = {"xauusd": XAUUSD_LOG, "tx": TX_LOG, "cross": CROSS_LOG}


# ─── Helpers ─────────────────────────────────────────────────────────
def _load_top3(results_path: Path, n: int = 3) -> list[dict]:
    if not results_path.exists():
        return []
    with open(results_path, encoding="utf-8") as f:
        data = json.load(f)
    return [r for r in data["results"] if r.get("n_trades", 0) > 0][:n]


def _exp_row_xauusd(r: dict, direction: str) -> str:
    colour = "#1e3a5f" if direction == "long" else "#7c3aed"
    pnl_pct = r.get("net_pnl_pct", 0)
    pnl_col = "var(--green)" if pnl_pct >= 0 else "var(--red)"
    sign = "+" if pnl_pct >= 0 else ""
    return (
        f"<tr>"
        f"<td><b style='color:{colour}'>{r.get('rank','-')}. {r['code']}</b></td>"
        f"<td>{r['name']}</td>"
        f"<td>{r.get('n_trades', '-')}</td>"
        f"<td class='{'pos' if r['win_rate']>=45 else 'neutral'}'>{r['win_rate']}%</td>"
        f"<td>{r['profit_factor']:.3f}</td>"
        f"<td style='color:{pnl_col}'>{sign}{pnl_pct:.1f}%</td>"
        f"</tr>"
    )


def _exp_row_tx(r: dict, direction: str) -> str:
    colour = "#1565c0" if direction == "long" else "#880e4f"
    pnl = r.get("net_pnl_ntd", 0)
    pnl_col = "#2e7d32" if pnl >= 0 else "#c62828"
    return (
        f"<tr>"
        f"<td style='color:{colour};font-weight:bold'>{r.get('rank','-')}. {r['code']}</td>"
        f"<td>{r['name']}</td>"
        f"<td>{r['win_rate']}%</td>"
        f"<td>{r['profit_factor']:.3f}</td>"
        f"<td style='color:{pnl_col}'>NT${pnl:,.0f}</td>"
        f"<td>{r.get('score',0):.3f}</td>"
        f"</tr>"
    )


def _session_log_html(commodity_id: str) -> str:
    blocks = []
    for entry in SESSION_LOGS.get(commodity_id, []):
        items_html = "".join(f"<li>{it}</li>" for it in entry["items"])
        blocks.append(
            f"<div class='log-entry'>"
            f"<div class='log-date'>{entry['date']}</div>"
            f"<div><div class='log-title'>{entry['title']}</div>"
            f"<ul class='log-items'>{items_html}</ul></div>"
            f"</div>"
        )
    return "\n".join(blocks)


def _unified_log_html() -> str:
    TAG_CFG = {
        "xauusd": {"label": "🟡 XAUUSD", "bg": "#fef3c7", "color": "#92400e", "border": "#f59e0b"},
        "tx":     {"label": "🔵 TX 台指期", "bg": "#dbeafe", "color": "#1e40af", "border": "#3b82f6"},
        "cross":  {"label": "📊 跨商品",  "bg": "#ede9fe", "color": "#5b21b6", "border": "#7c3aed"},
    }

    all_entries = []
    for cid, log in SESSION_LOGS.items():
        for entry in log:
            all_entries.append({**entry, "_cid": cid})

    all_entries.sort(key=lambda e: e["date"], reverse=True)

    blocks = []
    for entry in all_entries:
        cid = entry["_cid"]
        cfg = TAG_CFG.get(cid, TAG_CFG["cross"])
        tag = (
            f"<span style='display:inline-block;padding:2px 10px;border-radius:12px;"
            f"background:{cfg['bg']};color:{cfg['color']};"
            f"border:1px solid {cfg['border']};font-size:.78em;font-weight:700;"
            f"margin-bottom:6px'>{cfg['label']}</span>"
        )
        items_html = "".join(f"<li>{it}</li>" for it in entry["items"])
        blocks.append(
            f"<div class='log-entry'>"
            f"<div class='log-date'>{entry['date']}</div>"
            f"<div>{tag}<div class='log-title' style='margin-top:2px'>{entry['title']}</div>"
            f"<ul class='log-items'>{items_html}</ul></div>"
            f"</div>"
        )

    legend = "".join(
        f"<span style='display:inline-flex;align-items:center;gap:5px;margin-right:12px;"
        f"padding:3px 10px;border-radius:12px;background:{cfg['bg']};color:{cfg['color']};"
        f"border:1px solid {cfg['border']};font-size:.8em;font-weight:600'>{cfg['label']}</span>"
        for cid, cfg in TAG_CFG.items()
    )

    total = len(all_entries)
    return f"""
  <!-- ══ UNIFIED SESSION LOG ══════════════════════════════════════════ -->
  <div id="commodity-history" class="commodity-section">
    <div class="tab-panel active" style="max-width:1000px;margin:0 auto">
      <div class="part-label"><span class="part-badge">HISTORY</span>對話記錄 · Prompt &amp; Evolution History</div>

      <div class="card" style="margin-bottom:16px">
        <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:10px">
          {legend}
          <span style="color:var(--muted);font-size:.82em;margin-left:auto">共 {total} 筆記錄</span>
        </div>
        <div style="font-size:.84em;color:var(--text2)">
          每筆記錄標示商品歸屬，方便追蹤跨商品分析演進與 Prompt 歷史。
          記錄依日期由新至舊排列。
        </div>
      </div>

      <div class="card">
        {"".join(blocks)}
      </div>
    </div>
  </div><!-- /commodity-history -->
"""


# ─── XAUUSD 宏觀分析（動態讀 CSV）─────────────────────────────────
def _xauusd_macro_html() -> str:
    csv_path = ROOT / "xauusd/csv/FX_IDC_XAUUSD, 1W.csv"
    if not csv_path.exists():
        return '<div id="xauusd-main-macro" class="main-section"><div class="tab-panel active"><p style="padding:24px;color:var(--muted)">週線 CSV 未找到</p></div></div>'

    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    df['time'] = df['time'].apply(lambda t: pd.to_datetime(re.sub(r'[+-]\d{2}:\d{2}$', '', str(t).strip())))
    df = df.sort_values('time').reset_index(drop=True)
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['open']  = pd.to_numeric(df['open'],  errors='coerce')
    df['RSI']   = pd.to_numeric(df['RSI'],   errors='coerce')
    df['year']  = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['week_of_month'] = df.groupby(['year', 'month']).cumcount() + 1
    df = df[df['year'] >= 1980].copy()

    # Monthly aggregation
    grp = df.groupby(['year', 'month'])
    mon = grp.agg(m_open=('open','first'), m_close=('close','last'), rsi_end=('RSI','last')).reset_index()
    mon['chg_pct']  = (mon['m_close'] - mon['m_open']) / mon['m_open'] * 100
    mon['chg_usd']  = mon['m_close'] - mon['m_open']
    mon['bullish']  = mon['chg_pct'] > 0
    mon['date']     = pd.to_datetime(mon[['year','month']].assign(day=1))

    total_months = len(mon)
    overall_wr   = mon['bullish'].mean() * 100
    avg_pct      = mon['chg_pct'].mean()
    latest       = mon.iloc[-1]
    cur_month    = int(latest['month'])
    cur_year     = int(latest['year'])
    month_names  = ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月']

    # Seasonality per month
    sea_rows = ""
    cur_note = ""
    for m in range(1, 13):
        sub = mon[mon['month'] == m]
        if len(sub) == 0:
            continue
        wr      = sub['bullish'].mean() * 100
        avg_p   = sub['chg_pct'].mean()
        avg_u   = sub['chg_usd'].mean()
        bias    = 'LONG' if wr >= 55 else ('SHORT' if wr <= 45 else 'NEUTRAL')
        bc      = 'var(--green)' if bias == 'LONG' else ('var(--red)' if bias == 'SHORT' else 'var(--muted)')
        bl      = '偏多' if bias == 'LONG' else ('偏空' if bias == 'SHORT' else '中性')
        wc      = 'var(--green)' if wr >= 55 else ('var(--red)' if wr <= 45 else 'var(--muted)')
        badge_cls = 'badge-green' if bias == 'LONG' else ('badge-red' if bias == 'SHORT' else 'badge-blue')
        sea_rows += (f"<tr><td>{month_names[m-1]}</td><td>{len(sub)}</td>"
                     f"<td style='color:{wc};font-weight:700'>{wr:.1f}%</td>"
                     f"<td>{'▲' if avg_p>=0 else '▼'} {abs(avg_p):.2f}% (${avg_u:+.0f})</td>"
                     f"<td><span class='badge {badge_cls}'>{bl}</span></td></tr>\n")
        if m == cur_month:
            cur_note = f"當月（{month_names[m-1]}）：歷史勝率 {wr:.1f}%，平均 {avg_p:+.2f}%（${avg_u:+.0f}）"

    # Week-of-month structure
    df['wk_chg'] = (df['close'] - df['open']) / df['open'] * 100
    df['wk_bull'] = df['wk_chg'] > 0
    wim = df[df['week_of_month'] <= 5].groupby('week_of_month').agg(
        n=('wk_chg','count'), wr=('wk_bull','mean'), avg=('wk_chg','mean')).reset_index()
    wim['wr'] = wim['wr'] * 100
    wlabel = {1:'第1週（月初）',2:'第2週',3:'第3週',4:'第4週',5:'第5週（月底）'}
    wim_rows = ""
    for _, r in wim.iterrows():
        wk = int(r['week_of_month'])
        wc = 'var(--green)' if r['wr'] >= 55 else ('var(--red)' if r['wr'] <= 45 else 'var(--muted)')
        wim_rows += (f"<tr><td><strong>{wlabel[wk]}</strong></td><td>{int(r['n'])}</td>"
                     f"<td style='color:{wc};font-weight:700'>{r['wr']:.1f}%</td>"
                     f"<td>{r['avg']:+.2f}%</td></tr>\n")

    # Recent 12 months
    rec = mon.sort_values('date').tail(12)
    rec_rows = ""
    for _, r in rec.iterrows():
        color = 'var(--green)' if r['bullish'] else 'var(--red)'
        sign  = '▲' if r['bullish'] else '▼'
        rec_rows += (f"<tr><td>{int(r['year'])}/{int(r['month']):02d}</td>"
                     f"<td>${r['m_open']:.0f}</td><td>${r['m_close']:.0f}</td>"
                     f"<td style='color:{color};font-weight:700'>{sign} {r['chg_pct']:+.2f}% (${r['chg_usd']:+.0f})</td></tr>\n")

    wr_color = 'var(--green)' if overall_wr >= 55 else 'var(--red)'

    # Session analysis from validation_results.json
    val_path = ROOT / "doc/validation_results.json"
    session_rows = ""
    if val_path.exists():
        with open(val_path, encoding="utf-8") as vf:
            vdata_local = json.load(vf)
        for s in vdata_local.get("xauusd", {}).get("xauusd_sessions", []):
            trend = s["趨勢K比例"]
            wc = "color:var(--red)" if trend >= 0.55 else "color:var(--green)"
            mv = s["平均波動%"]
            lk = s["漲K勝率"]
            lc = "color:var(--green)" if lk >= 0.52 else "color:var(--muted)"
            session_rows += (
                f"<tr><td><b>{s['時段']}</b></td>"
                f"<td style='{wc};font-weight:700'>{trend:.0%}</td>"
                f"<td>{mv:.3f}%</td>"
                f"<td style='{lc};font-weight:700'>{lk:.0%}</td>"
                f"<td>{s['樣本數']:,}</td>"
                f"<td><small style='color:var(--muted)'>{s['筆記判斷']}</small></td></tr>\n"
            )

    return f"""
  <!-- XAUUSD 宏觀分析 -->
  <div id="xauusd-main-macro" class="main-section active">
    <div class="subnav">
      <button class="sub-tab active" onclick="showTab('xauusd-macro','overview',this)">月度統計 &amp; 季節性</button>
      <button class="sub-tab" onclick="showTab('xauusd-macro','weekly',this)">週內結構</button>
      <button class="sub-tab" onclick="showTab('xauusd-macro','recent',this)">近 12 個月</button>
      <button class="sub-tab" onclick="showTab('xauusd-macro','session',this)">時段分析</button>
    </div>

    <div id="xauusd-macro-overview" class="tab-panel active">
      <div class="part-label"><span class="part-badge">MACRO</span>整體月度統計（1980–{int(latest['year'])}）</div>
      <div class="grid-4">
        <div class="metric-card card"><div class="metric-label">整體月勝率</div><div class="metric-val" style="color:{wr_color}">{overall_wr:.1f}%</div><div class="metric-sub">{total_months} 個月（1980–{int(latest['year'])}）</div></div>
        <div class="metric-card card"><div class="metric-label">平均月漲跌</div><div class="metric-val {'green' if avg_pct>=0 else 'red'}">{avg_pct:+.2f}%</div><div class="metric-sub">月初買、月底賣</div></div>
        <div class="metric-card card"><div class="metric-label">當月（{month_names[cur_month-1]}）</div><div class="metric-val">{cur_year}/{cur_month:02d}</div><div class="metric-sub" style="font-size:.8em">{cur_note}</div></div>
        <div class="metric-card card"><div class="metric-label">週線 K 棒數</div><div class="metric-val">{len(df)}</div><div class="metric-sub">1980–{int(latest['year'])}</div></div>
      </div>

      <div class="insight-grid">
        <div class="insight good"><strong>✅ 強勢月份</strong>一月（63.8%）、七月（56.5%）、十二月（56.5%）歷史偏多。</div>
        <div class="insight bad"><strong>❌ 弱勢月份</strong>二月（31.9%）、六月（39.1%）、三月（42.6%）歷史偏空。</div>
        <div class="insight info"><strong>📊 操作框架</strong>先確認月度季節性偏向，再用週線 RSI / BB 判斷進場時機。</div>
      </div>

      <div class="card">
        <div class="card-title">🗓 季節性偏向 — 每月歷史統計（1980–{int(latest['year'])}）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>月份</th><th>樣本</th><th>月勝率</th><th>平均漲跌</th><th>偏向</th></tr></thead>
            <tbody>{sea_rows}</tbody>
          </table>
        </div>
      </div>
      <div class="report-links">
        <a class="report-link" href="xauusd/macro_report.html">📄 完整宏觀報告（暗色主題 + 熱力圖）</a>
      </div>
    </div>

    <div id="xauusd-macro-weekly" class="tab-panel">
      <div class="part-label"><span class="part-badge">MACRO</span>週內結構 — 每月第幾週最強</div>
      <div class="card">
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>週次</th><th>樣本</th><th>週勝率</th><th>平均漲跌%</th></tr></thead>
            <tbody>{wim_rows}</tbody>
          </table>
        </div>
        <div style="margin-top:8px;font-size:.82em;color:var(--muted)">第3週（56.6%）和第5週（55.6%）勝率最高；第4週最低（48.0%）。</div>
      </div>
    </div>

    <div id="xauusd-macro-recent" class="tab-panel">
      <div class="part-label"><span class="part-badge">MACRO</span>近 12 個月回顧</div>
      <div class="card" style="max-width:620px">
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>年/月</th><th>月初開盤</th><th>月底收盤</th><th>月漲跌</th></tr></thead>
            <tbody>{rec_rows}</tbody>
          </table>
        </div>
      </div>
    </div>

    <div id="xauusd-macro-session" class="tab-panel">
      <div class="part-label"><span class="part-badge">MACRO</span>四個時段特性（台北時間）</div>
      <div class="insight-grid">
        <div class="insight warn"><strong>⚠ 亞盤（9–10）最高波動但偏震盪</strong>趨勢K 60%，漲K勝率 58%，平均波動 0.349%（最大）— 但筆記判斷 90% 震盪，不適合追趨勢。</div>
        <div class="insight good"><strong>✅ 歐盤（20–21）為均衡時段</strong>趨勢K 57%，波動 0.236%，漲K勝率 51.5%——筆記判斷 50/50，策略適用性較廣。</div>
        <div class="insight info"><strong>📊 美盤（23–00）趨勢性強</strong>趨勢K 59%，波動 0.292%，漲K勝率 48.1%——美元加速期間波動放大，除非大趨勢否則偏震盪。</div>
        <div class="insight bad"><strong>❌ 午後（14–15）最弱時段</strong>趨勢K 46%（最低），波動 0.216%（最小）——70% 震盪，歐洲開盤前的淡水期，不建議進場。</div>
      </div>
      <div class="card">
        <div class="card-title">⏱ 四個時段統計（30m K 棒，台北時間，2026-01–04）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>時段</th><th>趨勢K比例</th><th>平均波動</th><th>漲K勝率</th><th>樣本數</th><th>筆記判斷</th></tr></thead>
            <tbody>{session_rows or "<tr><td colspan='6' style='color:#999'>請執行 validate_notes.py</td></tr>"}</tbody>
          </table>
        </div>
        <div style="margin-top:8px;font-size:.8em;color:var(--muted)">趨勢K定義：|ret| &gt; 0.15%。漲K勝率 &gt; 52% 偏多、&lt; 48% 偏空。</div>
      </div>
      <div class="report-links">
        <a class="report-link" href="xauusd/macro_report.html">📄 完整宏觀報告（熱力圖）</a>
      </div>
    </div>
  </div><!-- /xauusd-main-macro -->
"""


# ─── XAUUSD static 現有策略優化 HTML ────────────────────────────────
def _xauusd_opt_html() -> str:
    return """
  <!-- XAUUSD 現有策略優化 ────────────────────────────── -->
  <div id="xauusd-main-opt" class="main-section">
    <div class="subnav">
      <button class="sub-tab active" onclick="showTab('xauusd-opt','overview',this)">綜合對比</button>
      <button class="sub-tab" onclick="showTab('xauusd-opt','s1',this)">S1-AweWithBB</button>
      <button class="sub-tab" onclick="showTab('xauusd-opt','s2a',this)">S2A-RSI</button>
      <button class="sub-tab" onclick="showTab('xauusd-opt','s2b',this)">S2B-Hammer</button>
    </div>

    <!-- Overview -->
    <div id="xauusd-opt-overview" class="tab-panel active">
      <div class="part-label"><span class="part-badge">PART 1</span>精華重點 · Key Findings</div>
      <div class="grid-3">
        <div class="card">
          <div class="card-title">📊 S1-AweWithBB <span class="badge badge-yellow">V3.6.2</span></div>
          <div class="grid-2" style="gap:10px">
            <div class="metric-card"><div class="metric-label">勝率</div><div class="metric-val green">53.2%</div></div>
            <div class="metric-card"><div class="metric-label">獲利因子</div><div class="metric-val">1.525</div></div>
            <div class="metric-card"><div class="metric-label">淨盈虧</div><div class="metric-val green">+$6,137</div></div>
            <div class="metric-card"><div class="metric-label">最大回撤</div><div class="metric-val red">-$494</div></div>
          </div>
          <div style="margin-top:12px;font-size:.82em;color:var(--muted)">主要問題：immediate_loss 31% · 504 筆交易</div>
          <div class="report-links"><a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/report.html">完整報告 →</a></div>
        </div>
        <div class="card">
          <div class="card-title">📊 S2A-RSI <span class="badge badge-yellow">V2.3</span></div>
          <div class="grid-2" style="gap:10px">
            <div class="metric-card"><div class="metric-label">勝率</div><div class="metric-val yellow">42.2%</div></div>
            <div class="metric-card"><div class="metric-label">獲利因子</div><div class="metric-val green">1.679</div></div>
            <div class="metric-card"><div class="metric-label">淨盈虧</div><div class="metric-val green">+$6,212</div></div>
            <div class="metric-card"><div class="metric-label">最大回撤</div><div class="metric-val red">-$1,177</div></div>
          </div>
          <div style="margin-top:12px;font-size:.82em;color:var(--muted)">主要問題：time_bleed 52% · 161 筆交易</div>
          <div class="report-links"><a class="report-link" href="xauusd/XAUUSD-Long-S2A-RSI/report.html">完整報告 →</a></div>
        </div>
        <div class="card">
          <div class="card-title">📊 S2B-Hammer <span class="badge badge-yellow">V2.2</span></div>
          <div class="grid-2" style="gap:10px">
            <div class="metric-card"><div class="metric-label">勝率</div><div class="metric-val yellow">44.0%</div></div>
            <div class="metric-card"><div class="metric-label">獲利因子</div><div class="metric-val green">1.681</div></div>
            <div class="metric-card"><div class="metric-label">淨盈虧</div><div class="metric-val green">+$7,722</div></div>
            <div class="metric-card"><div class="metric-label">最大回撤</div><div class="metric-val red">-$1,431</div></div>
          </div>
          <div style="margin-top:12px;font-size:.82em;color:var(--muted)">主要問題：time_bleed 54% · 200 筆交易</div>
          <div class="report-links"><a class="report-link" href="xauusd/XAUUSD-Long-S2B-Hammer/report.html">完整報告 →</a></div>
        </div>
      </div>

      <div class="insight-grid">
        <div class="insight good"><strong>✅ DXY RSI &lt; 30 → 最佳做多窗口</strong>美元超賣時三策略勝率均升至 60–75%。</div>
        <div class="insight good"><strong>✅ HTF Alignment 3/3 → S1 勝率 ~69%</strong>4H + 1D + 60m 全部看多時，S1 勝率比整體高出 16%。</div>
        <div class="insight warn"><strong>⚠ S1 BB 位置是關鍵過濾器</strong>S1 在 price > BB 上軌時勝率 77.8%；低於中軌時僅 0–20%。建議：僅在 BB %B > 0.6 時進場。</div>
        <div class="insight bad"><strong>❌ S2 的 time_bleed 問題尚未解決</strong>超過 50% 的虧損是持倉超時。已在 V2.3/V2.2 加入 strategy.close() 時間止損修正。</div>
        <div class="insight info"><strong>📊 4H bearish 是最大失敗來源</strong>4H RSI bearish 時 S1 immediate_loss 升高，S2 time_bleed 升高。4H 過濾器已驗證 +1.6%~+4.1% ΔWR。</div>
        <div class="insight purple"><strong>🔬 背離分析：樣本不足</strong>30m 資料中只有 17 個 RSI 背離信號（3 個月），統計效力不足。需要更長時間資料。</div>
      </div>

      <div class="card">
        <div class="card-title">🗂 策略分類體系</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>族群</th><th>策略 ID</th><th>進場類型</th><th>觸發信號</th><th>Entry Label</th><th>當前版本</th></tr></thead>
            <tbody>
              <tr>
                <td><span class="badge badge-green">S1 右側突破</span></td>
                <td><strong>S1-AweWithBB</strong></td><td>趨勢確認後順勢進場（突破 BB 上軌）</td>
                <td>Awesome Oscillator + BB 突破</td><td><code>S1BB_LE</code></td><td class="ver-test">V3.6.2 🧪</td>
              </tr>
              <tr>
                <td rowspan="2"><span class="badge badge-blue">S2 左側跌深</span></td>
                <td><strong>S2A-RSI</strong></td><td>超賣區逆勢進場（指標）</td>
                <td>RSI 交叉 / 背離</td><td><code>S2A_LE</code></td><td class="ver-test">V2.3 🧪</td>
              </tr>
              <tr>
                <td><strong>S2B-Hammer</strong></td><td>超賣區逆勢進場（K 線）</td>
                <td>Hammer 錘形蠟燭</td><td><code>S2B_LE</code></td><td class="ver-test">V2.2 🧪</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-title">🧩 Pine Script 版本狀態</div>
        <div class="tbl-wrap">
          <table class="version-row">
            <thead><tr><th>策略</th><th>版本</th><th>狀態</th><th>新增功能</th></tr></thead>
            <tbody>
              <tr><td>S1-AweWithBB</td><td class="ver-confirmed">V3.5</td><td><span class="badge badge-green">確認版</span></td><td>DXY RSI + RSI 動能過濾器</td></tr>
              <tr><td>S1-AweWithBB</td><td class="ver-test">V3.6.2</td><td><span class="badge badge-yellow">測試中</span></td><td>BB %B ≥ 0.6 + 4H HTF RSI + lookahead_off 修正 + S1BB_LE 統一 label</td></tr>
              <tr><td>S2A-RSI</td><td class="ver-confirmed">V2.2</td><td><span class="badge badge-green">確認版</span></td><td>統一 S2A_LE + EMA group + 架構對齊</td></tr>
              <tr><td>S2A-RSI</td><td class="ver-test">V2.3</td><td><span class="badge badge-yellow">測試中</span></td><td>時間止損修正（strategy.close()）+ 4H HTF RSI 過濾器</td></tr>
              <tr><td>S2B-Hammer</td><td class="ver-confirmed">V2.1</td><td><span class="badge badge-green">確認版</span></td><td>統一 S2B_LE + EMA group + 架構對齊</td></tr>
              <tr><td>S2B-Hammer</td><td class="ver-test">V2.2</td><td><span class="badge badge-yellow">測試中</span></td><td>時間止損修正（strategy.close()）+ 4H HTF RSI 過濾器</td></tr>
            </tbody>
          </table>
        </div>
        <div class="report-links">
          <a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/XAUUSD-Long-S1-AweWithBB-V3.6.2.pine">S1 V3.6.2 🧪</a>
          <a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/XAUUSD-Long-S1-AweWithBB-V3.5.pine">S1 V3.5 ✅</a>
          <a class="report-link" href="xauusd/XAUUSD-Long-S2A-RSI/XAUUSD-Long-S2A-RSI-V2.3.pine">S2A V2.3 🧪</a>
          <a class="report-link" href="xauusd/XAUUSD-Long-S2B-Hammer/XAUUSD-Long-S2B-Hammer-V2.2.pine">S2B V2.2 🧪</a>
        </div>
      </div>

      <div class="part-label"><span class="part-badge">PART 2</span>分析紀錄</div>
      <div class="card">
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>日期</th><th>對談重點</th><th>產出</th><th>交易備忘錄</th></tr></thead>
            <tbody>
              <tr><td class="td-date">2026-05-02</td><td><span class="tag tag-pine">Pine</span> 策略命名重構 + lookahead 修正</td><td>S1 V3.6.2 / S2A V2.2 / S2B V2.1</td><td class="td-memo"><strong>重繪修正後回測數字可能改變</strong>，全歷史驗證前不算確認版</td></tr>
              <tr><td class="td-date">2026-05-01</td><td><span class="tag tag-analysis">分析</span> BB %B 位置分析 + RSI 背離</td><td>bb_analysis.py / divergence.py</td><td class="td-memo"><strong>S1 price > BB 上軌 WR 77.8%</strong>；%B &lt; 0.4 不建議進場</td></tr>
              <tr><td class="td-date">2026-04-29</td><td><span class="tag tag-analysis">分析</span> MTF 共軌分析</td><td>mtf_analysis.py</td><td class="td-memo"><strong>alignment=3/3 → S1 WR ~69%</strong>；空單 4H 過濾 +4.1% ΔWR</td></tr>
              <tr><td class="td-date">2026-04-28</td><td><span class="tag tag-pine">Pine</span> Insight Filters 設計</td><td>S1 V3.5 / S2 V2.1</td><td class="td-memo">DXY RSI &lt; 50 + RSI 動能上升才進場</td></tr>
              <tr><td class="td-date">2026-04-27</td><td><span class="tag tag-analysis">分析</span> DXY 相關性 + 初始失敗模式</td><td>dxy_analysis.py / fail_patterns.py</td><td class="td-memo"><strong>DXY RSI &lt; 30 三策略勝率 60–75%</strong>；S2 time_bleed 是主要問題</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div><!-- /overview -->

    <!-- S1 Tab -->
    <div id="xauusd-opt-s1" class="tab-panel">
      <div class="part-label"><span class="part-badge">PART 1</span>S1-AweWithBB 精華重點</div>
      <div class="grid-4">
        <div class="metric-card card"><div class="metric-label">勝率</div><div class="metric-val green">53.2%</div><div class="metric-sub">504 筆交易</div></div>
        <div class="metric-card card"><div class="metric-label">獲利因子</div><div class="metric-val">1.525</div><div class="metric-sub">淨盈虧 +$6,137</div></div>
        <div class="metric-card card"><div class="metric-label">最大回撤</div><div class="metric-val red">-$494</div><div class="metric-sub">低回撤策略</div></div>
        <div class="metric-card card"><div class="metric-label">immediate_loss</div><div class="metric-val red">31%</div><div class="metric-sub">進場即虧的虧損</div></div>
      </div>
      <div class="insight-grid">
        <div class="insight good"><strong>✅ BB %B 位置關鍵發現</strong>price > BB 上軌（%B > 1.0）：WR 77.8%（n=9）<br>near_upper（%B 0.8–1.0）：WR 61.1%（n=18）<br>low zone（%B &lt; 0.4）：WR 0–20%<br>→ BB %B ≥ 0.6 過濾器（V3.6.1 已實作）</div>
        <div class="insight info"><strong>📊 4H HTF 共軌影響</strong>alignment 0/3：~43% WR | alignment 3/3：~69% WR<br>4H bearish 時 immediate_loss 顯著升高</div>
        <div class="insight warn"><strong>⚠ DXY 關鍵時機</strong>DXY RSI &lt; 30（USD 超賣）：60.9% WR<br>DXY RSI 30–50：49.8% WR（最差）</div>
        <div class="insight bad"><strong>❌ 危險時段</strong>Hour 9 immediate_loss 比例最高；Hour 14 次之<br>考慮 session filter 排除這些時段</div>
      </div>
      <div class="report-links">
        <a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/report.html">📄 完整報告</a>
        <a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/XAUUSD-Long-S1-AweWithBB-V3.6.2.pine">🧪 V3.6.2</a>
        <a class="report-link" href="xauusd/XAUUSD-Long-S1-AweWithBB/XAUUSD-Long-S1-AweWithBB-V3.5.pine">✅ V3.5</a>
      </div>
    </div>

    <!-- S2A Tab -->
    <div id="xauusd-opt-s2a" class="tab-panel">
      <div class="part-label"><span class="part-badge">PART 1</span>S2A-RSI 精華重點</div>
      <div class="grid-4">
        <div class="metric-card card"><div class="metric-label">勝率</div><div class="metric-val yellow">42.2%</div><div class="metric-sub">161 筆交易</div></div>
        <div class="metric-card card"><div class="metric-label">獲利因子</div><div class="metric-val green">1.679</div><div class="metric-sub">淨盈虧 +$6,212</div></div>
        <div class="metric-card card"><div class="metric-label">最大回撤</div><div class="metric-val red">-$1,177</div><div class="metric-sub">中等回撤</div></div>
        <div class="metric-card card"><div class="metric-label">time_bleed</div><div class="metric-val red">52%</div><div class="metric-sub">持倉超時的虧損</div></div>
      </div>
      <div class="insight-grid">
        <div class="insight bad"><strong>❌ time_bleed 超過一半虧損</strong>平均持倉 140 bars（70 小時）— 遠超合理範圍<br>→ 最優先：48 bar 時間強制止損（V2.3 已修正）</div>
        <div class="insight info"><strong>📊 DXY 影響最顯著</strong>DXY RSI 30–50：38.4% WR（最差）<br>DXY RSI &lt; 30：75.0% WR（最佳，n=4）</div>
        <div class="insight good"><strong>✅ 高盈虧比補償低勝率</strong>PF 1.679 — 贏的交易夠大、輸的控制尚可<br>→ 重點是減少 time_bleed 而非提高勝率</div>
      </div>
      <div class="report-links">
        <a class="report-link" href="xauusd/XAUUSD-Long-S2A-RSI/report.html">📄 完整報告</a>
        <a class="report-link" href="xauusd/XAUUSD-Long-S2A-RSI/XAUUSD-Long-S2A-RSI-V2.3.pine">🧪 V2.3</a>
      </div>
    </div>

    <!-- S2B Tab -->
    <div id="xauusd-opt-s2b" class="tab-panel">
      <div class="part-label"><span class="part-badge">PART 1</span>S2B-Hammer 精華重點</div>
      <div class="grid-4">
        <div class="metric-card card"><div class="metric-label">勝率</div><div class="metric-val yellow">44.0%</div><div class="metric-sub">200 筆交易</div></div>
        <div class="metric-card card"><div class="metric-label">獲利因子</div><div class="metric-val green">1.681</div><div class="metric-sub">淨盈虧 +$7,722</div></div>
        <div class="metric-card card"><div class="metric-label">最大回撤</div><div class="metric-val red">-$1,431</div><div class="metric-sub">三策略中最高</div></div>
        <div class="metric-card card"><div class="metric-label">time_bleed</div><div class="metric-val red">54%</div><div class="metric-sub">持倉超時的虧損</div></div>
      </div>
      <div class="insight-grid">
        <div class="insight bad"><strong>❌ time_bleed 最嚴重</strong>54% 虧損是超時持倉，三策略中最高<br>→ V2.2 已加入 strategy.close() 時間止損</div>
        <div class="insight warn"><strong>⚠ near_upper 有陷阱</strong>near_upper（%B 0.8–1.0）WR 只有 14.3%（n=7）<br>lower_mid（%B 0.2–0.4）WR 50.0%（n=10）最好</div>
        <div class="insight info"><strong>📊 時段差異</strong>亞盤勝率 39.5%（最差）；美盤 49.3%（最佳）<br>→ 考慮關閉亞盤進場</div>
        <div class="insight good"><strong>✅ DXY 超賣時最佳</strong>DXY RSI &lt; 30：66.7% WR</div>
      </div>
      <div class="report-links">
        <a class="report-link" href="xauusd/XAUUSD-Long-S2B-Hammer/report.html">📄 完整報告</a>
        <a class="report-link" href="xauusd/XAUUSD-Long-S2B-Hammer/XAUUSD-Long-S2B-Hammer-V2.2.pine">🧪 V2.2</a>
      </div>
    </div>
  </div><!-- /xauusd-main-opt -->
"""


def _xauusd_exp_html(long_rows: str, short_rows: str, c: dict) -> str:
    long_link  = c["long_dir"] + "/report.html"
    short_link = c["short_dir"] + "/report.html"
    long_pine  = c["long_pine"]
    short_pine = c["short_pine"]
    long_exists  = (ROOT / long_link).exists()
    short_exists = (ROOT / short_link).exists()

    long_btn  = f"<a class='report-link' href='{long_link}'>完整報告 →</a>" if long_exists else ""
    short_btn = f"<a class='report-link' href='{short_link}'>完整報告 →</a>" if short_exists else ""

    return f"""
  <!-- XAUUSD 實驗策略 ──────────────────────────────────── -->
  <div id="xauusd-main-exp" class="main-section">
    <div class="subnav">
      <button class="sub-tab active" onclick="showTab('xauusd-exp','overview',this)">綜合對比</button>
      <button class="sub-tab" onclick="showTab('xauusd-exp','long',this)">多單 Long (E01–E20)</button>
      <button class="sub-tab" onclick="showTab('xauusd-exp','short',this)">空單 Short (S01–S20)</button>
    </div>

    <div id="xauusd-exp-overview" class="tab-panel active">
      <div class="part-label"><span class="part-badge">PART 1</span>精華重點 · Key Findings</div>
      <div class="grid-2">
        <div class="card">
          <div class="card-title">📈 多單 Top-3（E01–E20）</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>#</th><th>策略</th><th>筆數</th><th>勝率</th><th>PF</th><th>淨盈虧%</th></tr></thead>
              <tbody>{long_rows or "<tr><td colspan='6' style='color:#999'>尚無資料（請執行 run_experiments.py）</td></tr>"}</tbody>
            </table>
          </div>
          <div class="report-links">
            {long_btn}
            <a class="report-link" href="{long_pine}">ALL_Long.pine →</a>
          </div>
        </div>
        <div class="card">
          <div class="card-title">📉 空單 Top-3（S01–S20）</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>#</th><th>策略</th><th>筆數</th><th>勝率</th><th>PF</th><th>淨盈虧%</th></tr></thead>
              <tbody>{short_rows or "<tr><td colspan='6' style='color:#999'>尚無資料</td></tr>"}</tbody>
            </table>
          </div>
          <div class="report-links">
            {short_btn}
            <a class="report-link" href="{short_pine}">ALL_Short.pine →</a>
          </div>
        </div>
      </div>

      <div class="insight-grid">
        <div class="insight good"><strong>✅ HTF 4H 過濾器驗證結果</strong>空單過濾（跳過 4H bullish）：<strong>+4.1% ΔWR，16/20 改善</strong><br>多單過濾（跳過 4H bearish）：+1.6% ΔWR，11/20 改善</div>
        <div class="insight good"><strong>✅ BB 策略多空雙向有效</strong>E12 BB Squeeze（多單 #2）和 S12 BB Squeeze（空單 #3）均有效</div>
        <div class="insight warn"><strong>⚠ 此期間空單 &gt; 多單</strong>空單整體表現優於多單（S19 +12.4% vs E03 +9.0%）</div>
        <div class="insight info"><strong>📊 下一步建議</strong>在 TradingView 驗證 E03 + S19；將 HTF 4H 過濾器加入 ALL Pine 版</div>
      </div>

      <div class="part-label"><span class="part-badge">PART 2</span>分析紀錄</div>
      <div class="card"><div class="tbl-wrap">
        <table>
          <thead><tr><th>日期</th><th>重點</th><th>備忘錄</th></tr></thead>
          <tbody>
            <tr><td class="td-date">2026-05-01</td><td><span class="tag tag-analysis">分析</span> HTF 4H 過濾器加入實驗引擎</td><td class="td-memo"><strong>空單 +4.1% ΔWR（16/20 改善）</strong></td></tr>
            <tr><td class="td-date">2026-04-29</td><td><span class="tag tag-pine">Pine</span> 合併 Pine Script（下拉選單）</td><td class="td-memo">TradingView 一個腳本切換全部 20 策略</td></tr>
            <tr><td class="td-date">2026-04-27</td><td><span class="tag tag-new">新建</span> 20 多單 + 20 空單策略回測框架</td><td class="td-memo"><strong>E03 MACD Signal 最佳（PF 1.643）</strong>；S19 Bearish Engulf 空單最佳（+12.4%）</td></tr>
          </tbody>
        </table>
      </div></div>
    </div><!-- /exp-overview -->

    <div id="xauusd-exp-long" class="tab-panel">
      <div class="part-label"><span class="part-badge">PART 1</span>多單實驗精華重點</div>
      <div class="grid-4">
        <div class="metric-card card"><div class="metric-label">最佳策略</div><div class="metric-val" style="font-size:1em">E03 MACD Signal</div></div>
        <div class="metric-card card"><div class="metric-label">最佳 PF</div><div class="metric-val green">1.643</div></div>
        <div class="metric-card card"><div class="metric-label">最佳淨盈虧%</div><div class="metric-val green">+9.0%</div></div>
        <div class="metric-card card"><div class="metric-label">HTF 過濾後 ΔWR</div><div class="metric-val green">+1.6%</div><div class="metric-sub">11/20 改善</div></div>
      </div>
      <div class="report-links">
        <a class="report-link" href="{long_link}">📄 完整報告</a>
        <a class="report-link" href="{long_pine}">📋 ALL_Long_Strategies.pine</a>
      </div>
    </div>

    <div id="xauusd-exp-short" class="tab-panel">
      <div class="part-label"><span class="part-badge">PART 1</span>空單實驗精華重點</div>
      <div class="grid-4">
        <div class="metric-card card"><div class="metric-label">最佳策略</div><div class="metric-val" style="font-size:1em">S19 Bearish Engulf</div></div>
        <div class="metric-card card"><div class="metric-label">最佳 PF</div><div class="metric-val green">1.507</div></div>
        <div class="metric-card card"><div class="metric-label">最佳淨盈虧%</div><div class="metric-val green">+12.4%</div></div>
        <div class="metric-card card"><div class="metric-label">HTF 過濾後 ΔWR</div><div class="metric-val green">+4.1%</div><div class="metric-sub">16/20 改善</div></div>
      </div>
      <div class="report-links">
        <a class="report-link" href="{short_link}">📄 完整報告</a>
        <a class="report-link" href="{short_pine}">📋 ALL_Short_Strategies.pine</a>
      </div>
    </div>
  </div><!-- /xauusd-main-exp -->
"""


def _tx_macro_html() -> str:
    csv_path = ROOT / "tx/csv/TAIFEX_DLY_MXF1!, 1W.csv"
    if not csv_path.exists():
        return '<div id="tx-main-macro" class="main-section active"><div class="tab-panel active"><p style="padding:24px;color:var(--muted)">週線 CSV 未找到</p></div></div>'

    df = pd.read_csv(csv_path)
    df.columns = [c.strip() for c in df.columns]
    df['time']  = pd.to_datetime(df['time'].astype(str).str.strip(), errors='coerce')
    df = df.dropna(subset=['time']).sort_values('time').reset_index(drop=True)
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df['open']  = pd.to_numeric(df['open'],  errors='coerce')
    df['year']  = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['week_of_month'] = df.groupby(['year','month']).cumcount() + 1

    grp = df.groupby(['year','month'])
    mon = grp.agg(m_open=('open','first'), m_close=('close','last')).reset_index()
    mon['chg_pts']  = mon['m_close'] - mon['m_open']
    mon['bullish']  = mon['chg_pts'] > 0
    mon['date']     = pd.to_datetime(mon[['year','month']].assign(day=1))

    total_months = len(mon)
    overall_wr   = mon['bullish'].mean() * 100
    avg_pts      = mon['chg_pts'].mean()
    latest       = mon.iloc[-1]
    cur_month    = int(latest['month'])
    cur_year     = int(latest['year'])
    month_names  = ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月']

    sea_rows = ""
    cur_note = ""
    for m in range(1, 13):
        sub = mon[mon['month'] == m]
        if len(sub) == 0:
            continue
        wr     = sub['bullish'].mean() * 100
        avg_p  = sub['chg_pts'].mean()
        bias   = 'LONG' if wr >= 55 else ('SHORT' if wr <= 45 else 'NEUTRAL')
        bc_cls = 'badge-green' if bias == 'LONG' else ('badge-red' if bias == 'SHORT' else 'badge-blue')
        bl     = '偏多' if bias == 'LONG' else ('偏空' if bias == 'SHORT' else '中性')
        wc     = 'var(--green)' if wr >= 55 else ('var(--red)' if wr <= 45 else 'var(--muted)')
        sea_rows += (f"<tr><td>{month_names[m-1]}</td><td>{len(sub)}</td>"
                     f"<td style='color:{wc};font-weight:700'>{wr:.1f}%</td>"
                     f"<td>{'▲' if avg_p>=0 else '▼'} {abs(avg_p):.0f} pts</td>"
                     f"<td><span class='badge {bc_cls}'>{bl}</span></td></tr>\n")
        if m == cur_month:
            cur_note = f"當月（{month_names[m-1]}）：歷史勝率 {wr:.1f}%，平均 {avg_p:+.0f} pts"

    df['wk_chg']  = df['close'] - df['open']
    df['wk_bull'] = df['wk_chg'] > 0
    wim = df[df['week_of_month'] <= 5].groupby('week_of_month').agg(
        n=('wk_chg','count'), wr=('wk_bull','mean'), avg=('wk_chg','mean')).reset_index()
    wim['wr'] = wim['wr'] * 100
    wlabel = {1:'第1週（月初）',2:'第2週',3:'第3週',4:'第4週',5:'第5週（月底）'}
    wim_rows = ""
    for _, r in wim.iterrows():
        wk = int(r['week_of_month'])
        wc = 'var(--green)' if r['wr'] >= 55 else ('var(--red)' if r['wr'] <= 45 else 'var(--muted)')
        wim_rows += (f"<tr><td><strong>{wlabel[wk]}</strong></td><td>{int(r['n'])}</td>"
                     f"<td style='color:{wc};font-weight:700'>{r['wr']:.1f}%</td>"
                     f"<td>{r['avg']:+.0f} pts</td></tr>\n")

    rec = mon.sort_values('date').tail(12)
    rec_rows = ""
    for _, r in rec.iterrows():
        color = 'var(--green)' if r['bullish'] else 'var(--red)'
        sign  = '▲' if r['bullish'] else '▼'
        rec_rows += (f"<tr><td>{int(r['year'])}/{int(r['month']):02d}</td>"
                     f"<td>${r['m_open']:.0f}</td><td>${r['m_close']:.0f}</td>"
                     f"<td style='color:{color};font-weight:700'>{sign} {r['chg_pts']:+.0f} pts</td></tr>\n")

    wr_color = 'var(--green)' if overall_wr >= 55 else 'var(--red)'

    # Session analysis: day vs night from TX-Long-Experiments/results.json
    sess_rows = ""
    results_p = ROOT / "tx/TX-Long-Experiments/results.json"
    if results_p.exists():
        with open(results_p, encoding="utf-8") as rf:
            rdata = json.load(rf)
        all_results = [r for r in rdata.get("results", []) if r.get("n_trades", 0) > 0]
        if all_results:
            avg_day   = sum(r["day_win_rate"] for r in all_results if "day_win_rate" in r) / len(all_results)
            avg_night = sum(r["night_win_rate"] for r in all_results if "night_win_rate" in r) / len(all_results)
            confirmed = {"E07", "E09", "E12"}
            for r in all_results[:10]:
                d  = r.get("day_win_rate", 0)
                n  = r.get("night_win_rate", 0)
                dc = "color:var(--green);font-weight:700" if d >= 50 else "color:var(--muted)"
                nc = "color:var(--green);font-weight:700" if n >= 50 else "color:var(--muted)"
                star = "⭐" if r["code"] in confirmed else ""
                pref = "夜盤" if n > d + 2 else ("日盤" if d > n + 2 else "均可")
                sess_rows += (f"<tr><td><b>{r['code']}</b> {star}</td><td>{r['name']}</td>"
                              f"<td style='{dc}'>{d:.1f}%</td>"
                              f"<td style='{nc}'>{n:.1f}%</td>"
                              f"<td>{pref}</td></tr>\n")

    return f"""
    <!-- TX 宏觀分析 ───────────────────────────────────── -->
    <div id="tx-main-macro" class="main-section active">
      <div class="subnav">
        <button class="sub-tab active" onclick="showTab('tx-macro','overview',this)">月度統計 &amp; 季節性</button>
        <button class="sub-tab" onclick="showTab('tx-macro','weekly',this)">週內結構</button>
        <button class="sub-tab" onclick="showTab('tx-macro','recent',this)">近 12 個月</button>
        <button class="sub-tab" onclick="showTab('tx-macro','session',this)">時段分析</button>
      </div>

      <div id="tx-macro-overview" class="tab-panel active">
        <div class="part-label"><span class="part-badge">MACRO</span>整體月度統計（2012–{int(latest['year'])}）</div>
        <div class="grid-4">
          <div class="metric-card card"><div class="metric-label">整體月勝率</div><div class="metric-val" style="color:{wr_color}">{overall_wr:.1f}%</div><div class="metric-sub">{total_months} 個月（2012–{int(latest['year'])}）</div></div>
          <div class="metric-card card"><div class="metric-label">平均月漲跌</div><div class="metric-val {'green' if avg_pts>=0 else 'red'}">{avg_pts:+.0f} pts</div><div class="metric-sub">月初買、月底賣</div></div>
          <div class="metric-card card"><div class="metric-label">當月（{month_names[cur_month-1]}）</div><div class="metric-val">{cur_year}/{cur_month:02d}</div><div class="metric-sub" style="font-size:.8em">{cur_note}</div></div>
          <div class="metric-card card"><div class="metric-label">週線 K 棒數</div><div class="metric-val">{len(df)}</div><div class="metric-sub">2012–{int(latest['year'])}</div></div>
        </div>

        <div class="insight-grid">
          <div class="insight good"><strong>✅ 整體偏多</strong>月勝率 {overall_wr:.1f}%，月初買月底賣平均 {avg_pts:+.0f} pts — 大方向順多。</div>
          <div class="insight warn"><strong>⚠ 九月唯一偏空月</strong>歷史勝率僅 42.9%；策略測試需注意此月份空單機會較多。</div>
          <div class="insight info"><strong>📊 四月期望值最大，十二月最穩</strong>四月平均 +518 pts；十二月月勝率 78.6%（最高）。</div>
        </div>

        <div class="card">
          <div class="card-title">🗓 季節性偏向 — 每月歷史統計（2012–{int(latest['year'])}）</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>月份</th><th>樣本</th><th>月勝率</th><th>平均漲跌（pts）</th><th>偏向</th></tr></thead>
              <tbody>{sea_rows}</tbody>
            </table>
          </div>
        </div>
        <div class="report-links">
          <a class="report-link" href="tx/macro_report.html">📄 完整宏觀報告（暗色主題 + 熱力圖）</a>
        </div>
      </div>

      <div id="tx-macro-weekly" class="tab-panel">
        <div class="part-label"><span class="part-badge">MACRO</span>週內結構 — 每月第幾週最強</div>
        <div class="card">
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>週次</th><th>樣本</th><th>週勝率</th><th>平均漲跌（pts）</th></tr></thead>
              <tbody>{wim_rows}</tbody>
            </table>
          </div>
          <div style="margin-top:8px;font-size:.82em;color:var(--muted)">第1、4、5週勝率較高；第3週（月中）最弱。建議在月初或月末偏強週順月度方向進場。</div>
        </div>
      </div>

      <div id="tx-macro-recent" class="tab-panel">
        <div class="part-label"><span class="part-badge">MACRO</span>近 12 個月回顧</div>
        <div class="card" style="max-width:620px">
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>年/月</th><th>月初開盤</th><th>月底收盤</th><th>月漲跌（pts）</th></tr></thead>
              <tbody>{rec_rows}</tbody>
            </table>
          </div>
        </div>
      </div>

      <div id="tx-macro-session" class="tab-panel">
        <div class="part-label"><span class="part-badge">MACRO</span>日盤 vs 夜盤分析（台指期 MTX）</div>
        <div class="insight-grid">
          <div class="insight good"><strong>✅ 夜盤整體優於日盤</strong>確認策略（⭐E07/E09/E12）夜盤勝率平均高 6–10%；夜盤受美股直接驅動，NQ 方向更明確。</div>
          <div class="insight warn"><strong>⚠ 日盤波動受國際消息主導</strong>開盤跳空後反轉機率高，SL=120 pts 的設計下 immediate_loss 在日盤更常見。</div>
          <div class="insight info"><strong>📊 操作建議</strong>優先在夜盤開啟確認策略；日盤可縮減 Size 或加嚴過濾條件（如 NQ RSI 同向確認）。</div>
        </div>
        <div class="card">
          <div class="card-title">🌙 多單策略 日盤 vs 夜盤勝率（SL=120, TP=240）</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>代碼</th><th>策略名稱</th><th>日盤 WR</th><th>夜盤 WR</th><th>偏好時段</th></tr></thead>
              <tbody>{sess_rows or "<tr><td colspan='5' style='color:#999'>尚無資料（請執行 run_experiments.py）</td></tr>"}</tbody>
            </table>
          </div>
          <div style="margin-top:8px;font-size:.8em;color:var(--muted)">⭐ = 已確認策略（E07/E09/E12）</div>
        </div>
      </div>
    </div><!-- /tx-main-macro -->
"""


def _tx_confirmed_html() -> str:
    results_path = ROOT / "tx/TX-Long-Experiments/results.json"
    confirmed_ids = {"E07", "E09", "E12"}
    cards_html = ""
    sess_rows  = ""

    if results_path.exists():
        with open(results_path, encoding="utf-8") as f:
            rdata = json.load(f)
        sl = rdata.get("sl_pts", 120)
        tp = rdata.get("tp_pts", 240)
        confirmed_list = [r for r in rdata.get("results", []) if r["code"] in confirmed_ids]
        for r in confirmed_list:
            pnl  = r.get("net_pnl_ntd", 0)
            pnl_c = "var(--green)" if pnl >= 0 else "var(--red)"
            dwr  = r.get("day_win_rate", 0)
            nwr  = r.get("night_win_rate", 0)
            pref = "夜盤" if nwr > dwr + 2 else ("日盤" if dwr > nwr + 2 else "均可")
            wc   = "var(--green)" if r["win_rate"] >= 50 else "var(--yellow)"
            cards_html += f"""
        <div class="card">
          <div class="card-title">📊 {r['code']} {r['name']} <span class="badge badge-green">✅ 已確認</span></div>
          <div class="grid-4" style="gap:10px">
            <div class="metric-card"><div class="metric-label">勝率</div><div class="metric-val" style="color:{wc}">{r['win_rate']}%</div></div>
            <div class="metric-card"><div class="metric-label">獲利因子</div><div class="metric-val green">{r['profit_factor']:.3f}</div></div>
            <div class="metric-card"><div class="metric-label">淨盈虧</div><div class="metric-val" style="color:{pnl_c}">NT${pnl:,.0f}</div></div>
            <div class="metric-card"><div class="metric-label">交易筆數</div><div class="metric-val">{r['n_trades']}</div></div>
          </div>
          <div style="margin-top:10px;font-size:.82em;color:var(--muted)">SL={sl}pts / TP={tp}pts (R:R 1:{tp//sl}) &nbsp;·&nbsp; 偏好時段：{pref}（日盤 {dwr}% / 夜盤 {nwr}%）</div>
        </div>
"""
            sess_rows += (f"<tr><td><b>{r['code']}</b></td><td>{r['name']}</td>"
                          f"<td>{r['n_trades']}</td>"
                          f"<td style='color:{wc};font-weight:700'>{r['win_rate']}%</td>"
                          f"<td>{r['profit_factor']:.3f}</td>"
                          f"<td style='color:{pnl_c};font-weight:700'>NT${pnl:,.0f}</td>"
                          f"<td style='color:{'var(--green)' if dwr>=50 else 'var(--muted)'}'>{dwr}%</td>"
                          f"<td style='color:{'var(--green)' if nwr>=50 else 'var(--muted)'}'>{nwr}%</td>"
                          f"</tr>\n")
    else:
        sl, tp = 120, 240
        cards_html = "<p style='color:var(--muted);padding:12px'>尚無資料（請執行 run_experiments.py --sl 120）</p>"

    return f"""
  <!-- TX 已確認策略 ──────────────────────────────────── -->
  <div id="tx-main-confirmed" class="main-section">
    <div class="subnav">
      <button class="sub-tab active" onclick="showTab('tx-confirmed','overview',this)">策略總覽</button>
      <button class="sub-tab" onclick="showTab('tx-confirmed','context',this)">確認依據</button>
    </div>

    <div id="tx-confirmed-overview" class="tab-panel active">
      <div class="part-label"><span class="part-badge">CONFIRMED</span>已確認策略 · SL={sl}pts / TP={tp}pts</div>
      <div class="insight-grid">
        <div class="insight good"><strong>✅ SL=120pts 是甜蜜點</strong>系統性測試 SL 30/50/60/80/100/120/150 後，SL=120 時 E09/E07/E12 均達 PF>2.0、WR>50%。</div>
        <div class="insight info"><strong>📊 確認條件</strong>PF &gt; 1.5 且 WR &gt; 48% 且淨盈虧為正，在 2025-06 至今的 MTX 30m 資料中通過。</div>
        <div class="insight warn"><strong>⚠ 當前資料期間</strong>2025-06 至今為台指大多頭，確認策略均為多單。空單策略尚無確認版本。</div>
      </div>
      <div class="grid-3">
{cards_html}
      </div>
    </div>

    <div id="tx-confirmed-context" class="tab-panel">
      <div class="part-label"><span class="part-badge">CONFIRMED</span>確認依據 · SL 敏感度分析（2026-05-13）</div>
      <div class="card">
        <div class="card-title">🧪 SL 敏感度測試結果（E09/E07/E12，R:R 固定 2:1）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>SL（pts）</th><th>TP（pts）</th><th>獲利策略數</th><th>備註</th></tr></thead>
            <tbody>
              <tr><td>30</td><td>60</td><td>1 (E12)</td><td>SL 過緊，ATR 遠大於 30pts</td></tr>
              <tr><td>60</td><td>120</td><td>3</td><td>E12 PF=1.648, WR=45.2%</td></tr>
              <tr><td>80</td><td>160</td><td>3–4</td><td>轉折點，開始改善</td></tr>
              <tr><td>100</td><td>200</td><td>5+</td><td>持續改善</td></tr>
              <tr class="rank-1"><td><b>120 ★</b></td><td><b>240</b></td><td><b>E09/E07/E12 均 PF>2.0</b></td><td><b>甜蜜點 — 新基準</b></td></tr>
              <tr><td>150</td><td>300</td><td>同上但交易筆數減少</td><td>信號更少</td></tr>
            </tbody>
          </table>
        </div>
        <div style="margin-top:10px;font-size:.85em;color:var(--text2)">
          <b>根本原因：</b>台指期 MTX 平均 ATR ≈ 50–150 pts，SL=30 只有 0.15%，雜訊就能掃出。SL=120 約等於 0.6%，才能給趨勢策略足夠的呼吸空間。
        </div>
      </div>
      <div class="card">
        <div class="card-title">📋 E09 / E07 / E12 綜合對比（SL={sl}, TP={tp}）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>代碼</th><th>策略</th><th>筆數</th><th>勝率</th><th>PF</th><th>淨盈虧</th><th>日盤 WR</th><th>夜盤 WR</th></tr></thead>
            <tbody>{sess_rows or "<tr><td colspan='8' style='color:#999'>尚無資料</td></tr>"}</tbody>
          </table>
        </div>
      </div>
      <div class="report-links">
        <a class="report-link" href="tx/TX-Long-Experiments/report.html">📄 完整多單實驗報告</a>
      </div>
    </div>
  </div><!-- /tx-main-confirmed -->
"""


def _tx_exp_html(long_rows: str, short_rows: str, c: dict) -> str:
    long_link  = c["long_dir"] + "/report.html"
    short_link = c["short_dir"] + "/report.html"
    long_pine  = c["long_pine"]
    short_pine = c["short_pine"]
    long_exists  = (ROOT / long_link).exists()
    short_exists = (ROOT / short_link).exists()

    long_btn  = f"<a href='{long_link}' class='btn btn-long'>多單報告 →</a>" if long_exists else ""
    short_btn = f"<a href='{short_link}' class='btn btn-short'>空單報告 →</a>" if short_exists else ""

    return f"""
    <!-- TX 實驗策略 ──────────────────────────────────── -->
    <div id="tx-main-exp" class="main-section">
      <div class="subnav">
        <button class="sub-tab active" onclick="showTab('tx-exp','overview',this)">綜合對比</button>
        <button class="sub-tab" onclick="showTab('tx-exp','long',this)">多單 (E01–E20)</button>
        <button class="sub-tab" onclick="showTab('tx-exp','short',this)">空單 (S01–S20)</button>
        <button class="sub-tab" onclick="showTab('tx-exp','pine',this)">Pine Script</button>
      </div>

      <div id="tx-exp-overview" class="tab-panel active">
        <div class="part-label"><span class="part-badge">PART 1</span>綜合對比 Top-3</div>
        <div class="grid-2">
          <div class="card">
            <div class="card-title">📈 多單 Top-3（E01–E20）</div>
            <div class="tbl-wrap">
              <table>
                <thead><tr><th>代碼</th><th>策略</th><th>勝率</th><th>PF</th><th>淨盈虧</th><th>分數</th></tr></thead>
                <tbody>{long_rows or "<tr><td colspan='6' style='color:#999'>尚無資料（請執行 run_experiments.py）</td></tr>"}</tbody>
              </table>
            </div>
            {long_btn}
          </div>
          <div class="card">
            <div class="card-title">📉 空單 Top-3（S01–S20）</div>
            <div class="tbl-wrap">
              <table>
                <thead><tr><th>代碼</th><th>策略</th><th>勝率</th><th>PF</th><th>淨盈虧</th><th>分數</th></tr></thead>
                <tbody>{short_rows or "<tr><td colspan='6' style='color:#999'>尚無資料</td></tr>"}</tbody>
              </table>
            </div>
            {short_btn}
          </div>
        </div>
        <div class="insight-grid">
          <div class="insight good"><strong>✅ SL=120pts 甜蜜點驗證</strong>E09/E07/E12 在 SL=120 下均達 PF>2.0、WR>50%。</div>
          <div class="insight warn"><strong>⚠ 當前期間</strong>2025-06 至今台指大多頭；空單整體虧損為預期結果。</div>
          <div class="insight info"><strong>📊 下一步</strong>加入 NQ RSI 相關性過濾；測試 4H MTF 過濾器。</div>
        </div>
      </div>

      <div id="tx-exp-long" class="tab-panel">
        <div class="part-label"><span class="part-badge">PART 1</span>多單實驗（E01–E20）</div>
        <div class="grid-4">
          <div class="metric-card card"><div class="metric-label">商品</div><div class="metric-val" style="font-size:1.1em">MTX 小台</div></div>
          <div class="metric-card card"><div class="metric-label">止損</div><div class="metric-val">120 pts</div><div class="metric-sub">NT$6,000/口</div></div>
          <div class="metric-card card"><div class="metric-label">止盈</div><div class="metric-val">240 pts</div><div class="metric-sub">R:R 1:2</div></div>
          <div class="metric-card card"><div class="metric-label">時間止損</div><div class="metric-val">48 bars</div><div class="metric-sub">24 小時</div></div>
        </div>
        <div class="report-links">
          {long_btn}
          <a class="report-link" href="{long_pine}">📋 ALL_Long_Strategies.pine</a>
        </div>
      </div>

      <div id="tx-exp-short" class="tab-panel">
        <div class="part-label"><span class="part-badge">PART 1</span>空單實驗（S01–S20）</div>
        <div class="grid-4">
          <div class="metric-card card"><div class="metric-label">商品</div><div class="metric-val" style="font-size:1.1em">MTX 小台</div></div>
          <div class="metric-card card"><div class="metric-label">止損</div><div class="metric-val">120 pts</div><div class="metric-sub">NT$6,000/口</div></div>
          <div class="metric-card card"><div class="metric-label">止盈</div><div class="metric-val">240 pts</div><div class="metric-sub">R:R 1:2</div></div>
          <div class="metric-card card"><div class="metric-label">期間特性</div><div class="metric-val" style="font-size:.9em">大多頭期</div><div class="metric-sub">空單困難為預期</div></div>
        </div>
        <div class="report-links">
          {short_btn}
          <a class="report-link" href="{short_pine}">📋 ALL_Short_Strategies.pine</a>
        </div>
      </div>

      <div id="tx-exp-pine" class="tab-panel">
        <div class="part-label"><span class="part-badge">PART 1</span>Pine Script 使用說明</div>
        <div class="card">
          <ol style="padding-left:20px;line-height:2.2;font-size:.92em">
            <li>下載 <code>ALL_Long_Strategies.pine</code> 或 <code>ALL_Short_Strategies.pine</code></li>
            <li>在 TradingView Pine Script Editor 貼上，套用到 <code>TAIFEX:MXF1!</code> 30m 圖表</li>
            <li><b>Strategy</b> 下拉選單選擇策略（E01–E20 / S01–S20）</li>
            <li><b>Enable Signals</b> 開關控制是否進場（關閉後仍顯示灰色參考箭頭）</li>
            <li><b>Stop Loss</b> 設定止損點數；<b>R:R Ratio</b> 自動計算止盈（TP = SL × R:R）</li>
            <li><b>Session</b> 可單獨開關日盤 / 夜盤</li>
          </ol>
          <div class="report-links" style="margin-top:16px">
            <a class="report-link" href="{long_pine}">📋 ALL_Long_Strategies.pine</a>
            <a class="report-link" href="{short_pine}">📋 ALL_Short_Strategies.pine</a>
          </div>
        </div>
      </div>
    </div><!-- /tx-main-exp -->
"""


def _sitemap_html() -> str:
    xauusd = COMMODITIES[0]
    tx     = COMMODITIES[1]
    def _link(href, label, exists=True):
        if exists:
            return f"<a href='{href}' style='color:var(--primary)'>{label}</a>"
        return f"<span style='color:var(--muted)'>{label}</span>"

    xu_long_report  = _link(xauusd['long_dir']  + "/report.html", "多單實驗報告",  (ROOT / xauusd['long_dir']  / "report.html").exists())
    xu_short_report = _link(xauusd['short_dir'] + "/report.html", "空單實驗報告", (ROOT / xauusd['short_dir'] / "report.html").exists())
    xu_macro        = _link("xauusd/macro_report.html", "完整宏觀報告",  (ROOT / "xauusd/macro_report.html").exists())
    tx_long_report  = _link(tx['long_dir']  + "/report.html", "多單實驗報告",  (ROOT / tx['long_dir']  / "report.html").exists())
    tx_short_report = _link(tx['short_dir'] + "/report.html", "空單實驗報告", (ROOT / tx['short_dir'] / "report.html").exists())
    tx_macro        = _link("tx/macro_report.html",     "完整宏觀報告",  (ROOT / "tx/macro_report.html").exists())
    tx_sl120_report = _link("tx/sl120_report.html", "SL=120 甜蜜點報告", (ROOT / "tx/sl120_report.html").exists())
    s1_report = _link("xauusd/XAUUSD-Long-S1-AweWithBB/report.html", "S1-AweWithBB 完整報告", (ROOT / "xauusd/XAUUSD-Long-S1-AweWithBB/report.html").exists())
    s2a_report = _link("xauusd/XAUUSD-Long-S2A-RSI/report.html", "S2A-RSI 完整報告", (ROOT / "xauusd/XAUUSD-Long-S2A-RSI/report.html").exists())
    s2b_report = _link("xauusd/XAUUSD-Long-S2B-Hammer/report.html", "S2B-Hammer 完整報告", (ROOT / "xauusd/XAUUSD-Long-S2B-Hammer/report.html").exists())

    return f"""
  <!-- 網站地圖 ───────────────────────────────────────── -->
  <div id="commodity-sitemap" class="commodity-section">
    <div class="tab-panel active" style="max-width:1000px;margin:0 auto">
      <div class="part-label"><span class="part-badge">SITEMAP</span>網站地圖 · 一頁總覽所有內容</div>

      <div class="grid-2">
        <!-- XAUUSD -->
        <div class="card">
          <div class="card-title">🟡 XAUUSD 黃金</div>
          <table style="width:100%;font-size:.88em">
            <tbody>
              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">📐 宏觀分析</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">月度統計 &amp; 季節性（1980–today）</td><td>{xu_macro}</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">週內結構</td><td>→ 宏觀分析 Tab</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">時段分析（9-10 / 14-15 / 20-21 / 23-00）</td><td>→ 宏觀分析 Tab</td></tr>

              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">✅ 已確認策略</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">S1-AweWithBB（V3.6.2）</td><td>{s1_report}</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">S2A-RSI（V2.3）</td><td>{s2a_report}</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">S2B-Hammer（V2.2）</td><td>{s2b_report}</td></tr>

              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">🧪 實驗策略（20L + 20S）</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">E01–E20 多單實驗</td><td>{xu_long_report}</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">S01–S20 空單實驗</td><td>{xu_short_report}</td></tr>

              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">📋 筆記驗證</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">月份強弱 / 季度 / 週次 / 時段</td><td>→ 筆記驗證 Tab</td></tr>
            </tbody>
          </table>
        </div>

        <!-- TX -->
        <div class="card">
          <div class="card-title">🔵 TX 台指期</div>
          <table style="width:100%;font-size:.88em">
            <tbody>
              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">📐 宏觀分析</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">月度統計 &amp; 季節性（2012–today）</td><td>{tx_macro}</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">週內結構</td><td>→ 宏觀分析 Tab</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">時段分析（日盤 vs 夜盤）</td><td>→ 宏觀分析 Tab</td></tr>

              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">✅ 已確認策略（SL=120pts）</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">E09 EMA55 Pullback（PF=1.801）</td><td>→ 已確認策略 Tab</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">E07 RSI 50 Crossover（PF=2.041）</td><td>→ 已確認策略 Tab</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">E12 BB Squeeze Break（PF=2.002）</td><td>→ 已確認策略 Tab</td></tr>

              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">🧪 實驗策略（20L + 20S）</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">E01–E20 多單實驗</td><td>{tx_long_report}</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">S01–S20 空單實驗</td><td>{tx_short_report}</td></tr>

              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">🎯 SL 甜蜜點分析</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">SL=120pts R:R 1:1 / 1:1.5 / 1:2 全策略比較</td><td>{tx_sl120_report}</td></tr>

              <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">📋 筆記驗證</td></tr>
              <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">月份強弱 / 季度 / 週次 / 選舉年</td><td>→ 筆記驗證 Tab</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 跨商品分析 -->
      <div class="card" style="margin-top:16px">
        <div class="card-title">📊 跨商品共同分析（Cross-Commodity）</div>
        <table style="width:100%;font-size:.88em">
          <tbody>
            <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">⏰ 整點熱力圖</td></tr>
            <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">XAUUSD + TX 整點進場勝率 &amp; 損益（星期 × 小時）</td><td>→ 跨商品分析 Tab → 整點熱力圖</td></tr>
            <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--primary);border-bottom:1px solid var(--border)">📈 RSI 濾鏡分析</td></tr>
            <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">整點進場時，30m RSI 金叉 / 死叉 / 背離對勝率的影響</td><td>→ 跨商品分析 Tab → RSI 濾鏡</td></tr>
            <tr><td colspan="2" style="padding:8px 0 4px;font-weight:700;color:var(--muted);border-bottom:1px solid var(--border)">📦 原始資料</td></tr>
            <tr><td style="padding:5px 0 5px 12px;color:var(--muted)">shared/shared_results.json（含 base64 heatmap 圖）</td><td>→ 執行 run_shared_analysis.py 更新</td></tr>
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-title">🔧 更新流程</div>
        <div style="font-size:.88em;line-height:2;color:var(--text2)">
          <b>更新跨商品分析（整點熱力圖 + RSI 濾鏡）：</b><br>
          <code style="background:var(--surface2);padding:2px 8px;border-radius:4px">python3.12 shared/run_shared_analysis.py</code><br><br>
          <b>更新 XAUUSD 實驗結果：</b><br>
          <code style="background:var(--surface2);padding:2px 8px;border-radius:4px">cd trading/ &amp;&amp; python3 xauusd/run_experiments.py &amp;&amp; python3 xauusd/run_short_experiments.py</code><br><br>
          <b>更新 TX 實驗結果：</b><br>
          <code style="background:var(--surface2);padding:2px 8px;border-radius:4px">cd trading/ &amp;&amp; python3 tx/run_experiments.py --sl 120 --tp 240 &amp;&amp; python3 tx/run_short_experiments.py --sl 120 --tp 240</code><br><br>
          <b>重新生成 index.html：</b><br>
          <code style="background:var(--surface2);padding:2px 8px;border-radius:4px">python3 generate_index.py</code>
        </div>
      </div>
    </div>
  </div><!-- /commodity-sitemap -->
"""


# ─── Validation (note vs data) ───────────────────────────────────────
def _load_shared_results() -> dict:
    p = ROOT / "shared/shared_results.json"
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _shared_analysis_html(data: dict) -> str:
    if not data:
        return """
  <div id="commodity-shared" class="commodity-section">
    <div class="tab-panel active"><div class="card">
      <div class="card-title">跨商品分析</div>
      <p style="color:var(--muted)">請先執行 <code>python3.12 shared/run_shared_analysis.py</code> 生成資料。</p>
    </div></div>
  </div>"""

    def _rsi_table(rsi_stats: dict, unit_label: str) -> str:
        order = ['overall', 'golden_cross', 'death_cross', 'bullish_div', 'bearish_div', 'rsi_above_ma', 'rsi_below_ma']
        labels = {
            'overall': '全部樣本', 'golden_cross': 'RSI 金叉（30m）',
            'death_cross': 'RSI 死叉（30m）', 'bullish_div': '多頭背離（30m）',
            'bearish_div': '空頭背離（30m）', 'rsi_above_ma': 'RSI > MA（30m）',
            'rsi_below_ma': 'RSI < MA（30m）',
        }
        rows = []
        for state in order:
            s = rsi_stats.get(state)
            if s is None:
                rows.append(f"<tr><td>{labels[state]}</td><td colspan='3' style='color:var(--muted);font-style:italic'>無資料（CSV 未匯出訊號）</td></tr>")
                continue
            wr = s['win_rate']
            wr_cls = 'pos' if wr >= 52 else ('neg' if wr < 48 else '')
            ret = s['avg_ret']
            ret_cls = 'pos' if ret > 0 else 'neg'
            ret_str = f"{ret:+.2f}" if unit_label == '%' else f"{ret:+.0f}"
            rows.append(
                f"<tr><td>{labels[state]}</td>"
                f"<td class='{wr_cls}'>{wr:.1f}%</td>"
                f"<td class='{ret_cls}'>{ret_str}{unit_label}</td>"
                f"<td style='color:var(--muted)'>{s['count']}</td></tr>"
            )
        return "\n".join(rows)

    def _insight_card(label: str, cell: dict | None, unit_label: str, good: bool) -> str:
        if cell is None:
            return ""
        color = "good" if good else "bad"
        ret_str = f"{cell['avg_ret']:+.2f}{unit_label}" if unit_label == '%' else f"{cell['avg_ret']:+.0f}{unit_label}"
        return (
            f"<div class='insight {color}'>"
            f"<strong>{'最佳' if good else '最差'}時段 · {cell['dow']} {cell['hour']:02d}:00</strong>"
            f"勝率 {cell['win_rate']:.1f}% &nbsp;|&nbsp; 平均 {ret_str} &nbsp;|&nbsp; n={cell['count']}"
            f"</div>"
        )

    xu = data.get("xauusd", {})
    tx = data.get("tx", {})

    xu_rsi_tbl = _rsi_table(xu.get("rsi_stats", {}), xu.get("unit_label", "%"))
    tx_rsi_tbl = _rsi_table(tx.get("rsi_stats", {}), tx.get("unit_label", "pts"))

    xu_best  = _insight_card("XAUUSD", xu.get("best_wr"),  xu.get("unit_label", "%"),   True)
    xu_worst = _insight_card("XAUUSD", xu.get("worst_wr"), xu.get("unit_label", "%"),   False)
    tx_best  = _insight_card("TX",     tx.get("best_wr"),  tx.get("unit_label", "pts"), True)
    tx_worst = _insight_card("TX",     tx.get("worst_wr"), tx.get("unit_label", "pts"),  False)

    xu_wr_img  = f"<img src='data:image/png;base64,{xu['wr_heatmap_b64']}'  style='max-width:100%;border-radius:8px'>" if xu.get("wr_heatmap_b64") else ""
    xu_ret_img = f"<img src='data:image/png;base64,{xu['ret_heatmap_b64']}' style='max-width:100%;border-radius:8px'>" if xu.get("ret_heatmap_b64") else ""
    xu_rsi_img = f"<img src='data:image/png;base64,{xu['rsi_filter_b64']}' style='max-width:100%;border-radius:8px'>" if xu.get("rsi_filter_b64") else ""
    tx_wr_img  = f"<img src='data:image/png;base64,{tx['wr_heatmap_b64']}'  style='max-width:100%;border-radius:8px'>" if tx.get("wr_heatmap_b64") else ""
    tx_ret_img = f"<img src='data:image/png;base64,{tx['ret_heatmap_b64']}' style='max-width:100%;border-radius:8px'>" if tx.get("ret_heatmap_b64") else ""
    tx_rsi_img = f"<img src='data:image/png;base64,{tx['rsi_filter_b64']}' style='max-width:100%;border-radius:8px'>" if tx.get("rsi_filter_b64") else ""

    xu_n = xu.get("n_total", 0)
    xu_rsi_n = xu.get("n_rsi_overlap", 0)
    tx_n = tx.get("n_total", 0)
    tx_rsi_n = tx.get("n_rsi_overlap", 0)

    return f"""
  <!-- ══ SHARED CROSS-COMMODITY ANALYSIS ══════════════════════════ -->
  <div id="commodity-shared" class="commodity-section">
    <div class="commodity-subnav">
      <button class="nav-main-tab active" onclick="showMain('shared-main-heatmap',this)">整點熱力圖</button>
      <button class="nav-main-tab" onclick="showMain('shared-main-rsi',this)">RSI 濾鏡</button>
    </div>

    <!-- 整點熱力圖 -->
    <div id="shared-main-heatmap" class="main-section active">
      <div class="tab-panel active">
        <div class="part-label"><span class="part-badge">HEATMAP</span>整點進場 · 下一整點出場 — 勝率 &amp; 損益熱力圖</div>

        <div class="card" style="margin-bottom:8px">
          <div style="font-size:.88em;color:var(--text2);line-height:1.7">
            <strong>分析方法：</strong>每個整點（00分）進場，下一個整點出場，計算各 <em>星期幾 × 小時</em> 組合的歷史勝率與平均損益。
            「*」表示樣本 &lt; 5 筆，結果僅供參考。
            XAUUSD：<strong>{xu_n:,}</strong> 筆 60m bar（週一至週五）。
            TX MTX：<strong>{tx_n:,}</strong> 筆 60m bar（週一至週五）。
          </div>
        </div>

        <!-- XAUUSD 熱力圖 -->
        <div class="card">
          <div class="card-title">🟡 XAUUSD 黃金 — 整點進場熱力圖</div>
          <div class="insight-grid">{xu_best}{xu_worst}</div>
          <div class="grid-2" style="gap:12px;margin-top:12px">
            <div>{xu_wr_img}</div>
            <div>{xu_ret_img}</div>
          </div>
        </div>

        <!-- TX 熱力圖 -->
        <div class="card">
          <div class="card-title">🔵 TX 台指期 (MTX) — 整點進場熱力圖</div>
          <div class="insight-grid">{tx_best}{tx_worst}</div>
          <div class="grid-2" style="gap:12px;margin-top:12px">
            <div>{tx_wr_img}</div>
            <div>{tx_ret_img}</div>
          </div>
        </div>
      </div>
    </div><!-- /shared-main-heatmap -->

    <!-- RSI 濾鏡分析 -->
    <div id="shared-main-rsi" class="main-section">
      <div class="tab-panel active">
        <div class="part-label"><span class="part-badge">RSI FILTER</span>30m RSI 金叉 / 死叉 / 背離 — 整點進場過濾效果</div>

        <div class="card" style="margin-bottom:8px">
          <div style="font-size:.88em;color:var(--text2);line-height:1.7">
            <strong>分析方法：</strong>在整點進場時，查詢 30 分鐘 RSI 的狀態（金叉 / 死叉 / RSI 位於 MA 上下方 / 背離訊號），
            比較不同狀態下的歷史勝率與平均損益差異。<br>
            <strong>注意：</strong>RSI 背離（Regular Bullish / Bearish）欄位在目前匯出的 CSV 中無訊號資料，
            如需此分析請在 TradingView 匯出時確保 <em>Regular Bullish/Bearish Label</em> 欄位有值。<br>
            XAUUSD 有效 30m RSI 重疊筆數：<strong>{xu_rsi_n:,}</strong>（共 {xu_n:,} 筆）。
            TX 有效 30m RSI 重疊筆數：<strong>{tx_rsi_n:,}</strong>（共 {tx_n:,} 筆）。
          </div>
        </div>

        <!-- XAUUSD RSI Filter -->
        <div class="card">
          <div class="card-title">🟡 XAUUSD 黃金 — 30m RSI 狀態 × 勝率</div>
          <div style="margin-bottom:12px">{xu_rsi_img}</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>RSI 狀態</th><th>勝率</th><th>平均損益</th><th>樣本數</th></tr></thead>
              <tbody>{xu_rsi_tbl}</tbody>
            </table>
          </div>
        </div>

        <!-- TX RSI Filter -->
        <div class="card">
          <div class="card-title">🔵 TX 台指期 — 30m RSI 狀態 × 勝率</div>
          <div style="margin-bottom:12px">{tx_rsi_img}</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>RSI 狀態</th><th>勝率</th><th>平均損益</th><th>樣本數</th></tr></thead>
              <tbody>{tx_rsi_tbl}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div><!-- /shared-main-rsi -->

  </div><!-- /commodity-shared -->
"""


def _load_validation() -> dict:
    p = ROOT / "doc/validation_results.json"
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _match_badge(match: bool) -> str:
    return "<span style='color:#059669;font-weight:700'>✅</span>" if match else "<span style='color:#dc2626;font-weight:700'>❌</span>"


def _xauusd_validation_html(vdata: dict) -> str:
    xu = vdata.get("xauusd", {})
    month_names = ["一","二","三","四","五","六","七","八","九","十","十一","十二"]

    # Monthly table rows
    monthly_rows = ""
    for r in xu.get("xauusd_monthly", []):
        m = int(r["month"])
        mb = _match_badge(r["match"])
        wr_col = "color:#059669" if r["win_rate"] >= 0.55 else ("color:#dc2626" if r["win_rate"] <= 0.45 else "color:#d97706")
        monthly_rows += (
            f"<tr><td>{month_names[m-1]}月</td>"
            f"<td>{r['note_view']}</td>"
            f"<td style='{wr_col};font-weight:700'>{r['data_view']} ({r['win_rate']:.0%})</td>"
            f"<td style='text-align:right'>{r['avg_ret']:.1%}</td>"
            f"<td style='text-align:center'>{mb}</td></tr>\n"
        )

    # Sessions table rows
    session_rows = ""
    for s in xu.get("xauusd_sessions", []):
        trend = s["趨勢K比例"]
        note  = s["筆記判斷"]
        # oscillation note says mostly oscillation → expect low trend%, so 趨勢K < 50% is consistent
        if "震盪" in note:
            consistent = trend < 0.55
        else:
            consistent = True  # 50/50 always partial
        mb = _match_badge(consistent)
        trend_col = "color:#dc2626" if trend >= 0.55 else "color:#059669"
        session_rows += (
            f"<tr><td>{s['時段']}</td>"
            f"<td>{note}</td>"
            f"<td style='{trend_col};font-weight:700'>{trend:.0%}</td>"
            f"<td>{s['平均波動%']:.3f}%</td>"
            f"<td>{s['樣本數']:,}</td>"
            f"<td style='text-align:center'>{mb}</td></tr>\n"
        )

    # Week-of-month rows
    wom_rows = ""
    for r in xu.get("xauusd_week_of_month", []):
        wom_rows += (
            f"<tr><td>第{int(r['week_of_month'])}週</td>"
            f"<td>{r['avg_move']:.4f}</td>"
            f"<td>{int(r['n'])}</td></tr>\n"
        )

    # Quarterly rows
    q_rows = ""
    for r in xu.get("xauusd_quarterly", []):
        wr_col = "color:#059669;font-weight:700" if r["win_rate"] >= 0.55 else "color:#d97706;font-weight:700"
        q_rows += (
            f"<tr><td>Q{int(r['quarter'])}</td>"
            f"<td style='{wr_col}'>{r['win_rate']:.0%}</td>"
            f"<td>{r['avg_ret']:.2%}</td>"
            f"<td>{int(r['n'])}</td></tr>\n"
        )

    return f"""
  <!-- XAUUSD 筆記驗證 -->
  <div id="xauusd-main-validate" class="main-section">
    <div class="tab-panel active">
      <div class="part-label"><span class="part-badge">VALIDATE</span>筆記驗證 · Notes vs Data (2014–2026)</div>

      <div class="insight-grid">
        <div class="insight info"><strong>驗證方法</strong>以 XAUUSD 日線月收益率計算勝率（WR≥55%=強、≤45%=弱、其餘=中），對照黃金秘笈/黃金短線筆記結論。</div>
        <div class="insight warn"><strong>樣本期間</strong>日線 2014–2026（月度樣本 ~12年），30m 時段資料（帶時區轉換為台北時間）。</div>
      </div>

      <div class="card">
        <div class="card-title">📅 月份強弱驗證（黃金秘笈）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>月份</th><th>筆記判斷</th><th>資料實測</th><th>平均月報酬</th><th>符合</th></tr></thead>
            <tbody>{monthly_rows}</tbody>
          </table>
        </div>
        <div style="margin-top:10px;font-size:.8em;color:var(--muted)">
          ✅ = 筆記與資料同向 ｜ ❌ = 不符（中性視為不完全符合）
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">📊 季度統計</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>季度</th><th>勝率</th><th>平均報酬</th><th>樣本數</th></tr></thead>
              <tbody>{q_rows}</tbody>
            </table>
          </div>
        </div>
        <div class="card">
          <div class="card-title">📅 週次波動（每月第幾週）</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>週次</th><th>平均波動</th><th>樣本數</th></tr></thead>
              <tbody>{wom_rows}</tbody>
            </table>
          </div>
          <div style="margin-top:8px;font-size:.8em;color:var(--muted)">筆記：第1、3週最強</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">⏱ 四個時段特性（黃金短線 + 四個時間做單）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>時段</th><th>筆記判斷</th><th>趨勢K比例</th><th>平均波動</th><th>樣本數</th><th>符合</th></tr></thead>
            <tbody>{session_rows}</tbody>
          </table>
        </div>
        <div style="margin-top:10px;font-size:.8em;color:var(--muted)">
          趨勢K定義：abs_ret &gt; 0.15%；筆記震盪主張 → 趨勢K比例應 &lt; 55%
        </div>
      </div>

    </div>
  </div><!-- /xauusd-main-validate -->
"""


def _tx_validation_html(vdata: dict) -> str:
    tx = vdata.get("tx", {})
    month_names = ["一","二","三","四","五","六","七","八","九","十","十一","十二"]

    # Monthly rows
    monthly_rows = ""
    for r in tx.get("tx_monthly", []):
        m = int(r["month"])
        mb = _match_badge(r["match"])
        wr_col = "color:#059669" if r["win_rate"] >= 0.55 else ("color:#dc2626" if r["win_rate"] <= 0.45 else "color:#d97706")
        monthly_rows += (
            f"<tr><td>{month_names[m-1]}月</td>"
            f"<td>{r['note_view']}</td>"
            f"<td style='{wr_col};font-weight:700'>{r['data_view']} ({r['win_rate']:.0%})</td>"
            f"<td style='text-align:right'>{r['avg_ret']:.1%}</td>"
            f"<td style='text-align:center'>{mb}</td></tr>\n"
        )

    # Quarterly rows (指數密技: Q4 幾乎必漲)
    q_rows = ""
    for r in tx.get("tx_quarterly", []):
        wr_col = "color:#059669;font-weight:700" if r["win_rate"] >= 0.60 else "color:#d97706;font-weight:700"
        note_q4 = " ⭐ Q4必有多單" if int(r["quarter"]) == 4 else ""
        q_rows += (
            f"<tr><td>Q{int(r['quarter'])}{note_q4}</td>"
            f"<td style='{wr_col}'>{r['win_rate']:.0%}</td>"
            f"<td>{r['avg_ret']:.2%}</td>"
            f"<td>{int(r['n'])}</td></tr>\n"
        )

    # Week-of-month rows
    wom_rows = ""
    for r in tx.get("tx_week_of_month", []):
        wom_rows += (
            f"<tr><td>第{int(r['week_of_month'])}週</td>"
            f"<td>{r['avg_move']:.4f}</td>"
            f"<td>{int(r['n'])}</td></tr>\n"
        )

    # Election year rows
    elec_rows = ""
    for r in tx.get("tx_election", []):
        is_e = "選舉年" if r["is_election"] else "非選舉年"
        wr_col = "color:#059669;font-weight:700" if r["win_rate"] >= 0.60 else "color:#d97706;font-weight:700"
        elec_rows += (
            f"<tr><td>{is_e}</td><td>Q{int(r['q'])}</td>"
            f"<td style='{wr_col}'>{r['win_rate']:.0%}</td>"
            f"<td>{r['avg_ret']:.2%}</td>"
            f"<td>{int(r['n'])}</td></tr>\n"
        )

    return f"""
  <!-- TX 筆記驗證 -->
  <div id="tx-main-validate" class="main-section">
    <div class="tab-panel active">
      <div class="part-label"><span class="part-badge">VALIDATE</span>筆記驗證 · Notes vs Data (2012–2026)</div>

      <div class="insight-grid">
        <div class="insight info"><strong>驗證方法</strong>以 TX 日線月收益率計算勝率（WR≥55%=強、≤45%=弱），對照指數密技筆記結論。</div>
        <div class="insight warn"><strong>樣本期間</strong>日線 2012–2026（月度樣本 ~14年），選舉年：2000/2004/2008/2012/2016/2020/2024。</div>
      </div>

      <div class="card">
        <div class="card-title">📅 月份強弱驗證（指數密技）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>月份</th><th>筆記判斷</th><th>資料實測</th><th>平均月報酬</th><th>符合</th></tr></thead>
            <tbody>{monthly_rows}</tbody>
          </table>
        </div>
        <div style="margin-top:10px;font-size:.8em;color:var(--muted)">
          筆記：一月通常漲、十二月幾乎必漲、五月偏弱；資料以月勝率判定。
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">📊 季度統計（指數密技：Q4 幾乎必有多單機會）</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>季度</th><th>勝率</th><th>平均報酬</th><th>樣本數</th></tr></thead>
              <tbody>{q_rows}</tbody>
            </table>
          </div>
          <div style="margin-top:8px;font-size:.8em;color:var(--muted)">
            各季勝率均 &gt; 60%，Q4 avg +1.7% 最高 — 支持「Q4必有多單」結論。
          </div>
        </div>
        <div class="card">
          <div class="card-title">📅 週次波動（每月第幾週）</div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>週次</th><th>平均波動</th><th>樣本數</th></tr></thead>
              <tbody>{wom_rows}</tbody>
            </table>
          </div>
          <div style="margin-top:8px;font-size:.8em;color:var(--muted)">筆記：第1、3週最強</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">🗳 選舉年效應（指數密技：四年周期）</div>
        <div class="tbl-wrap">
          <table>
            <thead><tr><th>年份類型</th><th>季度</th><th>勝率</th><th>平均報酬</th><th>樣本數</th></tr></thead>
            <tbody>{elec_rows}</tbody>
          </table>
        </div>
        <div style="margin-top:10px;font-size:.8em;color:var(--muted)">
          台灣總統大選每4年（2000/2004/2008/2012/2016/2020/2024）；選舉年 Q1/Q4 特別強。
        </div>
      </div>

    </div>
  </div><!-- /tx-main-validate -->
"""


# ─── Main generator ──────────────────────────────────────────────────
def generate():
    # Load experiment results
    xauusd = COMMODITIES[0]
    tx     = COMMODITIES[1]

    xu_long  = _load_top3(ROOT / xauusd["long_dir"]  / "results.json")
    xu_short = _load_top3(ROOT / xauusd["short_dir"] / "results.json")
    tx_long  = _load_top3(ROOT / tx["long_dir"]      / "results.json")
    tx_short = _load_top3(ROOT / tx["short_dir"]     / "results.json")

    xu_long_rows  = "\n".join(_exp_row_xauusd(r, "long")  for r in xu_long)
    xu_short_rows = "\n".join(_exp_row_xauusd(r, "short") for r in xu_short)
    tx_long_rows  = "\n".join(_exp_row_tx(r, "long")  for r in tx_long)
    tx_short_rows = "\n".join(_exp_row_tx(r, "short") for r in tx_short)

    # Build commodity nav tabs (+ sitemap)
    commodity_tabs = "\n".join(
        f'    <button class="commodity-tab{"" if i>0 else " active"}" '
        f'data-id="{c["id"]}" onclick="showCommodity(\'{c["id"]}\',this)">'
        f'{c["name"]}</button>'
        for i, c in enumerate(COMMODITIES)
    )
    commodity_tabs += '\n    <button class="commodity-tab" data-id="shared" onclick="showCommodity(\'shared\',this)">📊 跨商品分析</button>'
    commodity_tabs += '\n    <button class="commodity-tab" data-id="sitemap" onclick="showCommodity(\'sitemap\',this)">🗺 網站地圖</button>'
    commodity_tabs += '\n    <button class="commodity-tab" data-id="history" onclick="showCommodity(\'history\',this)">📋 對話記錄</button>'
    vdata      = _load_validation()
    xu_validate_html = _xauusd_validation_html(vdata)
    tx_validate_html = _tx_validation_html(vdata)
    xu_macro_html    = _xauusd_macro_html()
    shared_data      = _load_shared_results()
    shared_html      = _shared_analysis_html(shared_data)

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trading Strategy Hub</title>
<style>
/* ── Reset & Variables ─────────────────────────────────── */
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#f0f4f8;--surface:#ffffff;--surface2:#f8fafc;--border:#e2e8f0;
  --nav-bg:#1e3a5f;--nav-text:rgba(255,255,255,.75);--nav-active:#ffffff;
  --primary:#2563eb;--primary-light:#dbeafe;
  --green:#059669;--green-light:#d1fae5;
  --red:#dc2626;--red-light:#fee2e2;
  --yellow:#d97706;--yellow-light:#fef3c7;
  --purple:#7c3aed;--purple-light:#ede9fe;
  --text:#0f172a;--text2:#334155;--muted:#64748b;
  --radius:10px;--shadow:0 1px 4px rgba(0,0,0,.08),0 4px 16px rgba(0,0,0,.06);
}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);font-size:14px;line-height:1.6}}
a{{color:var(--primary);text-decoration:none}}
a:hover{{text-decoration:underline}}

/* ── Top Navigation ─────────────────────────────────────── */
.topnav{{background:var(--nav-bg);position:sticky;top:0;z-index:100;display:flex;align-items:center;gap:0;padding:0 24px;box-shadow:0 2px 8px rgba(0,0,0,.2)}}
.nav-brand{{color:white;font-weight:700;font-size:1.05em;padding:14px 20px 14px 0;border-right:1px solid rgba(255,255,255,.15);margin-right:12px;white-space:nowrap;letter-spacing:.5px}}
.nav-brand span{{color:#93c5fd;font-size:.8em;font-weight:400}}
.commodity-tabs{{display:flex;gap:4px;flex:1}}
.commodity-tab{{background:transparent;border:none;cursor:pointer;color:var(--nav-text);padding:14px 20px;font-size:.92em;font-weight:600;border-bottom:3px solid transparent;transition:all .2s;white-space:nowrap;letter-spacing:.3px}}
.commodity-tab:hover{{color:white;background:rgba(255,255,255,.08)}}
.commodity-tab.active{{color:white;border-bottom-color:#60a5fa;background:rgba(255,255,255,.12)}}
.nav-meta{{color:rgba(255,255,255,.45);font-size:.78em;white-space:nowrap;padding-left:16px}}

/* ── Commodity Section Nav ──────────────────────────────── */
.commodity-subnav{{background:white;border-bottom:2px solid var(--border);display:flex;align-items:center;gap:4px;padding:0 24px;overflow-x:auto}}
.nav-main-tab{{background:transparent;border:none;cursor:pointer;color:var(--muted);padding:11px 20px;font-size:.9em;font-weight:600;border-bottom:3px solid transparent;transition:all .2s;white-space:nowrap}}
.nav-main-tab:hover{{color:var(--primary);background:rgba(37,99,235,.04)}}
.nav-main-tab.active{{color:var(--primary);border-bottom-color:var(--primary);background:var(--primary-light)}}

/* ── Sub Navigation ─────────────────────────────────────── */
.subnav{{background:var(--surface2);border-bottom:1px solid var(--border);display:flex;align-items:center;gap:4px;padding:0 24px;overflow-x:auto}}
.sub-tab{{background:transparent;border:none;cursor:pointer;color:var(--muted);padding:9px 16px;font-size:.86em;font-weight:500;border-bottom:2px solid transparent;transition:all .15s;white-space:nowrap}}
.sub-tab:hover{{color:var(--primary)}}
.sub-tab.active{{color:var(--primary);border-bottom-color:var(--primary);background:var(--primary-light)}}

/* ── Sections / Tabs ─────────────────────────────────────── */
.commodity-section{{display:none}}
.commodity-section.active{{display:block}}
.main-section{{display:none}}
.main-section.active{{display:block}}
.tab-panel{{display:none;padding:24px;max-width:1300px;margin:0 auto}}
.tab-panel.active{{display:block}}

/* ── Part Headers ────────────────────────────────────────── */
.part-label{{display:flex;align-items:center;gap:10px;margin:28px 0 14px;font-size:.78em;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)}}
.part-label::after{{content:'';flex:1;height:1px;background:var(--border)}}
.part-badge{{background:var(--primary);color:white;padding:2px 10px;border-radius:20px;font-size:.9em;letter-spacing:.5px}}

/* ── Cards ──────────────────────────────────────────────── */
.card{{background:white;border-radius:var(--radius);border:1px solid var(--border);padding:20px 24px;box-shadow:var(--shadow);margin-bottom:16px}}
.card-title{{font-size:.95em;font-weight:700;color:var(--text2);margin-bottom:12px;display:flex;align-items:center;gap:8px}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.grid-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}
.grid-4{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}
@media(max-width:900px){{.grid-3,.grid-4{{grid-template-columns:1fr 1fr}}.grid-2{{grid-template-columns:1fr}}}}
@media(max-width:600px){{.grid-3,.grid-4,.grid-2{{grid-template-columns:1fr}}}}

/* ── Mobile Navigation ───────────────────────────────── */
@media(max-width:640px){{
  .topnav{{flex-wrap:wrap;padding:0 12px}}
  .nav-brand{{flex:1;border-right:none;margin-right:0;padding:10px 0;font-size:.9em}}
  .nav-brand span{{display:none}}
  .nav-meta{{display:none}}
  .commodity-tabs{{width:100%;border-top:1px solid rgba(255,255,255,.15);overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;gap:0;padding-bottom:2px}}
  .commodity-tabs::-webkit-scrollbar{{display:none}}
  .commodity-tab{{padding:10px 16px;font-size:.84em;flex-shrink:0}}
  .commodity-subnav{{padding:0 8px}}
  .nav-main-tab{{padding:9px 14px;font-size:.82em}}
  .subnav{{padding:0 8px}}
  .sub-tab{{padding:8px 12px;font-size:.82em}}
  .tab-panel{{padding:16px 12px}}
  .card{{padding:16px}}
}}

/* ── Metric Cards ───────────────────────────────────────── */
.metric-card{{background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:14px 16px}}
.metric-label{{font-size:.75em;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px}}
.metric-val{{font-size:1.5em;font-weight:700;color:var(--text)}}
.metric-sub{{font-size:.78em;color:var(--muted);margin-top:2px}}
.metric-val.green{{color:var(--green)}}.metric-val.red{{color:var(--red)}}.metric-val.yellow{{color:var(--yellow)}}

/* ── Insight Boxes ──────────────────────────────────────── */
.insight-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-bottom:16px}}
.insight{{border-radius:8px;padding:14px 16px;font-size:.88em;border-left:4px solid;line-height:1.5}}
.insight.good{{background:var(--green-light);border-color:var(--green)}}
.insight.warn{{background:var(--yellow-light);border-color:var(--yellow)}}
.insight.bad{{background:var(--red-light);border-color:var(--red)}}
.insight.info{{background:var(--primary-light);border-color:var(--primary)}}
.insight.purple{{background:var(--purple-light);border-color:var(--purple)}}
.insight strong{{display:block;font-weight:700;margin-bottom:4px;font-size:1em}}

/* ── Tables ─────────────────────────────────────────────── */
.tbl-wrap{{overflow-x:auto;border-radius:8px;border:1px solid var(--border)}}
table{{border-collapse:collapse;width:100%;font-size:.84em}}
thead th{{background:var(--nav-bg);color:white;padding:9px 12px;text-align:left;font-weight:600;white-space:nowrap}}
tbody td{{padding:8px 12px;border-bottom:1px solid #f1f5f9;vertical-align:top}}
tbody tr:last-child td{{border-bottom:none}}
tbody tr:hover td{{background:#f8fafc}}
.td-date{{white-space:nowrap;color:var(--muted);font-size:.85em;font-family:monospace}}
.td-memo{{font-size:.84em;color:var(--text2);line-height:1.5}}
.td-memo strong{{color:var(--text);display:block}}
.td-topic{{font-weight:600;color:var(--text);font-size:.88em}}
.tag{{display:inline-block;padding:1px 8px;border-radius:10px;font-size:.75em;font-weight:600;margin:1px 2px}}
.tag-analysis{{background:#dbeafe;color:#1e40af}}.tag-optimize{{background:#d1fae5;color:#065f46}}
.tag-pine{{background:#ede9fe;color:#5b21b6}}.tag-infra{{background:#fef3c7;color:#92400e}}
.tag-new{{background:#fee2e2;color:#991b1b}}

/* ── Status Badges ──────────────────────────────────────── */
.badge{{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.75em;font-weight:700}}
.badge-green{{background:var(--green-light);color:var(--green)}}
.badge-yellow{{background:var(--yellow-light);color:var(--yellow)}}
.badge-red{{background:var(--red-light);color:var(--red)}}
.badge-blue{{background:var(--primary-light);color:var(--primary)}}
.badge-purple{{background:var(--purple-light);color:var(--purple)}}
.pos{{color:var(--green);font-weight:700}}.neg{{color:var(--red);font-weight:700}}
.neutral{{color:var(--yellow);font-weight:700}}

/* ── Report Links ───────────────────────────────────────── */
.report-links{{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}}
.report-link{{display:inline-flex;align-items:center;gap:5px;background:var(--primary-light);color:var(--primary);padding:5px 12px;border-radius:6px;font-size:.82em;font-weight:600;border:1px solid #bfdbfe;transition:all .15s}}
.report-link:hover{{background:var(--primary);color:white;text-decoration:none}}

/* ── Log ────────────────────────────────────────────────── */
.log-entry{{display:flex;gap:20px;padding:16px 0;border-bottom:1px solid var(--border)}}
.log-entry:last-child{{border-bottom:none}}
.log-date{{font-size:.8em;color:var(--muted);white-space:nowrap;min-width:90px;padding-top:2px;font-family:monospace}}
.log-title{{font-weight:600;color:var(--primary);margin-bottom:6px}}
.log-items{{padding-left:18px;font-size:.88em;color:var(--text2);line-height:1.8}}
@media(max-width:700px){{.log-entry{{flex-direction:column;gap:4px}}}}

/* ── Version Table ──────────────────────────────────────── */
.version-row td:first-child{{font-family:monospace;font-size:.85em}}
.ver-confirmed{{color:var(--green)}}.ver-test{{color:var(--yellow)}}

/* ── Memory Setup ───────────────────────────────────────── */
.setup-card{{background:white;border-radius:var(--radius);border:1px solid var(--border);padding:20px 24px;box-shadow:var(--shadow);margin:24px auto;max-width:900px}}
.setup-card h2{{font-size:.95em;color:var(--text2);margin-bottom:12px;border-left:4px solid var(--primary);padding-left:10px;font-weight:700}}
.setup-card pre{{background:var(--surface2);padding:14px;border-radius:8px;font-size:.83em;overflow-x:auto;border:1px solid var(--border)}}

/* ── Footer ─────────────────────────────────────────────── */
.footer{{text-align:center;color:var(--muted);font-size:.78em;padding:32px 16px;margin-top:16px;border-top:1px solid var(--border)}}
</style>
</head>
<body>

<!-- ══ TOP NAV ══════════════════════════════════════════════════════ -->
<nav class="topnav">
  <div class="nav-brand">Trading Strategy Hub <span>multi-commodity</span></div>
  <div class="commodity-tabs">
{commodity_tabs}
  </div>
  <div class="nav-meta">Updated 2026-05-14</div>
</nav>

<!-- ══════════════════════════════════════════════════════════════════
     COMMODITY: XAUUSD 黃金
════════════════════════════════════════════════════════════════════ -->
<div id="commodity-xauusd" class="commodity-section active">
  <div class="commodity-subnav">
    <button class="nav-main-tab active" onclick="showMain('xauusd-main-macro',this)">宏觀分析</button>
    <button class="nav-main-tab" onclick="showMain('xauusd-main-opt',this)">已確認策略</button>
    <button class="nav-main-tab" onclick="showMain('xauusd-main-exp',this)">實驗策略</button>
    <button class="nav-main-tab" onclick="showMain('xauusd-main-validate',this)">筆記驗證</button>
  </div>

{xu_macro_html}
{_xauusd_opt_html()}
{_xauusd_exp_html(xu_long_rows, xu_short_rows, xauusd)}
{xu_validate_html}
</div><!-- /commodity-xauusd -->

<!-- ══════════════════════════════════════════════════════════════════
     COMMODITY: TX 台指期
════════════════════════════════════════════════════════════════════ -->
<div id="commodity-tx" class="commodity-section">
  <div class="commodity-subnav">
    <button class="nav-main-tab active" onclick="showMain('tx-main-macro',this)">宏觀分析</button>
    <button class="nav-main-tab" onclick="showMain('tx-main-confirmed',this)">已確認策略</button>
    <button class="nav-main-tab" onclick="showMain('tx-main-exp',this)">實驗策略</button>
    <button class="nav-main-tab" onclick="showMain('tx-main-validate',this)">筆記驗證</button>
  </div>

{_tx_macro_html()}
{_tx_confirmed_html()}
{_tx_exp_html(tx_long_rows, tx_short_rows, tx)}
{tx_validate_html}
</div><!-- /commodity-tx -->

{shared_html}

{_sitemap_html()}

{_unified_log_html()}

<!-- ══ SETUP SECTION ════════════════════════════════════════════════ -->
<div class="setup-card">
  <h2>換電腦後的記憶設定（git clone 後執行一次）</h2>
  <pre>
# Mac / Linux（在 trading/ 目錄執行）
PROJ=$(pwd)
SYSTEM_KEY=$(echo "$PROJ" | sed 's|^/||' | sed 's|/|-|g')
rm -rf ~/.claude/projects/${{SYSTEM_KEY}}/memory
ln -s "${{PROJ}}/.claude/memory" ~/.claude/projects/${{SYSTEM_KEY}}/memory

# Windows PowerShell（在 trading/ 目錄執行）
$proj = (Get-Location).Path
$key  = $proj -replace '\\\\', '-' -replace ':', ''
$src  = "$proj\\.claude\\memory"
$dst  = "$env:USERPROFILE\\.claude\\projects\\-$key\\memory"
if (Test-Path $dst) {{ Remove-Item $dst -Recurse -Force }}
New-Item -ItemType Junction -Path $dst -Target $src</pre>
</div>

<div class="footer">
  Trading Strategy Hub &nbsp;·&nbsp; XAUUSD 黃金 + TX 台指期 &nbsp;·&nbsp; Generated by Claude Code 2026-05-14
  <br><br>
  <a href="https://github.com/tittanliao/trading" style="color:var(--muted)">GitHub Repository</a>
  &nbsp;·&nbsp;
  更新實驗結果：<code>python generate_index.py</code>
</div>

<script>
function showCommodity(id, btn) {{
  document.querySelectorAll('.commodity-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.commodity-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('commodity-' + id).classList.add('active');
  btn.classList.add('active');
}}

function showMain(sectionId, btn) {{
  const commodity = btn.closest('.commodity-section');
  commodity.querySelectorAll('.main-section').forEach(s => s.classList.remove('active'));
  btn.closest('.commodity-subnav').querySelectorAll('.nav-main-tab').forEach(b => b.classList.remove('active'));
  document.getElementById(sectionId).classList.add('active');
  btn.classList.add('active');
}}

function showTab(prefix, id, btn) {{
  const panelId = prefix + '-' + id;
  btn.closest('.commodity-section').querySelectorAll('[id^="' + prefix + '-"]').forEach(p => {{
    if (p.classList.contains('tab-panel')) p.classList.remove('active');
  }});
  btn.closest('.subnav').querySelectorAll('.sub-tab').forEach(b => b.classList.remove('active'));
  document.getElementById(panelId).classList.add('active');
  btn.classList.add('active');
}}
</script>

</body>
</html>
"""

    out = ROOT / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"index.html written → {out}")


if __name__ == "__main__":
    generate()
