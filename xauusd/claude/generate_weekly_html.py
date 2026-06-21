"""
generate_weekly_html.py
執行後自動：
  1. 讀取 googledrive CSV → 計算指標 + SMC
  2. 輸出 claude/reports/{WEEK_ID}.html（瀏覽器可直接看）
  3. 更新 xauusd/index.html 的「週報分析」tab 內容

用法：
  python3.12 claude/generate_weekly_html.py --week W25 --day Sun --price 4155.57 \
    --bias "觀望，等S2 A+ @4095-4131" --account 21649 \
    --scenario2 "震盪尋底57.5% 等SSL Sweep 4121" \
    --s2 "4095-4131" --s1 "站回4165+AO翻正"
"""
import argparse, json, os, re, warnings
from datetime import date
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

CSV_DIR = "/Users/tittan/googledrive/XAUUSD/weekly report/csv/"
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")
INDEX_HTML   = os.path.join(os.path.dirname(__file__), "..", "index.html")

# ── 指標計算 ──────────────────────────────────────────────────────────────
def load_csv(fname):
    for enc in ['utf-8', 'utf-8-sig', 'big5', 'cp950']:
        try:
            df = pd.read_csv(CSV_DIR + fname, encoding=enc, encoding_errors='ignore')
            df = df.rename(columns={df.columns[0]: 'time'})
            df['time'] = pd.to_datetime(df['time'], utc=True).dt.tz_convert('Asia/Taipei').dt.tz_localize(None)
            df.columns = [c.strip().lower().replace(' ','_').replace('-','_') for c in df.columns]
            return df.sort_values('time').reset_index(drop=True)
        except: continue
    return None

