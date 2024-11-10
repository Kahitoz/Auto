# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to ensure output is not buffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set up the working directory
WORKDIR /app

# Install system dependencies for performance
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Ensure Gunicorn is installed globally
RUN pip install gunicorn

# Copy the FastAPI app code into the container
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Run the FastAPI app using gunicorn and uvicorn
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--threads", "4", "-b", "0.0.0.0:8000", "app.main:app"]
