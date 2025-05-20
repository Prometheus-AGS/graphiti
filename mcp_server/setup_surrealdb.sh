#!/bin/bash
# This script sets up SurrealDB support in the Graphiti MCP server
set -e # Exit on error

# Install SurrealDB Python client
pip install surrealdb

# Create database directory if it doesn't exist
mkdir -p /app/.venv/lib/python3.11/site-packages/graphiti_core/database

# Create __init__.py file
cat > /app/.venv/lib/python3.11/site-packages/graphiti_core/database/__init__.py << 'EOL'
"""
Database adapters for Graphiti.
"""
EOL

# Create db_factory.py file
cat > /app/.venv/lib/python3.11/site-packages/graphiti_core/database/db_factory.py << 'EOL'
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
EOL

# Create db_interface.py file
cat > /app/.venv/lib/python3.11/site-packages/graphiti_core/database/db_interface.py << 'EOL'
"""
Interface for database adapters.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

# Type variables for driver and result types
DriverType = TypeVar('DriverType')
ResultType = TypeVar('ResultType')


class GraphDBInterface(Generic[DriverType, ResultType], ABC):
    """Interface for graph database adapters.
    
    This interface defines the methods that must be implemented by all database adapters.
    """
    
    @abstractmethod
    async def connect(self, uri: str, user: str, password: str, **kwargs) -> None:
        """Connect to the database.
        
        Args:
            uri: Database connection URI
            user: Database username
            password: Database password
            **kwargs: Additional connection parameters
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the database connection."""
        pass
    
    @abstractmethod
    async def get_driver(self) -> DriverType:
        """Get the database driver instance.
        
        Returns:
            Database driver instance
        """
        pass
    
    @abstractmethod
    async def get_session(self) -> Any:
        """Get a database session.
        
        Returns:
            Database session
        """
        pass
    
    @abstractmethod
    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> ResultType:
        """Execute a query against the database.
        
        Args:
            query: Query string
            parameters: Query parameters
            
        Returns:
            Query result
        """
        pass
    
    @abstractmethod
    async def build_indices(self, delete_existing: bool = False) -> None:
        """Build database indices.
        
        Args:
            delete_existing: Whether to delete existing indices
        """
        pass
    
    @abstractmethod
    async def clear_all_data(self) -> None:
        """Clear all data from the database."""
        pass
EOL

# Create neo4j_adapter.py file
cat > /app/.venv/lib/python3.11/site-packages/graphiti_core/database/neo4j_adapter.py << 'EOL'
"""
Neo4j adapter implementation for the GraphDBInterface.
"""
from typing import Any, Dict, List, Optional, cast

from neo4j import AsyncGraphDatabase, AsyncSession

from graphiti_core.database.db_interface import GraphDBInterface


class Neo4jAdapter(GraphDBInterface[AsyncGraphDatabase.Driver, List[Dict[str, Any]]]):
    """Neo4j implementation of the GraphDBInterface."""

    def __init__(self):
        """Initialize the Neo4j adapter."""
        self.driver = None

    async def connect(self, uri: str, user: str, password: str, **kwargs) -> None:
        """Connect to the Neo4j database.

        Args:
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
            **kwargs: Additional connection parameters (ignored for Neo4j)
        """
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self) -> None:
        """Close the Neo4j connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None

    async def get_driver(self) -> AsyncGraphDatabase.Driver:
        """Get the Neo4j driver instance.

        Returns:
            Neo4j driver instance

        Raises:
            ConnectionError: If the driver is not initialized
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")
        return self.driver

    async def get_session(self) -> AsyncSession:
        """Get a Neo4j session.

        Returns:
            Neo4j session

        Raises:
            ConnectionError: If the driver is not initialized
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")
        return self.driver.session()

    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a Cypher query against Neo4j.

        Args:
            query: Cypher query
            parameters: Query parameters

        Returns:
            Neo4j query result

        Raises:
            ConnectionError: If the driver is not initialized
            Exception: If the query execution fails
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        params = parameters or {}
        async with self.driver.session() as session:
            try:
                result = await session.run(query, params)
                records = await result.values()
                return cast(List[Dict[str, Any]], records)
            except Exception as e:
                raise Exception(f"Error executing Neo4j query: {str(e)}")

    async def build_indices(self, delete_existing: bool = False) -> None:
        """Build Neo4j indices and constraints.

        Args:
            delete_existing: Whether to delete existing indices
        """
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        # Define indices and constraints
        index_queries = [
            # Node indices
            "CREATE INDEX IF NOT EXISTS FOR (n:Episode) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Episode) ON (n.created_at)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Message) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Message) ON (n.timestamp)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Message) ON (n.role)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.type)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.group_id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Community) ON (n.id)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Community) ON (n.name)",
            
            # Relationship indices
            "CREATE INDEX IF NOT EXISTS FOR ()-[r:MENTIONS]-() ON (r.id)",
            "CREATE INDEX IF NOT EXISTS FOR ()-[r:HAS_MESSAGE]-() ON (r.id)",
            "CREATE INDEX IF NOT EXISTS FOR ()-[r:REFERS_TO]-() ON (r.id)",
            "CREATE INDEX IF NOT EXISTS FOR ()-[r:MEMBER_OF]-() ON (r.id)",
        ]
        
        if delete_existing:
            # Drop existing indices and constraints
            drop_queries = [
                "CALL apoc.schema.assert({}, {})",
            ]
            
            for query in drop_queries:
                await self.execute_query(query)
        
        # Create indices and constraints
        for query in index_queries:
            await self.execute_query(query)

    async def clear_all_data(self) -> None:
        """Clear all data from the Neo4j database."""
        if not self.driver:
            raise ConnectionError("Not connected to Neo4j")

        # Delete all nodes and relationships
        await self.execute_query("MATCH (n) DETACH DELETE n")
