# Stage 1: Builder
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# Stage 2: Final
FROM python:3.11-slim

# Create a non-root user
RUN useradd -m -d /home/appuser -s /bin/bash appuser
USER appuser

# Set work directory
WORKDIR /home/appuser/app

# Add the local bin to the path
ENV PATH="/home/appuser/.local/bin:${PATH}"

# Copy installed packages from builder stage
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run the application
CMD ["uwsgi", "--ini", "uwsgi.ini"]