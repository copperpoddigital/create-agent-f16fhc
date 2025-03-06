# Use a multi-stage build to reduce the final image size
# ------------------------------------------------------------------------------
# Builder stage: Install dependencies and prepare the application
FROM python:3.9-slim AS builder
# Version: python:3.9-slim
# Description: This stage is used to build the application and install dependencies.
# Requirements addressed:
# - Containerization (Technical Specifications/3.5 DEVELOPMENT & DEPLOYMENT)
# - Base Image Strategy (Technical Specifications/8.3.2 Base Image Strategy)
# - Build Optimization Techniques (Technical Specifications/8.3.4 Build Optimization Techniques)

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
# Application port
ENV PORT=8000

# Install system dependencies required for building Python packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev \
    curl

# Create working directory
WORKDIR /app

# Set up Poetry for dependency management
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy poetry.lock and pyproject.toml
COPY ./pyproject.toml ./poetry.lock ./

# Install project dependencies using Poetry
RUN poetry install --no-interaction --no-ansi

# Copy the application code
COPY ./src/backend /app

# ------------------------------------------------------------------------------
# Final stage: Create the runtime image
FROM python:3.9-slim AS final
# Version: python:3.9-slim
# Description: This stage is used to create the final image with only the runtime dependencies.
# Requirements addressed:
# - Containerization (Technical Specifications/3.5 DEVELOPMENT & DEPLOYMENT)
# - Base Image Strategy (Technical Specifications/8.3.2 Base Image Strategy)
# - Build Optimization Techniques (Technical Specifications/8.3.4 Build Optimization Techniques)

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1
# Application port
ENV PORT=8000

# Install runtime system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y libpq5

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /app/.venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the application code from the builder stage
COPY --from=builder /app /app

# Change ownership of application files to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s \
    CMD curl --fail http://localhost:$PORT/health || exit 1

# Run the application using gunicorn
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "wsgi:app"]
# Version: gunicorn==20.1.0
# Description: WSGI HTTP Server for running the application in production
# Requirements addressed:
# - Containerization (Technical Specifications/3.5 DEVELOPMENT & DEPLOYMENT)
# - Base Image Strategy (Technical Specifications/8.3.2 Base Image Strategy)
# - Build Optimization Techniques (Technical Specifications/8.3.4 Build Optimization Techniques)
# - IE2. For third-party or external imports, you must include the library version as a comment near the import. Again, you must ensure that you satisfy any prerequisites such as input parameters using the specific contents of your assigned file.
# - IE3. Be generous about your exports so long as it doesn't create a security risk.