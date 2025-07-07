FROM ubuntu:24.04

# Set non-interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and add deadsnakes PPA for Python 3.11
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
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
    libsdl2-dev \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    && add-apt-repository ppa:deadsnakes/ppa -y \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

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
    make -j$(nproc) && \
    cd /opt && rm -rf OpenFace/build

# Download OpenFace models
WORKDIR /opt/OpenFace
RUN bash download_models.sh

# Set up app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN python3.11 -m pip install --upgrade pip setuptools>=70.0.0 wheel --no-cache-dir && \
    python3.11 -m pip install -r requirements.txt --no-cache-dir && \
    python3.11 -m pip install opencv-python-headless==4.10.0.84 fastapi==0.115.0 "uvicorn[standard]==0.30.6" moviepy==1.0.3 nltk==3.9.1 --no-cache-dir

# Download NLTK data
RUN python3.11 -c "import nltk; nltk.download('universal_tagset')" && \
    python3.11 -c "import nltk; nltk.download('punkt')" && \
    python3.11 -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"

# Copy app code
COPY . .

# Create directories for video processing and shared data
RUN mkdir -p /shared_data/requests /shared_data/uploads /shared_data/output && \
    mkdir -p /app/videos/openface

# Add OpenFace to PATH
ENV PATH="/opt/OpenFace/build/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
