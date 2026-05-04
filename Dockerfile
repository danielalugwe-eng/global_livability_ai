# ─────────────────────────────────────────────────────────────────────────────
# Global Livability AI — Pipeline + Dashboard Image
# ─────────────────────────────────────────────────────────────────────────────
# Build:  docker build -t global-livability-ai:latest .
# Run:    docker compose up
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim AS base

# ── OS-level dependencies ────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git \
        curl \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ── Python dependencies (cached layer) ──────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Application code ─────────────────────────────────────────────────────────
COPY config.yaml .
COPY src/ src/
COPY app/ app/

# ── Create data / model / asset directories ──────────────────────────────────
RUN mkdir -p data/raw data/processed data/features data/forecasts \
             models app/assets

# ── Non-root user (security best practice) ───────────────────────────────────
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# ── Streamlit config ─────────────────────────────────────────────────────────
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

# Default: launch the dashboard.
# Override CMD in docker-compose for pipeline steps.
CMD ["streamlit", "run", "app/app.py", "--server.headless", "true"]
