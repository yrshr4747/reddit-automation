FROM python:3.11-slim

# Set working directory
WORKDIR /app

# 1. Install EVERY specific library Chromium needs manually
# This removes the need for 'playwright install-deps' which is failing.
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
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxss1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Install ONLY the Chromium binary (No deps command here)
RUN playwright install chromium

# 4. Copy code and setup
COPY . .
RUN mkdir -p sessions logs

# 5. Production Settings
EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--threads", "1", "--timeout", "120", "app:app"]
