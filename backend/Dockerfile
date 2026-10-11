
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Create a non-root user
RUN groupadd --system appuser && \
    useradd --system --gid appuser --no-create-home appuser

# Install dependencies separately for better build caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser app.py .

# Run without root privileges
USER appuser

EXPOSE 5000

# Production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "30", "app:app"]
