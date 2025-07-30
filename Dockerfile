# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install build dependencies
COPY requirements.txt .
COPY requirements-production.txt .
RUN apt-get update && apt-get install -y build-essential
# Build all wheels for test stage
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt
# Build production-only wheels for production stage
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/prod-wheels -r requirements-production.txt

# Stage 2: Base runtime (shared dependencies)
FROM python:3.11-slim AS base

# Install core runtime dependencies (pdftk, PostgreSQL client)
RUN apt-get update && apt-get install -y \
    pdftk \
    cron \
    wget \
    gnupg \
    curl \
    unzip \
    # PostgreSQL client
    && wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y postgresql-client-17 \
    && rm -rf /var/lib/apt/lists/*

# Stage 3: Test image (with Playwright browser dependencies)
FROM base AS test

# Install Playwright browser dependencies
RUN apt-get update && apt-get install -y \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcb1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Complete test image setup
# Create a non-root user
RUN useradd -m -d /home/appuser -s /bin/bash appuser
USER appuser

# Set work directory
WORKDIR /home/appuser/app

# Add the local bin to the path
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy and install Python wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# No browser dependencies - tests will run in separate Playwright container

# Switch to root to clean up wheels, then back to appuser
USER root
RUN rm -rf /wheels
USER appuser

# Copy application code
COPY . .

# Make startup script executable and fix ownership
USER root
RUN chmod +x /home/appuser/app/startup.sh
RUN mkdir -p /var/log/django && chown -R appuser:appuser /var/log/django
RUN mkdir -p /var/backups/autocusto && chown -R appuser:appuser /var/backups/autocusto
RUN chown -R appuser:appuser /home/appuser/app
USER appuser

# Expose port
EXPOSE 8001

# Use startup script as entrypoint
ENTRYPOINT ["/home/appuser/app/startup.sh"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]

# Stage 4: Production image (minimal, no browsers)
FROM base AS production

# Create a non-root user
RUN useradd -m -d /home/appuser -s /bin/bash appuser
USER appuser

# Set work directory
WORKDIR /home/appuser/app

# Add the local bin to the path
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy and install only production Python wheels (no test dependencies)
COPY --from=builder /app/prod-wheels /wheels
COPY --from=builder /app/requirements-production.txt .
RUN pip install --no-cache /wheels/*

# Switch to root to clean up wheels, then back to appuser
USER root
RUN rm -rf /wheels
USER appuser

# Copy application code (this runs as root even though USER is appuser)
COPY . .

# Make startup script executable
USER root
RUN chmod +x /home/appuser/app/startup.sh

# Fix ownership of copied files so appuser can write to static/tmp
# Create log directory for Django
RUN mkdir -p /var/log/django && chown -R appuser:appuser /var/log/django
# Create backup directory with proper permissions
RUN mkdir -p /var/backups/autocusto && chown -R appuser:appuser /var/backups/autocusto
RUN chown -R appuser:appuser /home/appuser/app
USER appuser

# Expose port
EXPOSE 8001

# Use startup script as entrypoint to set up memory mount, then run the application
ENTRYPOINT ["/home/appuser/app/startup.sh"]
CMD ["uwsgi", "--ini", "uwsgi.ini"]