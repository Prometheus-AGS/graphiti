#!/usr/bin/env python3
"""
Utility script to verify database configuration.
This can be run inside the Docker container to verify that environment variables are set correctly.
"""

import os
import sys

def print_env_vars():
    """Print environment variables related to database configuration."""
    print("Database Configuration Environment Variables:")
    print("-" * 50)
    
    db_vars = {
        "DATABASE_TYPE": os.environ.get("DATABASE_TYPE", "Not set"),
        "DATABASE_URI": os.environ.get("DATABASE_URI", "Not set"),
        "DATABASE_USER": os.environ.get("DATABASE_USER", "Not set"),
        "DATABASE_PASSWORD": os.environ.get("DATABASE_PASSWORD", "Not set (or masked)"),
    }
    
    for key, value in db_vars.items():
        print(f"{key}: {value}")
    
    # Check legacy Neo4j variables too
    neo4j_vars = {
        "NEO4J_URI": os.environ.get("NEO4J_URI", "Not set"),
        "NEO4J_USER": os.environ.get("NEO4J_USER", "Not set"),
        "NEO4J_PASSWORD": os.environ.get("NEO4J_PASSWORD", "Not set (or masked)"),
    }
    
    print("\nLegacy Neo4j Environment Variables:")
    print("-" * 50)
    for key, value in neo4j_vars.items():
        print(f"{key}: {value}")
    
    # Check Python version and packages
    print("\nPython Information:")
    print("-" * 50)
    print(f"Python version: {sys.version}")
    
    try:
        import graphiti_core
        print("graphiti_core package is installed")
        
        try:
            from graphiti_core.database.db_factory import DatabaseType
            print(f"Supported database types: {[t.value for t in DatabaseType]}")
        except ImportError:
            print("WARNING: Could not import DatabaseType")
    except ImportError:
        print("WARNING: graphiti_core package is not installed")
    
    try:
        import neo4j
        print(f"neo4j driver version: {neo4j.__version__}")
    except ImportError:
        print("WARNING: neo4j driver is not installed")
    
    try:
        import surrealdb
        print("surrealdb package is installed")
    except ImportError:
        print("WARNING: surrealdb package is not installed")


if __name__ == "__main__":
    print_env_vars() 