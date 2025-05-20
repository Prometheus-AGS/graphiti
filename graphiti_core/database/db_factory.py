"""
Factory for creating database adapters.
"""
from enum import Enum, auto
from typing import Any, Optional, Type

from graphiti_core.database.db_interface import GraphDBInterface
from graphiti_core.database.neo4j_adapter import Neo4jAdapter
from graphiti_core.database.surrealdb_adapter import SurrealDBAdapter


class DatabaseType(str, Enum):
    """Enum of supported database types."""
    NEO4J = "neo4j"
    SURREALDB = "surrealdb"


class DatabaseFactory:
    """Factory for creating database adapters.
    
    This factory creates instances of the appropriate database adapter based on the specified database type.
    """
    
    @staticmethod
    def create_db_adapter(db_type: DatabaseType) -> GraphDBInterface[Any, Any]:
        """Create a database adapter instance.
        
        Args:
            db_type: Type of database to create adapter for
            
        Returns:
            Database adapter instance
            
        Raises:
            ValueError: If an unsupported database type is specified
        """
        if db_type == DatabaseType.NEO4J:
            return Neo4jAdapter()
        elif db_type == DatabaseType.SURREALDB:
            return SurrealDBAdapter()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def get_adapter_class(db_type: DatabaseType) -> Type[GraphDBInterface[Any, Any]]:
        """Get the adapter class for a database type.
        
        Args:
            db_type: Type of database to get adapter class for
            
        Returns:
            Database adapter class
            
        Raises:
            ValueError: If an unsupported database type is specified
        """
        if db_type == DatabaseType.NEO4J:
            return Neo4jAdapter
        elif db_type == DatabaseType.SURREALDB:
            return SurrealDBAdapter
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
