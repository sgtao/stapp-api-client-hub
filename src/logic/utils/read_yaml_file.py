# read_yaml_file.py
import yaml
from fastapi import HTTPException


def read_yaml_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Config file not found: {file_path}"
        )
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=500, detail=f"Error parsing YAML file: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error reading config file: {e}"
        )