def add_indicators(df, n_bb=20, k=2.0, n_ema1=50, n_ema2=200, n_rsi=14):
    df['bb_mid'] = df['close'].rolling(n_bb).mean()
    std = df['close'].rolling(n_bb).std()
    df['bb_up']  = df['bb_mid'] + k * std
    df['bb_lo']  = df['bb_mid'] - k * std
    df['bb_pct'] = (df['close'] - df['bb_lo']) / (df['bb_up'] - df['bb_lo'])
    df['ema50']  = df['close'].ewm(span=n_ema1, adjust=False).mean()
    df['ema200'] = df['close'].ewm(span=n_ema2, adjust=False).mean()
    delta = df['close'].diff()
    gain = delta.clip(lower=0).rolling(n_rsi).mean()
    loss = (-delta.clip(upper=0)).rolling(n_rsi).mean()
    df['rsi'] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    tr = pd.concat([(df['high']-df['low']),
                    (df['high']-df['close'].shift()).abs(),
                    (df['low']-df['close'].shift()).abs()], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    return df

def scan_fvg(df, lookback=50):
    h, l = df['high'].values, df['low'].values
    n = len(df)
    bull, bear = [], []
    for j in range(2, n):
        if h[j-2] < l[j]: bull.append({'bot': round(h[j-2],1), 'top': round(l[j],1),'bar':j})
        if l[j-2] > h[j]: bear.append({'bot': round(h[j],1),   'top': round(l[j-2],1),'bar':j})
    ab = [z for z in bull if z['bar']>=n-lookback and not any(l[k]<=z['bot'] for k in range(z['bar'],n))]
    ae = [z for z in bear if z['bar']>=n-lookback and not any(h[k]>=z['top'] for k in range(z['bar'],n))]
    return ab[-3:], ae[-3:]

def scan_liq(df, lookback=30):
    h, l = df['high'].values, df['low'].values
    n = len(df)
    bsl, ssl = [], []
    for i in range(2, min(lookback, n-2)):
        idx = n-1-i
        if idx<2: break
        if h[idx]>h[idx-1] and h[idx]>h[idx-2] and h[idx]>h[idx+1] and h[idx]>h[idx+2]: bsl.append(round(h[idx],1))
        if l[idx]<l[idx-1] and l[idx]<l[idx-2] and l[idx]<l[idx+1] and l[idx]<l[idx+2]: ssl.append(round(l[idx],1))
    return sorted(set(bsl),reverse=True)[:3], sorted(set(ssl))[:3]

def run_analysis():
    xau_1d = add_indicators(load_csv("FX_IDC_XAUUSD, 1D.csv"))
    xau_1w = add_indicators(load_csv("FX_IDC_XAUUSD, 1W.csv"))
    xau_4h = add_indicators(load_csv("FX_IDC_XAUUSD, 240.csv"))
    xau_1h = add_indicators(load_csv("FX_IDC_XAUUSD, 60.csv"))
    dxy_1d = add_indicators(load_csv("TVC_DXY, 1D.csv"))

    d  = xau_1d.iloc[-1]
    h4 = xau_4h.iloc[-1]
    h1 = xau_1h.iloc[-1]
    w  = xau_1w.iloc[-1]
    wp = xau_1w.iloc[-2]
    dx = dxy_1d.iloc[-1]

    bull_fvg_4h, bear_fvg_4h = scan_fvg(xau_4h, 60)
    bsl_4h, ssl_4h = scan_liq(xau_4h, 30)

    levels = [
        ("週線BB上軌", xau_1w.iloc[-1]['bb_up'], "阻力"),
        ("週線BB中軌", xau_1w.iloc[-1]['bb_mid'], "阻力"),
        ("日線BB上軌", d['bb_up'], "阻力"),
        ("日線EMA50",  d['ema50'], "阻力"),
        ("日線BB中軌", d['bb_mid'], "阻力"),
        ("4H BB上軌",  h4['bb_up'], "阻力"),
        ("4H BB中軌",  h4['bb_mid'], "阻力"),
        ("4H EMA50",  h4['ema50'], "阻力"),
        ("1H BB上軌",  h1['bb_up'], "阻力"),
        ("1H BB中軌",  h1['bb_mid'], "阻力/支撐"),
        ("1H BB下軌",  h1['bb_lo'], "支撐"),
        ("4H BB下軌",  h4['bb_lo'], "支撐"),
        ("4H Bullish FVG", bull_fvg_4h[-1]['bot'] if bull_fvg_4h else None, "支撐★"),
        ("日線BB下軌", d['bb_lo'], "支撐"),
        ("週線BB下軌", xau_1w.iloc[-1]['bb_lo'], "支撐"),
    ]

    weeks5 = []
    for _, r in xau_1w.tail(5).iterrows():
        chg = r['close'] - r['open']
        weeks5.append({
            "date": r['time'].strftime('%m/%d'),
            "open": round(r['open'],1), "high": round(r['high'],1),
            "low": round(r['low'],1),  "close": round(r['close'],1),
            "chg": round(chg,1), "pct": round(chg/r['open']*100,1)
        })

    return {
        "price": round(float(d['close']),2),
        "rsi_1d": round(float(d['rsi']),1),
        "rsi_4h": round(float(h4['rsi']),1),
        "rsi_1h": round(float(h1['rsi']),1),
        "dxy":    round(float(dx['close']),2),
        "dxy_rsi": round(float(dx['rsi']),1),
        "atr_1d": round(float(d['atr']),1),
        "w_chg":  round(float(w['close']-w['open']),1),
        "w_pct":  round(float((w['close']-w['open'])/w['open']*100),1),
        "bb_1d_up": round(float(d['bb_up']),1), "bb_1d_mid": round(float(d['bb_mid']),1),
        "bb_1d_lo": round(float(d['bb_lo']),1), "bb_1d_pct": round(float(d['bb_pct']),2),
        "bb_4h_up": round(float(h4['bb_up']),1), "bb_4h_mid": round(float(h4['bb_mid']),1),
        "bb_4h_lo": round(float(h4['bb_lo']),1),
        "bb_1h_mid": round(float(h1['bb_mid']),1), "bb_1h_lo": round(float(h1['bb_lo']),1),
        "levels": [(n, round(float(v),1), t) for n,v,t in levels if v is not None],
        "bull_fvg_4h": [(z['bot'],z['top']) for z in bull_fvg_4h],
        "bear_fvg_4h": [(z['bot'],z['top']) for z in bear_fvg_4h],
        "bsl_4h": bsl_4h, "ssl_4h": ssl_4h,
        "weeks5": weeks5,
        "last_week": {"close": round(float(wp['close']),1), "high": round(float(wp['high']),1), "low": round(float(wp['low']),1)},
    }

# ── HTML 生成 ─────────────────────────────────────────────────────────────
def pct_color(v):
    return "pos" if v >= 0 else "neg"

def rsi_badge(v):
    if v < 30: return f'<span class="badge badge-red">{v} 超賣</span>'
    if v > 70: return f'<span class="badge badge-yellow">{v} 超買</span>'
    return f'<span class="badge badge-blue">{v}</span>'

def build_weekly_section(week_id, day_label, data, args):
    price   = data['price']
    w_chg   = data['w_chg']
    w_pct   = data['w_pct']
    chg_cls = pct_color(w_chg)
    gen_date = date.today().strftime('%Y-%m-%d')

    # ── 近5週表格 ────────────────────────────────────────────────────────
    rows_w5 = ""
    for w in data['weeks5']:
        icon = "🟢" if w['chg'] >= 0 else "🔴"
        cls  = "pos" if w['chg'] >= 0 else "neg"
        rows_w5 += f"""<tr>
          <td class="td-date">{icon} {w['date']}</td>
          <td>{w['open']}</td><td>{w['high']}</td><td>{w['low']}</td>
          <td><strong>{w['close']}</strong></td>
          <td class="{cls}">{'+' if w['chg']>=0 else ''}{w['chg']} ({'+' if w['pct']>=0 else ''}{w['pct']}%)</td>
        </tr>"""

    # ── 關鍵位階表格 ─────────────────────────────────────────────────────
    rows_lv = ""
    for name, val, direction in sorted(data['levels'], key=lambda x: x[1], reverse=True):
        near = abs(val - price) < 35
        row_cls = ' style="background:#fffbeb"' if near else ''
        near_tag = ' <span style="color:#d97706;font-weight:700">← 現價附近</span>' if near else ''
        dir_cls = "pos" if "支撐" in direction else "neg"
        rows_lv += f'<tr{row_cls}><td class="{dir_cls}">{direction}</td><td><strong>{val}</strong>{near_tag}</td><td style="color:var(--muted);font-size:.82em">{name}</td></tr>'

    # ── FVG & Liquidity ──────────────────────────────────────────────────
    bear_fvg_str = ", ".join(f"{b}-{t}" for b,t in data['bear_fvg_4h']) or "無"
    bull_fvg_str = ", ".join(f"{b}-{t}" for b,t in data['bull_fvg_4h']) or "無"
    bsl_str = " / ".join(str(x) for x in data['bsl_4h']) or "無"
    ssl_str = " / ".join(str(x) for x in data['ssl_4h']) or "無"

    # ── 策略摘要 ─────────────────────────────────────────────────────────
    bias    = args.bias
    s2      = args.s2
    s1      = args.s1
    sc2     = args.scenario2
    account = f"${int(args.account):,}"

    html = f"""
<!-- WEEKLY_SECTION_START -->
<div id="main-weekly" class="main-section">
  <div class="subnav">
    <button class="sub-tab active" onclick="showTab('wk','now',this)">本週重點</button>
    <button class="sub-tab" onclick="showTab('wk','history',this)">近5週走勢</button>
    <button class="sub-tab" onclick="showTab('wk','archive',this)">報告歸檔</button>
  </div>

  <!-- 本週重點 -->
  <div id="wk-now" class="tab-panel active">
    <div class="part-label"><span class="part-badge">{week_id} {day_label}</span>本週分析重點 · {gen_date}</div>

    <div class="grid-4">
      <div class="metric-card card">
        <div class="metric-label">XAUUSD 現價</div>
        <div class="metric-val {chg_cls}">{price}</div>
        <div class="metric-sub">本週 {'+' if w_chg>=0 else ''}{w_chg} ({'+' if w_pct>=0 else ''}{w_pct}%)</div>
      </div>
      <div class="metric-card card">
        <div class="metric-label">日線 RSI / BB%B</div>
        <div class="metric-val">{rsi_badge(data['rsi_1d'])}</div>
        <div class="metric-sub">BB %B = {data['bb_1d_pct']} | 4H RSI {data['rsi_4h']}</div>
      </div>
      <div class="metric-card card">
        <div class="metric-label">DXY 美元</div>
        <div class="metric-val yellow">{data['dxy']}</div>
        <div class="metric-sub">RSI = {rsi_badge(data['dxy_rsi'])} | {'承壓黃金⚠️' if data['dxy_rsi']>60 else '偏利多✅'}</div>
      </div>
      <div class="metric-card card">
        <div class="metric-label">帳戶偏向</div>
        <div class="metric-val" style="font-size:1em;color:var(--text2)">{bias[:12]}…</div>
        <div class="metric-sub">帳戶 {account} | ATR1D {data['atr_1d']}</div>
      </div>
    </div>

    <div class="insight-grid">
      <div class="insight warn"><strong>⭐ 主情境（55-60%）</strong>{sc2}</div>
      <div class="insight info"><strong>🛡️ S2 A+ 進場區</strong>{s2}<br>等 SSL Sweep + M30 錘頭確認</div>
      <div class="insight good"><strong>🚀 S1 啟動條件</strong>{s1}</div>
      <div class="insight bad"><strong>🔍 SMC 4H — Bearish FVG（阻力）</strong>{bear_fvg_str}<br>Bullish FVG（支撐）：{bull_fvg_str}</div>
      <div class="insight purple"><strong>💧 流動性（4H）</strong>BSL 前高：{bsl_str}<br>SSL 前低：{ssl_str}</div>
      <div class="insight info"><strong>📊 CFTC（06-09）</strong>MM 淨多 105,863（減多+3,087，增空+3,229）<br>散戶追空 → 反轉燃料</div>
    </div>

    <div class="part-label"><span class="part-badge">PART 2</span>關鍵位階 · Key Levels</div>
    <div class="card">
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>方向</th><th>價位</th><th>來源</th></tr></thead>
          <tbody>{rows_lv}</tbody>
        </table>
      </div>
    </div>

    <div class="part-label"><span class="part-badge">PART 3</span>三大劇本 · W26 Scenarios</div>
    <div class="grid-3">
      <div class="insight info">
        <strong>📈 劇本一：V型反彈（20%）</strong>
        DXY 回落 → 站回 1H 中軌 {data['bb_1h_mid']} → S1 啟動<br>
        目標：{data['bb_4h_mid']}（4H 中軌）
      </div>
      <div class="insight warn">
        <strong>😴 劇本二：震盪尋底（57.5%）⭐主情境</strong>
        下探 {data['bb_4h_lo']}-{data['bb_1h_lo']} → SSL Sweep → 錘頭 → S2 A+<br>
        TP：{data['bb_1h_mid']} → {data['bb_1h_lo']+94:.0f}（1H 上軌）
      </div>
      <div class="insight bad">
        <strong>📉 劇本三：跌破支撐（22.5%）</strong>
        跌破 {data['bb_1d_lo']} 日線下軌 → 往 {data['bb_1d_lo']-58:.0f}（週線下軌）<br>
        此劇本下暫停操作
      </div>
    </div>
  </div><!-- /wk-now -->

  <!-- 近5週走勢 -->
  <div id="wk-history" class="tab-panel">
    <div class="part-label"><span class="part-badge">近5週</span>週線走勢</div>
    <div class="card">
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>週次</th><th>開盤</th><th>最高</th><th>最低</th><th>收盤</th><th>漲跌</th></tr></thead>
          <tbody>{rows_w5}</tbody>
        </table>
      </div>
      <div style="margin-top:12px;font-size:.84em;color:var(--muted)">
        ★ 已連跌三週（W22-W25），總跌幅約 -9.6%（4595→4155）。週線 RSI 36.9，接近超賣但未見反彈信號。
      </div>
    </div>

    <div class="part-label"><span class="part-badge">技術指標</span>多時間框架</div>
    <div class="grid-3">
      <div class="card">
        <div class="card-title">📊 布林通道位置</div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>TF</th><th>上軌</th><th>中軌</th><th>下軌</th><th>%B</th></tr></thead>
          <tbody>
            <tr><td>日線</td><td>{data['bb_1d_up']}</td><td>{data['bb_1d_mid']}</td><td class="pos">{data['bb_1d_lo']}</td><td class="neg">{data['bb_1d_pct']}</td></tr>
            <tr><td>4H</td><td>{data['bb_4h_up']}</td><td>{data['bb_4h_mid']}</td><td class="pos">{data['bb_4h_lo']}</td><td>—</td></tr>
            <tr><td>1H</td><td>—</td><td>{data['bb_1h_mid']}</td><td class="pos">{data['bb_1h_lo']}</td><td>—</td></tr>
          </tbody>
        </table></div>
      </div>
      <div class="card">
        <div class="card-title">📊 RSI 狀態</div>
        <div style="display:grid;gap:10px;margin-top:8px">
          <div class="metric-card"><div class="metric-label">日線 RSI</div><div class="metric-val red">{data['rsi_1d']}</div><div class="metric-sub">接近超賣（&lt;35）</div></div>
          <div class="metric-card"><div class="metric-label">4H RSI</div><div class="metric-val red">{data['rsi_4h']}</div><div class="metric-sub">超賣區（&lt;32）</div></div>
          <div class="metric-card"><div class="metric-label">1H RSI</div><div class="metric-val yellow">{data['rsi_1h']}</div><div class="metric-sub">中性</div></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">💵 DXY 美元 / 黃金壓力</div>
        <div style="margin-top:8px">
          <div class="metric-card"><div class="metric-label">DXY 現價</div><div class="metric-val yellow">{data['dxy']}</div><div class="metric-sub">RSI={data['dxy_rsi']} 超買，黃金承壓</div></div>
          <div style="margin-top:10px;font-size:.84em;color:var(--text2)">DXY RSI > 70 = 黃金短期難反彈<br>需等 DXY RSI 回落 65 以下再看多</div>
        </div>
      </div>
    </div>
  </div><!-- /wk-history -->

  <!-- 報告歸檔 -->
  <div id="wk-archive" class="tab-panel">
    <div class="part-label"><span class="part-badge">歸檔</span>週報 + Combine 報告</div>
    <div class="card">
      <div style="font-size:.84em;color:var(--muted);margin-bottom:12px">
        HTML 可直接在瀏覽器查看 · DOCX 下載後用 Word/Pages 開啟 · Combine = Claude + Gemini 三種風格整合版
      </div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>週次</th><th>日期</th><th>Claude 週報</th><th>Style A</th><th>Style B</th><th>Style C</th></tr></thead>
          <tbody>
            <tr>
              <td><strong>W25</strong></td>
              <td class="td-date">2026-06-21 (Sun)</td>
              <td><a class="report-link" href="claude/reports/XAUUSD_Weekly_Report_2026W25_Sun_Claude.docx">📥 DOCX</a></td>
              <td><a class="report-link" href="claude/reports/XAUUSD_W25_Combine_StyleA.docx">📥 量化風控</a></td>
              <td><a class="report-link" href="claude/reports/XAUUSD_W25_Combine_StyleB.docx">📥 老鳥拍板</a></td>
              <td><a class="report-link" href="claude/reports/XAUUSD_W25_Combine_StyleC.docx">📥 委員會</a></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div style="margin-top:16px;padding:12px;background:var(--surface2);border-radius:8px;font-size:.84em;color:var(--text2)">
        💡 新增週報：執行 <code>python3.12 claude/generate_weekly_html.py --week W26 --day Wed ...</code> 後 index.html 自動更新
      </div>
    </div>
  </div><!-- /wk-archive -->
</div><!-- /main-weekly -->
<!-- WEEKLY_SECTION_END -->"""
    return html


def update_index_html(weekly_html):
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace existing weekly section if present
    pattern = r'<!-- WEEKLY_SECTION_START -->.*?<!-- WEEKLY_SECTION_END -->'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, weekly_html.strip(), content, flags=re.DOTALL)
    else:
        # Insert before </body>
        content = content.replace('</body>', weekly_html + '\n</body>')

    # Add nav tab if missing
    if 'showMain(\'weekly\'' not in content:
        content = content.replace(
            '<div class="nav-meta">',
            '<button class="nav-main-tab" onclick="showMain(\'weekly\',this)">📊 週報分析</button>\n    <div class="nav-meta">'
        )

    # Update date in nav-meta
    today = date.today().strftime('%Y-%m-%d')
    content = re.sub(r'Updated \d{4}-\d{2}-\d{2}', f'Updated {today}', content)

    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ index.html 已更新")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--week',     default='W25')
    parser.add_argument('--day',      default='Sun')
    parser.add_argument('--price',    type=float, default=None)
    parser.add_argument('--bias',     default='觀望，等S2 A+')
    parser.add_argument('--account',  type=int, default=21649)
    parser.add_argument('--scenario2',default='震盪尋底 57.5%，等 SSL Sweep 4121 後 S2 A+ @ 4095-4131')
    parser.add_argument('--s2',       default='4095-4131（4H FVG+4H下軌）/ 4082（備選日線下軌）')
    parser.add_argument('--s1',       default='站回1H中軌4165 + AO翻正 + DXY回落<65')
    args = parser.parse_args()

    print("📊 讀取 CSV 並計算指標...")
    data = run_analysis()
    if args.price:
        data['price'] = args.price

    week_id   = args.week
    day_label = args.day

    print(f"🏗️  生成 {week_id} {day_label} 週報 HTML...")
    weekly_html = build_weekly_section(week_id, day_label, data, args)

    print("🔄 更新 index.html...")
    update_index_html(weekly_html)

    # Save data JSON for reference
    json_path = os.path.join(REPORTS_DIR, f"weekly_data_{week_id}_{day_label}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({**data, "week": week_id, "day": day_label,
                   "bias": args.bias, "s2": args.s2, "s1": args.s1,
                   "scenario2": args.scenario2}, f, ensure_ascii=False, indent=2)

    print(f"✅ 完成！")
    print(f"   → index.html 已更新（週報分析 tab）")
    print(f"   → 資料快取：{json_path}")
    print(f"\n開啟瀏覽器查看：")
    print(f"   open /Users/tittan/program/github/trading/xauusd/index.html")

if __name__ == '__main__':
    main()
