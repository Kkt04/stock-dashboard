"""
Seed Script — Populates DB with mock NSE stock data.
Uses yfinance if available, falls back to synthetic generation.
"""

import sqlite3
import random
import math
from datetime import date, timedelta

COMPANIES = [
    ("RELIANCE", "Reliance Industries Ltd",     "Energy",          "NSE"),
    ("TCS",      "Tata Consultancy Services",   "IT",              "NSE"),
    ("INFY",     "Infosys Ltd",                 "IT",              "NSE"),
    ("HDFCBANK", "HDFC Bank Ltd",               "Banking",         "NSE"),
    ("WIPRO",    "Wipro Ltd",                   "IT",              "NSE"),
    ("ITC",      "ITC Ltd",                     "FMCG",            "NSE"),
    ("SBIN",     "State Bank of India",         "Banking",         "NSE"),
    ("BAJFINANCE","Bajaj Finance Ltd",           "NBFC",            "NSE"),
    ("HCLTECH",  "HCL Technologies Ltd",        "IT",              "NSE"),
    ("MARUTI",   "Maruti Suzuki India Ltd",      "Automobile",      "NSE"),
]

# Base prices (approx real INR levels)
BASE_PRICES = {
    "RELIANCE":  2800.0,
    "TCS":       3900.0,
    "INFY":      1600.0,
    "HDFCBANK":  1700.0,
    "WIPRO":      500.0,
    "ITC":        450.0,
    "SBIN":       750.0,
    "BAJFINANCE": 7000.0,
    "HCLTECH":   1400.0,
    "MARUTI":    12000.0,
}

VOLATILITY = {
    "RELIANCE":   0.012,
    "TCS":        0.010,
    "INFY":       0.013,
    "HDFCBANK":   0.011,
    "WIPRO":      0.015,
    "ITC":        0.009,
    "SBIN":       0.018,
    "BAJFINANCE": 0.020,
    "HCLTECH":    0.013,
    "MARUTI":     0.016,
}


def _generate_prices(symbol: str, n_days: int = 400):
    """
    Geometric Brownian Motion simulation for realistic OHLCV data.
    """
    price = BASE_PRICES[symbol]
    vol   = VOLATILITY[symbol]
    records = []
    today = date.today()

    for i in range(n_days, 0, -1):
        day = today - timedelta(days=i)
        if day.weekday() >= 5: 
            continue

        drift  = random.gauss(0.0002, vol)
        factor = math.exp(drift)
        close  = round(price * factor, 2)
        spread = abs(random.gauss(0, vol * price))
        high   = round(max(price, close) + spread * random.random(), 2)
        low    = round(min(price, close) - spread * random.random(), 2)
        open_p = round(price + random.gauss(0, vol * price * 0.3), 2)
        volume = random.randint(500_000, 10_000_000)

        records.append((symbol, str(day), open_p, high, low, close, volume))
        price = close

    return records


def seed(conn: sqlite3.Connection):
    """Insert companies and 400 days of synthetic price data."""
    conn.executemany(
        "INSERT OR IGNORE INTO companies (symbol, name, sector, exchange) VALUES (?,?,?,?)",
        COMPANIES,
    )

    all_prices = []
    for sym, *_ in COMPANIES:
        all_prices.extend(_generate_prices(sym))

    conn.executemany(
        """INSERT OR IGNORE INTO stock_prices
           (symbol, date, open, high, low, close, volume)
           VALUES (?,?,?,?,?,?,?)""",
        all_prices,
    )
    conn.commit()