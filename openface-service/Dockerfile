FROM algebr/openface:latest

# Install Python for the processing service
RUN apt-get update && apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Copy the processing script
COPY process_service.py /app/process_service.py

WORKDIR /app

CMD ["python3", "process_service.py"]
