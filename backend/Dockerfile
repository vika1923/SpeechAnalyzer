FROM ubuntu:23.04

# Set non-interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    unzip \
    pkg-config \
    libboost-all-dev \
    libopencv-dev \
    libtbb-dev \
    libopenblas-dev \
    libx11-dev \
    ffmpeg \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    libgtk2.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libx11-dev \
    libjpeg-dev \
    libpng-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

WORKDIR /opt

# Build dlib
RUN git clone https://github.com/davisking/dlib.git && \
    cd dlib && \
    mkdir build && \
    cd build && \
    cmake .. && \
    cmake --build . --config Release && \
    make install && \
    ldconfig

# Clone and build OpenFace
RUN git clone https://github.com/TadasBaltrusaitis/OpenFace.git && \
    cd OpenFace && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE .. && \
    make -j$(nproc)

# Download OpenFace models
WORKDIR /opt/OpenFace
RUN bash download_models.sh

# Set up app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install "fastapi[all]" uvicorn moviepy nltk

# Download NLTK data
RUN python -c "import nltk; nltk.download('universal_tagset')" && \
    python -c "import nltk; nltk.download('punkt')" && \
    python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"

# Copy app code
COPY . .

# Create directories for video processing and shared data
RUN mkdir -p /shared_data/requests /shared_data/uploads /shared_data/output && \
    mkdir -p /app/videos/openface

# Add OpenFace to PATH
ENV PATH="/opt/OpenFace/build/bin:${PATH}"

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
