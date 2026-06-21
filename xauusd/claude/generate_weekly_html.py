"""
generate_weekly_html.py
Combine 跑完後自動呼叫，更新 index.html 的「週報分析」tab。

用法 A（Merge 流程末尾自動呼叫，推薦）：
  python3.12 claude/generate_weekly_html.py \\
      --from-json claude/reports/weekly_consensus_W26_Sun.json

用法 B（手動補參數）：
  python3.12 claude/generate_weekly_html.py \\
      --week W26 --day Sun --price 4155.57 \\
      --bias "觀望，等S2 A+" --account 21649 \\
      --scenario2 "震盪尋底57.5%..." \\
      --s2 "4095-4131" --s1 "站回4165+AO翻正"
"""
import argparse, json, os, re, glob, warnings
from datetime import date
import pandas as pd
import numpy as np

warnings.filterwarnings('ignore')

CSV_DIR    = "/Users/tittan/googledrive/XAUUSD/weekly report/csv/"
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
INDEX_HTML  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html")

# ── CSV 指標計算 ──────────────────────────────────────────────────────────
def load_csv(fname):
    for enc in ['utf-8', 'utf-8-sig', 'big5', 'cp950']:
        try:
            df = pd.read_csv(CSV_DIR + fname, encoding=enc, encoding_errors='ignore')
            df = df.rename(columns={df.columns[0]: 'time'})
            df['time'] = (pd.to_datetime(df['time'], utc=True)
                          .dt.tz_convert('Asia/Taipei').dt.tz_localize(None))
            df.columns = [c.strip().lower().replace(' ','_').replace('-','_') for c in df.columns]
            return df.sort_values('time').reset_index(drop=True)
        except:
            continue
    return None

def add_indicators(df):
    df['bb_mid'] = df['close'].rolling(20).mean()
    std = df['close'].rolling(20).std()
    df['bb_up']  = df['bb_mid'] + 2 * std
    df['bb_lo']  = df['bb_mid'] - 2 * std
    df['bb_pct'] = (df['close'] - df['bb_lo']) / (df['bb_up'] - df['bb_lo'])
    df['ema50']  = df['close'].ewm(span=50,  adjust=False).mean()
    df['ema200'] = df['close'].ewm(span=200, adjust=False).mean()
    delta = df['close'].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df['rsi'] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    tr = pd.concat([(df['high']-df['low']),
                    (df['high']-df['close'].shift()).abs(),
                    (df['low'] -df['close'].shift()).abs()], axis=1).max(axis=1)
    df['atr'] = tr.rolling(14).mean()
    return df

def scan_fvg(df, lookback=60):
    h, l = df['high'].values, df['low'].values
    n = len(df)
    bull, bear = [], []
    for j in range(2, n):
        if h[j-2] < l[j]: bull.append({'bot': round(h[j-2],1), 'top': round(l[j],1), 'bar': j})
        if l[j-2] > h[j]: bear.append({'bot': round(h[j],1),   'top': round(l[j-2],1), 'bar': j})
    ab = [z for z in bull if z['bar']>=n-lookback and not any(l[k]<=z['bot'] for k in range(z['bar'],n))]
    ae = [z for z in bear if z['bar']>=n-lookback and not any(h[k]>=z['top'] for k in range(z['bar'],n))]
    return ab[-3:], ae[-3:]

def scan_liq(df, lookback=30):
    h, l = df['high'].values, df['low'].values
    n = len(df)
    bsl, ssl = [], []
    for i in range(2, min(lookback, n-2)):
        idx = n-1-i
        if idx < 2: break
        if h[idx]>h[idx-1] and h[idx]>h[idx-2] and h[idx]>h[idx+1] and h[idx]>h[idx+2]:
            bsl.append(round(h[idx],1))
        if l[idx]<l[idx-1] and l[idx]<l[idx-2] and l[idx]<l[idx+1] and l[idx]<l[idx+2]:
            ssl.append(round(l[idx],1))
    return sorted(set(bsl), reverse=True)[:3], sorted(set(ssl))[:3]

