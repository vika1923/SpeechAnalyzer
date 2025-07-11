FROM ubuntu:24.04

# Set non-interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and add deadsnakes PPA for Python 3.11
RUN apt-get update && apt-get install -y \
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    curl \
    libboost-all-dev \
    libopencv-dev \
    libtbb-dev \
    libopenblas-dev \
    liblapack-dev \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libjpeg-dev \
    libpng-dev \
    libgtk2.0-dev \
    pkg-config \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Upgrade pip and fix setuptools compatibility issue
RUN apt upgrade python3-pip && \
    pip install setuptools==58.2.0

WORKDIR /opt

# Build dlib
RUN git clone https://github.com/davisking/dlib.git && \
    cd dlib && \
    git checkout v19.24.2 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --config Release && \
    make install && \
    ldconfig && \
    cd /opt && rm -rf dlib

# Clone and build OpenFace
RUN git clone https://github.com/TadasBaltrusaitis/OpenFace.git && \
    cd OpenFace && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE .. && \
    make -j$(nproc) || exit 1 && \
    cd /opt && rm -rf OpenFace/build

# Download OpenFace models
WORKDIR /opt/OpenFace
RUN bash download_models.sh

# Set up app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt && \
    pip install opencv-python-headless fastapi[all] uvicorn nltk

# Download NLTK data
RUN python -c "import nltk; nltk.download('universal_tagset')" && \
    python -c "import nltk; nltk.download('punkt_tab')" && \
    python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"

RUN python -c "from deepmultilingualpunctuation import PunctuationModel; PunctuationModel()"
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('large-v3', device='cpu', compute_type='int8')"

# Copy app code
COPY . .

# Create directories for video processing and shared data
RUN mkdir -p /shared_data/requests /shared_data/uploads /shared_data/output && \
    mkdir -p /app/videos/openface

# Add OpenFace to PATH
ENV PATH="/opt/OpenFace/build/bin:${PATH}"

EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
