# Use Python 3.11 as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src/ src/
COPY test_run.py ./
COPY test_config.json ./
COPY .env.example .env

# Install dependencies
RUN poetry install --no-root --no-dev

# Create necessary directories
RUN mkdir -p reports .cache

# Set default command
ENTRYPOINT ["poetry", "run", "python", "test_run.py"]
CMD ["--help"]