def run_analysis():
    dfs = {
        '1d': add_indicators(load_csv("FX_IDC_XAUUSD, 1D.csv")),
        '1w': add_indicators(load_csv("FX_IDC_XAUUSD, 1W.csv")),
        '4h': add_indicators(load_csv("FX_IDC_XAUUSD, 240.csv")),
        '1h': add_indicators(load_csv("FX_IDC_XAUUSD, 60.csv")),
        'dxy': add_indicators(load_csv("TVC_DXY, 1D.csv")),
    }
    d, w, h4, h1, dx = (dfs[k].iloc[-1] for k in ['1d','1w','4h','1h','dxy'])
    wp = dfs['1w'].iloc[-2]
    bull_fvg, bear_fvg = scan_fvg(dfs['4h'])
    bsl, ssl = scan_liq(dfs['4h'])

    levels = [
        ("週線BB上軌", dfs['1w'].iloc[-1]['bb_up'], "阻力"),
        ("週線BB中軌", dfs['1w'].iloc[-1]['bb_mid'], "阻力"),
        ("日線BB上軌", d['bb_up'], "阻力"),
        ("日線EMA50",  d['ema50'], "阻力"),
        ("日線BB中軌", d['bb_mid'], "阻力"),
        ("4H BB上軌",  h4['bb_up'], "阻力"),
        ("4H BB中軌",  h4['bb_mid'], "阻力"),
        ("4H EMA50",  h4['ema50'], "阻力"),
        ("1H BB上軌",  h1['bb_up'], "阻力"),
        ("1H BB中軌",  h1['bb_mid'], "阻/撐"),
        ("1H BB下軌",  h1['bb_lo'], "支撐"),
        ("4H BB下軌",  h4['bb_lo'], "支撐★"),
        ("4H Bullish FVG", bull_fvg[-1]['bot'] if bull_fvg else None, "支撐★"),
        ("日線BB下軌", d['bb_lo'], "支撐"),
        ("週線BB下軌", dfs['1w'].iloc[-1]['bb_lo'], "支撐"),
    ]

    weeks5 = []
    for _, r in dfs['1w'].tail(5).iterrows():
        chg = r['close'] - r['open']
        weeks5.append({
            "date": r['time'].strftime('%m/%d'),
            "open": round(float(r['open']),1), "high": round(float(r['high']),1),
            "low":  round(float(r['low']),1),  "close": round(float(r['close']),1),
            "chg":  round(float(chg),1),
            "pct":  round(float(chg/r['open']*100),1),
        })

    return {
        "price":      round(float(d['close']),2),
        "rsi_1d":     round(float(d['rsi']),1),
        "rsi_4h":     round(float(h4['rsi']),1),
        "rsi_1h":     round(float(h1['rsi']),1),
        "dxy":        round(float(dx['close']),2),
        "dxy_rsi":    round(float(dx['rsi']),1),
        "atr_1d":     round(float(d['atr']),1),
        "w_chg":      round(float(w['close']-w['open']),1),
        "w_pct":      round(float((w['close']-w['open'])/w['open']*100),1),
        "bb_1d_up":   round(float(d['bb_up']),1),  "bb_1d_mid": round(float(d['bb_mid']),1),
        "bb_1d_lo":   round(float(d['bb_lo']),1),  "bb_1d_pct": round(float(d['bb_pct']),2),
        "bb_4h_up":   round(float(h4['bb_up']),1), "bb_4h_mid": round(float(h4['bb_mid']),1),
        "bb_4h_lo":   round(float(h4['bb_lo']),1),
        "bb_1h_mid":  round(float(h1['bb_mid']),1),"bb_1h_lo":  round(float(h1['bb_lo']),1),
        "bb_1h_up":   round(float(h1['bb_up']),1),
        "levels":     [(n, round(float(v),1), t) for n,v,t in levels if v is not None],
        "bull_fvg_4h":[(z['bot'],z['top']) for z in bull_fvg],
        "bear_fvg_4h":[(z['bot'],z['top']) for z in bear_fvg],
        "bsl_4h": bsl, "ssl_4h": ssl,
        "weeks5": weeks5,
    }

