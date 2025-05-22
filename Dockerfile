FROM python:3.11-slim

# Set environment variables to reduce prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install tshark and tcpdump with dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  tshark \
  tcpdump \
  libcap2-bin \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Set capture capabilities for dumpcap (used by tshark)
# NOTE: This only works if the container is started with --cap-add
RUN setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap && \
  chmod +x /usr/bin/dumpcap && \
  chgrp root /usr/bin/dumpcap && chmod g+rx /usr/bin/dumpcap

# Create working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ /app/

# Expose port
EXPOSE 5000

# Default command to run app
CMD ["python", "run.py"]
