from setuptools import setup, find_packages

setup(
    name="graphiti-mcp-server",
    version="0.1.0",
    py_modules=["graphiti_mcp_server"],  # Include the main module directly
    install_requires=[
        "fastapi",
        "uvicorn",
        "surrealdb",
        "pydantic",
    ],
    entry_points={
        "console_scripts": [
            "graphiti-mcp-server=graphiti_mcp_server:main",
        ],
    },
)
