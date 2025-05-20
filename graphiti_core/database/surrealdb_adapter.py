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

    async def get_episodes(self) -> List[Dict[str, Any]]:
        """Get all episodes from SurrealDB.

        Returns:
            List of episodes
        """
        if not self.client:
            raise ConnectionError("Not connected to SurrealDB")

        result = self.client.query(
            """
            SELECT * FROM Episode
            ORDER BY created_at DESC
            """
        )
        if hasattr(result, "__await__"):
            result = await result
        
        # SurrealDB query returns a list of results per query
        if result and isinstance(result, list) and len(result) > 0:
            episodes = result[0].get('result', [])
            return episodes
        
        return []

    async def get_one_episode(self, episode_id: str) -> Optional[Dict[str, Any]]:
        """Get a single episode by ID from SurrealDB.

        Args:
            episode_id: Episode ID

        Returns:
            Episode data or None if not found
        """
        if not self.client:
            raise ConnectionError("Not connected to SurrealDB")

        result = self.client.query(
            """
            SELECT * FROM Episode
            WHERE id = $episode_id
            LIMIT 1
            """,
            {"episode_id": episode_id}
        )
        if hasattr(result, "__await__"):
            result = await result
        
        # SurrealDB query returns a list of results per query
        if result and isinstance(result, list) and len(result) > 0:
            episodes = result[0].get('result', [])
            if episodes and len(episodes) > 0:
                return episodes[0]
        
        return None
