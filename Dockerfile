FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.awfdrs.main:app", "--host", "0.0.0.0", "--port", "8000"]
