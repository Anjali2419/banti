
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATABASE_PATH=/data/login.db

WORKDIR /app

RUN groupadd --system appuser \
    && useradd --system --gid appuser --no-create-home appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser app.py wsgi.py ./
COPY --chown=appuser:appuser templates/ ./templates/

USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "30", "wsgi:app"]
