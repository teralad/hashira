# Hashira

Hashira is a powerful code generation tool that converts API specifications into Java code implementations using AI. It takes either OpenAPI specifications or Word documents containing API descriptions and generates corresponding Java classes.

## Features

- Parse OpenAPI specifications (YAML/JSON format)
- Parse Word documents containing API descriptions
- Generate Java code implementations using the Hugging Face bigcode/starcoderbase model
- Support for code archetypes to guide the generation process
- Automatic file splitting and organization of generated code

## Prerequisites

- Python 3.7 or higher
- Required Python packages (see Installation section)
- **Note**: Model downloading from Hugging Face may experience intermittent connectivity issues. The app includes fallback templates if model loading fails.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hashira.git
cd hashira
```

2. Install the required dependencies:
```bash
pip install transformers torch pyyaml python-docx
```

## Usage

### Command Line Interface

The basic command to generate code is:

```bash
python cli.py --input <path_to_api_spec> --output <output_directory> [--archetype <archetype_directory>]
```

#### Parameters:

- `--input`: Path to the OpenAPI specification (.yaml/.json) or Word document (.docx)
- `--output`: Directory where the generated code will be saved
- `--archetype` (optional): Path to a directory containing code archetypes to guide the generation

### Examples

#### Generate code from an OpenAPI specification:

```bash
python cli.py --input ./tests/sample_api.yaml --output ./generated_code
```

#### Generate code from a Word document:

```bash
python cli.py --input ./api_documentation.docx --output ./generated_code
```

#### Use code archetypes to guide generation:

```bash
python cli.py --input ./tests/sample_api.yaml --output ./generated_code --archetype ./archetypes
```

## How It Works

1. **Parsing**: The tool parses the input file (OpenAPI spec or Word doc) to extract the API description.
2. **Code Generation**: The extracted API description is fed to the LLM model along with any archetype code to generate Java implementations.
3. **Code Writing**: The generated code is analyzed and split into individual Java class files, which are saved to the specified output directory.

## Project Structure

```
hashira/
├── cli.py                  # Command-line interface
├── llm/
│   └── generator.py        # LLM-based code generation
├── parsers/
│   ├── openapi.py          # Parser for OpenAPI specifications
│   └── word.py             # Parser for Word documents
├── templates/
│   └── writer.py           # Code writer and file organization
└── tests/
    └── sample_api.yaml     # Sample OpenAPI specification for testing
```

## Customization

### Changing the Model

You can modify the LLM model used for code generation by updating the `model_name` variable in `llm/generator.py`:

```python
# Using a different Hugging Face hosted model
model_name = "your-preferred-model"  # Replace with any HF hosted code model
```

### Extending Parser Support

To add support for additional input formats, create a new parser in the `parsers` directory following the pattern of the existing parsers.

## License

[Specify your license here]

## Contributing

[Contribution guidelines]
