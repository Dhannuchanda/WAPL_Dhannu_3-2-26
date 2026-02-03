FROM python:3.11-slim

WORKDIR /app

# Ensure Python output is sent straight to terminal (e.g. your container logs)
# without being first buffered and that you can see the output of your application (e.g. django logs) in real time.
ENV PYTHONUNBUFFERED=1


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

# Default port (Railway overrides with PORT env var)
ENV PORT=8080
EXPOSE 8080

# Start command using shell to expand $PORT
CMD ["sh", "-c", "gunicorn app:app -w 2 -b 0.0.0.0:$PORT --timeout 120 --log-level debug --access-logfile - --error-logfile -"]
