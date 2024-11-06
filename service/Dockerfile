# Stage 1: Build stage
FROM python:3.11-slim AS builder

# Set the working directory in the container
WORKDIR /service

# Install required system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc make build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file
COPY openapi/requirements.txt /service/requirements.txt

# Create a virtual environment and install Python dependencies
RUN python -m venv /service/venv && \
    /service/venv/bin/pip install --upgrade pip && \
    /service/venv/bin/pip install --no-cache-dir -r /service/requirements.txt

# Copy the rest of the application code
COPY . /service

# Stage 2: Runtime stage
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /service

# Install Uvicorn and other necessary runtime dependencies
RUN pip install uvicorn

# Copy from the builder stage
COPY --from=builder /service /service

# Set environment variables
ENV PATH="/service/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
