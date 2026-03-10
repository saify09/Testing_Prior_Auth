FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for some packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Setup non-root user (good practice for HF)
RUN useradd -m -u 1000 user
RUN chown -R user /app
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONPATH=/app

# EXPOSE HF default port
EXPOSE 7860

# Make script executable
RUN chmod +x start.sh

CMD ["./start.sh"]
