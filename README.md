# FountainAI Mock Server Development Plan (Dockerized Workflow)

## Introduction

This development plan outlines a **specification-driven approach** for implementing the **FountainAI Mock Server API** as a **FastAPI** application within a fully **Dockerized** local development environment. The Mock Server simulates various FountainAI services by providing endpoints defined in the unified **OpenAPI specification**, which is generated by merging multiple service-specific OpenAPI files using the [`merge_openapi.py`](https://github.com/Contexter/FountainAI-Mock/blob/main/service/scripts/merge_openapi.py)) script.

An essential component of this plan is the **FountainAI-OpenAPI-Parser**, which is factored out into its own project and treated as a dependency. The Mock Server development depends on the functional output of this parser project, which is responsible for **parsing the unified OpenAPI specification and providing structured data** that can be used by the main project's scripts to generate necessary components like Pydantic models and API routes.

**FountainAI-OpenAPI-Parser GitHub Repository:** [https://github.com/Contexter/FountainAI-OpenAPI-Parser](https://github.com/Contexter/FountainAI-OpenAPI-Parser)

---

## Project Organization and Script Management

To maintain a consistent and organized **project structure**, the repository follows a standardized **folder layout** with a clear **root directory** and explicitly defined **paths**. The root directory of the project is `/service`.

### Project Structure

```
/service
├── README.md
├── openapi/                             # Directory containing individual OpenAPI files
│   ├── Action-Service.yml
│   ├── Character-Service.yml
│   ├── ...                              # Other service-specific OpenAPI files
│   └── merged_openapi.yml               # Unified OpenAPI specification (generated)
├── merge_openapi.py                     # Script to merge OpenAPI files
├── run_setup.sh                         # Shell script to automate Docker build and setup
├── scripts/
│   ├── create_directory_structure.py    # Script to create project directories and initial files
│   ├── generate_dockerfile.py           # Script to generate the Dockerfile (after main.py is created)
│   ├── generate_schemas.py              # Script to generate Pydantic schemas (uses parser output)
│   ├── generate_api_routes.py           # Script to create FastAPI route files (uses parser output)
│   ├── setup_mock_server.py             # Master script to orchestrate setup by running all other scripts
│   └── ...                              # Placeholder for additional scripts
└── app/
    ├── api/
    │   └── routes/                      # FastAPI route files
    ├── schemas/                         # Pydantic schemas for request and response validation
    ├── main.py                          # FastAPI main application file (created by create_directory_structure.py)
    └── ...                              # Placeholder for additional application modules
```

---

## Implementation Using Modular Scripts

### Overview

The development workflow utilizes **modular Python scripts** placed within the `/service/scripts/` directory. Each script performs a specific task, contributing to the overall setup of the Mock Server. The `setup_mock_server.py` script orchestrates the execution of these scripts in the correct order.

The **FountainAI-OpenAPI-Parser** is a separate project and is treated as a dependency. It is responsible for parsing the unified OpenAPI specification and providing structured data. The scripts in the main project use this data to generate Pydantic models and API routes.

Below is a detailed description of each script, including its purpose and the prompt that defines its functionality.

### Dependencies

- **FountainAI-OpenAPI-Parser Project:** Must be developed and functional before running the main project's setup scripts.
- The FountainAI-OpenAPI-Parser is assumed to be available as an installable package (e.g., via `pip`).
- **GitHub Repository for Parser:** [https://github.com/Contexter/FountainAI-OpenAPI-Parser](https://github.com/Contexter/FountainAI-OpenAPI-Parser)

---

## Detailed Script Descriptions

### 1. `merge_openapi.py`

**Description:**

This script merges multiple service-specific OpenAPI YAML files located in `/service/openapi/` into a single unified OpenAPI specification (`merged_openapi.yml`). The merged specification serves as the source of truth for the Mock Server.

**Prompt:**

> Use the `merge_openapi.py` script to merge individual OpenAPI YAML files in the `/service/openapi/` directory into a single `merged_openapi.yml` file. Ensure the merged specification is validated and serves as the definitive OpenAPI document for the Mock Server.

### 2. `create_directory_structure.py`

**Description:**

This script creates the necessary **directories** and **initial files** for the Mock Server relative to the `/service` root directory, including the minimal `main.py`. This ensures that a minimal but functional **FastAPI application** is set up before the Docker image is built.

**Comprehensive Prompt:**

> Generate a script named `create_directory_structure.py` that performs the following tasks relative to the `/service` root directory:
>
> - **Create Directories:**
>   - `/service/app/`
>   - `/service/app/api/routes/`
>   - `/service/app/schemas/`
> - **Create Initial Files:**
>   - `__init__.py` files in each new directory to make them Python packages.
> - **Create a Minimal `main.py`:**
>   - Generate `/service/app/main.py` containing:
>     - Import of `FastAPI` from `fastapi`.
>     - Creation of a `FastAPI` app instance.
>     - A root endpoint (`/`) defined using `@app.get("/")` that returns a simple JSON response, e.g., `{"message": "FountainAI Mock Server is running."}`
>     - If necessary, include code to import routers from the `api/routes` directory (can be commented out initially).

**Purpose:**

By integrating the creation of `main.py` into `create_directory_structure.py`, we ensure that the minimal FastAPI application is ready before building the Docker image. This allows the Docker container to run the application immediately after the build.

### 3. `generate_dockerfile.py`

**Description:**

This script generates a `Dockerfile` in the `/service` root directory, setting up the **Docker environment** with the necessary configurations for the **FastAPI application**. Since `main.py` is now created before this script runs, the Docker image will include a runnable FastAPI app after the build.

**Prompt:**

> Generate a script named `generate_dockerfile.py` that creates a `Dockerfile` in the `/service` root directory. The Dockerfile should:
>
> - Use an official Python base image (e.g., `python:3.11-slim`).
> - Set the working directory to `/service`.
> - Install required system packages.
> - Copy the application code, including `main.py`, scripts, and `merged_openapi.yml` into the container.
> - Install Python dependencies using `pip`, including the **FountainAI-OpenAPI-Parser** package.
> - Expose the necessary port (`8000`).
> - Set environment variables as needed.
> - Specify the command to run the **FastAPI application** using **Uvicorn**.

### 4. `generate_schemas.py`

**Description:**

This script generates **Pydantic models** in `/service/app/schemas/` based on the parsed data from the unified **OpenAPI specification**. It uses the **FountainAI-OpenAPI-Parser** to parse the specification and provides structured data, which is then used to generate the models.

**Prompt:**

> Generate a script named `generate_schemas.py` that:
>
> - Uses the **FountainAI-OpenAPI-Parser** to parse `/service/openapi/merged_openapi.yml`.
> - Extracts the schema definitions from the parsed data.
> - Generates **Pydantic models** in `/service/app/schemas/` corresponding to the schemas defined in the specification.
> - Ensures that the Pydantic models match exactly with field types and validations specified in the OpenAPI schemas.

### 5. `generate_api_routes.py`

**Description:**

This script creates **FastAPI route files** in `/service/app/api/routes/` based on the parsed data from the unified **OpenAPI specification**, including **route decorators**. It uses the **FountainAI-OpenAPI-Parser** to obtain structured data, which is then used to generate the route files.

**Prompt:**

> Generate a script named `generate_api_routes.py` that:
>
> - Uses the **FountainAI-OpenAPI-Parser** to parse `/service/openapi/merged_openapi.yml`.
> - Extracts endpoint information such as paths, methods, parameters, and responses.
> - Creates **route files** in `/service/app/api/routes/` with **FastAPI endpoints** that match the specification.
> - Ensures that the generated routes include correct path parameters, query parameters, and response models as defined in the OpenAPI specification.

### 6. `setup_mock_server.py`

**Description:**

This master script executes all the previously generated Python scripts in the correct order to set up the **Mock Server project**.

**Prompt:**

> Generate a script named `setup_mock_server.py` that executes the following scripts in order:
>
> 1. `generate_schemas.py`
> 2. `generate_api_routes.py`
>
> Ensure that dependencies, including the **FountainAI-OpenAPI-Parser**, are handled correctly.

### 7. `run_setup.sh`

**Description:**

This **shell script** automates the **Docker build** and **setup process** by building and running the Docker container and executing the setup Python script within the container.

**Prompt:**

> Generate a shell script named `run_setup.sh` that:
>
> - Builds the Docker image using `docker build -t fountainai-mock .`.
> - Runs the Docker container with appropriate port mapping and volume mounting.
> - Executes `python scripts/setup_mock_server.py` inside the container.
> - Includes echo statements to inform the user of each step.

---

## Execution Order

1. **`merge_openapi.py`** (Manually executed to generate `merged_openapi.yml`)
2. **`create_directory_structure.py`** (Creates directories and `main.py`)
3. **`generate_dockerfile.py`** (Dockerfile includes `main.py`)
4. **`setup_mock_server.py`** (Runs `generate_schemas.py` and `generate_api_routes.py`)
5. **`run_setup.sh`**

This order ensures that the minimal `main.py` is created before building the Docker image, allowing for a runnable FastAPI app immediately after the Docker build.

---

## Workflow Details

### Step 1: Merge OpenAPI Specifications

Before setting up the Mock Server, merge the individual OpenAPI files into a unified specification using `merge_openapi.py`.

**Command:**

```bash
python merge_openapi.py merge-openapi --input-directory "./openapi" --output-file "./openapi/merged_openapi.yml" --validate --verbose
```

### Step 2: Create Directory Structure and Minimal Main

Run `create_directory_structure.py` to set up the project directories and create the minimal `main.py`.

```bash
python scripts/create_directory_structure.py
```

This script will:

- Create necessary directories.
- Generate a minimal `main.py` with a basic FastAPI application and a root endpoint (`/`).

### Step 3: Generate the Dockerfile

Run `generate_dockerfile.py` to create the `Dockerfile`. Since `main.py` now exists, the Docker image will build a runnable FastAPI app.

```bash
python scripts/generate_dockerfile.py
```

### Step 4: Setup Mock Server

Run `setup_mock_server.py` to execute `generate_schemas.py` and `generate_api_routes.py`, which use the **FountainAI-OpenAPI-Parser** to parse the specification and generate components.

```bash
python scripts/setup_mock_server.py
```

### Step 5: Build and Run the Docker Container

Use `run_setup.sh` to automate the Docker build and setup process.

```bash
chmod +x run_setup.sh
./run_setup.sh
```

---

## Notes on Workflow

### Prerequisites

- **Python 3.9+** must be installed on your local machine.
- **Docker** must be installed on your local machine.
- **FountainAI-OpenAPI-Parser** must be available as a Python package (installed via `pip`).
- **GitHub Repository for Parser:** [https://github.com/Contexter/FountainAI-OpenAPI-Parser](https://github.com/Contexter/FountainAI-OpenAPI-Parser)

### Clone the Repository

Clone the repository and navigate to the `/service` directory:

```bash
git clone https://github.com/Contexter/FountainAI-Mock.git
cd FountainAI-Mock/service
```

### Merge OpenAPI Specifications

Ensure that you have all individual OpenAPI files in the `/service/openapi/` directory.

Run the `merge_openapi.py` script as described in **Step 1** to generate the unified OpenAPI specification.

### Install FountainAI-OpenAPI-Parser Dependency

Ensure the **FountainAI-OpenAPI-Parser** is installed in your environment:

```bash
pip install fountainai-openapi-parser
```

### Develop and Test

With the **Docker container** running, you can engage in development and testing activities. **Editing code locally** will reflect changes inside the container due to **volume mounting**.

- **Access the application** by visiting [http://localhost:8000](http://localhost:8000).
- **API Documentation**: The interactive API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Stop the Docker Container

When development is complete, you can stop the Docker container with:

```bash
docker stop fountainai-mock-container
```

---

## Script Execution Details

### `create_directory_structure.py`

- Creates necessary directories.
- Generates `__init__.py` files.
- Generates a minimal `main.py` with a basic FastAPI app and root endpoint.

### `generate_dockerfile.py`

- Generates a `Dockerfile` that includes the `main.py`.
- Sets up the Docker environment for the FastAPI application.

### `generate_schemas.py`

- Uses the **FountainAI-OpenAPI-Parser** to parse the unified specification.
- Extracts schema definitions from the parser's output.
- Generates Pydantic models based on the extracted schemas.

### `generate_api_routes.py`

- Uses the **FountainAI-OpenAPI-Parser** to parse the unified specification.
- Extracts endpoint information from the parser's output.
- Generates FastAPI route files based on the extracted data.

### `setup_mock_server.py`

- Executes `generate_schemas.py` and `generate_api_routes.py` in the correct order.
- Ensures the **FountainAI-OpenAPI-Parser** is utilized properly.

---

## Summary

This development plan ensures that the minimal `main.py` is created within the `create_directory_structure.py` script, and that the **FountainAI-OpenAPI-Parser** is correctly utilized to parse the unified OpenAPI specification and provide structured data. The scripts in the main project then use this data to generate necessary components like Pydantic models and API routes.

**Key Features:**

- **Accurate Role of FountainAI-OpenAPI-Parser**: The parser is responsible for parsing and providing structured data, not generating components.
- **Early Creation of `main.py`**: Guarantees that the Docker image includes a runnable FastAPI application.
- **Unified OpenAPI Specification**: Serves as the source of truth for generating schemas and routes.
- **Modular Script-Based Setup**: Allows for easy customization and maintenance.
- **Dockerized Environment**: Provides a consistent development environment, simplifying dependency management and deployment.

---

## Next Steps

1. **Ensure the FountainAI-OpenAPI-Parser is Available:**

   - Install the parser from its GitHub repository or package manager.
   - **GitHub Repository:** [https://github.com/Contexter/FountainAI-OpenAPI-Parser](https://github.com/Contexter/FountainAI-OpenAPI-Parser)
   - Verify that the parser is installed and functional in your environment.

2. **Generate the Unified OpenAPI Specification:**

   - Use `merge_openapi.py` to merge individual OpenAPI files.

3. **Run the Setup Scripts:**

   - Execute `create_directory_structure.py` to set up directories and create `main.py`.
   - Run `generate_dockerfile.py` to create the Dockerfile.
   - Use `setup_mock_server.py` to generate schemas and API routes using the parser's output.

4. **Build and Run the Docker Image:**

   - Use `run_setup.sh` to build the Docker image and run the container.

5. **Start Developing:**

   - Begin developing and testing your endpoints as defined in the unified OpenAPI specification.

6. **Iterate and Refine:**

   - Use the modular nature of the setup to add additional features or make adjustments as needed.

---

**Note:** Ensure that all paths and commands are correctly adjusted to match your specific environment and directory structure. The provided commands assume you are running them from the `/service` directory of your project within the [FountainAI-Mock repository](https://github.com/Contexter/FountainAI-Mock).

---

## Appendix: Discussion on Using `merge_openapi.py` as an OpenAPI Parser

### Question:

*Is the `merge_openapi.py` script relevant in one of the development steps of this plan actually an OpenAPI parser too? If so, could we reuse this parser for our purpose at hand?*

### Answer:

Yes, the `merge_openapi.py` script does perform some parsing of OpenAPI files in the sense that it reads multiple OpenAPI specification files and merges them into a single unified specification. However, its primary purpose is to **merge** OpenAPI files, not to **parse** them in a way that extracts detailed structured data suitable for generating code components like Pydantic models or FastAPI routes.

#### Is `merge_openapi.py` an OpenAPI Parser?

- **Limited Parsing Functionality:** The script reads OpenAPI YAML files and combines their contents, handling paths, components, and tags.
- **Merging vs. Parsing:** While it processes the files to merge them, it doesn't deeply parse the OpenAPI specifications to extract the detailed structure required for code generation.
- **No Detailed Schema Extraction:** It doesn't provide functionality to extract schemas, operations, parameters, and other components in a way that you can programmatically use to generate code.

#### Can We Reuse `merge_openapi.py` for Our Purpose?

- **Not Suitable for Code Generation:** The current functionality of `merge_openapi.py` isn't sufficient for generating Pydantic models or API routes because it lacks the necessary parsing capabilities.
- **Extension Would Be Complex:** Modifying `merge_openapi.py` to add full OpenAPI parsing capabilities would require significant effort and essentially involve creating a new parser.
- **Risk of Reinventing the Wheel:** There are existing libraries and tools designed specifically for parsing OpenAPI specifications, which are robust and well-tested.

#### Recommendation

**Use the Dedicated FountainAI-OpenAPI-Parser:**

- **Purpose-Built:** The [FountainAI-OpenAPI-Parser](https://github.com/Contexter/FountainAI-OpenAPI-Parser) is specifically designed to parse OpenAPI specifications and provide structured data for code generation.
- **Modularity:** Keeping the parser as a separate project promotes modularity, allowing independent development and maintenance.
- **Reliability:** A dedicated parser is more likely to handle the complexities and edge cases of the OpenAPI specification.
- **Community Support:** Using standard parsing libraries or dedicated projects allows you to leverage community support and updates.

#### Advantages of Using FountainAI-OpenAPI-Parser

- **Structured Data Extraction:** It can parse the unified OpenAPI specification and extract all necessary components like schemas, paths, parameters, responses, and more.
- **Ease of Integration:** Designed to be integrated into projects like your Mock Server setup, providing the required data for your scripts.
- **Maintainability:** Updates or bug fixes in the parser can be managed separately without affecting your main project.

#### Conclusion

While `merge_openapi.py` does perform some parsing in the process of merging OpenAPI files, it isn't equipped to serve as a full OpenAPI parser suitable for your needs in generating Pydantic models and API routes. Using the **FountainAI-OpenAPI-Parser** is the recommended approach, as it is specifically designed for parsing OpenAPI specifications and can provide the structured data required for your code generation scripts.

---

### Next Steps:

1. **Use `merge_openapi.py` for Merging Only:**

   - Continue using `merge_openapi.py` to merge individual OpenAPI files into `merged_openapi.yml`.

2. **Install FountainAI-OpenAPI-Parser:**

   - Install the parser in your environment:

     ```bash
     pip install fountainai-openapi-parser
     ```

   - **GitHub Repository:** [https://github.com/Contexter/FountainAI-OpenAPI-Parser](https://github.com/Contexter/FountainAI-OpenAPI-Parser)

3. **Update Your Scripts:**

   - Ensure that `generate_schemas.py` and `generate_api_routes.py` use the **FountainAI-OpenAPI-Parser** to parse `merged_openapi.yml` and generate the necessary components.

4. **Proceed with the Development Plan:**

   - Follow the execution order and steps outlined in your development plan, using the dedicated parser for parsing tasks.

---

### Additional Considerations:

- **Avoid Duplication of Effort:** Using the dedicated parser prevents the need to reinvent parsing functionality, saving development time and resources.
- **Leverage Expertise:** Dedicated parsers are often built and maintained by teams familiar with the intricacies of the OpenAPI specification.
- **Future Proofing:** By using a standard parser, you ensure better compatibility with future versions of the OpenAPI specification or your own APIs.

---

### Final Thoughts

The decision to use the **FountainAI-OpenAPI-Parser** ensures that the Mock Server development is built on a robust and purpose-designed foundation. This approach promotes better maintainability, scalability, and alignment with best practices in software development.

