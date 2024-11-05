# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set the entry point for the Docker container
ENTRYPOINT ["python", "merge_openapi.py"]

# Set the default command for the Docker container
CMD ["merge-openapi"]
