# 📈 Stock Data Intelligence Dashboard

A mini financial data platform built with **FastAPI + SQLite + Pandas + Chart.js**  
for the JarNox Software Intern Assignment.

---

## 🏗️ Project Structure

```
stock-dashboard/
├── backend/
│   ├── main.py               ← FastAPI app entry point + lifespan
│   ├── database.py           ← SQLite init, connection helper
│   ├── requirements.txt
│   ├── routers/
│   │   ├── stocks.py         ← /companies, /data, /summary, /compare
│   │   └── analytics.py      ← /analytics/* (gainers, losers, sentiment)
│   └── scripts/
│       └── seed_data.py      ← GBM-based mock stock data generator
├── frontend/
│   └── index.html            ← Single-file dashboard (Chart.js)
├── data/
│   └── stocks.db             ← SQLite DB (auto-created on first run)
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Setup & Run

### Option 1 — Local (Python)

```bash
cd backend
pip install -r requirements.txt
python main.py           # starts on http://localhost:8000
```

Then open `frontend/index.html` in your browser.

### Option 2 — Docker

```bash
docker-compose up --build
# API  → http://localhost:8000
# UI   → http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/companies` | All companies (symbol, name, sector) |
| GET | `/data/{symbol}?days=30` | OHLCV + daily_return + MA7 |
| GET | `/summary/{symbol}` | 52W high/low, avg close, volatility |
| GET | `/compare?symbol1=X&symbol2=Y` | Dual chart + Pearson correlation |
| GET | `/analytics/top-gainers` | Top 5 performers (7d) |
| GET | `/analytics/top-losers` | Bottom 5 performers (7d) |
| GET | `/analytics/sentiment` | Custom Market Sentiment Index |
| GET | `/analytics/correlation-matrix` | Full correlation matrix |

Interactive Swagger docs: **http://localhost:8000/docs**

---

## 📊 Metrics Explained

| Metric | Formula |
|--------|---------|
| Daily Return | `(close − open) / open` |
| 7-Day MA | Rolling 7-day mean of close price |
| 52W High/Low | Max/min of `close` in last 365 days |
| **Volatility Score** | `std(daily_return) × 100` — custom metric |
| **Sentiment Index** | `50 + (mean_return / 0.02) × 50` clamped 0–100 |
| Pearson Correlation | `df.corr()` on dual closing price series |

---

## 🧩 Tech Stack

- **Python 3.11** with **FastAPI** — async REST API
- **SQLite** — lightweight persistent storage
- **Pandas / NumPy** — data cleaning and metric calculation
- **Chart.js 4** — interactive browser charts
- **Docker** — containerised deployment

---

## 💡 Key Design Decisions

1. **GBM Simulation** — Geometric Brownian Motion generates realistic price paths instead of flat random walks.
2. **Single-file frontend** — Zero build tools needed; drop `index.html` anywhere and open.
3. **Lifespan seeding** — DB is seeded exactly once at startup; re-runs are idempotent (`INSERT OR IGNORE`).
4. **Custom Sentiment Index** — A normalised score derived from average 7-day returns across all tracked stocks, providing a market-wide signal at a glance.

---

## 🚀 Optional Enhancements Included

- ✅ Swagger / OpenAPI docs (`/docs`)
- ✅ Docker + docker-compose
- ✅ Correlation between stocks
- ✅ Volatility score (custom metric)
- ✅ Market Sentiment Index (custom metric)
- ✅ Top Gainers / Losers
- ✅ Multi-period chart filters (30D / 90D / 180D)# stock-dashboard
