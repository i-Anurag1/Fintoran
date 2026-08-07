FROM python:3.11-slim

WORKDIR /app

# System deps: build tools needed for a couple of native wheels
# (chromadb/pysqlite3-binary/bcrypt) on some CPU architectures, plus curl
# for the healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# Persisted at runtime via docker-compose volumes
ENV DB_PATH=/app/database/financial_agent.db
ENV CHROMA_PERSIST_DIR=/app/data/chroma_db
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Run as a non-root user, and make sure it owns the directories that will
# be backed by named volumes (db_data / chroma_data) so writes don't fail
# on any host OS.
RUN useradd --create-home --uid 1000 appuser \
    && mkdir -p /app/database /app/data/chroma_db /app/data \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
