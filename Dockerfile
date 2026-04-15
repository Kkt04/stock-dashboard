# Stage 1: builder
FROM python:3.11-slim AS builder

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: runtime 
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY backend/ ./backend/
COPY data/    ./data/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]