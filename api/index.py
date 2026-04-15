import os
import sys

backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import init_db, get_connection
from routers import stocks, analytics
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Stock Data Intelligence Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, tags=["Stocks"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])


@app.get("/")
def root():
    return {"message": "Stock Dashboard API is running", "docs": "/docs"}


@app.get("/companies")
def get_companies():
    conn = get_connection()
    rows = conn.execute(
        "SELECT symbol, name, sector, exchange FROM companies ORDER BY symbol"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


handler = app
