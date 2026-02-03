FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/profile_pics uploads/resumes uploads/certificates uploads/qr_codes flask_session fonts

# Expose port
EXPOSE $PORT

# Start command
CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
