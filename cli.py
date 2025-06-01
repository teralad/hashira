# -*- coding: utf-8 -*-
import argparse
import os
from pathlib import Path
from parsers.openapi import parse_openapi
from parsers.word import parse_word_doc
from llm.generator import generate_code_from_description
from templates.writer import write_generated_code

def main():
    parser = argparse.ArgumentParser(description="Generate API code from OpenAPI or Word docs using a local LLM")
    parser.add_argument("--input", type=str, required=True, help="Path to OpenAPI spec (.yaml/.json) or Word doc (.docx)")
    parser.add_argument("--output", type=str, required=True, help="Output directory for generated code")
    parser.add_argument("--archetype", type=str, default=None, help="Optional path to code archetype folder")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    if input_path.suffix in [".yaml", ".yml", ".json"]:
        api_description = parse_openapi(input_path)
    elif input_path.suffix == ".docx":
        api_description = parse_word_doc(input_path)
    else:
        raise ValueError("Unsupported file type. Use .yaml, .json, or .docx")

    archetype_snippets = ""
    if args.archetype:
        for path in Path(args.archetype).rglob("*.java"):
            archetype_snippets += "\n// FILE: {}\n".format(path.name) + path.read_text()

    print("\n📤 Generating code from description...")
    generated_code = generate_code_from_description(api_description, archetype_snippets)

    print("\n💾 Writing generated code to output folder...")
    write_generated_code(generated_code, output_path)

    print(f"\n✅ Code generation complete! Files saved to: {output_path}\n")

if __name__ == "__main__":
    main()