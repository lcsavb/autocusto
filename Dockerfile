# Builder stage
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy your Django app source code
COPY . /app

# Final runtime image (minimal)
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PATH="/opt/venv/bin:$PATH"

# Install only required runtime packages (pdftk, Java for pdftk)
RUN apt-get update && apt-get install -y --no-install-recommends \
    pdftk \
    default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the virtualenv and your app from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# Run Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
