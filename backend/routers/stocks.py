"""
Stocks Router — Required API Endpoints
GET /companies
GET /data/{symbol}
GET /summary/{symbol}
GET /compare
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from database import get_connection
import pandas as pd

router = APIRouter()


@router.get("/companies")
def get_companies():
    """Returns a list of all available companies with basic metadata."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT symbol, name, sector, exchange FROM companies ORDER BY symbol"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/data/{symbol}")
def get_stock_data(symbol: str, days: int = Query(default=30, ge=1, le=365)):
    """
    Returns last N days of OHLCV data for a given symbol,
    enriched with daily_return and 7-day moving average.
    """
    symbol = symbol.upper()
    _check_symbol_exists(symbol)

    conn = get_connection()
    rows = conn.execute(
        """
        SELECT date, open, high, low, close, volume
        FROM   stock_prices
        WHERE  symbol = ?
        ORDER  BY date DESC
        LIMIT  ?
        """,
        (symbol, days),
    ).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No price data found for {symbol}.")

    df = pd.DataFrame([dict(r) for r in rows])
    df.sort_values("date", inplace=True)

    # Calculated metrics
    df["daily_return"] = ((df["close"] - df["open"]) / df["open"]).round(6)
    df["ma_7"]         = df["close"].rolling(7, min_periods=1).mean().round(2)

    return df.to_dict(orient="records")


@router.get("/summary/{symbol}")
def get_summary(symbol: str):
    """
    Returns 52-week high, 52-week low, average close,
    and basic volatility score for the given symbol.
    """
    symbol = symbol.upper()
    _check_symbol_exists(symbol)

    conn = get_connection()
    rows = conn.execute(
        """
        SELECT date, close, open, volume
        FROM   stock_prices
        WHERE  symbol = ?
          AND  date >= date('now', '-365 days')
        ORDER  BY date
        """,
        (symbol,),
    ).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No data in past 52 weeks for {symbol}.")

    df = pd.DataFrame([dict(r) for r in rows])
    df["daily_return"] = (df["close"] - df["open"]) / df["open"]

    return {
        "symbol":           symbol,
        "week52_high":      round(df["close"].max(), 2),
        "week52_low":       round(df["close"].min(), 2),
        "avg_close":        round(df["close"].mean(), 2),
        "volatility_score": round(df["daily_return"].std() * 100, 4),  # custom metric
        "avg_volume":       int(df["volume"].mean()),
        "data_points":      len(df),
    }


@router.get("/compare")
def compare_stocks(
    symbol1: str = Query(..., description="First stock symbol, e.g. INFY"),
    symbol2: str = Query(..., description="Second stock symbol, e.g. TCS"),
    days: int    = Query(default=30, ge=1, le=365),
):
    """
    Compares two stocks: closing prices, returns, and Pearson correlation.
    """
    s1, s2 = symbol1.upper(), symbol2.upper()
    _check_symbol_exists(s1)
    _check_symbol_exists(s2)

    conn = get_connection()

    def fetch(sym):
        rows = conn.execute(
            """
            SELECT date, close
            FROM   stock_prices
            WHERE  symbol = ?
              AND  date >= date('now', ?||' days')
            ORDER  BY date
            """,
            (sym, f"-{days}"),
        ).fetchall()
        return pd.DataFrame([dict(r) for r in rows]).set_index("date")["close"].rename(sym)

    df1, df2 = fetch(s1), fetch(s2)
    conn.close()

    merged = pd.concat([df1, df2], axis=1).dropna()
    correlation = round(merged.corr().iloc[0, 1], 4) if len(merged) > 1 else None

    return {
        "symbol1":    s1,
        "symbol2":    s2,
        "days":       days,
        "correlation": correlation,
        "data":       merged.reset_index().rename(columns={"index": "date"}).to_dict(orient="records"),
    }


def _check_symbol_exists(symbol: str):
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM companies WHERE symbol = ?", (symbol,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found.")