import os

def generate_dockerfile():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    service_dir = os.path.join(base_dir, 'service')

    dockerfile_content = """
    # Stage 1: Build stage
    FROM python:3.11-slim AS builder

    # Set the working directory in the container
    WORKDIR /service

    # Install required system packages
    RUN apt-get update && \
        apt-get install -y --no-install-recommends gcc make build-essential && \
        rm -rf /var/lib/apt/lists/*

    # Copy only the requirements file to leverage Docker cache
    COPY /service/openapi/requirements.txt /service/requirements.txt

    # Create a virtual environment and install Python dependencies
    RUN python -m venv /service/venv && \
        /service/venv/bin/pip install --no-cache-dir -r /service/requirements.txt

    # Copy the rest of the application code
    COPY . /service

    # Stage 2: Runtime stage
    FROM python:3.11-slim

    # Set the working directory in the container
    WORKDIR /service

    # Copy from the builder stage
    COPY --from=builder /service /service

    # Set environment variables
    ENV PATH="/service/venv/bin:$PATH"
    ENV PYTHONUNBUFFERED=1

    # Expose the FastAPI port
    EXPOSE 8000

    # Run the FastAPI application using Uvicorn
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
    """

    # Write the Dockerfile to the /service directory
    dockerfile_path = os.path.join(service_dir, 'Dockerfile')
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(dockerfile_content)

    # Create a .dockerignore file to exclude unnecessary files
    dockerignore_content = """
    **/__pycache__
    **/*.pyc
    .git
    .env
    .vscode
    .DS_Store
    **/*.log
    **/.pytest_cache
    node_modules
    """
    dockerignore_path = os.path.join(service_dir, '.dockerignore')
    with open(dockerignore_path, 'w') as dockerignore:
        dockerignore.write(dockerignore_content)

    print(f"Dockerfile generated at: {dockerfile_path}")
    print(f".dockerignore generated at: {dockerignore_path}")

if __name__ == "__main__":
    generate_dockerfile()

