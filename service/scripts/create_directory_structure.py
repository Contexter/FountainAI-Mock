import logging
import os
from pathlib import Path

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO), format='%(asctime)s - %(levelname)s - %(message)s')

def create_directory_structure():
    base_dir = Path(__file__).parent.resolve()
    service_dir = base_dir.parent

    # Create necessary directories using a list comprehension
    directories = [service_dir / 'app', service_dir / 'app' / 'api' / 'routes', service_dir / 'app' / 'core', service_dir / 'app' / 'schemas']
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logging.info(f"Directory created at: {directory}")

    # Define the content of main.py
    main_content = """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
        return {"message": "Hello, FountainAI!"}
    """

    # Write the main.py to the /service/app directory with error handling
    main_path = directories[0] / 'main.py'
    try:
        main_path.write_text(main_content, encoding='utf-8')
        logging.info(f"main.py generated at: {main_path}")
    except IOError as e:
        logging.error(f"IO error occurred while writing main.py at {main_path}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error occurred while writing main.py at {main_path}: {e}")

    # Create __init__.py files to make directories Python packages
    init_files = [directories[0] / '__init__.py', directories[1] / '__init__.py', directories[2] / '__init__.py', directories[3] / '__init__.py']
    for init_file in init_files:
        try:
            init_file.touch(exist_ok=True)
            logging.info(f"__init__.py created at: {init_file}")
        except IOError as e:
            logging.error(f"IO error occurred while creating __init__.py at {init_file}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error occurred while creating __init__.py at {init_file}: {e}")

if __name__ == "__main__":
    create_directory_structure()
