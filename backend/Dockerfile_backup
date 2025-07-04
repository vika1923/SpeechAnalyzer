FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for your Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install "fastapi[all]" uvicorn moviepy

# Download NLTK data
RUN python -c "import nltk; nltk.download('universal_tagset')" && \
    python -c "import nltk; nltk.download('punkt_tab')"

# Copy application code
COPY . .

# Create directories for shared data
RUN mkdir -p /shared_data/requests /shared_data/uploads /shared_data/output

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
