# -- AMW Django ERP - Dockerfile --
# Multi-stage build for production-ready deployment

# -- Base Image --
FROM python:3.11-slim as base

# -- Environment Variables --
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# -- Working Directory --
WORKDIR /app

# -- Install System Dependencies --
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# -- Install Python Dependencies --
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# -- Copy Project Files --
COPY . .

# -- Create Non-Root User --
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# -- Expose Port --
EXPOSE 8010

# -- Health Check --
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python manage.py check || exit 1

# -- Default Command --
CMD ["gunicorn", "--bind", "0.0.0.0:8010", "config.wsgi:application"]
