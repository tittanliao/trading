# Pine Script 開發標準
# 版本：20260609 | 適用：XAUUSD 劍盾策略系列

---

## 基本規範

- Pine Script 版本：**v5 或 v6**
- 所有 filter 必須可開關（`input.bool`）
- 避免重繪（repainting）
- 避免 bgcolor 在 local scope
- 保持 S1/S2/BB/AWE/Resonance/SNR/FVG 系列結構一致性

---

## 命名規範（強制執行）

所有策略訂單 ID 和 comment 必須遵守：

| 用途 | 格式 | 範例 |
|------|------|------|
| 進場 | `S#_LE` | `S1_LE`, `S2_LE` |
| 止損 | `S#_SL` | `S1_SL`, `S2_SL` |
| 止盈1 | `S#_LX_TP1` | `S1_LX_TP1` |
| 止盈2 | `S#_LX_TP2` | `S1_LX_TP2` |
| 時間出場（獲利）| `S#_LX_TimeWin` | `S1_LX_TimeWin` |
| 時間出場（虧損）| `S#_LX_TimeLoss` | `S1_LX_TimeLoss` |

---

## 風險管理預設值

| 參數 | 預設值 | 說明 |
|------|--------|------|
| `Profit_Ratio_1` | 2.0 | TP1 倍數 |
| `Profit_Ratio_2` | 4.0 | TP2 倍數 |
| `sl_fix_pct`（S1 突破型）| 0.5 | 緊止損 |
| `sl_fix_pct`（S2 回調型）| 1.0 | 寬止損 |
| `out_k_count` | 48 | 時間止損 bars（24H）|

---

## Profit Flyer 機制（動態出場，強制實施）

> **哲學**：時間到期不要直接 `strategy.close()`，改用 `strategy.exit()` 設 stop price，讓價格自然解決。

```pine
// 輸入
out_k_count = input.int(48, "Time Exit Bars")

// 在 if MP > 0 內，依優先順序：

// 優先 1：TP2 命中 → 鎖定主要獲利
if close >= PTPrice2
    strategy.exit(..., stop=math.max(PTPrice2, ta.lowest(low, out_k_count/4)), 
                  comment="S#_LX_TP2")

// 優先 2：TP1 命中 → 鎖定初始獲利
else if close >= PTPrice1
    strategy.exit(..., stop=math.max(PTPrice1, ta.lowest(low, out_k_count/2)), 
                  comment="S#_LX_TP1")

// 優先 3：時間到期（Profit Flyer 核心）
else if BarsSinceEntry >= out_k_count
    if strategy.openprofit >= 0
        // 獲利中 → stop 移至進場價或近期低點（保護獲利，讓它繼續跑）
        exit_stop = math.max(EntryPrice, ta.lowest(low, out_k_count))
        strategy.exit(..., stop=exit_stop, comment="S#_LX_TimeWin")
    else
        // 虧損中 → stop 設在當前 low（最後機會，繼續跌就砍）
        exit_stop = low
        strategy.exit(..., stop=exit_stop, comment="S#_LX_TimeLoss")

// 優先 4：預設硬止損
else
    strategy.exit(..., stop=SLPrice, comment_loss="S#_SL")
```

---

## 語法安全規則（Strict Mode）

### 1. 多行字串/邏輯 → 必須用括號包住

```pine
// ❌ 錯誤（copy-paste 後容易爆）
sShow = "LE: " + str.tostring(price) + 
        "\nSL: " + str.tostring(sl)

// ✅ 正確
sShow = ("LE: " + str.tostring(price) + 
         "\nSL: " + str.tostring(sl))
```

### 2. var 變數 → 每個獨立一行

```pine
// ❌ 錯誤
var wins = 0, var losses = 0

// ✅ 正確
var wins = 0
var losses = 0
```

---

## 統計表格規範

```pine
// 必須有 Master Switch（預設關閉，保持圖表整潔）
show_table = input.bool(false, "Show Statistics Table")

// Detail Switch
show_detail_stats = input.bool(true, "Show Detailed Session Stats")
```

---

## Dashboard 必要欄位

策略表格必須包含：
- Session 統計（亞/歐/美盤）
- Weekday 統計（週一到週五）
- HTF 趨勢狀態（4H / 1D）
- 勝率 / PF 統計
- Gold Strength vs DXY

---

## 策略系列結構一致性

所有策略必須維持相同架構（Input 分組、濾鏡命名、出場邏輯），方便版本比較：

```
S1-AweWithBB  ← 突破型（EMA + BB + AO）
S2-Pullback   ← 回調型（錘頭 + ATR）
```

新策略開發時，以上述兩者為模板，保持結構統一。
