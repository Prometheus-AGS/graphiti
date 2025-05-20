from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from graphiti_core.database.db_factory import DatabaseType
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore


class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: str | None = Field(None)
    model_name: str | None = Field(None)
    embedding_model_name: str | None = Field(None)

    # Database configuration
    database_type: str = Field('neo4j', env='DATABASE_TYPE')
    database_uri: str | None = Field(None, env='DATABASE_URI')
    database_user: str | None = Field(None, env='DATABASE_USER')
    database_password: str | None = Field(None, env='DATABASE_PASSWORD')

    # Neo4j specific configuration (for backward compatibility)
    neo4j_uri: str | None = Field(None)
    neo4j_user: str | None = Field(None)
    neo4j_password: str | None = Field(None)

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    def get_db_uri(self) -> str:
        """Get the database URI based on configuration."""
        if self.database_uri:
            return self.database_uri
        return self.neo4j_uri

    def get_db_user(self) -> str:
        """Get the database user based on configuration."""
        if self.database_user:
            return self.database_user
        return self.neo4j_user

    def get_db_password(self) -> str:
        """Get the database password based on configuration."""
        if self.database_password:
            return self.database_password
        return self.neo4j_password

    def get_db_type(self) -> DatabaseType:
        """Get the database type as a DatabaseType enum."""
        if self.database_type.lower() == 'surrealdb':
            return DatabaseType.SURREALDB
        return DatabaseType.NEO4J


@lru_cache
def get_settings():
    settings = Settings()
    # Override the database URI to use localhost instead of surrealdb
    if settings.database_uri and 'surrealdb:8001' in settings.database_uri:
        settings.database_uri = settings.database_uri.replace('surrealdb:8001', 'localhost:8001')
    return settings


ZepEnvDep = Annotated[Settings, Depends(get_settings)]
