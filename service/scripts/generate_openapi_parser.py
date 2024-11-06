import logging
import argparse
from pathlib import Path
try:
    from prance import ResolvingParser
except ImportError:
    import os
    os.system('pip install prance')
    from prance import ResolvingParser

# Set up basic logging configuration to log to file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='openapi_parser.log', filemode='w')

# Adding argument parser to enable verbosity control
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('--verbose', action='store_true', help='Enable detailed logging')
args = arg_parser.parse_args()

if args.verbose:
    # Enable detailed logging if verbose is set
    logging.getLogger().setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)
else:
    # Only log warnings and above to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

class OpenAPIParser:
    def __init__(self, openapi_path):
        """
        Initialize the OpenAPIParser with the path to the OpenAPI specification.
        :param openapi_path: Path to the OpenAPI YAML or JSON file.
        """
        logging.info(f"Initializing OpenAPIParser with path: {openapi_path}")
        self.openapi_path = openapi_path
        self.openapi_data = self.load_openapi()

    def load_openapi(self):
        """
        Load and parse the OpenAPI specification using Prance's ResolvingParser.
        :return: Parsed OpenAPI specification as a dictionary.
        """
        try:
            # Use Prance to parse and resolve the OpenAPI specification
            parser = ResolvingParser(str(self.openapi_path))
            logging.info(f"OpenAPI file loaded successfully from {self.openapi_path}")
            return parser.specification
        except Exception as e:
            logging.error(f"Failed to parse OpenAPI file: {e}")
            raise ValueError(f"Invalid OpenAPI specification: {e}")

    def get_schemas(self):
        """
        Extract schemas from the OpenAPI specification.
        :return: Dictionary of schemas defined in the OpenAPI specification.
        """
        schemas = self.openapi_data.get('components', {}).get('schemas', {})
        logging.info(f"Extracted {len(schemas)} schemas.")
        return schemas

    def get_paths(self):
        """
        Extract paths from the OpenAPI specification.
        :return: Dictionary of paths defined in the OpenAPI specification.
        """
        paths = self.openapi_data.get('paths', {})
        logging.info(f"Extracted {len(paths)} paths.")
        return paths

    def get_parameters(self):
        """
        Extract global parameters from the OpenAPI specification.
        :return: Dictionary of parameters defined in the OpenAPI specification.
        """
        parameters = self.openapi_data.get('components', {}).get('parameters', {})
        logging.info(f"Extracted {len(parameters)} parameters.")
        return parameters

    def get_responses(self):
        """
        Extract responses from the OpenAPI specification.
        :return: Dictionary of responses defined in the OpenAPI specification.
        """
        responses = self.openapi_data.get('components', {}).get('responses', {})
        logging.info(f"Extracted {len(responses)} responses.")
        return responses

    def get_request_bodies(self):
        """
        Extract request bodies from the OpenAPI specification.
        :return: Dictionary of request bodies defined in the OpenAPI specification.
        """
        request_bodies = self.openapi_data.get('components', {}).get('requestBodies', {})
        logging.info(f"Extracted {len(request_bodies)} request bodies.")
        return request_bodies

    def get_tags(self):
        """
        Extract tags from the OpenAPI specification.
        :return: List of tags defined in the OpenAPI specification.
        """
        tags = self.openapi_data.get('tags', [])
        logging.info(f"Extracted {len(tags)} tags.")
        return tags

    def get_operation_ids(self):
        """
        Extract operation IDs from the OpenAPI specification.
        :return: List of operation IDs defined in the OpenAPI specification.
        """
        paths = self.get_paths()
        operation_ids = []
        for path, methods in paths.items():
            for method, details in methods.items():
                operation_id = details.get('operationId')
                if operation_id:
                    operation_ids.append(operation_id)
        logging.info(f"Extracted {len(operation_ids)} operation IDs.")
        return operation_ids

    def get_servers(self):
        """
        Extract server information from the OpenAPI specification.
        :return: List of servers defined in the OpenAPI specification.
        """
        servers = self.openapi_data.get('servers', [])
        logging.info(f"Extracted {len(servers)} servers.")
        return servers

    def get_security_requirements(self):
        """
        Extract security requirements from the OpenAPI specification.
        :return: List of security requirements defined in the OpenAPI specification.
        """
        security_requirements = self.openapi_data.get('security', [])
        logging.info(f"Extracted {len(security_requirements)} security requirements.")
        return security_requirements

    def get_security_schemes(self):
        """
        Extract security schemes from the OpenAPI specification.
        :return: Dictionary of security schemes defined in the OpenAPI specification.
        """
        security_schemes = self.openapi_data.get('components', {}).get('securitySchemes', {})
        logging.info(f"Extracted {len(security_schemes)} security schemes.")
        return security_schemes

    def get_summaries_and_descriptions(self):
        """
        Extract summaries and descriptions for each operation in the OpenAPI specification.
        :return: Tuple of dictionaries containing summaries and descriptions.
        """
        paths = self.get_paths()
        summaries = {}
        descriptions = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                summary = details.get('summary')
                description = details.get('description')
                if summary:
                    summaries[f"{method.upper()} {path}"] = summary
                if description:
                    descriptions[f"{method.upper()} {path}"] = description
        logging.info(f"Extracted {len(summaries)} summaries and {len(descriptions)} descriptions.")
        return summaries, descriptions

    def update_requirements(self, requirements_path):
        """
        Check and update the requirements.txt file to ensure necessary packages are included.
        :param requirements_path: Path to the requirements.txt file.
        """
        required_packages = ['pyyaml', 'typer[all]', 'prance', 'fastapi', 'uvicorn']
        try:
            # Read the current requirements.txt content
            with open(requirements_path, 'r') as f:
                existing_requirements = f.read().splitlines()

            # Determine missing packages
            missing_packages = [pkg for pkg in required_packages if pkg.lower() not in (req.lower() for req in existing_requirements)]

            # If there are missing packages, append them to the file
            if missing_packages:
                with open(requirements_path, 'a') as f:
                    for pkg in missing_packages:
                        f.write(f"\n{pkg}")
                logging.info(f"Updated requirements.txt with missing packages: {missing_packages}")
            else:
                logging.info("All required packages are already present in requirements.txt")
        except Exception as e:
            logging.error(f"Failed to update requirements.txt: {e}")

    def validate_updates(self, requirements_path):
        """
        Validate that the requirements.txt file has been successfully updated.
        :param requirements_path: Path to the requirements.txt file.
        """
        try:
            with open(requirements_path, 'r') as f:
                existing_requirements = f.read().splitlines()
            for pkg in ['pyyaml', 'typer[all]', 'prance', 'fastapi', 'uvicorn']:
                if pkg.lower() not in (req.lower() for req in existing_requirements):
                    logging.error(f"Validation failed: {pkg} is missing from requirements.txt")
                    return False
            logging.info("Validation successful: All required packages are present in requirements.txt")
            return True
        except Exception as e:
            logging.error(f"Failed to validate requirements.txt: {e}")
            return False

