# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure stdout and stderr are sent straight to terminal without buffering
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (optional, but good practice)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
