# Comprehensive Documentation and Tutorial for `merge_openapi.py`

## Overview

The `merge_openapi.py` script is a Python-based command-line interface (CLI) that uses Typer to merge multiple OpenAPI YAML files into a single unified OpenAPI document. This unified specification represents a comprehensive mock server specification for testing purposes, simulating multiple services within a single API.

### Features:
- Load multiple OpenAPI YAML files.
- Merge them into a single unified OpenAPI document.
- Deduplicate and prefix paths to prevent conflicts.
- Provide detailed validation and output.
- Utilize a Dockerized environment to ensure consistency.

### Requirements:
- Python 3.9 or newer.
- Required Python packages: PyYAML, Typer, openapi-spec-validator.
- Docker (optional but recommended for a clean environment).

## Project Structure
The basic project structure for `merge_openapi.py` is as follows:

```
.
├── Dockerfile
├── requirements.txt
├── merge_openapi.py
├── Action-Service.yml
├── Story-Factory-Service.yml
├── Core-Script-Managment-Service.yml
└── ...
```

- **Dockerfile**: Used to create a Docker image that provides a clean Python environment for running the script.
- **requirements.txt**: Lists the Python dependencies required by the script.
- **merge_openapi.py**: The main Python script to merge OpenAPI files.
- **YAML Files**: Multiple OpenAPI YAML files that need to be merged.

## The Script: `merge_openapi.py`