if __name__ == "__main__":
    # Set the path to the OpenAPI specification file
    openapi_path = Path(__file__).parent.parent / 'openapi' / 'merged_openapi.yml'
    
    # Initialize the OpenAPIParser and extract different components
    parser = OpenAPIParser(openapi_path)
    schemas = parser.get_schemas()
    paths = parser.get_paths()
    parameters = parser.get_parameters()
    responses = parser.get_responses()
    request_bodies = parser.get_request_bodies()
    tags = parser.get_tags()
    operation_ids = parser.get_operation_ids()
    servers = parser.get_servers()
    security_requirements = parser.get_security_requirements()
    security_schemes = parser.get_security_schemes()
    summaries, descriptions = parser.get_summaries_and_descriptions()

    # Log extracted components to the log file
    logging.info(f"Schemas: {schemas}")
    logging.info(f"Paths: {paths}")
    logging.info(f"Parameters: {parameters}")
    logging.info(f"Responses: {responses}")
    logging.info(f"Request Bodies: {request_bodies}")
    logging.info(f"Tags: {tags}")
    logging.info(f"Operation IDs: {operation_ids}")
    logging.info(f"Servers: {servers}")
    logging.info(f"Security Requirements: {security_requirements}")
    logging.info(f"Security Schemes: {security_schemes}")
    logging.info(f"Summaries: {summaries}")
    logging.info(f"Descriptions: {descriptions}")

    # Set the path to the requirements.txt file and update it
    requirements_path = Path(__file__).parent.parent / 'openapi' / 'requirements.txt'
    parser.update_requirements(requirements_path)

    # Validate that the requirements.txt file has been updated
    parser.validate_updates(requirements_path)
