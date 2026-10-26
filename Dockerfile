# ==============================================================================
# RESUME LAB AI STUDIO - SECURE STATELESS CONTAINER (Cloud Run)
# ==============================================================================
# Zero-Cloud PII Architecture:
# - No personal knowledge bases, resumes, or client data are packaged.
# - Explicit folder copies ensure no accidental host files leak into the image.
# - Runs as a non-privileged user (appuser).
# ==============================================================================

FROM python:3.11-slim

# Set environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Install system dependencies (if needed by lxml)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly copy only application code, templates, and example knowledge base
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY template/ ./template/
COPY knowledge_base.example/ ./knowledge_base.example/
COPY tests/ ./tests/

# Create runtime directories for output with non-root ownership
RUN mkdir -p /app/output /app/my_applications && \
    useradd -u 10001 -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + str(os.environ.get('PORT', 8080)) + '/api/status')" || exit 1

ENTRYPOINT ["python", "app/server.py"]