EOL

# Create surrealdb_adapter.py file
cat > /app/.venv/lib/python3.11/site-packages/graphiti_core/database/surrealdb_adapter.py << 'EOL'
"""
SurrealDB adapter implementation for the GraphDBInterface.
"""
from typing import Any, Dict, List, Optional, cast

from surrealdb import Surreal

from graphiti_core.database.db_interface import GraphDBInterface


class SurrealDBAdapter(GraphDBInterface[Surreal, List[Dict[str, Any]]]):
    """SurrealDB implementation of the GraphDBInterface."""

    def __init__(self):
        """Initialize the SurrealDB adapter."""
        self.client: Optional[Surreal] = None
        self.namespace: Optional[str] = None
        self.database: Optional[str] = None

    async def connect(self, uri: str, user: str, password: str, namespace: str = "graphiti", database: str = "graphiti") -> None:
        """Connect to the SurrealDB database.

        Args:
            uri: SurrealDB connection URI
            user: SurrealDB username
            password: SurrealDB password
            namespace: SurrealDB namespace (default: graphiti)
            database: SurrealDB database (default: graphiti)
        """
        try:
            # Store namespace and database
            self.namespace = namespace
            self.database = database
            
            # Initialize the client with the URI
            self.client = Surreal(uri)
            
            # Add debug logging
            import logging
            import sys
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            logger.debug(f"SurrealDB client initialized with URI: {uri}")
            logger.debug(f"SurrealDB client type: {type(self.client)}")
            logger.debug(f"Attempting to sign in with username: {user}")
            
            try:
                signin_result = self.client.signin({"username": user, "password": password})
                if hasattr(signin_result, "__await__"):
                    await signin_result
                logger.debug("Successfully signed in to SurrealDB")
                
                use_result = self.client.use(namespace, database)
                if hasattr(use_result, "__await__"):
                    await use_result
                logger.debug(f"Successfully using namespace {namespace} and database {database}")
            except Exception as e:
                logger.error(f"Error during SurrealDB connection: {str(e)}")
                raise ConnectionError(f"Failed to connect to SurrealDB: {str(e)}")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SurrealDB: {str(e)}")

    async def close(self) -> None:
        """Close the SurrealDB connection."""
        if self.client:
            await self.client.close()
            self.client = None

    async def get_driver(self) -> Surreal:
        """Get the SurrealDB client instance.

        Returns:
            SurrealDB client instance

        Raises:
            ConnectionError: If the client is not initialized
        """
        if not self.client:
            raise ConnectionError("Not connected to SurrealDB")
        return self.client

    async def get_session(self) -> Surreal:
        """Get the SurrealDB client (session equivalent).

        Returns:
            SurrealDB client instance

        Raises:
            ConnectionError: If the client is not initialized
        """
        if not self.client:
            raise ConnectionError("Not connected to SurrealDB")
        return self.client

    async def execute_query(
        self, query: str, parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SurrealQL query against SurrealDB.

        Args:
            query: SurrealQL query
            parameters: Query parameters

        Returns:
            SurrealDB query result

        Raises:
            ConnectionError: If the client is not initialized
            Exception: If the query execution fails
        """
        if not self.client:
            raise ConnectionError("Not connected to SurrealDB")

        params = parameters or {}
        try:
            result = self.client.query(query, params)
            if hasattr(result, "__await__"):
                result = await result
            return cast(List[Dict[str, Any]], result)
        except Exception as e:
            raise Exception(f"Error executing SurrealDB query: {str(e)}")

    async def build_indices(self, delete_existing: bool = False) -> None:
        """Build SurrealDB indices and schema definitions.

        Args:
            delete_existing: Whether to delete existing indices
        """
        if not self.client:
            raise ConnectionError("Not connected to SurrealDB")

        # Define schema and indices in SurrealQL
        schema_queries = [
            # Define tables (collections)
            "DEFINE TABLE Episode SCHEMAFULL",
            "DEFINE TABLE Message SCHEMAFULL",
            "DEFINE TABLE Entity SCHEMAFULL",
            "DEFINE TABLE MENTIONS SCHEMAFULL",
            "DEFINE TABLE HAS_MESSAGE SCHEMAFULL",
            "DEFINE TABLE REFERS_TO SCHEMAFULL",
            
            # Define fields with types
            "DEFINE FIELD id ON Episode TYPE string",
            "DEFINE FIELD created_at ON Episode TYPE datetime",
            "DEFINE FIELD title ON Episode TYPE string",
            "DEFINE FIELD summary ON Episode TYPE string",
            
            "DEFINE FIELD id ON Message TYPE string",
            "DEFINE FIELD timestamp ON Message TYPE datetime",
            "DEFINE FIELD role ON Message TYPE string",
            "DEFINE FIELD content ON Message TYPE string",
            
            "DEFINE FIELD id ON Entity TYPE string",
            "DEFINE FIELD type ON Entity TYPE string",
            "DEFINE FIELD name ON Entity TYPE string",
            "DEFINE FIELD properties ON Entity TYPE object",
            
            # Define indices
            "DEFINE INDEX episode_id ON Episode FIELDS id UNIQUE",
            "DEFINE INDEX episode_created_at ON Episode FIELDS created_at",
            "DEFINE INDEX message_id ON Message FIELDS id UNIQUE",
            "DEFINE INDEX message_timestamp ON Message FIELDS timestamp",
            "DEFINE INDEX message_role ON Message FIELDS role",
            "DEFINE INDEX entity_id ON Entity FIELDS id UNIQUE",
            "DEFINE INDEX entity_type ON Entity FIELDS type",
            "DEFINE INDEX entity_name ON Entity FIELDS name",
        ]
        
        if delete_existing:
            # Drop existing tables and their data
            await self.clear_all_data()
        
        # Execute schema and index creation queries
        for query in schema_queries:
            result = self.client.query(query)
            if hasattr(result, "__await__"):
                await result

    async def clear_all_data(self) -> None:
        """Clear all data from the SurrealDB database."""
        if not self.client:
            raise ConnectionError("Not connected to SurrealDB")

        # Remove all data
        for table in ["Episode", "Message", "Entity", "MENTIONS", "HAS_MESSAGE", "REFERS_TO"]:
            result = self.client.query(f"REMOVE TABLE {table}")
            if hasattr(result, "__await__"):
                await result
EOL

echo "SurrealDB support has been set up successfully!"