```python
# merge_openapi.py

import os
import yaml
import typer
from openapi_spec_validator import validate_spec
from pathlib import Path
from typing import Dict

# Initialize a Typer app for command-line interface
app = typer.Typer()

# Function to load OpenAPI files
def load_openapi_files(input_directory: str) -> Dict[str, dict]:
    """
    Load all OpenAPI files from the input directory.
    Supports both `.yml` and `.yaml` files.
    """
    openapi_files = {}
    for file in list(Path(input_directory).glob('*.yml')) + list(Path(input_directory).glob('*.yaml')):
        typer.secho(f"Loading file: {file}", fg=typer.colors.CYAN)
        with open(file, 'r') as f:
            openapi_files[file.stem] = yaml.safe_load(f)
    typer.secho(f"Loaded {len(openapi_files)} OpenAPI files.", fg=typer.colors.GREEN)
    return openapi_files

# Function to merge multiple OpenAPI specifications into a single unified specification
def merge_openapi_files(openapi_files: Dict[str, dict]) -> dict:
    merged_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "Mock Server API",
            "version": "1.0.0",
            "description": "Unified Mock Server API specification",
        },
        "servers": [{
            "url": "http://localhost:8000"
        }],
        "tags": [],
        "paths": {},
        "components": {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "requestBodies": {},
        }
    }

    for service_name, spec in openapi_files.items():
        typer.secho(f"Merging paths for service: {service_name}", fg=typer.colors.CYAN)
        merge_paths(service_name, spec, merged_spec)
        typer.secho(f"Merging components for service: {service_name}", fg=typer.colors.CYAN)
        merge_components(service_name, spec, merged_spec)
        typer.secho(f"Merging tags for service: {service_name}", fg=typer.colors.CYAN)
        merge_tags(service_name, spec, merged_spec)

    typer.secho("Successfully merged all OpenAPI files.", fg=typer.colors.GREEN)
    return merged_spec

# Function to merge paths into the unified specification
def merge_paths(service_name: str, spec: dict, merged_spec: dict) -> None:
    for path, path_item in spec.get("paths", {}).items():
        if path in merged_spec["paths"]:
            typer.secho(f"Warning: Duplicate un-prefixed path detected for {path}. Skipping.", fg=typer.colors.YELLOW)
            continue
        prefixed_path = f"/{service_name}{path}"
        if prefixed_path not in merged_spec["paths"]:
            merged_spec["paths"][prefixed_path] = path_item
            typer.secho(f"Added path: {prefixed_path}", fg=typer.colors.GREEN)
        else:
            typer.secho(f"Warning: Duplicate path detected for {prefixed_path}. Skipping.", fg=typer.colors.YELLOW)

# Function to merge components into the unified specification
def merge_components(service_name: str, spec: dict, merged_spec: dict) -> None:
    for component_type, components in spec.get("components", {}).items():
        if component_type not in merged_spec["components"]:
            continue
        for name, component in components.items():
            prefixed_name = f"{service_name}_{name}"
            existing_component = merged_spec["components"][component_type].get(name)
            if existing_component is None:
                merged_spec["components"][component_type][name] = component
                typer.secho(f"Added component: {component_type}/{name}", fg=typer.colors.GREEN)
            elif existing_component != component:
                if existing_component == component:
                    typer.secho(f"Identical component already exists: {component_type}/{name}. Skipping.", fg=typer.colors.GREEN)
                else:
                    merged_spec["components"][component_type][prefixed_name] = component
                    typer.secho(f"Conflict detected. Added component with prefixed name: {component_type}/{prefixed_name}", fg=typer.colors.YELLOW)

# Function to merge tags into the unified specification
def merge_tags(service_name: str, spec: dict, merged_spec: dict) -> None:
    if "tags" in spec:
        for tag in spec["tags"]:
            if tag not in merged_spec["tags"]:
                merged_spec["tags"].append(tag)
                typer.secho(f"Added tag: {tag}", fg=typer.colors.GREEN)

# Function to validate the merged OpenAPI specification
def validate_openapi(openapi_spec: dict):
    try:
        typer.secho("Validating OpenAPI specification...", fg=typer.colors.CYAN)
        validate_spec(openapi_spec)
        typer.secho("Validation successful.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Validation Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=3)

# Function to write the merged OpenAPI specification to a file
def write_output(output_file: str, openapi_spec: dict):
    try:
        typer.secho(f"Writing output to file: {output_file}", fg=typer.colors.CYAN)
        with open(output_file, 'w') as f:
            yaml.safe_dump(openapi_spec, f, sort_keys=False, default_flow_style=False)
        typer.secho(f"Successfully wrote output to {output_file}", fg=typer.colors.GREEN)
    except FileNotFoundError:
        typer.secho(f"Error: The directory for the output file '{output_file}' does not exist.", fg=typer.colors.RED)
        raise typer.Exit(code=4)
    except PermissionError:
        typer.secho(f"Error: Permission denied when writing to the output file '{output_file}'.", fg=typer.colors.RED)
        raise typer.Exit(code=5)
    except Exception as e:
        typer.secho(f"Unexpected error when writing to the output file: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=6)

# Typer command to run the script
@app.command()
def merge_openapi(
    input_directory: str = typer.Option(..., "--input-directory", help="Path to the directory containing OpenAPI files."),
    output_file: str = typer.Option("mock_server_openapi.yml", "--output-file", help="Path to the output YAML file for the unified specification."),
    validate_spec: bool = typer.Option(True, "--validate/--no-validate", help="Enable or disable validation of the final OpenAPI document."),
    verbose: bool = typer.Option(False, "--verbose", help="Verbose output, providing step-by-step details of the merging process."),
):
    if verbose:
        typer.secho("Loading OpenAPI files...", fg=typer.colors.GREEN)
    openapi_files = load_openapi_files(input_directory)

    if verbose:
        typer.secho(f"Merging {len(openapi_files)} OpenAPI files...", fg=typer.colors.GREEN)
    merged_spec = merge_openapi_files(openapi_files)

    if validate_spec:
        if verbose:
            typer.secho("Validating merged OpenAPI specification...", fg=typer.colors.GREEN)
        validate_openapi(merged_spec)

    if verbose:
        typer.secho(f"Writing merged OpenAPI specification to {output_file}...", fg=typer.colors.GREEN)
    write_output(output_file, merged_spec)

    if verbose:
        typer.secho("Merging process completed successfully.", fg=typer.colors.BLUE)

if __name__ == "__main__":
    app()
```

