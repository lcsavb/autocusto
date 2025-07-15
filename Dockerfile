# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install build dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Stage 2: Final
FROM python:3.11-slim

# Install only runtime dependencies (pdftk with its Java runtime)
RUN apt-get update && apt-get install -y \
    pdftk \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m -d /home/appuser -s /bin/bash appuser
USER appuser

# Set work directory
WORKDIR /home/appuser/app

# Add the local bin to the path
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy and install Python wheels from builder (no build tools needed)
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Switch to root to clean up wheels, then back to appuser
USER root
RUN rm -rf /wheels
USER appuser

# Copy application code (this runs as root even though USER is appuser)
COPY . .

# Fix ownership of copied files so appuser can write to static/tmp
USER root
RUN chown -R appuser:appuser /home/appuser/app
USER appuser

# Expose port
EXPOSE 8001

# Run the application
CMD ["uwsgi", "--ini", "uwsgi.ini"]