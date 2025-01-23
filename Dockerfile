# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY src/ ./src/
COPY test_run.py run_analysis.py ./
COPY test_config.example.json ./test_config.json
COPY README.md ./

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Create necessary directories
RUN mkdir -p reports .cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python3", "run_analysis.py"]
