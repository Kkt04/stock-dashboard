"""
Stock Data Intelligence Dashboard - Backend API
Built with FastAPI + SQLite + Pandas
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from database import init_db
from routers import stocks, analytics

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup."""
    print("Starting Stock Dashboard API...")
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(
    title="Stock Data Intelligence Dashboard",
    description="A mini financial data platform for NSE/BSE stock analysis.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow all origins for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, tags=["Stocks"])
app.include_router(analytics.router, tags=["Analytics"])


@app.get("/", tags=["Health"])
def root():
    return {"message": "Stock Dashboard API is running", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)