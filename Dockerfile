# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to ensure output is not buffered
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set up the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Expose the FastAPI default port
EXPOSE 8000

# Start the FastAPI app
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--threads", "4", "-b", "0.0.0.0:8000", "app.main:app"]