# ── 報告歸檔：自動掃 reports/ 目錄 ───────────────────────────────────────
def build_archive_rows():
    """掃 reports/ 目錄，按週次分組，自動生成歸檔列。"""
    pattern = os.path.join(REPORTS_DIR, "*.docx")
    files   = sorted(glob.glob(pattern), reverse=True)

    # 分組：{(week, day): {claude, styleA, styleB, styleC}}
    groups = {}
    for f in files:
        name = os.path.basename(f)
        # Claude 週報：XAUUSD_Weekly_Report_2026W25_Sun_Claude.docx
        m = re.match(r'XAUUSD_Weekly_Report_(\d{4})(W\d+)_(\w+)_Claude\.docx', name)
        if m:
            key = (m.group(2), m.group(3), m.group(1))  # (W25, Sun, 2026)
            groups.setdefault(key, {})['claude'] = name
            continue
        # Combine：XAUUSD_W25_Combine_Style{A/B/C}.docx
        m = re.match(r'XAUUSD_(W\d+)_Combine_Style(\w)\.docx', name)
        if m:
            # Try to find matching key
            week = m.group(1)
            style = m.group(2)
            matched = [k for k in groups if k[0]==week]
            if matched:
                groups[matched[0]][f'style{style}'] = name
            else:
                groups.setdefault((week, '?', '2026'), {})[f'style{style}'] = name

    rows = ""
    for (week, day, year), info in sorted(groups.items(), reverse=True):
        def link(fname, label):
            if not fname: return '—'
            return f'<a class="report-link" href="claude/reports/{fname}">{label}</a>'
        rows += f"""<tr>
          <td><strong>{week}</strong></td>
          <td class="td-date">{year}-{day} {day}</td>
          <td>{link(info.get('claude'), '📥 週報')}</td>
          <td>{link(info.get('styleA'), '📥 量化')}</td>
          <td>{link(info.get('styleB'), '📥 老鳥')}</td>
          <td>{link(info.get('styleC'), '📥 委員會')}</td>
        </tr>"""
    return rows or '<tr><td colspan="6" style="color:var(--muted)">尚無報告</td></tr>'

# ── HTML 區塊生成 ──────────────────────────────────────────────────────────
def rsi_badge(v):
    if v < 30: return f'<span class="badge badge-red">{v} 超賣</span>'
    if v > 70: return f'<span class="badge badge-yellow">{v} 超買</span>'
    return f'<span class="badge badge-blue">{v}</span>'

