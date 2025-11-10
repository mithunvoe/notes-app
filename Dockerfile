# syntax=docker/dockerfile:1.4
FROM python:3.11-slim

# Install system dependencies
# Use BuildKit cache mount to cache apt packages between builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    build-essential \
    tesseract-ocr \
    poppler-utils \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
# Use BuildKit cache mount to cache pip packages between builds
COPY requirements.txt .

# Configure pip for better reliability with large packages
RUN pip install --upgrade pip setuptools wheel

# Install dependencies with increased timeout for large packages like PyTorch
# Remove --no-cache-dir to use BuildKit cache mount effectively
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --default-timeout=1000 --retries 10 -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /data/chroma

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
