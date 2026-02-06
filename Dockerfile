# Stage 1: Build dependencies in a lean environment
FROM python:3.11-slim AS builder

# Set environment variables for Poetry
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_VIRTUALENVS_CREATE=true

# Install Poetry and system dependencies
RUN pip install poetry
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copy dependency definition files and install dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --without dev

# Stage 2: Create the final, optimized production image
FROM python:3.11-slim AS final

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Install curl for health check
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN adduser -u 5678 --disabled-password --gecos "" appuser

# Set working directory and copy virtual environment from builder stage
WORKDIR /app
COPY --from=builder /app /app

# Copy application source code
COPY . .

# Set ownership and switch to non-root user
RUN chown -R appuser /app
USER appuser

# Add a health check to ensure the application is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Expose port and define the command to run the application
EXPOSE 8080
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8080} api.main:app"]