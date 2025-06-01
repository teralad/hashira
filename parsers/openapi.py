import yaml
import json

def parse_openapi(file_path):
    with open(file_path, 'r') as f:
        if file_path.suffix in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        elif file_path.suffix == '.json':
            data = json.load(f)
        else:
            raise ValueError("Unsupported OpenAPI file format")

    description = "OpenAPI Spec:\n"
    for path, methods in data.get("paths", {}).items():
        for method, details in methods.items():
            description += f"- {method.upper()} {path}: {details.get('summary', '')}\n"
    return description
