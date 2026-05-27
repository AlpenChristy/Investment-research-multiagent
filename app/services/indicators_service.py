import pandas as pd
import pandas_ta as ta

def compute_indicators(df: pd.DataFrame) -> dict:
    close = df["close"]
    high  = df["high"]
    low   = df["low"]
    vol   = df["volume"]

    # ── Trend ────────────────────────────────────────────────
    ema20  = ta.ema(close, length=20)
    ema50  = ta.ema(close, length=50)
    sma200 = ta.sma(close, length=200)
    macd   = ta.macd(close)          # returns DataFrame: MACD_12_26_9, MACDh_, MACDs_

    # ── Momentum ─────────────────────────────────────────────
    rsi   = ta.rsi(close, length=14)
    stoch = ta.stoch(high, low, close)   # STOCHk_14_3_3, STOCHd_14_3_3

    # ── Volatility ───────────────────────────────────────────
    bbands = ta.bbands(close, length=20)  # BBL, BBM, BBU, BBB, BBP
    atr    = ta.atr(high, low, close, length=14)

    # ── Volume ───────────────────────────────────────────────
    obv  = ta.obv(close, vol)
    vwap = ta.vwap(high, low, close, vol)

    price = float(close.iloc[-1])

    def last(series):
        if series is None: return None
        v = series.iloc[-1]
        return round(float(v), 4) if pd.notna(v) else None

    def last_col(df_col, col):
        if df_col is None or col not in df_col.columns: return None
        return last(df_col[col])

    return {
        "price": price,
        # trend
        "ema20":       last(ema20),
        "ema50":       last(ema50),
        "sma200":      last(sma200),
        "macd_line":   last_col(macd, "MACD_12_26_9"),
        "macd_signal": last_col(macd, "MACDs_12_26_9"),
        "macd_hist":   last_col(macd, "MACDh_12_26_9"),
        # momentum
        "rsi":         last(rsi),
        "stoch_k":     last_col(stoch, "STOCHk_14_3_3"),
        "stoch_d":     last_col(stoch, "STOCHd_14_3_3"),
        # volatility
        "bb_upper":    last_col(bbands, "BBU_20_2.0"),
        "bb_mid":      last_col(bbands, "BBM_20_2.0"),
        "bb_lower":    last_col(bbands, "BBL_20_2.0"),
        "bb_pct":      last_col(bbands, "BBP_20_2.0"),  # 0=at lower, 1=at upper
        "atr":         last(atr),
        # volume
        "obv":         last(obv),
        "vwap":        last(vwap),
        # support / resistance (simple: 20d high/low)
        "high_20d":    round(float(high.rolling(20).max().iloc[-1]), 4),
        "low_20d":     round(float(low.rolling(20).min().iloc[-1]),  4),
        "high_52w":    round(float(high.rolling(252).max().iloc[-1]), 4),
        "low_52w":     round(float(low.rolling(252).min().iloc[-1]),  4),
    }