def build_weekly_section(c):
    """c = consensus dict（含 CSV 數字 + 人工判斷欄位）"""
    price, w_chg, w_pct = c['price'], c['w_chg'], c['w_pct']
    chg_cls = "pos" if w_chg >= 0 else "neg"
    week_id, day_label, gen_date = c['week'], c['day'], date.today().strftime('%Y-%m-%d')

    # 關鍵位階表
    rows_lv = ""
    for name, val, direction in sorted(c['levels'], key=lambda x: x[1], reverse=True):
        near = abs(val - price) < 35
        style = ' style="background:#fffbeb"' if near else ''
        marker = ' <span style="color:#d97706;font-weight:700">← 現價</span>' if near else ''
        dir_cls = "pos" if "支撐" in direction else ("neg" if "阻力" in direction else "")
        rows_lv += f'<tr{style}><td class="{dir_cls}">{direction}</td><td><strong>{val}</strong>{marker}</td><td style="color:var(--muted);font-size:.82em">{name}</td></tr>'

    # 近5週表
    rows_w5 = ""
    for w in c['weeks5']:
        icon = "🟢" if w['chg'] >= 0 else "🔴"
        cls  = "pos" if w['chg'] >= 0 else "neg"
        sign = "+" if w['chg'] >= 0 else ""
        rows_w5 += f"""<tr>
          <td class="td-date">{icon} {w['date']}</td>
          <td>{w['open']}</td><td>{w['high']}</td><td>{w['low']}</td>
          <td><strong>{w['close']}</strong></td>
          <td class="{cls}">{sign}{w['chg']} ({sign}{w['pct']}%)</td>
        </tr>"""

    # SMC
    bear_fvg_str = ", ".join(f"{b}-{t}" for b,t in c['bear_fvg_4h']) or "無"
    bull_fvg_str = ", ".join(f"{b}-{t}" for b,t in c['bull_fvg_4h']) or "無"
    bsl_str = " / ".join(str(x) for x in c['bsl_4h']) or "無"
    ssl_str = " / ".join(str(x) for x in c['ssl_4h']) or "無"

    account = f"${int(c.get('account', 0)):,}"
    bias    = c.get('bias', '—')
    sc2     = c.get('scenario2', '—')
    s2      = c.get('s2', '—')
    s1      = c.get('s1', '—')
    cftc    = c.get('cftc_note', 'CFTC 資料請見完整週報')
    source  = c.get('source', 'Combine（Claude × Gemini 仲裁）')

    sc1_pct = c.get('scenario1_pct', 22)
    sc2_pct = c.get('scenario2_pct', 58)
    sc3_pct = c.get('scenario3_pct', 20)

    archive_rows = build_archive_rows()

    return f"""
<!-- WEEKLY_SECTION_START -->
<div id="main-weekly" class="main-section">
  <div class="subnav">
    <button class="sub-tab active" onclick="showTab('wk','now',this)">本週重點</button>
    <button class="sub-tab" onclick="showTab('wk','history',this)">近5週走勢</button>
    <button class="sub-tab" onclick="showTab('wk','archive',this)">報告歸檔</button>
  </div>

  <!-- ── 本週重點 ───────────────────────────────────────────────── -->
  <div id="wk-now" class="tab-panel active">
    <div class="part-label">
      <span class="part-badge">{week_id} {day_label}</span>
      本週重點 · {gen_date}
      <span style="font-size:.78em;color:var(--muted);font-weight:400;margin-left:8px">資料來源：{source}</span>
    </div>

    <div class="grid-4">
      <div class="metric-card card">
        <div class="metric-label">XAUUSD 現價</div>
        <div class="metric-val {chg_cls}">{price}</div>
        <div class="metric-sub">本週 {'+' if w_chg>=0 else ''}{w_chg}（{'+' if w_pct>=0 else ''}{w_pct}%）</div>
      </div>
      <div class="metric-card card">
        <div class="metric-label">RSI 狀態</div>
        <div class="metric-val" style="font-size:1.1em">{rsi_badge(c['rsi_1d'])}</div>
        <div class="metric-sub">日線 {c['rsi_1d']} · 4H {c['rsi_4h']} · 1H {c['rsi_1h']}</div>
      </div>
      <div class="metric-card card">
        <div class="metric-label">DXY 美元</div>
        <div class="metric-val yellow">{c['dxy']}</div>
        <div class="metric-sub">RSI {c['dxy_rsi']} · {'承壓⚠️' if c['dxy_rsi']>60 else '偏利多✅'} · ATR {c['atr_1d']}</div>
      </div>
      <div class="metric-card card">
        <div class="metric-label">帳戶偏向</div>
        <div class="metric-val" style="font-size:.95em;color:var(--text2)">{bias[:14]}{'…' if len(bias)>14 else ''}</div>
        <div class="metric-sub">{account}</div>
      </div>
    </div>

    <div class="insight-grid">
      <div class="insight warn">
        <strong>⭐ 主情境（{sc2_pct}%）</strong>{sc2}
      </div>
      <div class="insight info">
        <strong>🛡️ S2 A+ 進場區</strong>{s2}
        <br><span style="font-size:.88em;color:var(--text2)">等 SSL Sweep + M30 錘頭確認後進場</span>
      </div>
      <div class="insight good">
        <strong>🚀 S1 啟動條件</strong>{s1}
      </div>
      <div class="insight bad">
        <strong>🔍 SMC 4H Bearish FVG（阻力）</strong>{bear_fvg_str}
        <br>Bullish FVG（支撐）：{bull_fvg_str}
      </div>
      <div class="insight purple">
        <strong>💧 流動性（4H）</strong>
        BSL 前高：{bsl_str}
        <br>SSL 前低：{ssl_str}
      </div>
      <div class="insight info">
        <strong>📊 CFTC 籌碼</strong>{cftc}
      </div>
    </div>

    <div class="part-label"><span class="part-badge">PART 2</span>關鍵位階</div>
    <div class="card">
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>方向</th><th>價位</th><th>來源</th></tr></thead>
          <tbody>{rows_lv}</tbody>
        </table>
      </div>
    </div>

    <div class="part-label"><span class="part-badge">PART 3</span>三大劇本</div>
    <div class="grid-3">
      <div class="insight info">
        <strong>📈 劇本一：多頭爆發（{sc1_pct}%）</strong>
        DXY 回落 → 站回 1H 中軌 {c['bb_1h_mid']} → S1 啟動<br>
        TP：{c['bb_4h_mid']}（4H 中軌）
      </div>
      <div class="insight warn">
        <strong>😴 劇本二：震盪尋底（{sc2_pct}%）⭐主情境</strong>
        下探 {c['bb_4h_lo']}–{c['bb_1h_lo']} → SSL Sweep → 錘頭 → S2 A+<br>
        TP1 {c['bb_1h_mid']} · TP2 {c['bb_1h_up']}
      </div>
      <div class="insight bad">
        <strong>📉 劇本三：跌破支撐（{sc3_pct}%）</strong>
        跌破 {c['bb_1d_lo']} 日線下軌 → {round(c['bb_1d_lo']-60,0):.0f} 週線下軌方向<br>
        此劇本暫停操作
      </div>
    </div>
  </div><!-- /wk-now -->

  <!-- ── 近5週走勢 ──────────────────────────────────────────────── -->
  <div id="wk-history" class="tab-panel">
    <div class="part-label"><span class="part-badge">近5週</span>週線走勢</div>
    <div class="card">
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>週次</th><th>開盤</th><th>最高</th><th>最低</th><th>收盤</th><th>漲跌</th></tr></thead>
          <tbody>{rows_w5}</tbody>
        </table>
      </div>
    </div>

    <div class="part-label"><span class="part-badge">指標</span>多時間框架</div>
    <div class="grid-3">
      <div class="card">
        <div class="card-title">📊 布林通道</div>
        <div class="tbl-wrap"><table>
          <thead><tr><th>TF</th><th>上軌</th><th>中軌</th><th>下軌</th><th>%B</th></tr></thead>
          <tbody>
            <tr><td>1D</td><td>{c['bb_1d_up']}</td><td>{c['bb_1d_mid']}</td><td class="pos">{c['bb_1d_lo']}</td><td class="neg">{c['bb_1d_pct']}</td></tr>
            <tr><td>4H</td><td>{c['bb_4h_up']}</td><td>{c['bb_4h_mid']}</td><td class="pos">{c['bb_4h_lo']}</td><td>—</td></tr>
            <tr><td>1H</td><td>{c['bb_1h_up']}</td><td>{c['bb_1h_mid']}</td><td class="pos">{c['bb_1h_lo']}</td><td>—</td></tr>
          </tbody>
        </table></div>
      </div>
      <div class="card">
        <div class="card-title">📊 RSI 多框架</div>
        <div style="display:grid;gap:8px;margin-top:8px">
          <div class="metric-card"><div class="metric-label">日線 RSI</div><div class="metric-val {'red' if c['rsi_1d']<35 else 'yellow' if c['rsi_1d']>65 else ''}">{c['rsi_1d']}</div></div>
          <div class="metric-card"><div class="metric-label">4H RSI</div><div class="metric-val {'red' if c['rsi_4h']<35 else 'yellow' if c['rsi_4h']>65 else ''}">{c['rsi_4h']}</div></div>
          <div class="metric-card"><div class="metric-label">1H RSI</div><div class="metric-val">{c['rsi_1h']}</div></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">💵 DXY</div>
        <div class="metric-card" style="margin-top:8px">
          <div class="metric-label">DXY 現價</div>
          <div class="metric-val yellow">{c['dxy']}</div>
          <div class="metric-sub">RSI {c['dxy_rsi']} · {'超買，黃金承壓' if c['dxy_rsi']>70 else '偏強，注意壓力' if c['dxy_rsi']>55 else '中性偏弱'}</div>
        </div>
      </div>
    </div>
  </div><!-- /wk-history -->

  <!-- ── 報告歸檔 ────────────────────────────────────────────────── -->
  <div id="wk-archive" class="tab-panel">
    <div class="part-label"><span class="part-badge">歸檔</span>週報 + Combine 報告</div>
    <div class="card">
      <div style="font-size:.83em;color:var(--muted);margin-bottom:12px">
        DOCX 下載後用 Word/Pages 開啟 · Combine = Claude × Gemini 三風格整合版 · 每次 Merge 完自動更新
      </div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>週次</th><th>日期</th><th>Claude 週報</th><th>Style A 量化</th><th>Style B 老鳥</th><th>Style C 委員會</th></tr></thead>
          <tbody>{archive_rows}</tbody>
        </table>
      </div>
      <div style="margin-top:14px;padding:10px 14px;background:var(--surface2);border-radius:8px;font-size:.82em;color:var(--text2);font-family:monospace">
        python3.12 claude/generate_weekly_html.py --from-json claude/reports/weekly_consensus_W26_Sun.json
      </div>
    </div>
  </div><!-- /wk-archive -->
</div><!-- /main-weekly -->
<!-- WEEKLY_SECTION_END -->"""

