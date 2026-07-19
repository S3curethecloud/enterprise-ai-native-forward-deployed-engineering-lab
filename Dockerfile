FROM python:3.12-slim

LABEL org.opencontainers.image.title="Enterprise AI-Native Incident Diagnostic API"
LABEL org.opencontainers.image.description="Local recommendation-only Phase 3 prototype"
LABEL org.opencontainers.image.source="https://github.com/S3curethecloud/enterprise-ai-native-forward-deployed-engineering-lab"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN groupadd \
        --gid 10001 \
        appgroup \
    && useradd \
        --uid 10001 \
        --gid appgroup \
        --no-create-home \
        --shell /usr/sbin/nologin \
        appuser

COPY requirements/runtime.lock /app/requirements/runtime.lock

RUN python -m pip install \
        --require-hashes \
        --no-deps \
        --requirement /app/requirements/runtime.lock

COPY --chown=appuser:appgroup src /app/src

USER 10001:10001

EXPOSE 8000

HEALTHCHECK \
    --interval=10s \
    --timeout=3s \
    --start-period=5s \
    --retries=3 \
    CMD ["python", "-c", "import urllib.request; response = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2); raise SystemExit(0 if response.status == 200 else 1)"]

CMD ["uvicorn", "incident_diagnostic_api.services.gateway:app", "--host", "0.0.0.0", "--port", "8000"]
