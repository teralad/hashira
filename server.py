#!/usr/bin/env python3
"""
Hashira MCP Server
Exposes API code generation capabilities as MCP tools for AI assistants
"""

import asyncio
import json
from pathlib import Path
from typing import Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from parsers.openapi import parse_openapi
from parsers.word import parse_word_doc
from llm.generator import generate_code_from_description
from templates.writer import write_generated_code

# Initialize MCP server
app = Server("hashira")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for code generation"""
    return [
        Tool(
            name="parse_openapi_spec",
            description="Parse an OpenAPI specification file (YAML/JSON) and extract API descriptions. Returns structured text describing all endpoints, methods, and summaries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the OpenAPI specification file (.yaml, .yml, or .json)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="parse_word_api_doc",
            description="Parse a Word document (.docx) containing API descriptions and extract the text content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the Word document (.docx)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="generate_java_code",
            description="Generate Java code implementation from an API description using AI. Uses bigcode/starcoderbase model with fallbacks. Optionally accepts archetype code as reference.",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_description": {
                        "type": "string",
                        "description": "Text description of the API to implement (can be from parse_openapi_spec or parse_word_api_doc)"
                    },
                    "archetype_code": {
                        "type": "string",
                        "description": "Optional reference Java code to guide the generation style and patterns"
                    }
                },
                "required": ["api_description"]
            }
        ),
        Tool(
            name="generate_code_from_file",
            description="End-to-end: Parse an API specification file (OpenAPI or Word) and generate Java code. Optionally saves to output directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Absolute path to input file (.yaml, .yml, .json, or .docx)"
                    },
                    "output_directory": {
                        "type": "string",
                        "description": "Optional absolute path to directory where generated .java files will be saved. If not provided, code is returned without saving."
                    },
                    "archetype_directory": {
                        "type": "string",
                        "description": "Optional absolute path to directory containing example .java files to use as archetypes"
                    }
                },
                "required": ["input_file"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    
    if name == "parse_openapi_spec":
        file_path = Path(arguments["file_path"])
        if not file_path.exists():
            return [TextContent(type="text", text=f"Error: File not found: {file_path}")]
        
        if file_path.suffix not in [".yaml", ".yml", ".json"]:
            return [TextContent(type="text", text=f"Error: Unsupported file type. Expected .yaml, .yml, or .json")]
        
        try:
            description = parse_openapi(file_path)
            return [TextContent(type="text", text=description)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error parsing OpenAPI spec: {str(e)}")]
    
    elif name == "parse_word_api_doc":
        file_path = Path(arguments["file_path"])
        if not file_path.exists():
            return [TextContent(type="text", text=f"Error: File not found: {file_path}")]
        
        if file_path.suffix != ".docx":
            return [TextContent(type="text", text=f"Error: Expected .docx file")]
        
        try:
            content = parse_word_doc(file_path)
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error parsing Word document: {str(e)}")]
    
    elif name == "generate_java_code":
        api_description = arguments["api_description"]
        archetype_code = arguments.get("archetype_code", "")
        
        try:
            generated_code = generate_code_from_description(api_description, archetype_code)
            return [TextContent(type="text", text=generated_code)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error generating code: {str(e)}")]
    
    elif name == "generate_code_from_file":
        input_file = Path(arguments["input_file"])
        output_dir = arguments.get("output_directory")
        archetype_dir = arguments.get("archetype_directory")
        
        if not input_file.exists():
            return [TextContent(type="text", text=f"Error: Input file not found: {input_file}")]
        
        # Parse input file
        try:
            if input_file.suffix in [".yaml", ".yml", ".json"]:
                api_description = parse_openapi(input_file)
            elif input_file.suffix == ".docx":
                api_description = parse_word_doc(input_file)
            else:
                return [TextContent(type="text", text="Error: Unsupported file type. Use .yaml, .json, or .docx")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error parsing input file: {str(e)}")]
        
        # Load archetype if provided
        archetype_snippets = ""
        if archetype_dir:
            archetype_path = Path(archetype_dir)
            if archetype_path.exists():
                for java_file in archetype_path.rglob("*.java"):
                    archetype_snippets += f"\n// FILE: {java_file.name}\n" + java_file.read_text()
        
        # Generate code
        try:
            generated_code = generate_code_from_description(api_description, archetype_snippets)
        except Exception as e:
            return [TextContent(type="text", text=f"Error generating code: {str(e)}")]
        
        # Save to output directory if provided
        if output_dir:
            try:
                output_path = Path(output_dir)
                output_path.mkdir(parents=True, exist_ok=True)
                write_generated_code(generated_code, output_path)
                return [TextContent(
                    type="text", 
                    text=f"Code generated successfully!\n\nOutput saved to: {output_path}\n\n{generated_code}"
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Error saving files: {str(e)}\n\nGenerated code:\n{generated_code}")]
        else:
            return [TextContent(type="text", text=generated_code)]
    
    else:
        return [TextContent(type="text", text=f"Error: Unknown tool: {name}")]

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
