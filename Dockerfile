## syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv@sha256:1e3808aa9023d0980e7c15b1fa7c1ac16ff35925780cf5c459858b2d693f01a9 AS uv
FROM python:3.14-slim-trixie@sha256:b877e50bd90de10af8d82c57a022fc2e0dc731c5320d762a27986facfc3355c1

# Set working directory
WORKDIR /app

# Install uv for faster dependency resolution and installation
COPY --from=uv /uv /uvx /bin/

# Make uv more resilient in container builds and avoid cross-filesystem linking warnings
ENV UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=180 \
    UV_HTTP_RETRIES=5

# Copy dependency metadata first for better caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Use the project's virtual environment by default
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header", "--loop", "uvloop"]
