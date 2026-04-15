"""
Analytics Router — Custom & Bonus Endpoints

GET /analytics/top-gainers
GET /analytics/top-losers
GET /analytics/sentiment
GET /analytics/correlation-matrix
"""

from fastapi import APIRouter, Query
from database import get_connection
import pandas as pd

router = APIRouter(prefix="/analytics")


@router.get("/top-gainers")
def top_gainers(days: int = Query(default=7, ge=1, le=90), limit: int = 5):
    """Returns top N stocks by average daily return over last N days."""
    return _get_movers(days, limit, top=True)


@router.get("/top-losers")
def top_losers(days: int = Query(default=7, ge=1, le=90), limit: int = 5):
    """Returns worst N stocks by average daily return over last N days."""
    return _get_movers(days, limit, top=False)


@router.get("/sentiment")
def mock_sentiment():
    """
    Custom Metric: A mock 'Market Sentiment Index' (0–100)
    derived from average daily returns across all stocks.
    Score > 50 = Bullish, < 50 = Bearish.
    """
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT symbol, open, close
        FROM   stock_prices
        WHERE  date >= date('now', '-7 days')
        """
    ).fetchall()
    conn.close()

    if not rows:
        return {"sentiment_score": 50, "label": "Neutral", "detail": "No data"}

    df = pd.DataFrame([dict(r) for r in rows])
    df["ret"] = (df["close"] - df["open"]) / df["open"]
    mean_ret = df["ret"].mean()

    # Normalise to 0–100 (clamp at ±2%)
    score = round(50 + (mean_ret / 0.02) * 50, 1)
    score = max(0, min(100, score))

    label = "Bullish " if score > 55 else "Bearish " if score < 45 else "Neutral "
    return {
        "sentiment_score": score,
        "label":           label,
        "avg_daily_return": round(mean_ret * 100, 4),
    }


@router.get("/correlation-matrix")
def correlation_matrix(days: int = Query(default=30, ge=7, le=365)):
    """
    Returns a Pearson correlation matrix of closing prices
    for all tracked companies over the given window.
    """
    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT symbol, date, close
        FROM   stock_prices
        WHERE  date >= date('now', '-{days} days')
        ORDER  BY date
        """
    ).fetchall()
    conn.close()

    if not rows:
        return {"matrix": {}, "symbols": []}

    df = pd.DataFrame([dict(r) for r in rows])
    pivot = df.pivot(index="date", columns="symbol", values="close")
    corr  = pivot.corr().round(4)

    return {
        "symbols": list(corr.columns),
        "matrix":  corr.to_dict(),
    }


def _get_movers(days: int, limit: int, top: bool):
    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT sp.symbol, c.name, sp.open, sp.close
        FROM   stock_prices sp
        JOIN   companies c ON c.symbol = sp.symbol
        WHERE  sp.date >= date('now', '-{days} days')
        """
    ).fetchall()
    conn.close()

    if not rows:
        return []

    df = pd.DataFrame([dict(r) for r in rows])
    df["ret"] = (df["close"] - df["open"]) / df["open"]
    grouped = df.groupby(["symbol", "name"])["ret"].mean().reset_index()
    grouped.columns = ["symbol", "name", "avg_return"]
    grouped["avg_return"] = grouped["avg_return"].round(6)
    grouped.sort_values("avg_return", ascending=not top, inplace=True)

    return grouped.head(limit).to_dict(orient="records")