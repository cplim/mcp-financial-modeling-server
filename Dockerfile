# Dockerfile for MCP Financial Modeling Prep Server - Local Development
# Supports both stdio and HTTP transports with secure defaults

# Build stage
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ src/

# Install dependencies
RUN uv sync --frozen

# Production stage
FROM python:3.11-slim AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd -r mcp && useradd -r -g mcp -s /bin/false mcp

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/uv.lock ./

# Copy .env file if it exists (development convenience)
# Environment variables take precedence over .env file
COPY .env* ./

# Create data directory and set permissions
RUN mkdir -p /app/data && \
    chown -R mcp:mcp /app

# Switch to non-root user
USER mcp

# Set Python path and virtual environment
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

# Expose port for HTTP transport (default 8000)
EXPOSE 8000

# Health check for HTTP transport
# Note: Only works when container is running with HTTP transport
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command uses HTTP transport with secure localhost binding
# Can be overridden at runtime:
# - stdio: docker run mcp-financial python -m mcp_financial_modeling_prep.server --transport stdio
# - custom HTTP: docker run mcp-financial python -m mcp_financial_modeling_prep.server --transport http --host 0.0.0.0 --port 9000
CMD ["python", "-m", "mcp_financial_modeling_prep.server", "--transport", "http", "--host", "127.0.0.1", "--port", "8000"]