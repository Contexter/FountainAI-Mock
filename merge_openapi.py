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
