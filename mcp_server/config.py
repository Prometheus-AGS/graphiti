import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    # Database configuration
    database_type: str
    database_uri: str
    database_user: str
    database_password: str
    database_namespace: Optional[str] = None
    database_db: Optional[str] = None
    
    # OpenAI configuration
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-4-turbo-preview"
    temperature: float = 0.0
    max_tokens: int = 1024


def get_config() -> Config:
    """Get the configuration from environment variables."""
    database_type = os.getenv("DATABASE_TYPE", "neo4j")
    
    # Set database URI based on type
    if database_type.lower() == "surrealdb":
        database_uri = os.getenv("DATABASE_URI", "ws://localhost:8001/rpc")
        database_user = os.getenv("DATABASE_USER", "root")
        database_password = os.getenv("DATABASE_PASSWORD", "root")
        database_namespace = os.getenv("DATABASE_NAMESPACE", "graphiti")
        database_db = os.getenv("DATABASE_DB", "graphiti")
    else:
        database_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        database_user = os.getenv("NEO4J_USER", "neo4j")
        database_password = os.getenv("NEO4J_PASSWORD", "neo4j")
        database_namespace = None
        database_db = None
    
    # OpenAI configuration
    openai_api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")
    temperature = float(os.getenv("TEMPERATURE", "0.0"))
    max_tokens = int(os.getenv("MAX_TOKENS", "1024"))
    
    return Config(
        database_type=database_type,
        database_uri=database_uri,
        database_user=database_user,
        database_password=database_password,
        database_namespace=database_namespace,
        database_db=database_db,
        openai_api_key=openai_api_key,
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
    )