# ── index.html 更新 ───────────────────────────────────────────────────────
def update_index_html(weekly_html):
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = r'<!-- WEEKLY_SECTION_START -->.*?<!-- WEEKLY_SECTION_END -->'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, weekly_html.strip(), content, flags=re.DOTALL)
    else:
        content = content.replace('</body>', weekly_html + '\n</body>')

    if "showMain('weekly'" not in content:
        content = content.replace(
            '<div class="nav-meta">',
            '<button class="nav-main-tab" onclick="showMain(\'weekly\',this)">📊 週報分析</button>\n    <div class="nav-meta">'
        )

    today = date.today().strftime('%Y-%m-%d')
    content = re.sub(r'Updated \d{4}-\d{2}-\d{2}', f'Updated {today}', content)

    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(content)

# ── 主程式 ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='更新 index.html 週報分析 tab')
    parser.add_argument('--from-json',   dest='from_json', default=None,
                        help='從 consensus JSON 讀取人工判斷欄位（Merge 流程自動呼叫）')
    parser.add_argument('--week',        default='W??')
    parser.add_argument('--day',         default='Sun')
    parser.add_argument('--price',       type=float, default=None)
    parser.add_argument('--bias',        default='—')
    parser.add_argument('--account',     type=int, default=0)
    parser.add_argument('--scenario2',   default='主情境：待更新')
    parser.add_argument('--s2',          default='—')
    parser.add_argument('--s1',          default='—')
    parser.add_argument('--cftc-note',   dest='cftc_note', default='請見完整週報')
    parser.add_argument('--sc1-pct',     dest='scenario1_pct', type=int, default=22)
    parser.add_argument('--sc2-pct',     dest='scenario2_pct', type=int, default=58)
    parser.add_argument('--sc3-pct',     dest='scenario3_pct', type=int, default=20)
    parser.add_argument('--source',      default='Combine（Claude × Gemini 仲裁）')
    args = parser.parse_args()

    # 讀 consensus JSON（Merge 流程末尾自動傳入）
    consensus = {}
    if args.from_json and os.path.exists(args.from_json):
        with open(args.from_json, 'r', encoding='utf-8') as f:
            consensus = json.load(f)
        print(f"📋 從 JSON 讀取共識：{args.from_json}")

    # CLI 參數覆蓋 JSON（明確傳入的優先）
    for k, v in vars(args).items():
        if k == 'from_json': continue
        if v not in (None, '—', '主情境：待更新', '請見完整週報', 'Combine（Claude × Gemini 仲裁）', 0, 22, 58, 20, 'W??', 'Sun'):
            consensus[k] = v

    print("📊 讀取 CSV 計算指標...")
    market_data = run_analysis()

    # 合併：市場數字 + 共識判斷
    combined = {**market_data, **consensus}
    if args.price:
        combined['price'] = args.price

    print(f"🏗️  生成 {combined.get('week','?')} 週報區塊...")
    weekly_html = build_weekly_section(combined)

    print("🔄 更新 index.html...")
    update_index_html(weekly_html)

    # 儲存最終使用的 consensus JSON（供下次參考）
    json_out = os.path.join(REPORTS_DIR,
        f"weekly_consensus_{combined.get('week','??')}_{combined.get('day','?')}.json")
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2, default=str)

    print(f"✅ 完成")
    print(f"   consensus JSON → {json_out}")
    print(f"   index.html 已更新")

if __name__ == '__main__':
    main()
