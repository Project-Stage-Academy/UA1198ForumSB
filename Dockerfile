FROM python:3.11-slim

ARG DJANGO_ENV

# Install system dependencies and create a new user
RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    libpq-dev \
  && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  && useradd -m appuser

# Switch to the new user and set up Poetry
USER appuser

# Set environment variables
ENV PATH="/home/appuser/.local/bin:$PATH" \
    DJANGO_ENV=${DJANGO_ENV} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
  && poetry config virtualenvs.in-project true

# Set work directory
WORKDIR /app

# Copy dependency files first for better caching
COPY --chown=appuser:appuser pyproject.toml poetry.lock /app/

# Install dependencies
RUN poetry install

# Copy project files
COPY --chown=appuser:appuser forum /app/forum

# Activate virtual environment and set PYTHONPATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# Command to run the application
CMD ["python", "forum/manage.py", "runserver", "0.0.0.0:8000"]
