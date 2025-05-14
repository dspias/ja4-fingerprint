FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  tshark \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  # This will now install correct versions

COPY src/ /app/

EXPOSE 5000
CMD ["python", "run.py"]