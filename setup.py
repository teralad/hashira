from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hashira-mcp",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered Java code generator from API specifications - MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/teralad/hashira",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "pyyaml>=6.0",
        "python-docx>=0.8.11",
        "mcp>=1.0.0",
    ],
    extras_require={
        "web": ["streamlit>=1.28.0"],
    },
    entry_points={
        "console_scripts": [
            "hashira=cli:main",
            "hashira-mcp=server:main",
        ],
    },
    include_package_data=True,
)