## How to Use the Script

### 1. Running Locally

If you have Python and all the dependencies installed, you can run the script directly on your local machine.

#### Step 1: Install Dependencies
Make sure you have Python 3.9+ installed. You can install the required dependencies using:

```sh
pip install -r requirements.txt
```

#### Step 2: Run the Script
Run the script using the following command:

```sh
python merge_openapi.py merge-openapi --input-directory "./path/to/openapi/files" --output-file "merged_openapi.yml" --validate --verbose
```

- **`--input-directory`**: Path to the directory containing OpenAPI files.
- **`--output-file`**: Path to save the output merged YAML file.
- **`--validate/--no-validate`**: Enable or disable validation of the final OpenAPI document.
- **`--verbose`**: Provides detailed information during the process.

### 2. Running with Docker

To ensure the script runs in a clean and consistent environment, you can use Docker to containerize it.

#### Step 1: Create the Dockerfile

Here is a basic `Dockerfile` for containerizing the script:

```dockerfile
# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set the entry point for the Docker container
ENTRYPOINT ["python", "merge_openapi.py"]

# Set the default command for the container
CMD ["merge-openapi"]
```

#### Step 2: Build the Docker Image
Navigate to the directory containing the Dockerfile and build the image using the following command:

```sh
docker build -t merge-openapi .
```

#### Step 3: Run the Docker Container

To run the script in Docker, use the following command:

```sh
docker run --rm -v "/path/to/openapi/files:/app/input" -v "/path/to/output:/app/output" merge-openapi --input-directory "/app/input" --output-file "/app/output/merged_openapi.yml" --validate --verbose
```

### Explanation of the Command:
- **`docker run --rm`**: Runs the container and removes it after completion.
- **`-v "/path/to/openapi/files:/app/input"`**: Mounts the local directory containing OpenAPI files to `/app/input` in the Docker container. This makes the input files accessible to the container.
- **`-v "/path/to/output:/app/output"`**: Mounts the local directory where the output file will be saved to `/app/output` in the Docker container. This ensures the output is accessible on your host system.
- **`merge-openapi`**: This is the Docker image name.
- **`--input-directory "/app/input"`**: Specifies the directory inside the container where the OpenAPI files are located.
- **`--output-file "/app/output/merged_openapi.yml"`**: Specifies the output location for the merged file inside the container.
- **`--validate --verbose`**: Enables validation and verbose output.

### Bind Mounts Explained

A bind mount allows you to share directories between your host system and the Docker container, ensuring files created or modified within the container are saved on your local machine.

- **Input Directory Mount (`-v "/path/to/openapi/files:/app/input"`)**: This makes the OpenAPI YAML files available to the Docker container from your local filesystem.
- **Output Directory Mount (`-v "/path/to/output:/app/output"`)**: This ensures that the output merged file, `merged_openapi.yml`, generated by the script is available on your local machine even after the Docker container exits.

## Common Issues and Troubleshooting

### 1. Missing Dependencies
If you encounter errors about missing modules (e.g., `ModuleNotFoundError`), ensure you have installed all the dependencies specified in `requirements.txt`.

### 2. File Permission Errors
If you see a `PermissionError` when writing the output, make sure you have write permissions to the output directory specified.

### 3. File Not Found
Ensure that the paths provided in the command (for input and output) are correct and that the input directory contains the necessary OpenAPI files.

### 4. Docker Volume Bind Issues
If you do not see the merged output on your local filesystem, double-check the volume mount syntax and ensure that Docker has permissions to access the specified directories.

## Summary
- The `merge_openapi.py` script is a useful CLI tool for merging multiple OpenAPI YAML files into a unified document.
- It can be run locally or using Docker for consistent results.
- Docker bind mounts are used to provide input and output directories, allowing files to be shared between the host system and the Docker container.

Using this approach, you can create a comprehensive, mockable API specification for testing and development, while ensuring consistency in the environment with Docker.

