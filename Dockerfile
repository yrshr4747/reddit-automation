FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# We added libxshmfence1 and libxtst6 which are often missing in slim images
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libxshmfence1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Chromium WITH dependencies
# The --with-deps flag is the "magic" that fixes the error in your screenshot
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy application source code
COPY . .

# Create directories for sessions and logs
RUN mkdir -p sessions logs

# Render Free Tier default port
EXPOSE 10000

# SINGLE WORKER ONLY to stay under 512MB RAM
# Added threads=1 to keep memory usage predictable
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--threads", "1", "--timeout", "120", "app:app"]
